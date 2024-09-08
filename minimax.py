from board import Board
from player import Player
from random import random
import random

class MiniMax(Player):
    def __init__(self, num_moves_lookahead = 4, num_moves_considered = 20):
        self.firstMoveMade = False
        self.num_moves_lookahead = num_moves_lookahead
        self.num_moves_considered = num_moves_considered
        self.count = 0
       
    def getPosition(self, game):
        self.count = 0
        eval, bestMove = self.miniMax(game, self.num_moves_lookahead, True)
        print("Moves Considered:")
        print(game.generateValidMoves(self,self.num_moves_considered))
        print("Best move:", bestMove, "with evaluation:", eval)
        print("Static_evals made: ", self.count)
    
        
        # print(bestMove)
        return bestMove
        raise Exception("Stop")
        
        
    #everything relating to a particular board state. shuold be in the board object
    #and NOTHING ELSE
    
    def miniMax(self, game_state, depth, maximizingPlayer, alpha=float('-inf'), beta=float('inf')):
        if depth == 0 or game_state.checkGameOver():
            self.count +=1
            return self.static_evaluation(game_state), None
        player = game_state.currPlayer()
        if maximizingPlayer:
            # print("Considering move: ", move)
            maxEval = float('-inf')
            bestMove = None
            validMoves = game_state.generateValidMoves(player, self.num_moves_considered)
            for move in validMoves:
                # print("Considering move for AI: ", move)
                copyGameState = game_state.simulateMove(self, move)
                if copyGameState == None:
                    continue
                eval, _ = self.miniMax(copyGameState, depth-1, False, alpha, beta)
                if eval > maxEval:
                    maxEval = eval
                    bestMove = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval, bestMove
        else:
            minEval = float('inf')
            validMoves = game_state.generateValidMoves(player, self.num_moves_considered)
            for move in validMoves:
                # print("Considering move for opponent: ", move)
                copyGameState = game_state.simulateMove(self, move)
                if copyGameState == None:
                    continue
                eval, _ = self.miniMax(copyGameState, depth-1, True, alpha, beta)
                if eval < minEval:
                    minEval = eval
                beta = min(beta, eval)
                if beta <= alpha: 
                    break
            return minEval, None

    def static_evaluation(self, game_state):

        total_territory = game_state.getTotalTerritory()
        self_territory = game_state.getTerritoryCount(self)
        
        return (self_territory/total_territory)*2 -1
    

    def __deepcopy__(self, memo):
        return self



class MiniMax_Control(MiniMax):
    def static_evaluation(self, game_state):
        if self.isBlack:
            eval = -game_state.board.eval()
        else:
            eval =  game_state.board.eval()
        return eval
    



        
    
    