import json

# Wczytaj swój stary plik JSON (Python dict)
with open("AI/bots/agent_O.json", "r") as f:
    old_data = json.load(f)

# Wybierz tylko wartości dla pustej planszy
# Załóżmy, że pustą planszą jest klucz "((' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '), 0)"
empty_board_key = "((' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '), 0)"

move_values = []
for i in range(9):
    key = f"((' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '), {i})"
    move_values.append(old_data.get(key, 0.0))  # domyślnie 0.0 jeśli nie ma wartości

# Stwórz nowy format do Unity
new_data = {
    "moveValues": move_values
}

# Zapisz do nowego pliku JSON
with open("AI/bots/botHard_O.json", "w") as f:
    json.dump(new_data, f, indent=4)

print("Gotowe! Plik zapisany jako botHard_X_unity.json")
