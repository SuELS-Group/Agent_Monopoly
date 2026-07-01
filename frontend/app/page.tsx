"use client";

import { useEffect, useState, useRef } from "react";

// --- INTERFACES ---
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
  color: string | null;
  price: number;
  house_cost: number;
  space_type: string;
}

interface GameState {
  turn: number;
  players: Player[];
  board: Space[];
  recent_logs: string[];
}

interface AgentConfig {
  id: number;
  name: string;
  model: string;
  persona: string;
}

// --- CONFIGURATION CONSTANTS ---
const AVAILABLE_MODELS = [
  "llama3:latest",
  "mistral:latest",
  "deepseek-r1:32b",
  "llama3.1:70b",
  "mixtral:8x7b",
  "qwen3:32b",
  "gemma3:27b",
  "nemotron-3-nano:30b"
];

// NOUVEAU: Les Archétypes Socio-Économiques
const AVAILABLE_PERSONAS = [
  { value: "Neutral AI", label: "🤖 Neutral AI (Logical)" },
  { value: "The Wall Street Shark: Aggressive, purely capitalist, speaks arrogantly, never gives gifts, highly focused on monopolies.", label: "🦈 The Wall Street Shark" },
  { value: "The Cooperative Diplomat: Seeks harmony, proposes alliances, uses polite and diplomatic language.", label: "🕊️ The Cooperative Diplomat" },
  { value: "The Underground Hustler: Street-smart, seeks to bypass rules, proposes secret deals and collusions, uses slang.", label: "🕶️ The Underground Hustler" },
  { value: "The Old-Money Aristocrat: Rich heir, despises small transactions, only allies with 'worthy' opponents, highly formal language.", label: "🎩 The Old-Money Aristocrat" }
];

const AGENT_COLORS = [
  { bg: "bg-emerald-500", text: "text-emerald-400", border: "border-emerald-500", shadow: "shadow-[0_0_10px_rgba(16,185,129,0.8)]" },
  { bg: "bg-rose-500", text: "text-rose-400", border: "border-rose-500", shadow: "shadow-[0_0_10px_rgba(244,63,94,0.8)]" },
  { bg: "bg-amber-500", text: "text-amber-400", border: "border-amber-500", shadow: "shadow-[0_0_10px_rgba(245,158,11,0.8)]" },
  { bg: "bg-sky-500", text: "text-sky-400", border: "border-sky-500", shadow: "shadow-[0_0_10px_rgba(14,165,233,0.8)]" },
  { bg: "bg-purple-500", text: "text-purple-400", border: "border-purple-500", shadow: "shadow-[0_0_10px_rgba(168,85,247,0.8)]" },
  { bg: "bg-orange-500", text: "text-orange-400", border: "border-orange-500", shadow: "shadow-[0_0_10px_rgba(249,115,22,0.8)]" }
];

const MONOPOLY_COLORS: Record<string, string> = {
  Brown: "bg-[#8b4513]",
  LightBlue: "bg-[#87ceeb]",
  Pink: "bg-[#ff69b4]",
  Orange: "bg-[#ff8c00]",
  Red: "bg-[#ff0000]",
  Yellow: "bg-[#ffd700]",
  Green: "bg-[#008000]",
  DarkBlue: "bg-[#00008b]",
};

