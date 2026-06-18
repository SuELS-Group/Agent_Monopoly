import asyncio
import json
import os
import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from engine import GameState, Player, GameEngine

app = FastAPI(title="Monopoly MAS API")

# Ensure the logs directory exists for our datasets
if not os.path.exists("logs"):
    os.makedirs("logs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/simulation")
async def simulation_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize environment
    player1 = Player(id=0, name="Agent_Alpha", model_name="llama3")
    player2 = Player(id=1, name="Agent_Beta", model_name="mistral")
    state = GameState(players=[player1, player2])
    engine = GameEngine(state)
    
    # Initialize data logging properties
    session_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/game_session_{session_timestamp}.json"
    game_history_dataset = []
    
    def generate_payload():
        # Calculate dynamic net worth for each active player
        player_net_worth = {}
        for p in state.players:
            net_worth = p.balance
            for s in state.board:
                if s.owner_id == p.id:
                    net_worth += (s.price // 2)
                    if s.buildings > 0:
                        net_worth += (s.buildings * (s.house_cost // 2))
            player_net_worth[p.id] = net_worth

        return {
            "turn": state.turn_number,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "balance": p.balance,
                    "net_worth": player_net_worth[p.id],
                    "position": p.position,
                    "is_bankrupt": p.is_bankrupt,
                    "is_in_jail": p.is_in_jail
                } for p in state.players
            ],
            "board": [
                {
                    "id": s.id,
                    "name": s.name,
                    "owner_id": s.owner_id,
                    "is_mortgaged": s.is_mortgaged,
                    "buildings": s.buildings
                } for s in state.board
            ],
            "recent_logs": state.logs[-7:]
        }
    
    try:
        # Send initial state (Turn 0)
        initial_payload = generate_payload()
        await websocket.send_json(initial_payload)
        
        while True:
            data = await websocket.receive_text()
            
            if data == "NEXT_TURN":
                engine.execute_turn()
                current_payload = generate_payload()
                
                # Append to our local historical data list and commit to file
                game_history_dataset.append(current_payload)
                with open(log_filename, "w", encoding="utf-8") as dataset_file:
                    json.dump(game_history_dataset, dataset_file, indent=4, ensure_ascii=False)
                
                await websocket.send_json(current_payload)
                
    except Exception as e:
        print(f"Simulation WebSocket connection closed: {e}")