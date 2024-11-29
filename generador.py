import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.colors import ListedColormap

def read_scenario(file_path):

    escenario = {
        "dimensiones": None,
        "q0": None,
        "qf": None,
        "dFrente": None,
        "dDerecha": None,
        "obstaculos": [],
    }

    with open(file_path, 'r') as file:
        #Save dimension
        line = file.readline().strip()
        _, width, height = line.split(',')
        escenario["dimensiones"] = (float(width), float(height))

        #Save q0
        line = file.readline().strip()
        _,x,y,theta = line.split(',')
        escenario["q0"] = (float(x), float(y), float(theta))

        #Save qf
        line = file.readline().strip()
        _,x,y,theta = line.split(',')
        escenario["qf"] = (float(x), float(y), float(theta))

        #Save dFrente
        line = file.readline().strip()
        _, dis = line.split(',')
        escenario["dFrente"] = float(dis)

        #Save dDerecha
        line = file.readline().strip()
        _, dis = line.split(',')
        escenario["dDerecha"] = float(dis)

        #Get number of obstacles
        line = file.readline().strip()
        _, numObstaculos = line.split(',')

        #Save obstacles
        for i in range(int(numObstaculos)):

            point1 = file.readline().strip()
            _,x1,y1 = point1.split(',')
            obs1 = (float(x1), float(y1))

            point2 = file.readline().strip()
            _,x2,y2 = point2.split(',')
            obs2 = (float(x2), float(y2))

            escenario["obstaculos"].append((obs1, obs2))

    return escenario


def wavefront_pathfind(escenario):

    

    grid = generar_grid(escenario)

    grid_original = np.copy(grid)

    width, height = escenario['dimensiones']
    width = int(width * 2) 
    height = int(height * 2) 
    
    qf = escenario['qf']
    x = int(np.ceil(qf[0] * 2)) -1
    y = int(np.ceil(qf[1] * 2)) -1
    qf = (y,x)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    queue =[qf]

    while queue:

        current = queue.pop(0)
        current_value = grid[current]


        for move in moves:
            neighbor = (current[0] + move[0], current[1] + move[1])
            if (0 <= neighbor[0] < height and 0 <= neighbor[1] < width and grid[neighbor] == 0):
                grid[neighbor] = current_value + 1
                queue.append(neighbor)

    q0 = escenario['q0']
    x = int(np.ceil(q0[0] * 2)) -1
    y = int(np.ceil(q0[1] * 2)) -1
    q0 = (y,x)
    
    path = [q0]
    current = q0
    
    while current != qf:

        min_value = grid[current]
        next_cell = None
        
        for move in moves:
            neighbor = (current[0] + move[0], current[1] + move[1])
            if (0 <= neighbor[0] < height and 0 <= neighbor[1] < width and grid[neighbor] != -1):
                if grid[neighbor] < min_value:
                    min_value = grid[neighbor]
                    next_cell = neighbor
        if next_cell:
            path.append(next_cell)
            current = next_cell
        else:
            raise ValueError("No path found")
        
    
        
    grid_original[q0] = -2


    for i,value in enumerate(path):
        y = (value[0]/height)*(height/2) + 0.25
        x = (value[1]/width)*(width/2) + 0.25
        path[i] = (y,x)

    visualize_grid(grid_original, escenario, path)

    return path



def print_state(grid):
    reversed_array = np.flipud(grid)
    print(reversed_array)



def generar_grid(escenario):
    x_max, y_max = escenario['dimensiones']

    grid_width = int(x_max * 2) 
    grid_height = int(y_max * 2)

    grid = np.zeros((grid_height, grid_width))

    obstacles = escenario['obstaculos']

    for (x1, y1), (x2, y2) in obstacles:
        
        x = int(np.ceil(x1 + x2))-1
        y = int(np.ceil(y1 + y2))-1

        try:
            grid[y][x] = -1

        except:
           pass

    qf = escenario['qf']
    x = int(np.ceil(qf[0] * 2)) -1
    y = int(np.ceil(qf[1] * 2)) -1
    grid[y][x] = 1

    return grid


