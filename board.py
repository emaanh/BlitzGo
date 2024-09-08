# from filesize import deep_getsizeof
from random import randint
import numpy as np
import matplotlib.pyplot as plt


class Board:
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
        

    def update_board_change(self, player, position, direction):
        self.incrementTerritory(player, direction)
        self.update_maps(player, position, direction)
        
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
        x, y = position   
        
        if not self.isValidMove(position):
            return 1 #for invalid move
        
        self.stones[y][x] = player 
        self.update_hash(position, None, player)

        if self.isDuplicateMove():
            self.removeStone(position)
            self.incrementTerritory(player, 1) #The issue is that remove stone removes a territory but we hadn't added it yet until duplicate check so we shall add the territory back now. 
            return 2 #for duplicate move
        
        self.update_board_change(player, position, 1)
                   
        captured = self.update_other_stones(player,position)
           
        self.move_history.append(position) 
        return 0 # for successful move.
        
        # print("Size of set: ",deep_getsizeof(self.board_set)/1000, "KB")
                
                
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
        
        captured = self.update_territories_and_remove_inside_stones(player, position) 
        penetrated = False
        
        if captured:
            penetrated = self.bfs_update_opponent_territory(player, position) 
            
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
                enclosed_territory = self.bfs_enclosed_territory(player, (nx, ny), totalVisited)
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

        return captured
    
    def bfs_update_opponent_territory(self, player, start):
        anyUpdated = False
        queue = [start]        
        x,y = start
        
        #check at start position
        if self.is_within_bounds((x,y)) and self.territory[y][x] != player and self.territory[y][x] != None:
            self.update_board_change(self.territory[y][x], (x,y), -1)
            self.territory[y][x] = None
            anyUpdated = True
            
        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
                nx, ny = x + dx, y + dy
                
                if self.is_within_bounds((nx,ny)) and self.territory[ny][nx] != player and self.territory[ny][nx] != None:
                    queue.append((nx, ny))
                    self.update_board_change(self.territory[ny][nx], (nx,ny), -1) #Fix
                    self.territory[ny][nx] = None
                    anyUpdated = True
                    
        return anyUpdated


    def bfs_enclosed_territory(self, player, start, totalVisited: set):
        queue = [start]
        totalVisited.add(start)
        walls_touched = set()
        visited = set(queue)

        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
                nx, ny = x + dx, y + dy
                
                boolTouchWall = False
                if ny < 0:
                    walls_touched.add('north')
                    boolTouchWall = True
                if ny >= self.size:
                    walls_touched.add('south')
                    boolTouchWall = True
                if nx < 0:
                    walls_touched.add('west')
                    boolTouchWall = True
                if nx >= self.size:
                    walls_touched.add('east')
                    boolTouchWall = True    
                               
                
                if len(walls_touched)>2:
                    return None
                if boolTouchWall or (nx, ny) in visited:
                    continue

                if (nx, ny) not in visited and self.stones[ny][nx] != player:                    
                    queue.append((nx, ny))
                    totalVisited.add((nx, ny))
                    visited.add((nx, ny))
                    
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
    
    
    
    #Anything to do with AI move generation:
    def generateValidMoves_old(self, player, num_moves_considered):
        move_scores = {}  # Dictionary to store moves and their scores
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1), (1, 1), (-1, -1)]  # All 8 directions
        
        for y in range(self.size):
            for x in range(self.size):
                if self.stones[y][x] is not None:  # Only check from occupied cells

                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:  # Ensure within bounds
                            if self.stones[ny][nx] is None:  # Check if the adjacent cell is empty
                                
                                new_hash = self.current_hash^ self.zobrist_table[ny][nx][self.player_to_state(player)]
                                
                                if new_hash not in self.board_set:
                                    
                                    if (nx, ny) not in move_scores:
                                        move_scores[(nx, ny)] = 1
                                    else:
                                        move_scores[(nx, ny)] += 1  # Increment score for each adjacent stone

        # Sort the moves by their scores in descending order and get the top 20
        sorted_moves = sorted(move_scores.items(), key=lambda item: item[1], reverse=True)
        top_moves = [move for move, score in sorted_moves[:num_moves_considered]]  
        if not top_moves:
            x = randint(1,self.size-2)
            y = randint(1,self.size-2)
            top_moves.append((x,y))
        return top_moves  # Returns a list of positions
    
    def generateValidMoves(self, player, num_moves_considered):
        move_scores = {}  # Dictionary to store moves and their scores
        
        for y in range(self.size):
            for x in range(self.size):
                if self.stones[y][x] is None:  # Only check from occupied cells
                    new_hash = self.current_hash^ self.zobrist_table[y][x][self.player_to_state(player)]
                    if new_hash not in self.board_set:  
                        
                        if self.territory[y][x] != None and self.territory[y][x] != player:
                            countCorner = 0
                            for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:  
                                nx, ny = x + dx, y + dy
                                if self.is_within_bounds((nx,ny)) and self.stones[ny][nx] == player:
                                    countCorner +=1
                            if countCorner >=2:
                                move_scores[(x, y)] = self.tension_map[y][x]
                                
                        elif self.tension_map[y][x]>0: 
                            move_scores[(x, y)] = self.tension_map[y][x]

        # Sort the moves by their scores in descending order and get the top 20
        sorted_moves = sorted(move_scores.items(), key=lambda item: item[1], reverse=True)
        top_moves = [move for move, score in sorted_moves[:num_moves_considered]]  
        
        if not top_moves:
            x = randint(1,self.size-2)
            y = randint(1,self.size-2)
            print("random: ", (x,y))
            print(self.tension_map[y][x])
            top_moves.append((x,y))
            
        # print(top_moves)
        return top_moves  # Returns a list of positions
    
    
    
    #ANYTHING TO DO WITH PRINTING OR HASHING    
    
    def original_hash_board(self):
        return tuple(tuple(row) for row in self.stones)
    
    def __str__(self):
        board_str = "  " + ''.join([str(i + 1).rjust(2) for i in range(self.size)]) + "\n"  # Adding column headers
        for index, row in enumerate(self.stones):
            row_str = str(index + 1).rjust(2) + ' '  # Adding row numbers
            row_str += ' '.join(['.' if player is None else player.symbol for player in row])
            board_str += row_str + "\n"
        return board_str
        
    def flattenBoard(self):
        flattenList = [0 for x in range(self.size_2)]
        for y in range(self.size):
            for x in range(self.size):
                if self.stones[y][x] == None:
                    if self.territory[y][x] == None:
                        pass
                    else:
                        flattenList[y*self.size + x] = self.territory[y][x].getTerritoryCode()
                else:
                    flattenList[y*self.size + x] = self.stones[y][x].getStoneCode()
                    
        return flattenList
    
    def TerritoryBoard(self):
        board_str = "  " + ''.join([str(i + 1).rjust(2) for i in range(self.size)]) + "\n"  # Adding column headers
        for index, row in enumerate(self.territory):
            row_str = str(index + 1).rjust(2) + ' '  # Adding row numbers
            row_str += ' '.join(['.' if stone is None else stone.symbol for stone in row])
            board_str += row_str + "\n"
        return board_str  
    
    #Anything to do with MAPS/FIELDS
    def eval(self):
        return self.total_control
                
    def update_other_maps_at_position(self, position):
        x,y = position
        self.tension_map[y][x] = self.vector_gravity_map[y][x][0] * self.vector_gravity_map[y][x][1]
        old_control_val = self.control_map[y][x]
        new_control_val = self.vector_gravity_map[y][x][0]* -1 + self.vector_gravity_map[y][x][1]
        self.control_map[y][x] = new_control_val
        
        self.total_control += new_control_val-old_control_val
    
    def update_maps(self, player, position, direction):
        queue = [(position, 1)] #distance from source
        x,y = position
        index_of_color = (0 if player.isBlack else 1) #black 0, white 1, black -1, white 1
        visited = set()
        
        self.vector_gravity_map[y][x][index_of_color] += direction #distance 1 away. #direction times 1 over distance squared
        self.update_other_maps_at_position(position)
 

        while(queue):
            position, distance = queue.pop(0)
            x,y = position
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:  
                nx, ny = x + dx, y + dy
                n_pos = (nx,ny)
                
                if self.is_within_bounds(n_pos) and n_pos not in visited:
                    
                    visited.add(n_pos)
                    queue.append((n_pos, distance+1))
                    
                    self.vector_gravity_map[ny][nx][index_of_color] += direction*(1/(distance**2))
                    self.update_other_maps_at_position(n_pos)



        
        

