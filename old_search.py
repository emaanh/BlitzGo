    def dfs_enclosed_territory(self, player, start, totalVisited: set):
        
        # start_time_total = time.time()
        
        # start_time = time.time()
        # queue = deque([start])
        queue = [start]
        totalVisited.add(start)
        walls_touched = 0
        # walls_touched = set()
        visited = set(queue)
        # self.record_time("init", start_time)

        count_bfs = 0
        x, y = start


        while queue:
            # start_time = time.time()
            x, y = queue.pop()
            # self.record_time("pop", start_time)
            # self.p(visited)
            # time.sleep(.125)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
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
                        
                if self.LOOKUP_TABLE[walls_touched]:
                    self.search.append(count_bfs)
                    return None
                    
                count_bfs+=1
                
        # self.search.append(count_bfs)
        # self.search_num +=1
                    
                    
        return visited  
    
    
        
    def update_priority(self, value, new_priority):
        return (new_priority, value)


    def p_dfs_enclosed_territory(self, player, start, totalVisited: set):
        
        # start_time_total = time.time()
        
        # start_time = time.time()
        # queue = deque([start])
        queue = [start]
        totalVisited.add(start)
        walls_touched = 0
        # walls_touched = set()
        visited = set(queue)
        # self.record_time("init", start_time)

        count_bfs = 0
        x, y = start


        while queue:
            # start_time = time.time()
            x, y = queue.pop()
            # self.record_time("pop", start_time)
            # self.p(visited)
            # time.sleep(.125)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
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
                        # heuristic_value = self.heuristic_maps[walls_touched][ny][nx]
                        if False:
                        # if queue and heuristic_value > self.heuristic_maps[walls_touched][queue[-1][1]][queue[-1][0]]:
                        #     temp = queue.pop()                            
                        #     queue.append((nx, ny))
                        #     totalVisited.add((nx, ny))
                        #     visited.add((nx, ny))
                        #     queue.append(temp)
                        else:
                            queue.append((nx, ny))
                            totalVisited.add((nx, ny))
                            visited.add((nx, ny))
                        
                if self.LOOKUP_TABLE[walls_touched]:
                    self.search.append(count_bfs)
                    return None
                    
                count_bfs+=1
                
        # self.search.append(count_bfs)
        # self.search_num +=1
                    
                    
        return visited  
                
                    
        # count_bfs+=1
        # self.total_bfs +=1
                
        self.search.append(count_bfs)
        # self.search_num +=1
                    
                    
        return visited  

    def greedy_bfs_enclosed_territory(self, player, start, totalVisited: set):
        min_heap = []
        totalVisited.add(start)
        walls_touched = 0
        visited = set([start])
        before_walls_touched = walls_touched

        count_bfs = 0
        
        heapq.heappush(min_heap, (self.heuristic_maps[walls_touched], start))


        while min_heap:
            # x, y = queue.pop()
        
            proior, coordinate = heapq.heappop(min_heap)
            x,y = coordinate
            
            # print(proior, ":" ,x,y)
            
            self.p(visited)
            print(self.heuristic_maps[walls_touched])
            time.sleep(1)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
                
                count_bfs+=1
                nx, ny = x + dx, y + dy
                
                # print(f"Before: {before_walls_touched}, After: {walls_touched}")
                before_walls_touched = walls_touched
                touched_wall = False
                
                
                if ny < 0:
                    walls_touched |= self.WALL_NORTH
                    touched_wall = True
                elif ny >= self.size:
                    walls_touched |= self.WALL_SOUTH
                    touched_wall = True
                elif nx < 0:
                    walls_touched |= self.WALL_WEST
                    touched_wall = True
                elif nx >= self.size:
                    walls_touched |= self.WALL_EAST
                    touched_wall = True
                
                
                if before_walls_touched != walls_touched:
                    # print("UPATING HEAP\n\n\n\n")
                    elements = [heapq.heappop(min_heap) for _ in range(len(min_heap))]
                    updated_elements = [(self.heuristic_maps[walls_touched][item[1][1]][item[1][0]], item[1]) for item in elements]

                    min_heap = updated_elements
                    heapq.heapify(min_heap) 
                else:  
                    if  (nx, ny) not in visited and not touched_wall and self.stones[ny][nx] != player:
                        heapq.heappush(min_heap, (self.heuristic_maps[walls_touched][ny][nx], (nx, ny)))
                        totalVisited.add((nx, ny))
                        visited.add((nx, ny))
                        continue
                    
                    
                
                if self.LOOKUP_TABLE[walls_touched]: #check for two wall
                    self.search.append(count_bfs)
                    
                        
                    return None      

                
            
                
                    
        # count_bfs+=1
        # self.total_bfs +=1
                
        self.search.append(count_bfs)
        # self.search_num +=1
                    
                    
        return visited  

        
    def bfs_enclosed_territory(self, player, start, totalVisited: set):
        
        # start_time_total = time.time()
        
        # start_time = time.time()
        # queue = deque([start])
        queue = [start]
        totalVisited.add(start)
        walls_touched = 0
        # walls_touched = set()
        visited = set(queue)
        # self.record_time("init", start_time)

        count_bfs = 0
        px, py = 0,0


        while queue:
            # start_time = time.time()
            x, y = queue.pop()
            # self.record_time("pop", start_time)
            self.p(visited)
            # time.sleep(.125)
            
            dx = x-px
            dy = y-py
            nx, ny = x + dx, y + dy
            px, py = nx ,ny
            valid_add = False
            attempts = 0
            # for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            
            
            while(not valid_add and attempts < 4):
                # print(dx, dy)
                
                print(directions)
                print("attempts: ", attempts)
                
                if((dx, dy)) in directions:
                    directions.remove((dx, dy))
                else:
                    dx,dy = directions.pop()
                    
                nx, ny = x + dx, y + dy
                print(dx, dy)
                print(nx, ny)
                
                if (nx, ny) in visited:
                    attempts+=1 
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
                        valid_add = True
                        px, py = nx, ny
                        queue.append((nx, ny))
                        totalVisited.add((nx, ny))
                        visited.add((nx, ny))
                        continue
                        
                if self.LOOKUP_TABLE[walls_touched]:
                    self.search.append(count_bfs)
                    return None
                
                attempts+=1                    
                count_bfs+=1
                
        # self.search.append(count_bfs)
        # self.search_num +=1
                    
                    
        return visited  
    
    
       # def bfs_enclosed_territory(self, player, start, totalVisited: set):
    #     queue = deque([start])
    #     totalVisited.add(start)
    #     walls_touched = set()

    #     while queue:
    #         x, y = queue.popleft()  # Use deque for efficient popping
    #         for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
    #             nx, ny = x + dx, y + dy

    #             # Check for boundary conditions
    #             if ny < 0:
    #                 walls_touched.add('north')
    #             elif ny >= self.size:
    #                 walls_touched.add('south')
    #             elif nx < 0:
    #                 walls_touched.add('west')
    #             elif nx >= self.size:
    #                 walls_touched.add('east')
    #             else:
    #                 # Skip already visited nodes
    #                 if (nx, ny) in totalVisited:
    #                     continue
                    
    #                 # Skip nodes not matching player
    #                 if self.stones[ny][nx] != player:
    #                     queue.append((nx, ny))
    #                     totalVisited.add((nx, ny))

    #         # Early exit if more than two walls are touched
    #         if len(walls_touched) > 2:
    #             return None

    #     return totalVisited

    # def bfs_enclosed_territory(self, player, start, totalVisited: set):
    #     queue = [start]
    #     totalVisited.add(start)
    #     walls_touched = set()
    #     visited = set(queue)

    #     while queue:
    #         x, y = queue.pop(0)
    #         for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
    #             nx, ny = x + dx, y + dy
                
    #             boolTouchWall = False
    #             if ny < 0:
    #                 walls_touched.add('north')
    #                 boolTouchWall = True
    #             if ny >= self.size:
    #                 walls_touched.add('south')
    #                 boolTouchWall = True
    #             if nx < 0:
    #                 walls_touched.add('west')
    #                 boolTouchWall = True
    #             if nx >= self.size:
    #                 walls_touched.add('east')
    #                 boolTouchWall = True    
                               
                
    #             if len(walls_touched)>2:
    #                 return None
    #             if boolTouchWall or (nx, ny) in visited:
    #                 continue

    #             if (nx, ny) not in visited and self.stones[ny][nx] != player:                    
    #                 queue.append((nx, ny))
    #                 totalVisited.add((nx, ny))
    #                 visited.add((nx, ny))
                    
    #     return visited  
    