"use client";

import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface PlayerData {
  id: number;
  name: string;
  balance: number;
  net_worth: number;
  is_bankrupt: boolean;
}

interface TurnData {
  turn: number;
  players: PlayerData[];
  board: any[];
  recent_logs: string[];
}

export default function AnalyticsDashboard() {
  const [logData, setLogData] = useState<TurnData[] | null>(null);

  // Gère l'upload du fichier JSON généré par Python
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string);
        setLogData(json);
      } catch (error) {
        console.error("Invalid JSON file", error);
        alert("Failed to parse JSON. Please upload a valid game log.");
      }
    };
    reader.readAsText(file);
  };

  // Formate les données brutes pour le graphique Recharts
  const processChartData = () => {
    if (!logData) return [];
    return logData.map((state) => {
      const alpha = state.players.find((p) => p.id === 0);
      const beta = state.players.find((p) => p.id === 1);
      return {
        turn: state.turn,
        Alpha_NetWorth: alpha?.net_worth || 0,
        Beta_NetWorth: beta?.net_worth || 0,
        Alpha_Liquid: alpha?.balance || 0,
        Beta_Liquid: beta?.balance || 0,
      };
    });
  };

  const chartData = processChartData();

  // Statistiques de fin de partie
  const finalState = logData ? logData[logData.length - 1] : null;
  const totalTurns = logData ? logData.length : 0;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 font-sans">
      <header className="mb-8 border-b border-gray-800 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-amber-400">MAS Post-Match Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Upload a simulation JSON log to analyze AI strategies.</p>
        </div>
        
        <div className="bg-gray-900 border border-gray-700 p-2 rounded-lg">
          <input 
            type="file" 
            accept=".json" 
            onChange={handleFileUpload}
            className="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
          />
        </div>
      </header>

      {!logData ? (
        <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-gray-800 rounded-xl text-gray-600">
          <p className="text-lg">No data loaded.</p>
          <p className="text-sm">Please select a game_session_XXXX.json file from your logs folder.</p>
        </div>
      ) : (
        <div className="space-y-6">
          
          {/* STATISTIQUES GLOBALES */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl">
              <h3 className="text-gray-500 text-sm">Total Turns</h3>
              <p className="text-2xl font-bold text-white">{totalTurns}</p>
            </div>
            
            {finalState?.players.map((p) => (
              <div key={p.id} className={`bg-gray-900 border ${p.is_bankrupt ? 'border-red-900 opacity-50' : 'border-gray-800'} p-4 rounded-xl`}>
                <div className="flex justify-between">
                  <h3 className={`text-sm font-bold ${p.id === 0 ? 'text-emerald-400' : 'text-rose-400'}`}>{p.name}</h3>
                  {p.is_bankrupt && <span className="text-red-500 text-xs font-bold border border-red-500 px-2 rounded">BANKRUPT</span>}
                </div>
                <div className="mt-2">
                  <p className="text-2xl font-bold text-white">${p.net_worth} <span className="text-xs text-gray-500 font-normal">Final Net Worth</span></p>
                  <p className="text-sm text-gray-400">${p.balance} Liquid</p>
                </div>
              </div>
            ))}
          </div>

          {/* GRAPHIQUE DE COMPARAISON */}
          <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl" style={{ height: "500px" }}>
            <h2 className="text-xl font-bold mb-4">Wealth Trajectory Comparison</h2>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="turn" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#F3F4F6' }}
                  itemStyle={{ fontWeight: 'bold' }}
                />
                <Legend />
                
                {/* Lignes de Valeur Nette (Plus épaisses) */}
                <Line type="monotone" dataKey="Alpha_NetWorth" name="Alpha Net Worth" stroke="#34D399" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="Beta_NetWorth" name="Beta Net Worth" stroke="#FB7185" strokeWidth={3} dot={false} />
                
                {/* Lignes de Liquidité (Plus fines et pointillées) */}
                <Line type="monotone" dataKey="Alpha_Liquid" name="Alpha Cash" stroke="#059669" strokeWidth={1} strokeDasharray="5 5" dot={false} />
                <Line type="monotone" dataKey="Beta_Liquid" name="Beta Cash" stroke="#E11D48" strokeWidth={1} strokeDasharray="5 5" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

        </div>
      )}
    </div>
  );
}