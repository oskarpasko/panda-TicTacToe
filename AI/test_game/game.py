import pickle
from collections import defaultdict
import os
import random

# ----------------------
# Środowisko gry
# ----------------------
class TicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [" "] * 9
        return tuple(self.board)

    def print_board(self):
        b = self.board
        print(f"{b[0]} | {b[1]} | {b[2]}")
        print("---------")
        print(f"{b[3]} | {b[4]} | {b[5]}")
        print("---------")
        print(f"{b[6]} | {b[7]} | {b[8]}")
        print()

    def available_moves(self):
        return [i for i, x in enumerate(self.board) if x == " "]

    def step(self, action, player):
        if self.board[action] != " ":
            return False, None, None
        self.board[action] = player
        winner = self.check_winner()
        done = winner is not None or " " not in self.board
        rewards = {"X": 0, "O": 0}
        if done:
            if winner == "X":
                rewards = {"X": 1, "O": -1}
            elif winner == "O":
                rewards = {"X": -1, "O": 1}
            else:
                rewards = {"X": 0, "O": 0}
        return True, rewards, done

    def check_winner(self):
        lines = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        for a,b,c in lines:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                return self.board[a]
        return None

# ----------------------
# Q-learning Agent
# ----------------------
class QLearningAgent:
    def __init__(self, symbol, q_table=None):
        self.symbol = symbol
        self.q_table = q_table or defaultdict(float)

    def choose_action(self, state, available_moves):
        qs = [self.q_table.get((state, a), 0) for a in available_moves]
        max_q = max(qs)
        best_moves = [a for a, q in zip(available_moves, qs) if q == max_q]
        return random.choice(best_moves)  # losowy wybór spośród najlepszych

# ----------------------
# Gra z botem
# ----------------------
def play_game(agent, human_symbol):
    env = TicTacToe()
    bot_symbol = agent.symbol
    # jeśli bot jest X, zaczyna
    current_player = "X"
    state = env.reset()
    done = False

    print("\nPlansza:")
    env.print_board()

    while not done:
        if current_player == bot_symbol:
            # ruch bota
            moves = env.available_moves()
            action = agent.choose_action(state, moves)
            _, _, done = env.step(action, bot_symbol)
            print(f"Bot ({bot_symbol}) zagrał na polu {action+1}")
        else:
            # ruch człowieka
            moves = env.available_moves()
            move = None
            while move not in moves:
                try:
                    move = int(input(f"Twój ruch ({human_symbol}) [1-9]: ")) - 1
                except ValueError:
                    move = -1
            _, _, done = env.step(move, human_symbol)

        state = tuple(env.board)
        env.print_board()
        # zmiana kolejki
        current_player = human_symbol if current_player == bot_symbol else bot_symbol

    winner = env.check_winner()
    if winner == bot_symbol:
        print("Bot wygrał!")
    elif winner == human_symbol:
        print("Wygrałeś!")
    else:
        print("Remis!")

# ----------------------
# Uruchomienie
# ----------------------
if __name__ == "__main__":
    file_path = os.path.join("AI", "bots", input("Podaj plik z botem (np. agent_X_easy.pkl): "))
    human_symbol = input("Wybierz swój symbol (X lub O): ").upper()
    human_symbol = human_symbol if human_symbol in ["X","O"] else "X"

    with open(file_path, "rb") as f:
        q_table = pickle.load(f)

    bot_agent = QLearningAgent("O" if human_symbol == "X" else "X", q_table)
    play_game(bot_agent, human_symbol)
