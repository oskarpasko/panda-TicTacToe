import pickle
import random
from collections import defaultdict
from tqdm import trange
import os

# ----------------------
# KONFIGURACJA BOTÓW
# ----------------------
CONFIG = {
    "alpha": 0.1,            # szybkość uczenia się Q-table (0-1). Wyższe = szybciej się uczy.
    "gamma": 0.9,            # współczynnik dyskontowania przyszłych nagród (0-1). Wyższe = bardziej przewiduje przyszłość.
    "epsilon": 0.8,          # eksploracja (0-1). Wyższe = częściej losowy ruch, niż najlepszy wg Q.
    "heuristic_bonus": 0.1    # premia za blokadę wygranej przeciwnika lub wygranie samemu. Wyższe = bot częściej blokuje i wygrywa.
}

# ----------------------
# Środowisko gry
# ----------------------
class TicTacToe:
    def __init__(self):
        self.reset()

    def reset(self, starting_player="X"):
        self.board = [" "] * 9
        self.current_player = starting_player
        return tuple(self.board)

    def available_moves(self):
        return [i for i, x in enumerate(self.board) if x == " "]

    def step(self, action):
        self.board[action] = self.current_player
        winner = self.check_winner()
        done = winner is not None or " " not in self.board

        rewards = {"X": 0, "O": 0}
        if done:
            if winner == "X":
                rewards = {"X": 1, "O": -1}
            elif winner == "O":
                rewards = {"X": -1, "O": 1}

        self.current_player = "O" if self.current_player == "X" else "X"
        return tuple(self.board), rewards, done

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

    def print_board(self):
        b = self.board
        print(f"{b[0]} | {b[1]} | {b[2]}")
        print("---------")
        print(f"{b[3]} | {b[4]} | {b[5]}")
        print("---------")
        print(f"{b[6]} | {b[7]} | {b[8]}")
        print()

# ----------------------
# Q-learning Agent z miękką heurystyką
# ----------------------
class QLearningAgent:
    def __init__(self, symbol):
        self.symbol = symbol
        self.q_table = defaultdict(float)
        self.alpha = CONFIG["alpha"]
        self.gamma = CONFIG["gamma"]
        self.epsilon = CONFIG["epsilon"]
        self.heuristic_bonus = CONFIG["heuristic_bonus"]

    def get_q(self, state, action):
        return self.q_table[(state, action)]

    def choose_action(self, state, available_moves, board=None, exploit=False):
        move_scores = []
        for move in available_moves:
            score = self.get_q(state, move)
            if board is not None:
                # sprawdzamy, czy ruch blokuje przeciwnika
                tmp = board.copy()
                tmp[move] = "O" if self.symbol == "X" else "X"
                if TicTacToe.check_winner_static(tmp) == ("O" if self.symbol == "X" else "X"):
                    score += self.heuristic_bonus
                # sprawdzamy, czy ruch daje wygraną
                tmp[move] = self.symbol
                if TicTacToe.check_winner_static(tmp) == self.symbol:
                    score += self.heuristic_bonus
            move_scores.append(score)

        max_score = max(move_scores)
        best_moves = [m for m, s in zip(available_moves, move_scores) if s == max_score]

        if not exploit and random.random() < self.epsilon:
            return random.choice(available_moves)  # eksploracja
        return random.choice(best_moves)  # najlepsze wg Q + heurystyki

    def learn(self, state, action, reward, next_state, next_moves):
        old_q = self.q_table[(state, action)]
        next_q = max([self.get_q(next_state, a) for a in next_moves]) if next_moves else 0
        self.q_table[(state, action)] = old_q + self.alpha * (reward + self.gamma * next_q - old_q)

# statyczna metoda do heurystyki
def check_winner_static(board):
    lines = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in lines:
        if board[a] == board[b] == board[c] != " ":
            return board[a]
    return None
TicTacToe.check_winner_static = staticmethod(check_winner_static)

