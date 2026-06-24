import asyncio
import json
import os
import datetime
import traceback
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from engine import GameState, Player, GameEngine

app = FastAPI(title="Monopoly MAS API")

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
    
    state = None
    engine = None
    log_filename = ""
    game_history_dataset = []
    
    def generate_payload():
        if not state:
            return {}
        
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
                    "buildings": s.buildings,
                    "color": s.color,
                    "price": s.price,
                    "house_cost": s.house_cost,
                    "space_type": s.space_type.value
                } for s in state.board
            ],
            "recent_logs": state.logs[-50:]
        }
    
    try:
        while True:
            try:
                data_str = await websocket.receive_text()
            except WebSocketDisconnect:
                print("\n🔌 Frontend disconnected (Tab closed or backgrounded). Waiting for reconnect...")
                break
            except Exception as e:
                if "keepalive" in str(e).lower() or "10054" in str(e):
                    print("\n🔌 Browser throttled the inactive tab. Socket dead.")
                    break
                raise e
            
            if data_str == "NEXT_TURN" and engine is not None:
                engine.execute_turn()
                current_payload = generate_payload()
                
                game_history_dataset.append(current_payload)
                with open(log_filename, "w", encoding="utf-8") as dataset_file:
                    json.dump(game_history_dataset, dataset_file, indent=4, ensure_ascii=False)
                
                try:
                    await websocket.send_json(current_payload)
                except Exception as e:
                    print(f"\n⚠️ Could not send payload to frontend (Tab likely sleeping): {e}")
                    break
            
            else:
                try:
                    data = json.loads(data_str)
                    if data.get("action") == "INIT":
                        print("\n🚀 INITIALIZING NEW GAME SESSION...")
                        players_config = data.get("players", [])
                        
                        players = []
                        for idx, p_data in enumerate(players_config):
                            players.append(Player(id=idx, name=p_data["name"], model_name=p_data["model"]))
                            print(f"   -> Added {p_data['name']} ({p_data['model']})")
                        
                        state = GameState(players=players)
                        engine = GameEngine(state)
                        
                        session_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        log_filename = f"logs/game_session_{session_timestamp}.json"
                        
                        initial_payload = generate_payload()
                        await websocket.send_json(initial_payload)
                        print("✅ Game successfully initialized and sent to frontend.\n")
                
                except json.JSONDecodeError:
                    print("Unrecognized command received.")
                    
    except Exception as e:
        print(f"\n❌ SERVER CRASH:")
        traceback.print_exc()
        print(f"Simulation WebSocket connection closed: {e}\n")