import numpy
import pygame
import sys
from random import randint, sample, random
from pygame.locals import *


Size = 4                                          # 4*4行列
Block_WH = 110                                    # 每个块的长度宽度
BLock_Space = 10                                  # 两个块之间的间隙
Block_Size = Block_WH*Size+(Size+1)*BLock_Space   # 整个游戏界面的宽度
Matrix = numpy.zeros([Size, Size])                # 初始化矩阵4*4的0矩阵
Screen_Size = (Block_Size, Block_Size+Block_WH)        # 整个游戏界面的大小，加的一行是用来显示游戏标题分数等信息
Title_Rect = pygame.Rect(0, 0, Block_Size, Block_WH)   # 设置标题矩形的大小
Score = 0

Block_Color = {
        0: (150, 150, 150),
        2: (255, 255, 255),
        4: (255, 255, 128),
        8: (255, 255, 0),
        16: (255, 220, 128),
        32: (255, 220, 0),
        64: (255, 190, 0),
        128: (255, 160, 0),
        256: (255, 130, 0),
        512: (255, 100, 0),
        1024: (255, 70, 0),
        2048: (255, 40, 0),
        4096: (255, 10, 0),
}                                # 各个分数方块显示的颜色


class UpdateNew(object):
    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix
        self.zerolist = []    # 用于存储棋盘上空位的位置
        self.score = 0

    def removeZero(self, rowlist):
        # 每次都删除第一个0，然后在末尾添加一个0，直到0都放在后边
        while True:
            mid = rowlist[:]        # 拷贝一份修改前的列表
            try:
                rowlist.remove(0)
                rowlist.append(0)
            except Exception as e:
                pass
                # print(e)
            if mid == rowlist:
                break
        return self.combineList(rowlist)

    def combineList(self, rowlist):
        # 合并相邻相同的数字，四个2在一行，操作一次的话只会变成两个4而非一个8
        start_num = 0
        end_num = Size - rowlist.count(0) - 1    # 结束的位置
        while start_num < end_num:
            if rowlist[start_num] == rowlist[start_num+1]:
                self.score += int(rowlist[start_num])
                rowlist[start_num] *= 2
                rowlist[start_num+1:] = rowlist[start_num+2:]
                rowlist.append(0)
            start_num += 1
        return rowlist

    def toSequence(self, matrix):
        # 返回合并操作之后的矩阵
        lastmatrix = matrix.copy()
        m, n = matrix.shape
        for i in range(m):
            newlist = self.removeZero(list(matrix[i]))        # 合并操作
            matrix[i] = newlist
            # 将合并之后0的位置添加到zerolist当中
            for k in range(Size-1, Size-newlist.count(0)-1, -1):
                self.zerolist.append((i, k))
        # 矩阵中有0且合并操作之后和原来的矩阵不同才能移动
        # 这里的any()函数，只要两个矩阵有任意一个值不相等就返回True
        # print((lastmatrix!=matrix).any())
        # print(not (lastmatrix==matrix).all())
        if matrix.min() == 0 and (lastmatrix!=matrix).any():
            GameInit.initData(Size, matrix, self.zerolist)
        return matrix


