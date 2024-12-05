import rclpy
import math
import time
from rclpy.node import Node
from geometry_msgs.msg import PoseArray
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class PathFollow(Node):

    num = int(input("Numero de escena a correr: "))
    file_path = f"../Paths-txt/Escena-Path{num}.txt"
    path = []

    with open(file_path) as file:

        lines = file.readlines()

        for line in lines:

            line = line.strip(",")
            elements = tuple(map(float, line.split(",")))
            path.append((elements))

    def __init__(self):
        super().__init__("pathFollow")

        self.pose_subscriber = self.create_subscription(PoseArray, "/world/pioneer3_world/pose/info", self.callback_sensor, 10)
        self.sensor_subscriber = self.create_subscription(LaserScan, "/lidar", self.callback_lidar, 10)
        self.cmd_vel_publisher_ = self.create_publisher(Twist, "/model/pioneer3dx/cmd_vel", 10)

        # Robot's current position and orientation
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.current_index = 0  # Index of the current waypoint in the path
        self.path_completed = False  # Flag to indicate if the path is completed

        self.d_frente = 0.0
        self.d_derecha = 0.0

        # Timer for control logic
        self.control_timer = self.create_timer(0.1, self.follow_path)  # Execute control logic at 10 Hz

        self.get_logger().info("Initialized successfully.")


    def callback_lidar(self, msg):
        lecturas = msg.ranges   
        self.d_derecha = lecturas[0]
        self.d_frente = lecturas[4]


    def callback_sensor(self, msg):
        """
        Callback to update robot's position and orientation as quickly as possible.
        """
        robot_info = msg.poses[1]
        ori = robot_info.orientation
        pos = robot_info.position

        self.x = pos.x
        self.y = pos.y
        self.yaw = (2 * math.atan2(ori.z, ori.w)) % (2 * math.pi)

    def follow_path(self):
        """
        Control logic for following the path. Runs in a separate timer callback.
        """
        if self.path_completed:
            self.stop_robot()
            rclpy.shutdown()  # Shut down the program
            return

        target_x, target_y, target_theta_deg = self.path[self.current_index]
        target_theta = math.radians(target_theta_deg)

        # Check if the robot is aligned with the target orientation
        if not self.is_oriented(target_theta):
            self.rotate_towards(target_theta)
        # Check if the robot has reached the target position
        elif not self.reached_target(target_x, target_y, target_theta_deg):
            self.move_straight()
        else:
            #Relocalizar
            if self.current_index>0:

                if (self.path[self.current_index][0] == self.path[self.current_index-1][0] and self.path[self.current_index][1] == self.path[self.current_index-1][1]) and self.current_index + 1 < len(self.path):

                    self.stop_new()

                    time.sleep(2)

                    q = self.path[self.current_index + 1]

                    print(f"qf = {q[0]},{q[1]},{q[2]}")
                    print(f"qf-est = {round(self.x, 4)},{round(self.y,4)},{round(math.degrees(self.yaw),4)}")

                    self.calculate_real()


            self.get_logger().info(f"Reached waypoint {self.current_index + 1}/{len(self.path)}")
            self.current_index += 1
            if self.current_index >= len(self.path):
                self.path_completed = True  # Mark path as completed

    def is_oriented(self, target_theta):
        yaw_diff = abs(target_theta - self.yaw)
        return yaw_diff < 0.08  # Adjust tolerance as needed

    def rotate_towards(self, target_theta):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.1 if (target_theta - self.yaw) > 0 else -0.1
        self.cmd_vel_publisher_.publish(msg)

    def reached_target(self, target_x, target_y, target_theta_deg):
        """
        Checks if the robot has reached the target position based on its orientation.
        """

        if self.current_index>0 and (self.path[self.current_index][0] == self.path[self.current_index-1][0] and self.path[self.current_index][1] == self.path[self.current_index-1][1]):

            return True

        elif target_theta_deg == 90.0 or target_theta_deg == 270.0:  # Robot aligned vertically
            return abs(self.y - target_y) < 0.1
        elif target_theta_deg == 0.0 or target_theta_deg == 180.0:  # Robot aligned horizontally
            return abs(self.x - target_x) < 0.1
        else:  # For other angles, check both x and y
            return abs(self.x - target_x) < 0.1 and abs(self.y - target_y) < 0.1

    def move_straight(self):
        msg = Twist()
        msg.linear.x = 0.2  # Forward speed
        msg.angular.z = 0.0
        self.cmd_vel_publisher_.publish(msg)


    def stop_new(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_vel_publisher_.publish(msg)


    def stop_robot(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_vel_publisher_.publish(msg)

        self.get_logger().info("Path Finished")

        time.sleep(2)

        q = self.path[len(self.path)-1]

        print(f"q0 = {q[0]},{q[1]},{q[2]}")
        print(f"q0-est = {round(self.x, 4)},{round(self.y,4)},{round(math.degrees(self.yaw),4)}")


    def calculate_real(self):

        df_th = 0.75316
        dd_th = 0.70617 

        ef = self.d_frente - df_th
        er = self.d_derecha - dd_th

        qf = self.path[self.current_index]

        qf_act =  (qf[0] - er, qf[1] - ef)

        angle = 90.0

        print(f"qf-act = {round(qf_act[0],4)}, {round(qf_act[1], 4)}, {round(angle,4)}")


def main(args=None):
    rclpy.init(args=args)
    node = PathFollow()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
