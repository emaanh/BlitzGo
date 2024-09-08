from board import Board

class Player:
	def getPosition(self, board):
		raise NotImplementedError("This method should be overridden by subclasses")
	def __init__(self):
		pass

	def setColor(self, isBlack):
		self.isBlack = isBlack
		self.name = "Black" if isBlack else "White"
		self.symbol = "○" if isBlack else "●"
		self.stone_code = 1 if isBlack else 2
		self.territory_code = 10 if isBlack else 20
	
	
	def getStoneCode(self):
		return self.stone_code
	
	def getTerritoryCode(self):
		return self.territory_code
	
class User(Player):
	def getPosition(self, game):
		position = None
		try:
			x,y = map(int, input("Enter your move as 'x y': ").split())
		except ValueError as e:
			print("You did not enter your move in the right format")
		else: 
			position = (x-1,y-1) 
			
		return position
		
class Replay(Player):
	def __init__(self, moves_list):
		# super().__init__()
		self.moves_list = moves_list
		self.moveCount = 0
	
	def getPosition(self, game):
		position = None
		try:
			x,y = self.moves_list[self.moveCount]
		except ValueError as e:
			print("Move list is does not represent full game")
		else: 
			self.moveCount +=1 #but what if it fails in the next check
			position = (x,y) 
			
		return position
	
	def transformMovesList(moves_list, twoReplays=True):
		moves_list_1 = []
		moves_list_2 = []
		turn = 0
		
		for move_string in moves_list:
			x, y = map(int, move_string.split(';'))
			if turn == 0:
				moves_list_1.append((y-1, x-1))
			else:
				moves_list_2.append((y-1, x-1))
			if twoReplays:
				turn = 1-turn 
			
		if twoReplays:
			return moves_list_1, moves_list_2
		else:
			return moves_list_1
		
	