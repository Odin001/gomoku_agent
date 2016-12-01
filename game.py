from random import randint
import collections

const_agentId = 1

class Gomoku:

	def __init__(self, N):
		# chess board
		self.chessBoard = [[0 for i in range(N)] for i in range(N)]
		self.chessSize = N

		# player 
		self.nextPlayer = 1
		self.lastMove 	= (-1, -1)
		self.totalSteps = [0, 0] # (player 1, player 2)

	def currentGame(self): # return the next player, total steps for player 1 and 2 respectively
		return (self.nextPlayer, self.totalSteps[0], self.totalSteps[1])

	# update chess board given a move
	def updateBoard(self, pos):
		assert(pos[0] >= 0 and pos[0] < self.chessSize and pos[1] >= 0 and pos[1] < self.chessSize)
		self.chessBoard[pos[0]][pos[1]] = self.nextPlayer
		self.totalSteps[self.nextPlayer - 1] += 1
		self.lastMove = pos
		self.nextPlayer = 2 if self.nextPlayer == 1 else 1

	# revert last move given updated last postion
	def revert(self, lastPos):
		assert( (lastPos[0] == -1 and lastPos[0] == -1 and sum(self.totalSteps) == 1) or \
			(lastPos[0] >= 0 and lastPos[0] < self.chessSize and lastPos[1] >= 0 and lastPos[1] < self.chessSize))
		assert(lastPos == (-1,-1) or self.chessBoard[lastPos[0]][lastPos[1]] == self.nextPlayer)
		assert(self.totalSteps[2 - self.nextPlayer] > 0)
		self.totalSteps[2 - self.nextPlayer] -= 1
		self.chessBoard[self.lastMove[0]][self.lastMove[1]] = 0
		self.nextPlayer = 3 - self.nextPlayer
		self.lastMove = lastPos

	# check if the game ends
	# return if a game terminates
		# -1 - not end
		# 0 - break even
		# 1 - player 1 wins
		# 2 - player 2 wins
	def isEnd(self, debug = False): 

		# helper function to return state of a position
		def boardState(pos): # pos = (coor x, coor y)
			if (pos[0] < 0 or pos[0] >= self.chessSize or pos[1] < 0 or pos[1] >= self.chessSize):
				return -1
			else:
				return self.chessBoard[pos[0]][pos[1]]

		if sum(self.totalSteps) >= self.chessSize*self.chessSize:
			return 0
		direction = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1),
					'NE': (-1, 1), 'NW': (-1, -1), 'SE': (1, 1), 'SW': (1, -1)}
		count = {'N': 0, 'S': 0, 'W': 0, 'E': 0,
				'NE': 0, 'NW': 0, 'SE': 0, 'SW': 0}
		lastPlayer = 2 if self.nextPlayer == 1 else 1
		for d in direction:
			i = self.lastMove[0]
			j = self.lastMove[1]
			while boardState((i, j)) == lastPlayer:
				count[d] += 1
				i += direction[d][0]
				j += direction[d][1]
		if debug:
			print count
		if (count['N'] + count['S'] >= 6) or (count['W'] + count['E'] >= 6) \
			or (count['NE'] + count['SW'] >= 6) or (count['NW'] + count['SE'] >= 6):
			return lastPlayer
		else:
			return -1

# a random policy 
class RandomPolicy:

	def getNextAction(self, game):
		agent = game.nextPlayer
		op = 2 if agent == 1 else 1
		chessBoard = game.chessBoard
		while True:
			x = randint(0,len(chessBoard) - 1)
			y = randint(0,len(chessBoard) - 1)
			if (chessBoard[x][y] == 0):
				return (x, y)

# a naive policy to play Gomoku
class BaselinePolicy:

	def getNextAction(self, game):
		agent = game.nextPlayer
		op = 2 if agent == 1 else 1
		chessBoard = game.chessBoard
		totalCount = 0
		nextMove = []

		# desired pattern
		fourInRow = ([op, op, op, op, 0], [0, op, op, op, op])
		threeInRow = ([0, op, op, op, 0], [agent, op, op, op, 0], [0, op, op, op, agent])
		for i in range(len(chessBoard)):
			for j in range(len(chessBoard)):
				allPattern = ( [chessBoard[p][j] if p >= 0 and p < len(chessBoard) else -2 for p in range(i-4, i+1)], \
								[chessBoard[p][j] if p >= 0 and p < len(chessBoard) else -2 for p in range(i, i+5)], \
								[chessBoard[i][p] if p >= 0 and p < len(chessBoard) else -2 for p in range(j-4, j+1)], \
								[chessBoard[i][p] if p >= 0 and p < len(chessBoard) else -2 for p in range(j, j+5)], \
								[chessBoard[i+p][j+p] if i + p >= 0 and i + p < len(chessBoard) and j + p >= 0 and j + p < len(chessBoard) else -2 for p in range(-4, 0)], \
								[chessBoard[i+p][j+p] if i + p >= 0 and i + p < len(chessBoard) and j + p >= 0 and j + p < len(chessBoard) else -2 for p in range(0, 5)] \
							)
				for pattern in allPattern:
					if (pattern in fourInRow and chessBoard[i][j] == 0):
						nextMove = [(i, j)] + nextMove
					elif (pattern in threeInRow and chessBoard[i][j] == 0):
						nextMove.append((i, j))
		# generate random position
		if len(nextMove) < 1:
			while True:
				x = randint(0,len(chessBoard) - 1)
				y = randint(0,len(chessBoard) - 1)
				if (chessBoard[x][y] == 0):
					nextMove.append((x, y))
					break
		return nextMove[0]

