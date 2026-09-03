import React from "react";
import { Cpu, Trash2 } from "lucide-react";

export function Header({ hasMessages, onClearChat }) {
  return (
    <header className="border-b border-slate-900 bg-slate-900/60 backdrop-blur-md px-6 py-3.5 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-tr from-indigo-600 to-violet-500 p-2 rounded-xl text-white shadow-lg shadow-indigo-500/20">
          <Cpu className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <h1 className="font-bold text-base tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            M4 AI Nexus Orchestrator
          </h1>
          <p className="text-[11px] text-indigo-400 font-medium">Local Multi-Agent Hybrid Stack</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {hasMessages && (
          <button
            type="button"
            onClick={onClearChat}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-rose-400 bg-slate-900 hover:bg-slate-850 px-3 py-1.5 rounded-lg border border-slate-800 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" /> Clear Chat
          </button>
        )}
        <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800 text-xs text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          FastAPI: 8000 &middot; .NET: 5137
        </div>
      </div>
    </header>
  );
}
