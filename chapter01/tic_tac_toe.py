import numpy as np
import pickle


BOARD_SIZE = 3
PRIORITY_PROB = 0.5

class State:

    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE))
        self.winner = None
        self.finish = None

    def is_finished(self):
        
        if self.finish is not None:
            return self.finish

        counts = []
        diag = 0
        reverse_diag = 0

        #Calculate results for each row and column
        for i in range(BOARD_SIZE):
            counts.append(np.sum(self.board[i,:]))
            counts.append(np.sum(self.board[:,i]))
        
        #Calculate results for both diagonals
        for i in range(BOARD_SIZE):
            diag += self.board[i, i]
            reverse_diag += self.board[i, BOARD_SIZE - 1 - i]

        counts.append(diag)
        counts.append(reverse_diag)

        if 3 in counts:
            self.winner = 1
            self.finish = True
            return self.finish
        
        if -3 in counts:
            self.winner = -1
            self.finish = True
            return self.finish
        
        #If board is fully populated --> draw
        board_sum = np.sum(np.abs(self.board))
        if board_sum == BOARD_SIZE * BOARD_SIZE:
            self.winner = 0
            self.finish = True
            return self.finish



        #Game has not ended
        self.finish = False
        return self.finish



class Player:

    def __init__(self):
        pass

if __name__ == "__main__":
    game = State()
    