import random
import os
import warnings
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import trange

# ======================
# KONFIGURACJA
# ======================
EPISODES = 50000       # liczba gier treningowych
TEST_GAMES = 5000      # liczba gier testowych
EPSILON = 0.1          # eksploracja ε-greedy
LR = 0.001             # learning rate
GAMMA = 0.95           # współczynnik dyskontowania

SAVE_DIR = "AI/bots"
os.makedirs(SAVE_DIR, exist_ok=True)

# Wyłączamy ostrzeżenia DeprecationWarning od torch.onnx
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ======================
# DEFINICJA GRY
# ======================
class TicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [0] * 9
        self.current_player = 1 if random.random() < 0.5 else -1  # losuj kto zaczyna
        return self.board[:]

    def available_moves(self):
        return [i for i, v in enumerate(self.board) if v == 0]

    def make_move(self, move):
        if self.board[move] != 0:
            return False
        self.board[move] = self.current_player
        self.current_player *= -1
        return True

    def winner(self):
        wins = [(0,1,2),(3,4,5),(6,7,8),
                (0,3,6),(1,4,7),(2,5,8),
                (0,4,8),(2,4,6)]
        for a,b,c in wins:
            s = self.board[a] + self.board[b] + self.board[c]
            if s == 3: return 1
            if s == -3: return -1
        if 0 not in self.board:
            return 0
        return None

# ======================
# SIEĆ NEURONOWA
# ======================
class Bot(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(9, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 9)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# ======================
# WYBÓR RUCHU ε-greedy
# ======================
def select_move(bot, state, available, epsilon):
    if random.random() < epsilon:
        return random.choice(available)
    state_t = torch.tensor(state, dtype=torch.float32)
    with torch.no_grad():
        q_values = bot(state_t)
    q_values = q_values.numpy()
    # maska niedozwolonych ruchów
    for i in range(9):
        if i not in available:
            q_values[i] = -1e9
    return int(q_values.argmax())

# ======================
# TRENING (self-play)
# ======================
def train(bot_X, bot_O):
    optim_X = optim.Adam(bot_X.parameters(), lr=LR)
    optim_O = optim.Adam(bot_O.parameters(), lr=LR)
    loss_fn = nn.MSELoss()

    env = TicTacToe()

    for _ in trange(EPISODES, desc="Trening X vs O"):
        state = env.reset()
        history = []

        while True:
            current_bot = bot_X if env.current_player == 1 else bot_O
            move = select_move(current_bot, state, env.available_moves(), EPSILON)
            env.make_move(move)
            next_state = env.board[:]
            winner = env.winner()
            history.append((state[:], move, env.current_player * -1))  # zapis ruchu
            if winner is not None:
                # nagrody z biasem: X ma lekką przewagę
                for s, m, p in history:
                    reward = 0
                    if winner == p:
                        reward = 1.2 if p == 1 else 1.0   # X dostaje +20%
                    elif winner == -p:
                        reward = -1
                    # aktualizacja sieci
                    bot = bot_X if p == 1 else bot_O
                    optim_bot = optim_X if p == 1 else optim_O

                    s_t = torch.tensor(s, dtype=torch.float32)
                    target = bot(s_t).clone().detach()
                    target[m] = reward

                    q_pred = bot(s_t)

                    loss = loss_fn(q_pred, target)
                    optim_bot.zero_grad()
                    loss.backward()
                    optim_bot.step()
                break
            state = next_state

# ======================
# TESTOWANIE
# ======================
def test(bot_X, bot_O):
    results = {"X": 0, "O": 0, "Draw": 0}
    env = TicTacToe()

    for _ in trange(TEST_GAMES, desc="Testowanie meczów"):
        state = env.reset()
        while True:
            current_bot = bot_X if env.current_player == 1 else bot_O
            move = select_move(current_bot, state, env.available_moves(), 0.0)  # bez eksploracji
            env.make_move(move)
            state = env.board[:]
            winner = env.winner()
            if winner is not None:
                if winner == 1: results["X"] += 1
                elif winner == -1: results["O"] += 1
                else: results["Draw"] += 1
                break
    return results

# ======================
# GŁÓWNY SKRYPT
# ======================
if __name__ == "__main__":
    bot_X, bot_O = Bot(), Bot()

    print("🔄 Trening w trybie self-play...")
    train(bot_X, bot_O)

    print("🎮 Rozgrywki testowe...")
    results = test(bot_X, bot_O)
    print("📊 Wyniki z", TEST_GAMES, "gier:")
    print(results)

    # Eksport do ONNX (zapis w AI/bots)
    dummy = torch.randn(9, dtype=torch.float32)
    torch.onnx.export(bot_X, dummy, os.path.join(SAVE_DIR, "tictactoe_X.onnx"),
                      input_names=['board'], output_names=['move'])
    torch.onnx.export(bot_O, dummy, os.path.join(SAVE_DIR, "tictactoe_O.onnx"),
                      input_names=['board'], output_names=['move'])

    print(f"Modele zapisane jako ONNX w folderze {SAVE_DIR} ✅")
