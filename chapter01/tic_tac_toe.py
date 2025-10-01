import numpy as np
import pickle


BOARD_SIZE = 3
PRIORITY_PROB = 0.5


class State:

    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE))
        self.hash_val = None
        self.winner = None
        self.finish = None

    def hash(self):
        if self.hash_val == None:
            self.hash_val = 0

            for i in np.nditer(self.board):
                self.hash_val = self.hash_val * 3 + i + 1

        return self.hash_val

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
        new_state = State()
        new_state.board = np.copy(self.board)
        self.board[i, j] = token
        return new_state

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

def get_all_states_adjacent(current_state, current_symbol, all_states):
    for i in range(BOARD_SIZE):

        for j in range(BOARD_SIZE):

            if current_state.board[i][j] == 0:
                new_state = current_state.next_state(i, j, current_symbol)
                new_hash = new_state.hash()

                if new_hash not in all_states:
                    is_finished = new_state.is_finished()
                    all_states[new_hash] = (new_state, is_finished)

                    if not is_finished:
                        get_all_states_adjacent(new_state, -current_symbol, all_states)

def get_all_states():
    current_symbol = 1
    current_state = State()
    all_states = dict()
    all_states[current_state.hash()] = (current_state, current_state.is_finished())
    get_all_states_adjacent(current_state, current_symbol, all_states)
    return all_states

ALL_STATES = get_all_states()


class Player:

    def __init__(self, step_size = 0.1, epsilon = 0.1):
        self.estimations = dict()
        self.step_size = step_size
        self.epsilon = epsilon
        self.states = []
        self.token = 0
        
    def initialize_estimations(self, token):
        self.token = token

        for hash_val in ALL_STATES:
            state, is_finished = ALL_STATES[hash_val]

            if is_finished:
                if state.winner == self.token:
                    self.estimations[hash_val] = 1.0
                elif state.winner == 0:
                    self.estimations[hash_val] = 0.5
                else:
                    self.estimations[hash_val] = 0.0
            else:
                self.estimations[hash_val] = 0.5


    #TODO: CHECK BOOK
    def update(self):
        states = [state.hash() for state in self.states]
        
        for i in reversed(range(len(states) - 1)):
            state = states[i]
            td_error = self.greedy[i] * (
                self.estimations[states[i + 1]] - self.estimations[state]
            )
            self.estimations[state] += self.step_size * td_error


    def reset(self):
        self.states = []

    def act(self):
        state = self.states[-1]
        next_states = []
        next_positions = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if state.data[i, j] == 0:
                    next_positions.append([i, j])
                    next_states.append(state.next_state(i, j, self.symbol).hash())
        
        if np.random.rand() < self.epsilon:
            action = next_positions[np.random.randint(len(next_positions))]
            action.append(self.token)
            self.greedy[-1] = False
            return action
        
        values = []
        #TODO: HERE NEXT

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

def main():
    all_states = get_all_states()


if __name__ == "__main__":
    

    #TODO: pylint
    