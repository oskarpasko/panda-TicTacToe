import random
import pickle
from collections import defaultdict
from tqdm import trange

# ----------------------
# Środowisko gry
# ----------------------
class TicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [" "] * 9
        self.current_player = "O"  # O zawsze dla treningu O
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
            else:
                rewards = {"X": 0, "O": 0}

        self.current_player = "X" if self.current_player == "O" else "O"
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

# ----------------------
# Q-learning Agent
# ----------------------
class QLearningAgent:
    def __init__(self, symbol, alpha=0.1, gamma=0.9, epsilon=0.8):
        self.symbol = symbol
        self.q_table = defaultdict(float)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def get_q(self, state, action):
        return self.q_table[(state, action)]

    def choose_action(self, state, available_moves, exploit=False):
        if not exploit and random.random() < self.epsilon:
            return random.choice(available_moves)
        qs = [self.get_q(state, a) for a in available_moves]
        max_q = max(qs)
        best_moves = [a for a, q in zip(available_moves, qs) if q == max_q]
        return random.choice(best_moves)

    def learn(self, state, action, reward, next_state, next_moves):
        old_q = self.q_table[(state, action)]
        next_q = max([self.get_q(next_state, a) for a in next_moves]) if next_moves else 0
        self.q_table[(state, action)] = old_q + self.alpha * (reward + self.gamma * next_q - old_q)

# ----------------------
# Trening agenta O
# ----------------------
def train_O(agent_o, episodes=50000, decay=0.9999):
    for ep in trange(episodes, desc="Trening O"):
        env = TicTacToe()
        state = env.reset()
        done = False

        while not done:
            if env.current_player == "O":
                moves = env.available_moves()
                action = agent_o.choose_action(state, moves)
                next_state, rewards, done = env.step(action)
                next_moves = env.available_moves()
                agent_o.learn(state, action, rewards["O"], next_state, next_moves)
                state = next_state
            else:
                moves = env.available_moves()
                action = random.choice(moves)  # X losowo
                state, rewards, done = env.step(action)

        agent_o.epsilon *= decay

# ----------------------
# Uruchomienie treningu
# ----------------------
if __name__ == "__main__":
    agent_O_easy = QLearningAgent("O", epsilon=0.8)
    train_O(agent_O_easy, episodes=100000)

    # Zapis do pliku
    with open("AI/bots/agent_O_hard.pkl", "wb") as f:
        pickle.dump(agent_O_easy.q_table, f)
    print("Trening O zakończony i zapisany do agent_O_easy.pkl")