# ----------------------
# Trening self-play
# ----------------------
def train(agent_x, agent_o, episodes=50000, decay=0.9999):
    for ep in trange(episodes, desc="Trening"):
        env = TicTacToe()
        state = env.reset()
        done = False

        while not done:
            current_agent = agent_x if env.current_player == "X" else agent_o
            moves = env.available_moves()
            action = current_agent.choose_action(state, moves, board=env.board)
            next_state, rewards, done = env.step(action)
            next_moves = env.available_moves()
            current_agent.learn(state, action, rewards[current_agent.symbol], next_state, next_moves)
            state = next_state

        agent_x.epsilon *= decay
        agent_o.epsilon *= decay

    os.makedirs("AI/bots", exist_ok=True)
    with open("AI/bots/agent_X.pkl", "wb") as f:
        pickle.dump(agent_x.q_table, f)
    with open("AI/bots/agent_O.pkl", "wb") as f:
        pickle.dump(agent_o.q_table, f)
    print("Trening zakończony i zapisany.")

# ----------------------
# Test botów
# ----------------------
def test(agent_x, agent_o, episodes=10000):
    results = {"X_win":0, "O_win":0, "draw":0}
    for _ in trange(episodes, desc="Testowanie"):
        env = TicTacToe()
        state = env.reset()
        done = False
        while not done:
            current_agent = agent_x if env.current_player == "X" else agent_o
            moves = env.available_moves()
            action = current_agent.choose_action(state, moves, board=env.board, exploit=True)
            state, rewards, done = env.step(action)

        winner = env.check_winner()
        if winner == "X":
            results["X_win"] += 1
        elif winner == "O":
            results["O_win"] += 1
        else:
            results["draw"] += 1

    total = sum(results.values())
    print(f"\n📊 Wyniki z {total} gier:")
    print(f"X wygrane : {100*results['X_win']/total:.2f}%")
    print(f"O wygrane : {100*results['O_win']/total:.2f}%")
    print(f"Remisy    : {100*results['draw']/total:.2f}%")

# ----------------------
# Gra z człowiekiem
# ----------------------
def play_human():
    file_path = os.path.join("AI", "bots", input("Podaj plik z botem (X lub O, np. agent_X.pkl): "))
    human_symbol = input("Wybierz swój symbol (X lub O): ").upper()
    with open(file_path, "rb") as f:
        q_table = pickle.load(f)
    bot_symbol = "O" if human_symbol == "X" else "X"
    agent_bot = QLearningAgent(bot_symbol)
    agent_bot.q_table = q_table

    env = TicTacToe()
    state = env.reset(starting_player="X")
    done = False
    env.print_board()

    while not done:
        if env.current_player == human_symbol:
            move = None
            moves = env.available_moves()
            while move not in moves:
                try:
                    move = int(input(f"Twój ruch ({human_symbol}) [1-9]: ")) - 1
                except:
                    move = -1
            state, rewards, done = env.step(move)
        else:
            moves = env.available_moves()
            action = agent_bot.choose_action(state, moves, board=env.board, exploit=True)
            state, rewards, done = env.step(action)
            print(f"Bot ({bot_symbol}) zagrał na polu {action+1}")
        env.print_board()

    winner = env.check_winner()
    if winner == human_symbol:
        print("Wygrałeś!")
    elif winner == bot_symbol:
        print("Bot wygrał!")
    else:
        print("Remis!")

# ----------------------
# Menu
# ----------------------
if __name__ == "__main__":
    while True:
        print("1. Trening self-play")
        print("2. Test botów")
        print("3. Gra z człowiekiem")
        print("4. Wyjście")
        choice = input("Wybierz opcję [1-4]: ")
        if choice == "1":
            agent_x = QLearningAgent("X")
            agent_o = QLearningAgent("O")
            episodes = int(input("Podaj liczbę epizodów treningu: "))
            train(agent_x, agent_o, episodes=episodes)
        elif choice == "2":
            agent_x = QLearningAgent("X")
            agent_o = QLearningAgent("O")
            with open("AI/bots/agent_X.pkl","rb") as f:
                agent_x.q_table = pickle.load(f)
            with open("AI/bots/agent_O.pkl","rb") as f:
                agent_o.q_table = pickle.load(f)
            episodes = int(input("Podaj liczbę gier testowych: "))
            test(agent_x, agent_o, episodes=episodes)
        elif choice == "3":
            play_human()
        elif choice == "4":
            break
        else:
            print("Niepoprawna opcja, spróbuj ponownie.")
