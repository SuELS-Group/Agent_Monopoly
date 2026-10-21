from engine import GameState, Player, GameEngine

player1 = Player(id=0, name="Agent_Alpha", model_name="llama3:latest")
player2 = Player(id=1, name="Agent_Beta", model_name="llama3:latest")

state = GameState(players=[player1, player2])
engine = GameEngine(state)

print("--- STARTING ENGINE SIMULATION ---")
for _ in range(20):
    engine.execute_turn()

for log in state.logs:
    print(log)

print("\n--- FINAL AGENT STATE ---")
for p in state.players:
    print(f"{p.name} -> Position: {p.position} | Balance: ${p.balance} | In Jail: {p.is_in_jail}")