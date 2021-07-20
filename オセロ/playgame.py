#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@author: Keisuke Ueda
http://qiita.com/keisuke1111/items/53353896a957136b1d7e
refactoring by @shiracamus
'''

import time
import random
import copy


class Othello:

    def play(self):
        start_time = time.time()
        board = Board()
        player1 = computer = Computer(BLACK, "PC")
        player2 = user = User(WHITE, "あなた")
        #player1 = user = User(BLACK, "あなた")
        #player2 = computer = Computer(WHITE, "PC")

        turn = 0
        hand1 = hand2 = None
        while board.is_playable() and not hand1 == hand2 == "pass":
            turn += 1
            print("TURN = %s" % turn)

            print(board)
            hand1 = player1.play(board)
            print("%sの手: %s" % (player1.name, hand1))

            print(board)
            hand2 = player2.play(board)
            print("%sの手: %s" % (player2.name, hand2))

        self.show_result(board)

        end_time = time.time()
        print("試合時間:" + str(end_time - start_time))

    def show_result(self, board):
        print("------------------RESULT-------------------")  # 結果発表
        print(board)
        computer_stones = board.count(computer.stone)
        user_stones = board.count(user.stone)
        print("Computer: %s" % computer_stones)
        print("You: %s" % user_stones)
        print()
        if computer_stones > user_stones:
            print("YOU LOST!!!!!")
        elif computer_stones < user_stones:
            print("YOU WON!!!!!")
        else:
            print("DRAW")


class Stone(str):
    pass

BLACK = Stone("●")
WHITE = Stone("○")
BLANK = Stone("×")
OPPONENT = {BLACK: WHITE, WHITE: BLACK}


class Board:
    SIZE = 8
    DIRECTIONS_XY = ((-1, -1), (+0, -1), (+1, -1),
                     (-1, +0),           (+1, +0),
                     (-1, +1), (+0, +1), (+1, +1))

    def __init__(self):
        size = self.SIZE
        center = size // 2
        square = [[BLANK for y in range(size)] for x in range(size)]  # 最初の盤面を定義
        square[center - 1][center - 1:center + 1] = [WHITE, BLACK]
        square[center + 0][center - 1:center + 1] = [BLACK, WHITE]
        self.square = square

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.square)

    def __getitem__(self, x):
        return self.square[x]

    def is_playable(self):
        return any(col != BLANK
                   for row in self.square
                   for col in row)

    def count(self, stone):         # 石が何個あるかを返す関数
        return sum(col == stone     # True is 1, False is 0
                   for row in self.square
                   for col in row)

    def put(self, x, y, stone):     # y,xは置く石の座標、stoneにはWHITEかBLACKが入る。
        self[x][y] = stone
        # reverse
        for dx, dy in Board.DIRECTIONS_XY:
            n = self.count_reversible(x, y, dx, dy, stone)
            for i in range(1, n + 1):
                self[x + i * dx][y + i * dy] = stone

    def count_reversible(self, x, y, dx, dy, stone):
        size = self.SIZE
        for n in range(size):
            x += dx
            y += dy
            if not (0 <= x < size and 0 <= y < size):
                return 0
            if self[x][y] == BLANK:
                return 0
            if self[x][y] == stone:
                return n
        return 0

    def is_available(self, x, y, stone):
        if self[x][y] != BLANK:
            return False
        return any(self.count_reversible(x, y, dx, dy, stone) > 0
                   for dx, dy in self.DIRECTIONS_XY)

    def availables(self, stone):  # 打てる場所の探索
        return [(x, y)
                for x in range(self.SIZE)
                for y in range(self.SIZE)
                if self.is_available(x, y, stone)]


class Player:   # abstract class

    def __init__(self, stone, name):
        self.stone = stone
        self.name = name

    def play(self, board):
        availables = board.availables(self.stone)
        if not availables:
            return "pass"
        return self.think(board, availables)


class Computer(Player):

    def think(self, board, availables):
        starttime = time.time()
        print(availables)
        print("thinking……")
        own = self.stone
        opponent = OPPONENT[own]
        evaluations, x, y = AlphaBeta(board, availables, own, opponent)
        print(evaluations)
        board.put(x, y, self.stone)
        endtime = time.time()
        interval = endtime - starttime
        print("%s秒" % interval)  # 計算時間を表示
        return x, y


class User(Player):

    def think(self, board, availables):
        while True:
            print("打てる場所(Y, X): " + str(availables))   # 内部のx,yと表示のX,Yが逆なので注意
            try:
                line = input("Y X or quit: ")
            except:
                print("強制終了")
                exit(1)
            if line == "quit" or line == "exit":
                print("放棄終了")
                exit(1)
            try:
                x, y = map(int, line.split())
                if (x, y) in availables:
                    board.put(x, y, self.stone)
                    return x, y
                else:
                    print("そこには置けません")
            except:
                print("意味不明")


def AlphaBeta(board, availables, own, opponent):  # AlphaBeta法で探索する
    evaluations = AlphaBeta_evaluate1(board, availables, own, opponent)
    if evaluations:
        maximum_evaluation_index = evaluations.index(max(evaluations))
    else:
        maximum_evaluation_index = 0
    x, y = availables[maximum_evaluation_index]
    return evaluations, x, y

def AlphaBeta_evaluate1(board, availables, own, opponent):
    def pruning2(max_evaluations3):
        return len(evaluations1) > 0 and max(evaluations1) >= max_evaluations3
    evaluations1 = []
    for x, y in availables:
        board1 = copy.deepcopy(board)
        board1.put(x, y, own)
        evaluations2 = AlphaBeta_evaluate2(board1, own, opponent, pruning2)
        if len(evaluations2) > 0:
            evaluations1 += [min(evaluations2)]
    return evaluations1

def AlphaBeta_evaluate2(board, own, opponent, pruning):
    def pruning3(min_evaluations4):
        return len(evaluations2) > 0 and min(evaluations2) <= min_evaluations4
    evaluations2 = []
    for x, y in board.availables(opponent):
        board2 = copy.deepcopy(board)
        board2.put(x, y, opponent)
        evaluations3 = AlphaBeta_evaluate3(board2, own, opponent, pruning3)
        if len(evaluations3) > 0:
            max_evaluations3 = max(evaluations3)
            evaluations2 += [max_evaluations3]
            if pruning(max_evaluations3):
                break
    return evaluations2

def AlphaBeta_evaluate3(board, own, opponent, pruning):
    def pruning4(max_evaluations5):
        return len(evaluations3) > 0 and max(evaluations3) >= max_evaluations5
    evaluations3 = []
    for x, y in board.availables(own):
        board3 = copy.deepcopy(board)
        board3.put(x, y, own)
        evaluations4 = AlphaBeta_evaluate4(board3, own, opponent, pruning4)
        if len(evaluations4) > 0:
            min_evaluations4 = min(evaluations4)
            evaluations3 += [min_evaluations4]
            if pruning(min_evaluations4):
                break
    return evaluations3

def AlphaBeta_evaluate4(board, own, opponent, pruning):
    def pruning5(evaluation5):
        return len(evaluations4) > 0 and min(evaluations4) <= evaluation5
    evaluations4 = []
    for x, y in board.availables(opponent):
        board4 = copy.deepcopy(board)
        board4.put(x, y, opponent)
        evaluations5 = AlphaBeta_evaluate5(board4, own, opponent, pruning5)
        if len(evaluations5) > 0:
            max_evaluation5 = max(evaluations5)
            evaluations4 += [max_evaluation5]
            if pruning(max_evaluation5):
                break
    return evaluations4

def AlphaBeta_evaluate5(board, own, opponent, pruning):
    evaluations5 = []
    for x, y in board.availables(own):
        board5 = copy.deepcopy(board)
        board5.put(x, y, own)
        ev_own = evaluate(board5, own)
        ev_opponent = evaluate(board5, opponent)
        evaluation = ev_own - ev_opponent
        evaluations5 += [evaluation]
        if pruning(evaluation):
            break
    return evaluations5


# pp = [45,-11,-16,4,-1,2,-1,-3,-1,0]
EVALUATION_BOARD = (  # どのマスに石があったら何点かを表す評価ボード
    ( 45, -11,  4, -1, -1,  4, -11,  45),
    (-11, -16, -1, -3, -3, -1, -16, -11),
    (  4,  -1,  2, -1, -1,  2,  -1,   4),
    ( -1,  -3, -1,  0,  0, -1,  -3,  -1),
    ( -1,  -3, -1,  0,  0, -1,  -3,  -1),
    (  4,  -1,  2, -1, -1,  2,  -1,   4),
    (-11, -16, -1, -3, -3, -1, -16, -11),
    ( 45, -11,  4, -1, -1,  4, -11,  45))

def evaluate(board, stone):  # 任意の盤面のどちらかの石の評価値を計算する
    bp = 0
    for x in range(board.SIZE):
        for y in range(board.SIZE):
            if board[x][y] == BLANK:
                pass
            elif board[x][y] == stone:
                bp += EVALUATION_BOARD[x][y] * random.random() * 3
            else:
                bp -= EVALUATION_BOARD[x][y] * random.random() * 3

    p = confirm_stone(board, stone)
    q = confirm_stone(board, OPPONENT[stone])
    fs = ((p - q) + random.random() * 3) * 11

    b = board.availables(stone)
    cn = (len(b) + random.random() * 2) * 10

    evaluation = bp * 2 + fs * 5 + cn * 1
    return evaluation

def confirm_stone(board, stone):  # 確定石の数を数える
    forward = range(0, board.SIZE)
    backward = range(board.SIZE - 1, -1, -1)
    corners = ((+0, +0, forward, forward),
               (+0, -1, forward, backward),
               (-1, +0, backward, forward),
               (-1, -1, backward, backward))
    confirm = 0
    for x, y, rangex, rangey in corners:
        for ix in rangex:
            if board[ix][y] != stone:
                break
            confirm += 1
        for iy in rangey:
            if board[x][iy] != stone:
                break
            confirm += 1
    return confirm


if __name__ == '__main__':
    Othello().play()