def evaluate(game, player):
	chessBoard = game.chessBoard
	chessBoardSize = len(chessBoard)
	windowSize = 5

	agent, opponent = player, 1 if player == 2 else 2
	totalCount = collections.defaultdict(int)

	startPos = {'row': [(i, 0) for i in range(chessBoardSize)], \
				'column': [(0, j) for j in range(chessBoardSize)], \
				'diagonal': [(i, 0) for i in range(1, chessBoardSize)] + [(0, j) for j in range(chessBoardSize)], \
				'rdiagonal': [(i, chessBoardSize - 1) for i in range(1, chessBoardSize)] + [(0, j) for j in range(chessBoardSize)]}
	direction = {'row': (0, 1), 'column': (1, 0), 'diagonal': (1, 1), 'rdiagonal': (1, -1)}
	diff = {'row': (0, -windowSize), 'column': (-windowSize, 0), 'diagonal': (-windowSize, -windowSize), 'rdiagonal': (-windowSize, windowSize)}
	
	def validPos(i, j):
		return (i >= 0 and i < chessBoardSize) and (j >= 0 and j < chessBoardSize)

	for d in direction:
		for (i, j) in startPos[d]:
			initial = 0
			windowCount = {'agent': 0, 'opponent': 0}
			while validPos(i, j):
				if initial < windowSize - 1:
					if chessBoard[i][j] == agent:
						windowCount['agent'] += 1
					elif chessBoard[i][j] == opponent:
						windowCount['opponent'] += 1
					initial += 1
					i += direction[d][0]
					j += direction[d][1]
					continue

				if (chessBoard[i][j] == agent):
					windowCount['agent'] += 1
				elif (chessBoard[i][j] == opponent):
					windowCount['opponent'] += 1

				previ, prevj = i + diff[d][0], j + diff[d][1]

				if validPos(previ, prevj):
					prevLoc = chessBoard[previ][prevj]
					if (prevLoc == agent):
						windowCount['agent'] -= 1
					elif (prevLoc == opponent):
						windowCount['opponent'] -= 1

				if windowCount['agent'] == windowSize:
					return float("inf")
				elif (windowCount['opponent'] <= 0 and windowCount['agent'] > 0):
					totalCount[windowCount['agent']] += 1

				i += direction[d][0]
				j += direction[d][1]
				
	value = 0
	for key in totalCount:
		value += key*totalCount[key]
	return value


class MinimaxPolicy:

	def __init__(self, evalFunc = evaluate, depth = 1, pruning = True):
		self.depth = depth
		self.pruning = pruning
		self.evalFunc = evalFunc

	def getNextAction(self, game):

		def recurseAlphaBeta(d, lowerBound, upperBound):
			winner = game.isEnd()
			if winner == const_agentId:
				return (float('inf'), None)
			elif winner >= 0:
				return (float('-inf'), None)
			if d == self.depth:
				return (self.evalFunc(game, game.nextPlayer), None)

			chessBoard = game.chessBoard
			lastMove = game.lastMove
			player = game.nextPlayer

			nextd = d + 1 if player == 2 else d
			choices = []
			for i in range(len(chessBoard)):
				for j in range(len(chessBoard)):
					if chessBoard[i][j] == 0:
						game.updateBoard((i, j))
						if self.pruning:
							choices.append((self.evalFunc(game, player), (i, j)))
						else:
							choices.append((0, (i, j)))
						game.revert(lastMove)
			if self.pruning:
				choices.sort()
				if player == const_agentId:
					choices = choices[::-1]

			maxPair = (float('-inf'), None)
			minPair = (float('inf'), None)
			for _, a in choices:
				game.updateBoard(a)
				if player == const_agentId:
					v, _ = recurseAlphaBeta(nextd, maxPair[0], upperBound)
				else:
					v, _ = recurseAlphaBeta(nextd, lowerBound, minPair[0])
				maxPair = max(maxPair, (v, a))
				minPair = min(minPair, (v, a))
				game.revert(lastMove)
				if self.pruning and player == const_agentId and maxPair[0] > upperBound:
					return maxPair
				elif self.pruning and player != const_agentId and minPair[0] < lowerBound:
					return minPair

			return maxPair if player == const_agentId else minPair

		value, action = recurseAlphaBeta(0, float('-inf'), float('inf'))
		return action



	








