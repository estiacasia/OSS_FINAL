#!/usr/bin/python3
# -*- coding: utf-8 -*-

# 게임의 데이터 모델 구현
import random

class Shape(object):
    shapeNone = 0
    shapeI = 1
    shapeL = 2
    shapeJ = 3
    shapeT = 4
    shapeO = 5
    shapeS = 6
    shapeZ = 7

    shapeCoord = ( 
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),  #일자 블록
        ((0, -1), (0, 0), (0, 1), (1, 1)),  #L 모양 블록
        ((0, -1), (0, 0), (0, 1), (-1, 1)), #L 모양 뒤입은 모양 블럭
        ((0, -1), (0, 0), (0, 1), (1, 0)),  #T 모양 블럭
        ((0, 0), (0, -1), (1, 0), (1, -1)), #네모 모양 블럭
        ((0, 0), (0, -1), (-1, 0), (1, -1)),#Z 모양 블럭
        ((0, 0), (0, -1), (1, 0), (-1, -1)) #S 모양 블럭
    )

    def __init__(self, shape=0): #초기화
        self.shape = shape

    def getRotatedOffsets(self, direction): #회전시키기
        tmpCoords = Shape.shapeCoord[self.shape]
        #조건에 따라 coords 값 변환하여 리턴
        if direction == 0 or self.shape == Shape.shapeO:
            return ((x, y) for x, y in tmpCoords)

        if direction == 1:
            return ((-y, x) for x, y in tmpCoords)

        if direction == 2:
            if self.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
                return ((x, y) for x, y in tmpCoords)
            else:
                return ((-x, -y) for x, y in tmpCoords)

        if direction == 3:
            if self.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
                return ((-y, x) for x, y in tmpCoords)
            else:
                return ((y, -x) for x, y in tmpCoords)

    def getCoords(self, direction, x, y): # 현재 블럭 위치 가져옴
        return ((x + xx, y + yy) for xx, yy in self.getRotatedOffsets(direction))

    def getBoundingOffsets(self, direction): #최대 최소 범위 설정
        tmpCoords = self.getRotatedOffsets(direction)
        minX, maxX, minY, maxY = 0, 0, 0, 0
        for x, y in tmpCoords:
            if minX > x:
                minX = x
            if maxX < x:
                maxX = x
            if minY > y:
                minY = y
            if maxY < y:
                maxY = y
        return (minX, maxX, minY, maxY)


class BoardData(object): #보드 정보
    width = 10 # 가로
    height = 22 # 높이

    def __init__(self):
        self.backBoard = [0] * BoardData.width * BoardData.height

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()
        self.nextShape = Shape(random.randint(1, 7)) #다음블록모양
        #random.randint(1, 7) 1부터 6까지 랜덤 1개.
        
        self.shapeStat = [0] * 8 

    def getData(self):
        return self.backBoard[:]

    def getValue(self, x, y):
        return self.backBoard[x + y * BoardData.width]

    def getCurrentShapeCoord(self): #현재블럭좌표
        return self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY)

    def createNewPiece(self):   #새로운 조각 만들기
        minX, maxX, minY, maxY = self.nextShape.getBoundingOffsets(0)
        result = False
        
        #tryMoveCurrent 의 출력값은 boolean값임.
        if self.tryMoveCurrent(0, 5, -minY): #참인경우. 즉,  tryMoveCurrent -> tryMove함수 출력시 결과값 True
            self.currentX = 5
            self.currentY = -minY
            self.currentDirection = 0
            self.currentShape = self.nextShape
            self.nextShape = Shape(random.randint(1, 7))
            result = True       #움직인다.
        else:
            #나머지 경우 즉, False
            
            self.currentShape = Shape()
            self.currentX = -1
            self.currentY = -1
            self.currentDirection = 0
            result = False      #못움직임.
        self.shapeStat[self.currentShape.shape] += 1
        return result

    def tryMoveCurrent(self, direction, x, y):
        return self.tryMove(self.currentShape, direction, x, y) # True or False return.

    def tryMove(self, shape, direction, x, y): # 움직이기 가능한가? 판단.
        for x, y in shape.getCoords(direction, x, y):
            if x >= BoardData.width or x < 0 or y >= BoardData.height or y < 0: #보드의 가로나 세로를 벗어날 때
                return False #불가능합니다.
            if self.backBoard[x + y * BoardData.width] > 0: #설정값보다 보드의 넓이가 클 때.
                return False #불가능합니다.
        return True #가능!

 #블록 조정, 자연낙하, 파괴 함수들
    def moveDown(self):
        lines = 0
        if self.tryMoveCurrent(self.currentDirection, self.currentX, self.currentY + 1):
            self.currentY += 1
        else:
            self.mergePiece()
            lines = self.removeFullLines()
            self.createNewPiece()
        return lines

    def dropDown(self):
        while self.tryMoveCurrent(self.currentDirection, self.currentX, self.currentY + 1):
            self.currentY += 1
        self.mergePiece()
        lines = self.removeFullLines()
        self.createNewPiece()
        return lines

    def moveLeft(self):
        if self.tryMoveCurrent(self.currentDirection, self.currentX - 1, self.currentY):
            self.currentX -= 1

    def moveRight(self):
        if self.tryMoveCurrent(self.currentDirection, self.currentX + 1, self.currentY):
            self.currentX += 1

    def rotateRight(self):
        if self.tryMoveCurrent((self.currentDirection + 1) % 4, self.currentX, self.currentY):
            self.currentDirection += 1
            self.currentDirection %= 4

    def rotateLeft(self):
        if self.tryMoveCurrent((self.currentDirection - 1) % 4, self.currentX, self.currentY):
            self.currentDirection -= 1
            self.currentDirection %= 4

    def removeFullLines(self): # 꽉찬 줄 블록 제거하는 함수
        newBackBoard = [0] * BoardData.width * BoardData.height #새로운 백보드
        newY = BoardData.height - 1  #새로운 높이
        lines = 0
        for y in range(BoardData.height - 1, -1, -1):
            blockCount = sum([1 if self.backBoard[x + y * BoardData.width] > 0 else 0 for x in range(BoardData.width)])
            if blockCount < BoardData.width:
                for x in range(BoardData.width):
                    newBackBoard[x + newY * BoardData.width] = self.backBoard[x + y * BoardData.width]
                newY -= 1
            else:
                lines += 1
        if lines > 0:
            self.backBoard = newBackBoard
        return lines

    def mergePiece(self):
        for x, y in self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY):
            self.backBoard[x + y * BoardData.width] = self.currentShape.shape

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()

    def clear(self):
        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()
        self.backBoard = [0] * BoardData.width * BoardData.height


BOARD_DATA = BoardData()
