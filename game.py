from board import Board
from player import Player
from random import random
from copy import deepcopy


class Game:
	def __init__(self, size):
		self.board = Board(size)
		self.players = []
		self.moveCount = 0

	def addPlayer(self, player: Player, isBlack= None): 
		if not self.players: 
			playerColor = random() < 0.5 if isBlack is None else isBlack
			self.turn = 0 if playerColor else 1
		else:
			playerColor = not self.players[-1].isBlack		
		player.setColor(playerColor)
		self.players.append(player)
		self.board.players.append(player)
		self.board.initalizeTerritoryCounts(player)

		
	def placeStone(self, position):
		current_player = self.currPlayer()
		move_valid = self.board.placeStone(current_player, position)
		if move_valid == 0:
			self.switchPlayer()
		return move_valid
			
	def switchPlayer(self):
		self.turn = 1-self.turn 
		self.moveCount +=1
		
	def currPlayer(self):
		return self.players[self.turn]
	
	def checkGameOver(self):
		if self.board.totalTerritory() >= self.board.size_2:
			return self.board.checkGameOver()
		return False
	
	def getTerritoryCount(self, player):
		return self.board.territory_counts[player]

	def getTerritoryCount_Black(self, isBlack):
		for player in self.players:
			if player.isBlack == isBlack:
				return self.board.territory_counts[player]
	
	def getTotalTerritory(self):
		return self.board.total_territory_count
	
	def generateValidMoves(self, player, num_moves_considered):
		return self.board.generateValidMoves(player, num_moves_considered)
		
	def simulateMove(self, player, position):
		new_game = deepcopy(self)
		if new_game.placeStone(position) == 0:
			return new_game
		return None
		
	def printBothTerritories(self):
		self.board.printBothTerritories()
		