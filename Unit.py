from Rectangle import Rectangle
import pygame, math

class Unit(Rectangle):
	"""A class for units."""
	def __init__(self, game, position):
		self.game = game
		self.finishedTurn = False
		Rectangle.__init__(self, self.game, position, [16,16], [136,0,0])
		self.movementPattern = [
										  [ 0, -3],
								[-1, -2], [ 0, -2], [ 1, -2],
					  [-2, -1], [-1, -1], [ 0, -1], [ 1, -1], [ 2, -1],
			[-3,  0], [-2,  0], [-1,  0],           [ 1,  0], [ 2,  0], [ 3,  0],
					  [-2,  1], [-1,  1], [ 0,  1], [ 1,  1], [ 2,  1],
								[-1,  2], [ 0,  2], [ 1,  2],
										  [ 0,  3],
		]
		self.legalMovementPattern = self.movementPattern[:]
		self.showMovement = False
		self.movementRectangles = []
		for position in self.legalMovementPattern:
			realPosition = [x + y for x, y in zip(self.position, [coordinate * 16 for coordinate in position])]
			self.movementRectangles.append(
				Rectangle(self.game, realPosition, self.size, [0, 255, 0], 1)
			)

	def finishTurn(self):
		self.finishedTurn = True
		self.changeColor([64, 64, 64])

	def unfinishTurn(self):
		self.finishedTurn = False
		self.changeColor([136, 0, 0])

	def move(self, x, y):
		Rectangle.move(self, x, y)
		self.finishTurn()


	def draw(self, screen):
		Rectangle.draw(self, screen)
		if self.showMovement:
			for elem in self.movementRectangles:
				elem.draw(screen)

	def update(self, deltaTime, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = self.game.cursor.get_pos()
				pos = [pos[0], pos[1]]
				if hasattr(self.game, 'scrollableLayer'):
					pos[0] = pos[0] - self.game.scrollableLayer.position[0]
					pos[1] = pos[1] - self.game.scrollableLayer.position[1]
					pos[0] = pos[0] - self.game.scrollableLayer.offset[0]
					pos[1] = pos[1] - self.game.scrollableLayer.offset[1]
				if self.showMovement:
					for movementRectangle in self.movementRectangles:
						if movementRectangle.rect.collidepoint(pos):
							deltaX = movementRectangle.rect.left - self.rect.left
							deltaY = movementRectangle.rect.top - self.rect.top
							self.move(deltaX, deltaY)
							self.showMovement = False
				elif self.rect.collidepoint(pos) and not self.finishedTurn:
					self.girlScout(5)
					unitPosition = (self.rect.left, self.rect.top)
					self.movementRectangles = []
					self.generateLegalMovementPattern()
					for position in self.legalMovementPattern:
						realPosition = [x + y for x, y in zip(unitPosition, [coordinate * 16 for coordinate in position])]
						self.movementRectangles.append(
							Rectangle(self.game, realPosition, self.size, [64, 64, 64], 1)
						)
					self.showMovement = not self.showMovement

	def checkSurrounding(self,func,x = "NIX", y = "NIX", extralist = False, multiplier = 16):
		unitPosition = (self.rect.left, self.rect.top)
		if x == "NIX":
			x = unitPosition[0]
		if y == "NIX":
			y = unitPosition[1]
		out = {}
		if extralist:
			out["T"] = func(x             , y - multiplier, extralist)
			out["L"] = func(x - multiplier, y             , extralist)
			out["B"] = func(x             , y + multiplier, extralist)
			out["R"] = func(x + multiplier, y             , extralist)
		else:
			out["T"] = func(x             , y - multiplier)
			out["L"] = func(x - multiplier, y             )
			out["B"] = func(x             , y + multiplier)
			out["R"] = func(x + multiplier, y             )
		return out

	def isOnPlayer(self, x, y):
		return x == self.rect.left and y == self.rect.top

	def isReachable(self, x, y):
		unitPosition = (self.rect.left, self.rect.top)
		realX = int(x / 16) - int(math.floor(unitPosition[0] / 16))
		realY = int(y / 16) - int(math.floor(unitPosition[1] / 16))
		return self.game.map.getTileAtCoordinate(x, y) == 0 and [realX, realY] in self.movementPattern and not [realX, realY] in self.legalMovementPattern

	def generateLegalMovementPattern(self):
		unitPosition = (self.rect.left, self.rect.top)
		self.legalMovementPattern = []
		self.checkList = [[0, 0]]
		while self.checkList != []:
			for position in self.checkList:
				realPosition = [x + y for x, y in zip(unitPosition, [coordinate * 16 for coordinate in position])]
				self.checkDict = self.checkSurrounding(self.isReachable, realPosition[0], realPosition[1])
				for key in self.checkDict.keys():
					if self.checkDict[key]:
						if key == "T":
							self.legalMovementPattern.append([position[0], position[1]-1])
							self.checkList.append([position[0], position[1] - 1])
						if key == "L":
							self.legalMovementPattern.append([position[0] -1, position[1]])
							self.checkList.append([position[0] -1, position[1]])
						if key == "B":
							self.legalMovementPattern.append([position[0], position[1]+1])
							self.checkList.append([position[0], position[1] + 1])
						if key == "R":
							self.legalMovementPattern.append([position[0] +1, position[1]])
							self.checkList.append([position[0] +1, position[1]])
				self.checkList.remove(position)

	def girlScout(self, movesLeft, forbiddenList = [], way = [], currentPos = "notSet"):
		if currentPos == "notSet":
			unitPosition = (self.rect.left, self.rect.top)
			currentPos = (unitPosition[0]/16,unitPosition[1]/16)
		loacalWay = way[:]
		loacalWay.append(currentPos)
		forbiddenList.append(currentPos)
		if movesLeft == 0 or ((currentPos[0] + 1, currentPos[1]) in forbiddenList and (
				currentPos[0], currentPos[1] + 1) in forbiddenList and (
			currentPos[0] - 1, currentPos[1]) in forbiddenList and (
				currentPos[0], currentPos[1] - 1) in forbiddenList):
			return [loacalWay]
		else:
			outList = [loacalWay]
			for pos in [(currentPos[0] + 1, currentPos[1]), (currentPos[0], currentPos[1] + 1),
						(currentPos[0] - 1, currentPos[1]), (currentPos[0], currentPos[1] - 1)]:
				for newWay in self.girlScout(movesLeft - 1, forbiddenList, loacalWay, pos):
					print newWay
					outList.append(newWay)
			return outList

	def endTurn(self):
		self.unfinishTurn()

