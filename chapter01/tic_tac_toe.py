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
        new_state.board[i, j] = token
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
        self.greedy = []
        self.token = 0
        
    def set(self, token):
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


    #V(S_t) <- V(S_t) + alpha * [V(S_(t+1)) - V(S_t)]
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

    def set_state(self, state):
        self.states.append(state)
        self.greedy.append(True)

    def act(self):
        state = self.states[-1]
        next_states = []
        next_positions = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if state.board[i, j] == 0:
                    next_positions.append([i, j])
                    next_states.append(state.next_state(i, j, self.token).hash())
        
        if np.random.rand() < self.epsilon:
            action = next_positions[np.random.randint(len(next_positions))]
            action.append(self.token)
            self.greedy[-1] = False
            return action
        
        values = []
        for hash_val, pos in zip(next_states, next_positions):
            values.append((self.estimations[hash_val], pos))
        np.random.shuffle(values)
        values.sort(key = lambda x: x[0], reverse = True)
        action = values[0][1]
        action.append(self.token)
        return action

    def save_policy(self):
        with open('policy_%s.bin' % ('first' if self.token == 1 else 'second'), 'wb') as f:
            pickle.dump(self.estimations, f)

    def load_policy(self):
        with open('policy_%s.bin' % ('first' if self.token == 1 else 'second'), 'rb') as f:
            self.estimations = pickle.load(f)

class Game_Master:

    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2
        self.current_player = None
        self.p1_token = 1
        self.p2_token = -1
        self.p1.set(self.p1_token)
        self.p2.set(self.p2_token)
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

        current_state = State()
        self.p1.set_state(current_state)
        self.p2.set_state(current_state)
        
        while True:
            player = next(alternator)
            i, j, token = player.act()
            #Get hash for next state of the game
            next_state_hash = current_state.next_state(i, j, token).hash()
            current_state, is_finished = ALL_STATES[next_state_hash]
            #Set states for each player
            self.p1.set_state(current_state)
            self.p2.set_state(current_state)

            #Check for completion of game
            if is_finished:
                return current_state.winner
            #Return winner

def train(epochs, print_every_n = 500):
    player1 = Player(epsilon = 0.01)
    player2 = Player(epsilon = 0.01)

    gm = Game_Master(player1, player2)

    player1_win = 0.0
    player2_win = 0.0
    ties = 0.0

    for i in range(1, epochs + 1):
        winner = gm.play()
        if winner == 1:
            player1_win +=1
        if winner == -1:
            player2_win += 1
        if winner == 0:
            ties += 1
        if i % print_every_n == 0:
            print('Epoch %d, Player 1 Winrate: %.02f, Player 2 Winrate: %0.2f, Tie Rate: %.02f' % (i, player1_win/ i, player2_win / i, ties / i))

        player1.update()
        player2.update()

        gm.reset()

    player1.save_policy()
    player2.save_policy()

def compete(turns):
    player1 = Player(epsilon=0)
    player2 = Player(epsilon=0)

    gm = Game_Master(player1, player2)
    player1.load_policy()
    player2.load_policy()
    player1_win = 0.0
    player2_win = 0.0
    ties = 0.0

    for _ in range(turns):
        winner = gm.play()
        if winner == 1:
            player1_win += 1
        if winner == -1:
            player2_win += 1
        if winner == 0:
            ties += 1
        gm.reset()

    print('In %d turns, Player 1 winrate: %.02f, Player 2 win %.02f, Tie Rate: %.02f' % (turns, player1_win / turns, player2_win / turns, ties / turns))

if __name__ == "__main__":
    
    train(int(1e5))
    compete(int(1e3))
    