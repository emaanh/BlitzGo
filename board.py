# from filesize import deep_getsizeof
from random import randint
import numpy as np
import matplotlib.pyplot as plt
import time
from collections import deque

class Board:
    
    WALL_NORTH = 1 << 0  # Bit 0
    WALL_SOUTH = 1 << 1  # Bit 1
    WALL_WEST = 1 << 2   # Bit 2
    WALL_EAST = 1 << 3   # Bit 3
    LOOK_UP_MASK = 61440
    
    def __init__(self,size):
        self.stones = [[None for _ in range(size)] for _ in range(size)]
        self.territory = [[None for _ in range(size)] for _ in range(size)]
        self.players = []
        self.territory_counts = {}
        self.total_territory_count = 0
        self.size = size
        self.size_2 = size**2
        self.move_history = []
        
        self.board_set = set()
        self.intermediateHash = 0
        self.current_hash = 0
        self.zobrist_table = self.initialize_zobrist_hash(size)
        
        self.control_map = [[0 for _ in range(size)] for _ in range(size)]
        self.vector_gravity_map = [[[0,0] for _ in range(size)] for _ in range(size)]
        self.tension_map = [[0 for _ in range(size)] for _ in range(size)]
        self.total_control = 0
        
        self.method_times = {}      

        # self.LOOKUP_TABLE = [self.hamming_weight(i) for i in range(16) > 2]
        # self.LOOKUP_TABLE = [int(bin(i).count('1') > 2) for i in range(16)]
        # self.count_bfs = 
        self.search = []
        self.search_num = 0
        self.total_bfs = 0
        self.heuristic_maps = self.create_heuristic_maps()
        # Load the compiled shared library


        
        
    def create_heuristic_maps(self):
        """
        Create a 3D NumPy array containing all 16 heuristic maps, 
        one for each combination of excluded walls.
        """
        rows = self.size
        cols = self.size

        heuristic_maps = np.zeros((15, rows, cols), dtype=int) 

        for exclude_walls in range(15):#2^n-1 because you cant have all 4 walls excluded.
            distances = []

            if not exclude_walls & self.WALL_NORTH:
                distances.append(np.arange(rows).reshape(-1, 1))
            if not exclude_walls & self.WALL_SOUTH:
                distances.append(rows - 1 - np.arange(rows).reshape(-1, 1))
            if not exclude_walls & self.WALL_WEST:
                distances.append(np.arange(cols).reshape(1, -1))
            if not exclude_walls & self.WALL_EAST:
                distances.append(cols - 1 - np.arange(cols).reshape(1, -1))

            distances = [d + np.zeros((rows, cols), dtype=int) for d in distances]

            heuristic_maps[exclude_walls] = np.minimum.reduce(distances)

        return heuristic_maps
    
    def update_board_change(self, player, position, direction):
        self.incrementTerritory(player, direction)
        # self.update_maps(player, position, direction)
        

    def playerNumberID(self, player):
        for i in range(len(self.players)):
            if self.players[i] == player:
                return i
            
    def player_to_state(self, player):
        if player is None:
            return 0
        elif player == self.players[0]:
            return 1
        elif player == self.players[1]:
            return 2
        else:
            raise ValueError("Unknown player identifier")
        
    def initialize_zobrist_hash(self, size):
        # Generate unique random numbers for two player states (1 and 2). State 0 (empty) will not affect the hash.
        zobrist_table = [[[0] * 3 for _ in range(size)] for _ in range(size)]
        for y in range(size):
            for x in range(size):
                for state in range(1, 3):  # Only generate numbers for player1 and player2
                    zobrist_table[y][x][state] = randint(1, 2**64 - 1)
        return zobrist_table
    
    
    def update_hash(self, position, old_player, new_player):
        x,y = position
        
        # Convert player objects or identifiers to state indices
        old_state = self.player_to_state(old_player)
        new_state = self.player_to_state(new_player)
        # XOR to remove old state effect and add new state effect
        if old_state != 0:
            self.current_hash ^= self.zobrist_table[y][x][old_state]
        if new_state != 0:
            self.current_hash ^= self.zobrist_table[y][x][new_state]

    #ANY HELPERS /CHECKS
    #if within bounds and its empty
    def isValidMove(self,position):
        x,y = position
        if not self.is_within_bounds(position):
            return False
        if self.stones[y][x] is not None:
            return False
        return True
    
    def isDuplicateMove(self):
        # hashed_board = self.hash_board()
        if self.current_hash in self.board_set:
            return True
        else:
            self.intermediateHash = self.current_hash
            return False 

    def removeStone(self, position):
        x,y = position
        self.update_hash(position, self.stones[y][x], None)
        self.update_board_change(self.stones[y][x], (x,y), -1)
        
        
        self.stones[y][x] = None
        
    def is_within_bounds(self, position):
        x, y = position
        return 0 <= x < self.size and 0 <= y < self.size
    
    #ALL PLACE STONE LOGIC
    def remove_last_move(self, position):
        x,y = position
        if self.stones[y][x] != None and self.territory[y][x] != None and self.stones[y][x] != self.territory[y][x]:
            self.update_board_change(self.territory[y][x], (x,y), 1)
            self.removeStone(position)
            return True
        return False
    
    def placeStone(self, player, position):
        start_time2 = time.time()
        
        x, y = position   
        
        start_time = time.time()
        if not self.isValidMove(position):
            # self.record_time("isValidMove", start_time)
            return 1  # for invalid move
        
        start_time = time.time()
        self.stones[y][x] = player 
        self.update_hash(position, None, player)
        # self.record_time("update_hash", start_time)

        start_time = time.time()
        if self.isDuplicateMove():
            # self.record_time("isDuplicateMove", start_time)
            
            start_time = time.time()
            self.removeStone(position)
            # self.record_time("removeStone", start_time)
            
            start_time = time.time()
            self.incrementTerritory(player, 1)  # Adjusting for duplicate check
            # self.record_time("incrementTerritory", start_time)
            
            return 2  # for duplicate move
        
        # self.record_time("isDuplicateMove", start_time)

        start_time = time.time()
        self.update_board_change(player, position, 1)
        # self.record_time("update_board_change", start_time)

        # start_time = time.time()
        captured = self.update_other_stones(player, position)
        # self.record_time("update_other_stones", start_time)

        start_time = time.time()
        self.move_history.append(position) 
        # self.record_time("move_history.append", start_time)
        
        # self.record_time("TOTAL PLACE STONE", start_time2)
        
        return 0  # for successful move
                
                
    #edge_case check
    def double_suicide(self, player, position):
        if not self.move_history:
            return
        x,y = position
        x_prev, y_prev = self.move_history[-1]
        if self.territory[y][x] != player and self.territory[y][x] != None and self.territory[y_prev][x_prev] == player:
            return True
        return False

    def update_other_stones(self, player, position):
        
        start_time = time.time()        
        captured = self.update_territories_and_remove_inside_stones(player, position) 
        penetrated = False
        # self.record_time("update_territories_and_remove_inside_stones", start_time)
        
        if captured:
            start_time = time.time()        

            penetrated = self.bfs_update_opponent_territory(player, position) 
            # self.record_time("bfs_update_opponent_territory", start_time)
            
        if penetrated or self.double_suicide(player, position):
            self.board_set.add(self.intermediateHash)
            
        if self.move_history:
            if (self.remove_last_move(self.move_history[-1])):
                captured = True
                
        self.removeSingleTerritory(position)
        return captured             
    
    def removeSingleTerritory(self, position):
        x,y = position
        if self.territory[y][x] != None and self.stones[y][x] != None and self.territory[y][x] != self.stones[y][x]:
            self.update_board_change(self.territory[y][x], (x,y), -1) #Fix
            
    def remove_stones_in_territory(self, player, total_territory):
        captured = False
        for territory in total_territory:
            x,y = territory
            if self.stones[y][x] != None and self.stones[y][x] != player:
                self.removeStone(territory)
                captured = True
        return captured
                
    def update_territories_and_remove_inside_stones(self, player, position):
        x,y = position
        total_territory = set()
        captured = False
        
        #This updates personal territory if you place inside your own territory.
        if self.territory[y][x] == player:
            self.update_board_change(player, position, -1)
            self.territory[y][x] = None
            return captured
        
        totalVisited = set()
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  
        for dx, dy in directions:
            nx, ny = position[0] + dx, position[1] + dy
            if self.is_within_bounds((nx, ny)) and self.stones[ny][nx] != player and (nx,ny) not in totalVisited:
                start_time = time.time()  
                enclosed_territory = self.dfs_enclosed_territory(player, (nx, ny), totalVisited)
                # self.record_time("bfs_enclosed_territory", start_time)
                
                start_time = time.time()  
                if enclosed_territory:
                    for (tx, ty) in enclosed_territory:
                        if self.territory[ty][tx] != player:
                            if self.territory[ty][tx] != None:
                                self.update_board_change(self.territory[ty][tx], (tx,ty), -1)
                            self.update_board_change(player, (tx,ty), 1) 
                            self.territory[ty][tx] = player

                        if self.stones[ty][tx] != None and self.stones[ty][tx] != player:
                            self.removeStone((tx, ty))
                            captured = True
                            
                # self.record_time("enclosed_territory", start_time)

        return captured
    
    def bfs_update_opponent_territory(self, player, start):
        anyUpdated = False
        queue = [start]        
        queue = deque([start])
        x,y = start
        
        #check at start position
        if self.is_within_bounds((x,y)) and self.territory[y][x] != player and self.territory[y][x] != None:
            self.update_board_change(self.territory[y][x], (x,y), -1)
            self.territory[y][x] = None
            anyUpdated = True
            
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
                nx, ny = x + dx, y + dy
                
                if self.is_within_bounds((nx,ny)) and self.territory[ny][nx] != player and self.territory[ny][nx] != None:
                    queue.append((nx, ny))
                    self.update_board_change(self.territory[ny][nx], (nx,ny), -1) #Fix
                    self.territory[ny][nx] = None
                    anyUpdated = True
                    
        return anyUpdated

        
    def dfs_enclosed_territory(self, player, start, totalVisited: set):
        queue = [start]
        totalVisited.add(start)
        visited = set(queue)
        walls_touched = 0
        # result = self.my_lib.sqrt(9.0)

        while queue:
            x, y = queue.pop()
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
                
        # # Call the function
                
        # print(f"Result: {result}")
                nx, ny = x + dx, y + dy
                
                if (nx, ny) in visited:
                    continue  
                
                if ny < 0:
                    walls_touched |= self.WALL_NORTH
                elif ny >= self.size:
                    walls_touched |= self.WALL_SOUTH
                elif nx < 0:
                    walls_touched |= self.WALL_WEST
                elif nx >= self.size:
                    walls_touched |= self.WALL_EAST
                else:
                    if self.stones[ny][nx] != player:
                        queue.append((nx, ny))
                        totalVisited.add((nx, ny))
                        visited.add((nx, ny))                
            if self.LOOK_UP_MASK & (1 << walls_touched):
                return None
                    
        return visited  
    
    #Operates on Heidari's Fundemental Win Condition Theorem
    def stability_test(self, position):
        x,y = position
        player = self.territory[y][x]
        
        if player == None:
            raise Exception("Win check called when board wans't filled.")
        
        countCorner = 0
                
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:  
            nx, ny = x + dx, y + dy
            if self.is_within_bounds((nx,ny)) and self.stones[ny][nx] != None and self.stones[ny][nx] != player:
                countCorner +=1
        
        if countCorner >= 2:
            return False
        
        if countCorner == 1:
            if x == 0 or y ==0 or x == self.size-1 or y == self.size-1:
                return False

        return True
                    
    def checkGameOver(self):      
        for y in range(self.size):
            for x in range(self.size):
                if self.territory[y][x] != None and not self.stability_test((x,y)):
        
                    return False
        return True
    
    #ANYTHING TO DO WITH TERRITORY COUNTS
    def initalizeTerritoryCounts(self, player):
        self.territory_counts[player] = 0
        
    def totalTerritory(self):
        return self.total_territory_count
    
    def incrementTerritory(self, player, delta):
        self.territory_counts[player] +=delta
        self.total_territory_count += delta
        
    def printBothTerritories(self):
        for player in self.territory_counts:
            print(f"{player.name}'s territory: ", self.territory_counts[player])
            
        print("Total: ", self.total_territory_count)


        
        

