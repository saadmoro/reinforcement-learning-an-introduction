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
    
    def next_state(self, i, j, token):
        self.board[i, j] = token

    def print_board(self):
        horiz = '----'
        for i in range(BOARD_SIZE):
            horiz += '---'

        for i in range(BOARD_SIZE):
            print(horiz)
            row = '| '
            for j in range(BOARD_SIZE):
                if self.board[i, j] == 1:
                    row += 'X | '
                elif self.board[i,j] == -1:
                    row += 'O | '
                else:
                    row += '. | '
                
            print(row)
        print(horiz)


class Player:

    def __init__(self, step_size = 0.1, epsilon = 0.1):
        self.estimations = dict()
        self.step_size = step_size
        self.epsilon = epsilon
        self.token = 0
        
    def set_token(self, token):
        self.token = token

    def reset(self):
        pass

    def act(self):
        pass

    def save_policy(self):
        pass

    def load_policy(self):
        pass

class game_master:

    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2
        self.current_player = None
        self.p1_token = 1
        self.p2_token = -1
        self.p1.set_token(self.p1_token)
        self.p2.set_token(self.p2_token)
        self.state = State()

    def reset(self):
        self.p1.reset()
        self.p2.reset()

    def alternate(self):
        while True:
            yield self.p1
            yield self.p2

    def play(self):
        alternator = self.alternate()
        self.reset()
        
        while True:
            player = next(alternator)
            i, j, token = player.act()
            #Get hash for next state of the game

            #Set states for each player

            #Check for completion of game

            #Return winner



if __name__ == "__main__":
    game = State()
    game.print_board()
    