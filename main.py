import time
# import matplotlib.pyplot as plt
from game import Game
from player import Player, User, Replay
from minimax import MiniMax, MiniMax_Control
from testing_moves import testingMoves

import numpy as np
import matplotlib.pyplot as plt


def runFromUserInput():
    position = None
    try:
        x,y = map(int, input("Enter your move as 'x y': ").split())
    except ValueError as e:
        print("You did not enter your move in the right format")
    else: 
        position = (x-1,y-1) 
        
    return position

def transformMovesList(moves_list):
    new_moves_list = []
    for move_string in moves_list:
        x, y = map(int, move_string.split(';'))
        new_moves_list.append((y-1, x-1))
    return new_moves_list



    

def main(size, sleep=0, print_ = True, moves_list=None):
    game = Game(size)
    
    # game.addPlayer(MiniMax(5, 10))
    game.addPlayer(MiniMax(5, 12))
    
    
    game.addPlayer(MiniMax_Control(5,12))
    print("Is Control Black?", game.players[1].isBlack)
    
    # game.addPlayer(MiniMax_Control(5,10))
    
    
    # game.addPlayer(User())
    # game.addPlayer(User())
    
    # moves_list_1, moves_list_2 = Replay.transformMovesList(moves_list, True)
    # game.addPlayer(Replay(moves_list_1), True) 
    # game.addPlayer(Replay(moves_list_2))
    
    if print_:
        print(game.board)
        
    # plt.ion()
    # self_control_map = game.board.tension_map
    
    # fig, ax = plt.subplots()
    # cax = ax.imshow(np.array(self_control_map), cmap='gray', vmin=-1, vmax=10)
    # fig.colorbar(cax, ax=ax, orientation='vertical')
    # ax.set_xticks([])
    # ax.set_yticks([])
    
    # def update_plot(new_control_map):
    #     # Convert list to NumPy array for processing
    #     new_control_map = np.array(new_control_map)
    #     # new_control_map = new_control_map.T
        
    #     # # Normalize the new control map
    #     max_val = max(np.max(new_control_map),1)
    #     # normalized_map = (new_control_map) / (max_val)
    #     normalized_map = new_control_map
        
    #     # Update the data for the plot
    #     cax.set_data(normalized_map)
    #     # print("set data")
    #     ax.draw_artist(ax.patch)
    #     ax.draw_artist(cax)
    #     # print("draw")
    #     fig.canvas.update()
    #     # print("update")
    #     # fig.canvas.flush_events()
    #     # print("end")
    
    while(not game.checkGameOver()):
        currPlayer: Player = game.currPlayer()    
        
        success = False        
        while not success:
            
            #position None if failed
            position = currPlayer.getPosition(game)

            if print_:
                print(f"{currPlayer.name}'s turn") 
                
            time.sleep(sleep)
            
            if position:
                result = game.placeStone(position)
                if result == 0:
                    success = True
                elif result == 2:
                    print("Your move reverted the board to a previous state. Try again.", "\n"*2)
                else:
                    print("Invalid Move")
                    
            if print_:    
                print("\n")   
                print(game.board)
                # print(game.board.current_hash)
                game.printBothTerritories()
                # update_plot(game.board.tension_map)
    
    
    
    #return result
    if game.board.territory_counts[game.players[1]] >  game.board.territory_counts[game.players[0]]:
        return 1 #player 1 win
    elif game.board.territory_counts[game.players[1]] <  game.board.territory_counts[game.players[0]]:
        return -1 #player 2 win
    else:
        return 0 #tie
    
def speed_test(size, repeats):
    total_moves_made = 0
    moves = testingMoves
    
    start = time.time()
    for i in range(repeats):
        for move_list in moves.moves_list:
            main(size, 0, False, move_list)
            total_moves_made += len(move_list)
        
    stop = time.time()
    
    print(total_moves_made, "moves in", stop-start, "seconds")
    print("Time for 100 move game: ", 100 * (stop-start)/total_moves_made)
    

def bot_battle(size, games):
    total_games = 0 #can divide by zero if only ties
    total_won = 0
    for i in range(games):
        result = main(size, 0, True)
        if result== 1:
            total_games +=1
            total_won +=1
        elif result == -1:
            total_games +=1
            
        print("games played: ", i)
        
    print("total games non tied: ", total_games)
    print("total_games won: ", total_won)
    print("win %: ",total_won/total_games * 100 )

if __name__ == '__main__':  
    # speed_test(13,10)
    # bot_battle(5,1)
    # main(13, 0, True, Moves_986551)
    
    main(5)
    

