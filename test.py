import numpy as np
import time

def distance_from_edge_exclude_walls(board_size, exclude_walls):

    rows, cols = board_size  
    distances = []
    
    if not exclude_walls & WALL_NORTH:
        distances.append(np.arange(rows).reshape(-1, 1))
    if not exclude_walls & WALL_SOUTH:
        distances.append(rows - 1 - np.arange(rows).reshape(-1, 1)) 
    if not exclude_walls & WALL_WEST:
        distances.append(np.arange(cols).reshape(1, -1)) 
    if not exclude_walls & WALL_EAST:
        distances.append(cols - 1 - np.arange(cols).reshape(1, -1)) 

    distances = [d + np.zeros((rows, cols), dtype=int) for d in distances]
    return np.minimum.reduce(distances)

# Correct usage
board_size = (13, 13)


WALL_NORTH = 1 << 0  # Bit 0
WALL_SOUTH = 1 << 1  # Bit 1
WALL_WEST = 1 << 2   # Bit 2
WALL_EAST = 1 << 3   # Bit 3

exclude_walls = 0
exclude_walls |= WALL_NORTH


start = time.time()
for i in range(100000):
    pass
print(time.time()-start)
start = time.time()
for i in range(100000):
    result = distance_from_edge_exclude_walls(board_size, exclude_walls)
print(time.time()-start)

# Print the full 2D array
print(result)