export default function Dashboard() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isAutoPlay, setIsAutoPlay] = useState(false);
  
  const [isConfiguring, setIsConfiguring] = useState(true);
  const [activeTab, setActiveTab] = useState<"BOARD" | "LOGS">("BOARD");
  
  // Modification de l'état initial pour inclure le persona
  const [agentsConfig, setAgentsConfig] = useState<AgentConfig[]>([
    { id: 0, name: "Agent_Alpha", model: "llama3:latest", persona: AVAILABLE_PERSONAS[0].value },
    { id: 1, name: "Agent_Beta", model: "mistral:latest", persona: AVAILABLE_PERSONAS[0].value }
  ]);

  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/simulation");
    
    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => {
      setIsConnected(false);
      setIsAutoPlay(false);
    };
    socket.onmessage = (event) => {
      setGameState(JSON.parse(event.data));
      setIsConfiguring(false);
    };

    wsRef.current = socket;
    return () => socket.close();
  }, []);

  useEffect(() => {
    if (activeTab === "LOGS" && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [gameState?.recent_logs, activeTab]);

  const startGame = () => {
    if (wsRef.current && isConnected) {
      // Le persona est maintenant envoyé au backend lors du lancement
      wsRef.current.send(JSON.stringify({ action: "INIT", players: agentsConfig }));
    }
  };

  const nextTurn = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send("NEXT_TURN");
    }
  };

  useEffect(() => {
    let playTimer: NodeJS.Timeout | null = null;
    
    const activePlayers = gameState?.players.filter(p => !p.is_bankrupt) || [];
    const isGameOver = activePlayers.length <= 1;
    
    if (isAutoPlay && isConnected && !isConfiguring && gameState && !isGameOver) {
      playTimer = setTimeout(() => {
        nextTurn();
      }, 1000); 
    }
    
    if (isGameOver && isAutoPlay) {
        setIsAutoPlay(false);
    }
    
    return () => {
      if (playTimer) clearTimeout(playTimer);
    };
  }, [isAutoPlay, isConnected, isConfiguring, gameState]);

  const colorGroupTotals: Record<string, number> = {};
  if (gameState) {
    gameState.board.forEach(space => {
      if (space.color) {
        colorGroupTotals[space.color] = (colorGroupTotals[space.color] || 0) + 1;
      }
    });
  }

  if (isConfiguring) {
    return (
      <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-6 text-gray-100 font-sans">
        <div className="w-full max-w-5xl bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl p-8">
          <div className="text-center mb-8 border-b border-gray-800 pb-6">
            <h1 className="text-4xl font-bold text-blue-400 mb-2">🤖 MAS AI Arena</h1>
            <p className="text-gray-400">Configure your autonomous LLM agents before launching the simulation.</p>
            <p className="text-sm mt-2">
              Connection: <span className={isConnected ? "text-green-500" : "text-red-500 font-bold"}>
                {isConnected ? "🟢 Ready" : "🔴 Disconnected. Start Python Backend."}
              </span>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {agentsConfig.map((agent, index) => (
              <div key={agent.id} className={`p-4 rounded-xl border border-gray-700 bg-gray-950/50 flex flex-col gap-3 relative overflow-hidden`}>
                <div className={`absolute top-0 left-0 w-2 h-full ${AGENT_COLORS[index].bg}`}></div>
                <div className="flex justify-between items-center pl-3">
                  <h3 className={`font-bold ${AGENT_COLORS[index].text}`}>Player {index + 1}</h3>
                  {agentsConfig.length > 2 && (
                    <button onClick={() => setAgentsConfig(agentsConfig.filter(a => a.id !== agent.id))} className="text-gray-500 hover:text-red-400 text-sm">❌ Remove</button>
                  )}
                </div>
                <div className="pl-3 space-y-3">
                  <div>
                    <label className="text-xs text-gray-500 uppercase font-bold block mb-1">Agent Name</label>
                    <input type="text" value={agent.name} onChange={(e) => { const newConfig = [...agentsConfig]; newConfig[index].name = e.target.value; setAgentsConfig(newConfig); }} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm text-white focus:border-blue-500 focus:outline-none"/>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs text-gray-500 uppercase font-bold block mb-1">LLM Model</label>
                      <select value={agent.model} onChange={(e) => { const newConfig = [...agentsConfig]; newConfig[index].model = e.target.value; setAgentsConfig(newConfig); }} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm text-white focus:border-blue-500 focus:outline-none">
                        {AVAILABLE_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
                      </select>
                    </div>
                    {/* NOUVEAU MENU DÉROULANT POUR LE PERSONA */}
                    <div>
                      <label className="text-xs text-fuchsia-500 uppercase font-bold block mb-1">Behavioral Persona</label>
                      <select value={agent.persona} onChange={(e) => { const newConfig = [...agentsConfig]; newConfig[index].persona = e.target.value; setAgentsConfig(newConfig); }} className="w-full bg-gray-900 border border-fuchsia-900/50 rounded p-2 text-sm text-fuchsia-100 focus:border-fuchsia-500 focus:outline-none">
                        {AVAILABLE_PERSONAS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center">
            <button onClick={() => { if (agentsConfig.length < 6) setAgentsConfig([...agentsConfig, { id: Date.now(), name: `Agent_00${agentsConfig.length + 1}`, model: "llama3:latest", persona: AVAILABLE_PERSONAS[0].value }]); }} disabled={agentsConfig.length >= 6} className="px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-white rounded-lg transition-colors border border-gray-700">➕ Add Agent (Max 6)</button>
            <button onClick={startGame} disabled={!isConnected} className="px-8 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white font-bold rounded-lg transition-colors shadow-[0_0_15px_rgba(37,99,235,0.5)]">🚀 Launch Simulation</button>
          </div>
        </div>
      </div>
    );
  }

  if (!gameState) return null;
  const totalWealth = Math.max(1, ...gameState.players.map(p => p.net_worth));

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 flex flex-col font-sans">
      
      {/* HEADER AMELIORE */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-800 pb-4 mb-4 gap-4">
        <div className="flex items-center gap-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-blue-400">MAS Simulation</h1>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${isConnected ? 'bg-green-900/50 text-green-400 border border-green-800' : 'bg-red-900/50 text-red-400 border border-red-800'}`}>
                {isConnected ? '🟢 Live' : '🔴 Offline'}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-1">Turn: {gameState.turn}</p>
          </div>
          
          <div className="flex bg-gray-900 p-1 rounded-lg border border-gray-800 ml-4">
            <button onClick={() => setActiveTab("BOARD")} className={`px-6 py-2 rounded-md font-bold text-sm transition-all ${activeTab === "BOARD" ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-400 hover:text-gray-200'}`}>🎲 Board & Wealth</button>
            <button onClick={() => setActiveTab("LOGS")} className={`px-6 py-2 rounded-md font-bold text-sm transition-all flex gap-2 items-center ${activeTab === "LOGS" ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-400 hover:text-gray-200'}`}><span>🔬</span> Microscope Logs</button>
          </div>
        </div>
        
        {/* CONTROLES EPURES */}
        <div className="flex flex-wrap items-center gap-3">
          <button 
            onClick={() => setIsAutoPlay(!isAutoPlay)} 
            disabled={!isConnected} 
            className={`px-6 py-2.5 rounded-lg font-bold transition-all shadow-lg whitespace-nowrap ${isAutoPlay ? 'bg-amber-600 hover:bg-amber-500 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-white'}`}
          >
            {isAutoPlay ? "⏸️ Pause Auto" : "▶️ Auto-Play"}
          </button>
          
          <button 
            onClick={nextTurn} 
            disabled={!isConnected || isAutoPlay} 
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded-lg font-bold transition-all shadow-lg active:scale-95"
          >
            👉 Step Turn
          </button>
        </div>
      </header>

      {/* --- VUE 1 : PLATEAU --- */}
      {activeTab === "BOARD" && (
        <div className="flex flex-col flex-1">
          {/* LÉGENDE UI */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-3 mb-4 flex flex-wrap gap-6 text-xs text-gray-400 items-center shadow-md">
            <span className="font-bold text-gray-300 uppercase tracking-wider">Legend:</span>
            <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-green-500 rounded-sm shadow-[0_0_5px_green]"></span> House</div>
            <div className="flex items-center gap-1.5"><span className="w-3 h-3 bg-red-600 rounded-sm shadow-[0_0_5px_red]"></span> Hotel</div>
            <div className="flex items-center gap-1.5"><span className="text-red-400 line-through font-bold">Property</span> / <span className="border border-red-900 bg-red-950/30 px-1 rounded text-[10px]">Red Background</span> = Mortgaged (No Rent)</div>
            <div className="flex items-center gap-1.5"><span className="text-yellow-400 font-bold">3/3</span> = Full Monopoly</div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 flex-1">
            <div className="xl:col-span-3 bg-gray-900 border border-gray-800 rounded-xl p-4 overflow-y-auto" style={{ maxHeight: "calc(100vh - 200px)" }}>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 xl:grid-cols-8 gap-3">
                {gameState.board.map((space) => {
                  const playersHere = gameState.players.filter(p => p.position === space.id);
                  const owner = gameState.players.find(p => p.id === space.owner_id);
                  const isMortgaged = space.is_mortgaged;
                  
                  let monopolyText = "";
                  let isFullMonopoly = false;
                  if (space.color && owner) {
                    const ownedInGroup = gameState.board.filter(s => s.color === space.color && s.owner_id === owner.id).length;
                    const totalInGroup = colorGroupTotals[space.color];
                    isFullMonopoly = ownedInGroup === totalInGroup;
                    monopolyText = `${ownedInGroup}/${totalInGroup}`;
                  }

                  return (
                    <div key={space.id} className={`rounded-xl text-sm border overflow-hidden flex flex-col justify-between h-36 transition-all duration-300 relative bg-gray-950 ${isMortgaged ? 'border-red-900 bg-red-950/30' : 'border-gray-800'}`}>
                      {space.color && (
                        <div className={`h-5 w-full flex items-center justify-center text-[10px] font-bold text-white/90 shadow-sm ${MONOPOLY_COLORS[space.color]} ${isMortgaged ? 'grayscale opacity-30' : ''}`}>
                          {space.color.toUpperCase()}
                        </div>
                      )}
                      {!space.color && (
                        <div className="h-5 w-full bg-gray-800 flex items-center justify-center text-[10px] font-bold text-gray-400">
                          {space.space_type.toUpperCase()}
                        </div>
                      )}

                      {isMortgaged && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
                          <span className="bg-red-900/90 text-red-100 text-xs font-bold px-2 py-1 rounded shadow-lg transform -rotate-12 border border-red-500">
                            🔒 MORTGAGED
                          </span>
                        </div>
                      )}

                      <div className={`p-2 flex flex-col h-full relative ${isMortgaged ? 'opacity-40' : ''}`}>
                        <div className="text-[10px] text-gray-500 mb-0.5">#{space.id}</div>
                        <div className={`font-bold leading-tight text-xs ${isMortgaged ? 'line-through text-red-400' : 'text-gray-200'}`} title={space.name}>
                          {space.name}
                        </div>

                        {space.price > 0 && (
                          <div className="mt-1 flex flex-col gap-0.5">
                            <span className="text-[11px] font-mono text-green-400">${space.price}</span>
                            {space.house_cost > 0 && <span className="text-[10px] text-gray-400">🏠 ${space.house_cost}</span>}
                          </div>
                        )}

                        <div className="mt-auto pt-2">
                          {owner && (
                            <div className={`flex justify-between items-center text-[10px] font-bold px-1.5 py-0.5 rounded bg-gray-900 border ${AGENT_COLORS[owner.id % AGENT_COLORS.length].border} ${AGENT_COLORS[owner.id % AGENT_COLORS.length].text}`}>
                              <span className="truncate">{owner.name.split('_')[1] || owner.name}</span>
                              {monopolyText && <span className={isFullMonopoly ? "text-yellow-400" : ""}>{monopolyText}</span>}
                            </div>
                          )}

                          {space.buildings > 0 && !isMortgaged && (
                            <div className="flex gap-1 mt-1 justify-center">
                              {space.buildings === 5 ? (
                                <div className="w-3 h-3 bg-red-600 rounded-sm shadow-[0_0_5px_red]" title="Hotel"></div>
                              ) : (
                                Array.from({ length: space.buildings }).map((_, i) => (
                                  <div key={i} className="w-2.5 h-2.5 bg-green-500 rounded-sm shadow-[0_0_5px_green]" title="House"></div>
                                ))
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-wrap justify-end gap-1 absolute top-1 right-1 max-w-[50%] z-20">
                        {playersHere.map(p => (
                          <span key={p.id} className={`inline-block w-3.5 h-3.5 rounded-full border-2 border-gray-950 ${AGENT_COLORS[p.id % AGENT_COLORS.length].bg} ${AGENT_COLORS[p.id % AGENT_COLORS.length].shadow}`} title={p.name}></span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="xl:col-span-1 bg-gray-900 border border-gray-800 rounded-xl p-4 overflow-y-auto" style={{ maxHeight: "calc(100vh - 200px)" }}>
              <h2 className="text-xl font-bold mb-4 border-b border-gray-800 pb-2 text-white">Wealth Analytics</h2>
              <div className="space-y-4">
                {gameState.players.map(player => {
                  const colors = AGENT_COLORS[player.id % AGENT_COLORS.length];
                  return (
                    <div key={player.id} className={`p-4 rounded-xl border bg-gray-950 shadow-md ${player.is_bankrupt ? 'border-red-900 opacity-40' : colors.border}`}>
                      <div className="flex justify-between items-center mb-2">
                        <h3 className={`font-bold text-lg ${colors.text}`}>{player.name}</h3>
                        <span className="text-2xl font-mono text-green-400 font-bold">${player.balance}</span>
                      </div>
                      <div className="mb-3">
                        <div className="flex justify-between text-xs text-gray-400 mb-1 font-semibold">
                          <span>Net Worth</span><span>${player.net_worth}</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2.5 border border-gray-700 overflow-hidden">
                          <div className={`h-full rounded-full transition-all duration-500 ${colors.bg} ${colors.shadow}`} style={{ width: `${(player.net_worth / totalWealth) * 100}%` }}></div>
                        </div>
                      </div>
                      <div className="text-xs font-semibold text-gray-400 flex justify-between border-t border-gray-800 pt-2 mt-2">
                        <span className="bg-gray-800 px-2 py-1 rounded">Pos: {player.position}</span>
                        {player.is_in_jail && <span className="bg-orange-900/50 text-orange-400 px-2 py-1 rounded border border-orange-800">IN JAIL</span>}
                        {player.is_bankrupt && <span className="bg-red-900/50 text-red-500 px-2 py-1 rounded border border-red-800">BANKRUPT 💀</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --- VUE 2 : MICROSCOPE --- */}
      {activeTab === "LOGS" && (
        <div className="flex-1 bg-gray-900 border border-gray-800 rounded-xl p-6 overflow-y-auto" style={{ maxHeight: "calc(100vh - 150px)" }}>
          <h2 className="text-2xl font-bold mb-6 border-b border-gray-800 pb-3 flex items-center gap-3">
            <span>🔬</span> AI Strategies & Event Logs
          </h2>
          <div className="max-w-5xl mx-auto space-y-4 font-mono text-sm">
            {gameState.recent_logs.map((log, index) => {
              if (log.includes('[AI THOUGHT]')) {
                const parts = log.split('[AI THOUGHT] :');
                const agentString = parts[0].replace(/\[LOG\]\[Turn \d+\]\s*/, '').trim();
                const thought = parts[1]?.trim();
                const player = gameState.players.find(p => p.name === agentString);
                const colorClass = player ? AGENT_COLORS[player.id % AGENT_COLORS.length].text : "text-purple-400";
                const borderClass = player ? AGENT_COLORS[player.id % AGENT_COLORS.length].border : "border-purple-800";
                
                return (
                  <div key={index} className={`bg-gray-950 border ${borderClass} rounded-xl p-5 my-6 shadow-xl relative overflow-hidden`}>
                    <div className="absolute top-0 left-0 w-1.5 h-full bg-current opacity-50" style={{color: "inherit"}}></div>
                    <div className={`font-bold ${colorClass} mb-3 flex items-center gap-2 text-base`}>
                      <span>🧠</span> {agentString} Strategy Analysis
                    </div>
                    <div className="text-gray-300 leading-relaxed italic text-sm md:text-base px-2">"{thought}"</div>
                  </div>
                );
              }
              
              let colorClass = "text-gray-400";
              if (log.includes('BUYS') || log.includes('unmortgages') || log.includes('WINS')) colorClass = "text-emerald-400 font-bold bg-emerald-950/30 inline-block px-2 py-1 rounded";
              if (log.includes('mortgages') || log.includes('BANKRUPTCY') || log.includes('Jail')) colorClass = "text-rose-400 font-bold bg-rose-950/30 inline-block px-2 py-1 rounded";
              if (log.includes('built')) colorClass = "text-sky-400 font-bold bg-sky-950/30 inline-block px-2 py-1 rounded";
              if (log.includes('bids $')) colorClass = "text-amber-300 font-bold bg-amber-950/30 inline-block px-2 py-1 rounded border border-amber-900";
              if (log.includes('AUCTION')) colorClass = "text-amber-400 font-bold";
              if (log.includes('TRADE') || log.includes('PROPOSES') || log.includes('ACCEPTS') || log.includes('REJECTS')) {
                  colorClass = "text-fuchsia-400 font-bold bg-fuchsia-950/30 inline-block px-2 py-1 rounded border border-fuchsia-900";
              }
              // NOUVEAU STYLE POUR LE CHAT (MESSAGERIE PUBLIQUE)
              if (log.includes('[CHAT]')) {
                  colorClass = "text-cyan-400 font-bold bg-cyan-950/30 inline-block px-3 py-2 rounded-lg border border-cyan-800 w-full";
              }
              // NOUVEAU STYLE POUR LA COLLUSION
              if (log.includes('COLLUSION')) {
                  colorClass = "text-yellow-400 font-bold bg-yellow-950/30 inline-block px-2 py-1 rounded border border-yellow-600";
              }
              
              return (
                <div key={index} className="pb-3 border-b border-gray-800/50 flex items-start gap-4">
                  {!log.includes('[CHAT]') && <span className="text-gray-600 shrink-0 mt-1">▶</span>}
                  <span className={`${colorClass} leading-relaxed block`}>{log.replace('[CHAT] ', '')}</span>
                </div>
              );
            })}
            <div ref={logsEndRef} />
          </div>
        </div>
      )}
    </div>
  );
}