class GameInit(object):
    def __init__(self):
        super().__init__()

    @staticmethod
    def getRandomLocal(zerolist = None):
        # 随机获取零元素的位置，用于在该位置上随机生成2或4
        return (randint(0, Size-1), randint(0, Size-1)) if zerolist is None else sample(zerolist, 1)[0]

    @staticmethod
    def getNum():
        n = random()
        return 2 if n > 0.2 else 4

    @classmethod
    def initData(cls, Size, matrix=None, zerolist=None):
        if matrix is None:
            matrix = Matrix.copy()
        a, b = cls.getRandomLocal(zerolist)    # 随机返回zerolist的一个元素, 若zerolist为为None则返回棋盘随机位置
        matrix[a][b] = cls.getNum()              # 将该位置上的元素变成2或4
        return matrix                            # 返回任意两个位置初始化为2或4之后的矩阵

    @classmethod
    def drawSurface(cls, screen, matrix, score):
        pygame.draw.rect(screen, (255, 255, 255), Title_Rect)
        font1 = pygame.font.SysFont('simsun', 48)
        font2 = pygame.font.SysFont(None, 32)
        # font.render第一个参数是文本内容，第二个参数是否抗锯齿，第三个参数字体颜色。blit函数的第二个参数是绘图的其实坐标
        screen.blit(font1.render('Score:', True, (255, 127, 0)), (20, 25))
        screen.blit(font1.render('{}'.format(score), True, (255, 127, 0)), (170, 25))
        screen.blit(font2.render('up', True, (255, 127, 0)), (360, 20))
        screen.blit(font2.render('left  down  right', True, (255, 127, 0)), (300, 50))
        a, b = matrix.shape        # matrix是一个numpy创建的矩阵，使用shape返回该矩阵的每一个维度的长度
        for i in range(a):
            for j in range(b):
                cls.drawBlock(screen, i, j, Block_Color[matrix[i][j]], matrix[i][j])


    @staticmethod
    def drawBlock(screen, row, column, color, blocknum):
        font = pygame.font.SysFont('stxingkai', 80)
        w = column*Block_WH+(column+1)*BLock_Space            # 绘制操作起始点的x轴坐标
        h = row*Block_WH+(row+1)*BLock_Space+Block_WH         # 绘制操作起始点的y轴坐标
        pygame.draw.rect(screen, color, (w, h, Block_WH, Block_WH))
        if blocknum != 0:
            fw, fh = font.size(str(int(blocknum)))
            # 将矩阵当中的数据转成字符串画在屏幕上
            screen.blit(font.render(str(int(blocknum)), True, (0, 0, 0)), (w+(Block_WH-fw)/2, h+(Block_WH-fh)/2))

    @staticmethod
    def keyDownPressed(keyvalue, matrix):
        if keyvalue == K_LEFT:
            return LeftAction(matrix)
        elif keyvalue == K_RIGHT:
            return RightAction(matrix)
        elif keyvalue == K_UP:
            return UpAction(matrix)
        elif keyvalue == K_DOWN:
            return DownAction(matrix)
    @staticmethod
    def gameOver(matrix):
        testmatrix = matrix.copy()
        a, b = testmatrix.shape
        # 有相邻相同的数，游戏继续
        for i in range(a):
            for j in range(b-1):
                if testmatrix[i][j] == testmatrix[i][j+1]:
                    print("请继续游戏！")
                    return False
        for i in range(b):
            for j in range(a-1):
                if testmatrix[j][i] == testmatrix[j+1][i]:
                    print("请继续游戏！")
                    return False
        print("游戏结束！")
        return True


class LeftAction(UpdateNew):
    def __init__(self, matrix):
        super().__init__(matrix)

    def handleData(self):
        matrix = self.matrix.copy()
        newmatrix = self.toSequence(matrix)
        return newmatrix, self.score


class RightAction(UpdateNew):
    def __init__(self, matrix):
        super().__init__(matrix)

    def handleData(self):
        matrix = self.matrix.copy()[:, ::-1]
        newmatrix = self.toSequence(matrix)
        return newmatrix[:, ::-1], self.score


class UpAction(UpdateNew):
    def __init__(self, matrix):
        super().__init__(matrix)

    def handleData(self):
        matrix = self.matrix.copy().T       # T是对矩阵进行转置，行变列
        newmatrix = self.toSequence(matrix)
        return newmatrix.T, self.score


class DownAction(UpdateNew):
    def __init__(self, matrix):
        super().__init__(matrix)

    def handleData(self):
        matrix = self.matrix.copy()[::-1].T
        newmatrix = self.toSequence(matrix)
        return newmatrix.T[::-1], self.score

def main():
    pygame.init()
    screen = pygame.display.set_mode(Screen_Size, 0, 32)    # 参数1为长宽，参数2为扩展，参数3为色深
    # pygame.display.set_caption("2048")
    matrix = GameInit.initData(Size)               # 初始化矩阵，随机两个位置生成数字2或4
    current_score = 0
    GameInit.drawSurface(screen, matrix, current_score)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                actionObject = GameInit.keyDownPressed(event.key, matrix)
                matrix, score = actionObject.handleData()
                current_score += score
                GameInit.drawSurface(screen, matrix, current_score)
                if matrix.min() != 0:
                    GameInit.gameOver(matrix)
            else:
                pass
        pygame.display.update()


if __name__ == '__main__':
    main()

