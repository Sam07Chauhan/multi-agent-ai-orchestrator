import React from "react";
import { Sparkles } from "lucide-react";

export function ChatEmptyState({ onSelectPreset }) {
  return (
    <div className="h-full min-h-[420px] flex flex-col items-center justify-center text-center p-6 gap-4 text-slate-500">
      <div className="w-14 h-14 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-center text-indigo-400 shadow-xl shadow-indigo-500/5">
        <Sparkles className="w-7 h-7 animate-pulse" />
      </div>
      <div className="max-w-md">
        <h3 className="text-sm font-semibold text-slate-300">Ready to Orchestrate</h3>
        <p className="text-xs text-slate-500 mt-1 leading-relaxed">
          Start a conversation by typing a prompt, uploading an image for inpainting / face analysis, or querying your MySQL database.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 w-full max-w-lg mt-2">
        <button
          type="button"
          onClick={() => onSelectPreset("image", "Transform outfit into a luxury navy blue Italian wool suit")}
          className="p-3 bg-slate-900/50 hover:bg-slate-900 border border-slate-850 rounded-xl text-left transition-all"
        >
          <p className="text-[11px] font-semibold text-indigo-400">AI Canvas</p>
          <p className="text-[10px] text-slate-400 mt-0.5 truncate">"Transform outfit into luxury suit..."</p>
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("image_analysis", "Analyze the facial structure, eye distance and proportions")}
          className="p-3 bg-slate-900/50 hover:bg-slate-900 border border-slate-850 rounded-xl text-left transition-all"
        >
          <p className="text-[11px] font-semibold text-indigo-400">Analyze</p>
          <p className="text-[10px] text-slate-400 mt-0.5 truncate">"Analyze face & body proportions..."</p>
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("data", "Find all users created in the last 30 days with orders > 5")}
          className="p-3 bg-slate-900/50 hover:bg-slate-900 border border-slate-850 rounded-xl text-left transition-all"
        >
          <p className="text-[11px] font-semibold text-indigo-400">DB Engine</p>
          <p className="text-[10px] text-slate-400 mt-0.5 truncate">"Find all users created..."</p>
        </button>
      </div>
    </div>
  );
}
