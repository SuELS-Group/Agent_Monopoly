"use client";

import { useEffect, useState, useRef } from "react";

interface Player {
  id: number;
  name: string;
  balance: number;
  net_worth: number;
  position: number;
  is_bankrupt: boolean;
  is_in_jail: boolean;
}

interface Space {
  id: number;
  name: string;
  owner_id: number | null;
  is_mortgaged: boolean;
  buildings: number;
}

interface GameState {
  turn: number;
  players: Player[];
  board: Space[];
  recent_logs: string[];
}

export default function Dashboard() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isAutoPlay, setIsAutoPlay] = useState(false);
  const [autoPlaySpeed, setAutoPlaySpeed] = useState(1500); // Default delay matching reading speed (1.5s)
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/simulation");
    
    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => {
      setIsConnected(false);
      setIsAutoPlay(false);
    };
    socket.onmessage = (event) => {
      setGameState(JSON.parse(event.data));
    };

    wsRef.current = socket;
    return () => socket.close();
  }, []);

  const nextTurn = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send("NEXT_TURN");
    }
  };

  // Auto-play throttling loop implementation
  useEffect(() => {
    let playInterval: NodeJS.Timeout | null = null;
    
    if (isAutoPlay && isConnected) {
      playInterval = setInterval(() => {
        nextTurn();
      }, autoPlaySpeed);
    }
    
    return () => {
      if (playInterval) clearInterval(playInterval);
    };
  }, [isAutoPlay, isConnected, autoPlaySpeed]);

  if (!gameState) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
        <h1 className="text-2xl animate-pulse">Waiting for Python Engine connection...</h1>
      </div>
    );
  }

  const totalWealth = Math.max(1, ...gameState.players.map(p => p.net_worth));

  // Identity Map to bind strict styling profiles based on Agent ID
  const getAgentTheme = (id: number) => {
    return id === 0 
      ? { token: "bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]", border: "border-emerald-500", text: "text-emerald-400" }
      : { token: "bg-rose-400 shadow-[0_0_10px_rgba(251,113,133,0.8)]", border: "border-rose-500", text: "text-rose-400" };
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 flex flex-col font-sans">
      
      {/* HEADER WITH INTEGRATED CONTROLS */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-800 pb-4 mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-blue-400">MAS Simulation: Monopoly</h1>
          <p className="text-sm text-gray-500 mt-1">
            Status: <span className={isConnected ? "text-green-500" : "text-red-500"}>
              {isConnected ? "Connected (WebSocket)" : "Disconnected"}
            </span>
          </p>
        </div>
        
        {/* ACTION AND THROTTLE CONTROLS */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex bg-gray-900 border border-gray-800 rounded-lg p-1 text-xs font-semibold">
            <button onClick={() => setAutoPlaySpeed(2500)} className={`px-3 py-1.5 rounded-md ${autoPlaySpeed === 2500 ? 'bg-gray-800 text-blue-400' : 'text-gray-400'}`}>Slow</button>
            <button onClick={() => setAutoPlaySpeed(1500)} className={`px-3 py-1.5 rounded-md ${autoPlaySpeed === 1500 ? 'bg-gray-800 text-blue-400' : 'text-gray-400'}`}>Normal</button>
            <button onClick={() => setAutoPlaySpeed(600)} className={`px-3 py-1.5 rounded-md ${autoPlaySpeed === 600 ? 'bg-gray-800 text-blue-400' : 'text-gray-400'}`}>Fast</button>
          </div>

          <button 
            onClick={() => setIsAutoPlay(!isAutoPlay)}
            disabled={!isConnected}
            className={`px-5 py-2.5 rounded-lg font-semibold transition-colors shadow-lg text-white ${isAutoPlay ? 'bg-amber-600 hover:bg-amber-500' : 'bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700'}`}
          >
            {isAutoPlay ? "⏸️ Pause Simulation" : "▶️ Auto-Play"}
          </button>

          <button 
            onClick={nextTurn}
            disabled={!isConnected || isAutoPlay}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white px-5 py-2.5 rounded-lg font-semibold transition-all shadow-lg"
          >
            👉 Step Turn {gameState.turn}
          </button>
        </div>
      </header>

      {/* WEB APPLICATION GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        
        {/* BOARD PLATFORM CONTAINER */}
        <div className="col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-4 overflow-y-auto" style={{ maxHeight: "calc(100vh - 150px)" }}>
          <h2 className="text-xl font-bold mb-4 border-b border-gray-800 pb-2">Board State (40 Spaces)</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {gameState.board.map((space) => {
              const playersHere = gameState.players.filter(p => p.position === space.id);
              const owner = gameState.players.find(p => p.id === space.owner_id);
              
              const isMortgaged = space.is_mortgaged;
              const bgClass = owner 
                ? (isMortgaged ? 'border-red-900 bg-red-950/10 opacity-60' : 'border-blue-900 bg-blue-950/20') 
                : 'border-gray-800 bg-gray-800/40';

              return (
                <div key={space.id} className={`p-3 rounded-lg text-sm border ${bgClass} relative flex flex-col justify-between h-24 transition-all duration-300`}>
                  <div>
                    <div className="text-xs text-gray-500 flex justify-between items-center">
                      <span>#{space.id}</span>
                      {isMortgaged && <span className="text-red-400 font-bold text-xs">MORTGAGED 🔒</span>}
                    </div>
                    <div className={`font-semibold truncate mt-0.5 ${isMortgaged ? 'line-through text-gray-500' : ''}`} title={space.name}>
                      {space.name}
                    </div>
                  </div>
                  
                  <div className="mt-auto">
                    {owner && (
                      <div className={`text-xs font-medium ${getAgentTheme(owner.id).text}`}>
                        Owner: {owner.name}
                      </div>
                    )}

                    {space.buildings > 0 && !isMortgaged && (
                      <div className="flex gap-1 mt-1">
                        {space.buildings === 5 ? (
                          <div className="w-3 h-3 bg-red-500 rounded-sm" title="Hotel"></div>
                        ) : (
                          Array.from({ length: space.buildings }).map((_, i) => (
                            <div key={i} className="w-2 h-2 bg-blue-400 rounded-sm" title="House"></div>
                          ))
                        )}
                      </div>
                    )}
                  </div>

                  {/* IDENTIFIABLE COLORED TOKENS */}
                  <div className="flex gap-1.5 absolute top-2 right-2">
                    {playersHere.map(p => (
                      <span 
                        key={p.id} 
                        className={`inline-block w-3.5 h-3.5 rounded-full border border-gray-950 transition-all duration-300 ${getAgentTheme(p.id).token}`} 
                        title={p.name}
                      ></span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* METRICS SIDEBAR CONTAINER */}
        <div className="flex flex-col gap-6">
          
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <h2 className="text-xl font-bold mb-4 border-b border-gray-800 pb-2">Wealth & Assets Analytics</h2>
            <div className="space-y-4">
              {gameState.players.map(player => (
                <div key={player.id} className={`p-4 rounded-lg border bg-gray-800/40 ${player.is_bankrupt ? 'border-red-900 opacity-40' : getTheme(player.id).border}`}>
                  
                  <div className="flex justify-between items-center mb-1">
                    <h3 className={`font-bold text-lg ${getAgentTheme(player.id).text}`}>{player.name}</h3>
                    <span className="text-xl font-mono text-green-400">${player.balance} <span className="text-xs text-gray-500 font-sans">Cash</span></span>
                  </div>
                  
                  <div className="mb-1">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>Net Worth</span>
                      <span>${player.net_worth}</span>
                    </div>
                    <div className="w-full bg-gray-950 rounded-full h-2 border border-gray-800 overflow-hidden">
                      <div 
                        className={`h-2 rounded-full transition-all duration-500 ${player.id === 0 ? 'bg-emerald-500' : 'bg-rose-500'}`} 
                        style={{ width: `${(player.net_worth / totalWealth) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="text-sm text-gray-400 flex justify-between border-t border-gray-800 pt-2 mt-2">
                    <span>Pos: Space {player.position}</span>
                    {player.is_in_jail && <span className="text-red-400 font-bold">IN JAIL</span>}
                    {player.is_bankrupt && <span className="text-red-500 font-bold">BANKRUPT 💀</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex-1 flex flex-col" style={{ maxHeight: "400px" }}>
            <h2 className="text-xl font-bold mb-4 border-b border-gray-800 pb-2">Microscope (Live Actions)</h2>
            <div className="flex-1 bg-black rounded-lg p-3 overflow-y-auto font-mono text-xs text-gray-300 space-y-2">
              {gameState.recent_logs.length === 0 ? (
                <span className="text-gray-600">Waiting for engine execution execution...</span>
              ) : (
                gameState.recent_logs.map((log, index) => {
                  let colorClass = "text-gray-300";
                  if (log.includes('[AI THOUGHT]')) colorClass = "text-purple-400";
                  if (log.includes('BUYS') || log.includes('unmortgages') || log.includes('WINS')) colorClass = "text-green-400";
                  if (log.includes('mortgages') || log.includes('BANKRUPTCY') || log.includes('Jail')) colorClass = "text-red-400";
                  if (log.includes('built')) colorClass = "text-blue-400";
                  if (log.includes('AUCTION')) colorClass = "text-amber-400 font-semibold";
                  
                  return (
                    <div key={index} className={colorClass}>
                      {log}
                    </div>
                  );
                })
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

// Global fallback helper inside compiling range
function getTheme(id: number) {
  return id === 0 ? { border: "border-emerald-900/50" } : { border: "border-rose-900/50" };
}