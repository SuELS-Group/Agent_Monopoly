"use client";

import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const PLAYER_COLORS = ['#34D399', '#FB7185', '#60A5FA', '#FBBF24', '#A78BFA', '#F472B6'];
const LIQUID_COLORS = ['#059669', '#E11D48', '#2563EB', '#D97706', '#7C3AED', '#DB2777'];

export default function AnalyticsDashboard() {
  const [logData, setLogData] = useState<any[] | null>(null);
  const [rawFile, setRawFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiReport, setAiReport] = useState<string | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setRawFile(file);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string);
        setLogData(json);
        setAiReport(null); // Reset report on new file
      } catch (error) {
        console.error("Invalid JSON file", error);
        alert("Failed to parse JSON. Please upload a valid game log.");
      }
    };
    reader.readAsText(file);
  };

  const handleAnalyzeGame = async () => {
    if (!rawFile) return;
    setIsAnalyzing(true);
    
    const formData = new FormData();
    formData.append("file", rawFile);

    try {
      const response = await fetch("http://localhost:8000/api/analyze-game", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.report) {
        setAiReport(data.report);
      } else {
        alert("Error during AI analysis: " + data.error);
      }
    } catch (error) {
      console.error("Analysis failed", error);
      alert("Failed to connect to the backend analysis engine.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const processChartData = () => {
    if (!logData || logData.length === 0) return [];
    
    return logData.map((state) => {
      const turnPoint: any = { turn: state.turn };
      state.players.forEach((p: any) => {
        turnPoint[`${p.name}_NetWorth`] = p.net_worth;
        turnPoint[`${p.name}_Liquid`] = p.balance;
      });
      return turnPoint;
    });
  };

  const chartData = processChartData();
  const finalState = logData ? logData[logData.length - 1] : null;
  const totalTurns = logData ? logData.length : 0;
  
  const playerNames = finalState ? finalState.players.map((p: any) => p.name) : [];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 font-sans">
      <header className="mb-8 border-b border-gray-800 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-amber-400">MAS Post-Match Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Upload a simulation log to analyze emergent AI behaviors.</p>
        </div>
        
        <div className="flex gap-4 items-center">
          <div className="bg-gray-900 border border-gray-700 p-2 rounded-lg">
            <input 
              type="file" 
              accept=".json" 
              onChange={handleFileUpload}
              className="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
            />
          </div>
          {logData && (
            <button 
              onClick={handleAnalyzeGame}
              disabled={isAnalyzing}
              className={`py-3 px-6 rounded-lg font-bold text-sm shadow-lg transition-all ${
                isAnalyzing 
                ? "bg-gray-700 text-gray-400 cursor-not-allowed" 
                : "bg-fuchsia-600 hover:bg-fuchsia-500 text-white border border-fuchsia-400"
              }`}
            >
              {isAnalyzing ? "Analysis in progress (LLM)..." : " Request behavioral analysis (AI)"}
            </button>
          )}
        </div>
      </header>

      {!logData ? (
        <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-gray-800 rounded-xl text-gray-600">
          <p className="text-lg">No data loaded.</p>
          <p className="text-sm">Please select a game_session_XXXX.json file from your logs folder.</p>
        </div>
      ) : (
        <div className="space-y-6">
          
          {/* OVERALL STATISTICS */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col justify-center">
              <h3 className="text-gray-500 text-sm uppercase tracking-wider">Total Turns</h3>
              <p className="text-4xl font-black text-white mt-1">{totalTurns}</p>
            </div>
            
            {finalState?.players.map((p: any, index: number) => (
              <div key={p.id} className={`bg-gray-900 border-l-4 ${p.is_bankrupt ? 'border-red-900 opacity-50' : 'border-gray-800'} p-4 rounded-xl shadow-md`} style={{ borderLeftColor: p.is_bankrupt ? '#7f1d1d' : PLAYER_COLORS[index % PLAYER_COLORS.length] }}>
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-bold text-gray-200">Agent {p.name}</h3>
                  {p.is_bankrupt && <span className="text-red-500 text-xs font-bold border border-red-500 px-2 py-1 rounded bg-red-950/30">BANKRUPT 💀</span>}
                </div>
                <div className="mt-3">
                  <p className="text-2xl font-bold text-white">${p.net_worth.toLocaleString()} <span className="text-xs text-gray-500 font-normal">Net Worth</span></p>
                  <p className="text-sm text-gray-400 mt-1">${p.balance.toLocaleString()} Liquid Cash</p>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* COMPARISON CHART (Dynamic) */}
            <div className="lg:col-span-2 bg-gray-900 border border-gray-800 p-4 rounded-xl" style={{ height: "600px" }}>
              <h2 className="text-xl font-bold mb-4 text-gray-200">Wealth Trajectory Comparison</h2>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="turn" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#F3F4F6', borderRadius: '8px' }}
                    itemStyle={{ fontWeight: 'bold' }}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  
                  {/* Dynamic generation of lines based on the number of players */}
                  {playerNames.map((name: string, index: number) => (
                    <Line 
                      key={`net_${name}`} 
                      type="monotone" 
                      dataKey={`${name}_NetWorth`} 
                      name={`Agent ${name} (Net Worth)`} 
                      stroke={PLAYER_COLORS[index % PLAYER_COLORS.length]} 
                      strokeWidth={3} 
                      dot={false} 
                    />
                  ))}
                  {playerNames.map((name: string, index: number) => (
                    <Line 
                      key={`liq_${name}`} 
                      type="monotone" 
                      dataKey={`${name}_Liquid`} 
                      name={`Agent ${name} (Cash)`} 
                      stroke={LIQUID_COLORS[index % LIQUID_COLORS.length]} 
                      strokeWidth={1} 
                      strokeDasharray="4 4" 
                      dot={false} 
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* AI BEHAVIORAL REPORT */}
            <div className="bg-gray-900 border border-fuchsia-900/50 p-6 rounded-xl flex flex-col h-[600px]">
              <h2 className="text-xl font-bold mb-4 text-fuchsia-400 flex items-center gap-2">
                <span>🧠</span> AI Behavioral Report
              </h2>
              <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar text-sm text-gray-300 leading-relaxed bg-gray-950 p-4 rounded-lg border border-gray-800">
                {isAnalyzing ? (
                  <div className="flex flex-col items-center justify-center h-full space-y-4 animate-pulse">
                    <div className="w-8 h-8 border-4 border-fuchsia-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-fuchsia-400 font-medium">Llama-3.1-70B is analyzing agent strategies...</p>
                    <p className="text-xs text-gray-500 text-center">Processing 38k+ lines of Chain of Thought and Trading interactions.</p>
                  </div>
                ) : aiReport ? (
                  <div dangerouslySetInnerHTML={{ __html: aiReport }} />
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-gray-600 text-center">
                    <p>No analysis generated yet.</p>
                    <p className="text-xs mt-2">Click the button above to trigger the NLP evaluation via the workstation LLM.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}