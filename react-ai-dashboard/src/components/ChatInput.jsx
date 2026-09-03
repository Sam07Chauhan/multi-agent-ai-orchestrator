import React, { useRef } from "react";
import { Sparkles, Database, Image as ImageIcon, ScanSearch, Send, Loader2 } from "lucide-react";

export function ChatInput({
  prompt,
  setPrompt,
  mode,
  setMode,
  selectedFile,
  previewUrl,
  onFileChange,
  onClearFile,
  onSubmit,
  loading,
}) {
  const fileInputRef = useRef(null);

  const modeOptions = [
    { id: "auto", label: "Auto Agent", icon: Sparkles },
    { id: "image", label: "AI Canvas", icon: ImageIcon },
    { id: "image_analysis", label: "Analyze", icon: ScanSearch },
    { id: "data", label: "DB Engine", icon: Database },
  ];

  return (
    <div className="bg-slate-900/80 border border-slate-850 rounded-2xl p-3 backdrop-blur-md shadow-2xl">
      {/* Mode Selector Tabs */}
      <div className="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-850">
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {modeOptions.map((tab) => {
            const Icon = tab.icon;
            const active = mode === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setMode(tab.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                  active
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Attached Image Badge Preview */}
        {previewUrl && (
          <div className="flex items-center gap-2 bg-slate-950 px-2 py-1 rounded-lg border border-slate-800">
            <img src={previewUrl} alt="Attached" className="w-5 h-5 rounded object-cover" />
            <span className="text-[10px] text-slate-400 truncate max-w-[100px]">Attached</span>
            <button
              type="button"
              onClick={onClearFile}
              className="text-rose-400 hover:text-rose-300 text-xs font-bold px-1"
            >
              &times;
            </button>
          </div>
        )}
      </div>

      {/* Form */}
      <form onSubmit={onSubmit} className="flex items-end gap-2">
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          onChange={onFileChange}
          className="hidden"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          title="Attach Image"
          className={`p-2.5 rounded-xl border transition-colors ${
            selectedFile
              ? "bg-indigo-600/20 text-indigo-400 border-indigo-500/40"
              : "bg-slate-950 text-slate-400 hover:text-slate-200 border-slate-800 hover:border-slate-700"
          }`}
        >
          <ImageIcon className="w-4 h-4" />
        </button>

        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSubmit(e);
            }
          }}
          rows={2}
          placeholder={
            mode === "data"
              ? "Ask anything about your database (e.g., 'Find all users with > 5 orders')..."
              : mode === "image_analysis"
              ? "Describe what to analyze (e.g., 'Measure facial proportions and shoulder ratio')..."
              : "Type instructions (e.g., 'Transform casual dress into navy blue silk blazer')... [Enter to send]"
          }
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none transition-colors"
        />

        <button
          type="submit"
          disabled={loading || (!prompt.trim() && !selectedFile)}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white p-2.5 rounded-xl shadow-lg shadow-indigo-600/20 transition-all flex items-center justify-center shrink-0"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>
    </div>
  );
}