def visualize_grid(grid, escenario, path):

    x_max, y_max = escenario['dimensiones']

    q0 = escenario["q0"]
    qf = escenario["qf"]
    

    # Create a figure for visualization
    plt.figure()

    plt.plot(q0[0], q0[1], 'go', label="Start (q0)")  # Start point in green
    plt.plot(qf[0], qf[1], 'ro', label="End (qf)") 

    plt.xlim(0, x_max)
    plt.ylim(0, y_max)

    cmap = ListedColormap(['green', 'black', 'white', 'red'])

    # Display the grid using a color map
    plt.imshow(grid, cmap=cmap, origin='lower', extent=[0, x_max, 0, y_max], vmin=-2, vmax=1)

    # Set the title and axis labels
    plt.title("Grid Visualization with Obstacles")
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.grid(which='both', color='gray', linestyle='--', linewidth=0.5)
    plt.xticks(np.arange(0, x_max + 0.5, 0.5))
    plt.yticks(np.arange(0, y_max + 0.5, 0.5))


    y, x = zip(*path)
    plt.plot(x,y)



def visualizar_escenario(scenario):
    # Create plot without subplot
    plt.figure()
    
    # Set plot dimensions
    width, height = scenario["dimensiones"]
    plt.xlim(0, width)
    plt.ylim(0, height)
    
    # Plot start and end points
    q0 = scenario["q0"]
    qf = scenario["qf"]
    plt.plot(q0[0], q0[1], 'go', label="Start (q0)")  # Start point in green
    plt.plot(qf[0], qf[1], 'ro', label="End (qf)")    # End point in red
    
    # Plot obstacles as rectangles
    for ((x1, y1), (x2, y2)) in scenario["obstaculos"]:
        # Calculate rectangle width and height
        rect_width = abs(x2 - x1)
        rect_height = abs(y2 - y1)
        bottom_left_x = min(x1, x2)
        bottom_left_y = min(y1, y2)
        
        # Create a rectangle patch and add it to the plot
        rect = patches.Rectangle((bottom_left_x, bottom_left_y), rect_width, rect_height, linewidth=1, edgecolor='black', facecolor='black', alpha=0.5)
        plt.gca().add_patch(rect)
    
    # Add labels and legend
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Robot Path Planning Scenario")
    plt.legend()

    plt.grid(which='both', color='gray', linestyle='--', linewidth=0.5)
    plt.xticks(np.arange(0, width + 0.5, 0.5))
    plt.yticks(np.arange(0, height + 0.5, 0.5))
    

def format_path(path, escenario):

    formatted_path = [] 

    # Iterate through the path
    for i in range(len(path)):

        if i == 0:
            yant, xant = path[i]

        else:
            yant, xant = path[i-1]

        y, x = path[i]

        vector1 = np.array([1, 0])  # Fixed vector
        vector2 = np.array([x-xant, y-yant]) 

        dot_product = np.dot(vector1, vector2)
        magnitude1 = np.linalg.norm(vector1)
        magnitude2 = np.linalg.norm(vector2)

        angle_degrees = escenario['q0'][2]

        if i != 0:
            angle_radians = np.arccos(dot_product / (magnitude1 * magnitude2))
            angle_degrees = np.degrees(angle_radians)

        formatted_path.append((x,y,float(angle_degrees)))

    formatted_path.append(escenario['qf'])

    return formatted_path

def export_path(formatted_path, file_name):


    with open(file_name, "w") as file:

        for tup in formatted_path:
            file.write(",".join(map(str, tup)) + "\n")




for num in range(1,7):

    escenario = read_scenario(f"./Escenas-txt/Escena-Problema{num}.txt")
    path = wavefront_pathfind(escenario)
    formatted_path = format_path(path, escenario)
    export_path(formatted_path, f"./Paths-txt/Escena-Path{num}.txt")

plt.show()
