import React from "react";
import { Bot, User, Code, ScanSearch, Copy, Check } from "lucide-react";

export function ChatMessage({ message, copiedId, onCopy }) {
  const isUser = message.sender === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"} animate-fadeIn`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shrink-0 shadow-md shadow-indigo-600/20">
          <Bot className="w-4 h-4" />
        </div>
      )}

      <div className={`flex flex-col gap-1.5 max-w-[85%] sm:max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        {/* Header Ribbon */}
        <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
          {isUser ? (
            <>
              <span>{message.timestamp}</span>
              <span className="bg-slate-850 text-slate-300 px-2 py-0.5 rounded uppercase font-semibold text-[9px] border border-slate-800">
                {message.mode}
              </span>
            </>
          ) : (
            <>
              <span className="bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded uppercase font-semibold text-[9px] border border-indigo-900">
                {message.type}
              </span>
              <span>{message.timestamp}</span>
            </>
          )}
        </div>

        {/* User Content */}
        {isUser && (
          <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm p-4 shadow-lg shadow-indigo-600/10 border border-indigo-500/20">
            {message.imagePreview && (
              <div className="mb-3 rounded-lg overflow-hidden border border-indigo-400/30 max-w-[200px]">
                <img src={message.imagePreview} alt="User Upload" className="w-full h-auto object-cover" />
              </div>
            )}
            <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
          </div>
        )}

        {/* Assistant Content */}
        {!isUser && (
          <div className="bg-slate-900/90 border border-slate-855 rounded-2xl rounded-tl-sm p-4 shadow-xl w-full">
            {/* 1. Image Base64 */}
            {message.type === "IMAGE_BASE64" && (
              <div className="flex flex-col gap-3">
                <div className="rounded-xl overflow-hidden border border-slate-800 bg-slate-950 p-2 flex justify-center">
                  <img
                    src={`data:image/jpeg;base64,${message.payload}`}
                    alt="AI Generated Output"
                    className="max-h-[420px] w-auto rounded-lg object-contain"
                  />
                </div>
                <a
                  href={`data:image/jpeg;base64,${message.payload}`}
                  download={`ai-inpaint-${message.id}.jpg`}
                  className="self-end text-[11px] text-indigo-400 hover:text-indigo-300 font-medium bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 transition-colors"
                >
                  Download Image
                </a>
              </div>
            )}

            {/* 2. SQL Output */}
            {message.type === "DATABASE_SQL" && (
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5">
                    <Code className="w-3.5 h-3.5 text-indigo-400" /> Generated SQL Query
                  </span>
                  <button
                    type="button"
                    onClick={() => onCopy(message.payload, message.id)}
                    className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white bg-slate-950 px-2 py-1 rounded border border-slate-800 transition-colors"
                  >
                    {copiedId === message.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copiedId === message.id ? "Copied" : "Copy"}
                  </button>
                </div>
                <pre className="bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-400 p-3.5 rounded-xl overflow-x-auto whitespace-pre-wrap select-all">
                  {message.payload}
                </pre>
              </div>
            )}

            {/* 3. Image Analysis */}
            {message.type === "IMAGE_ANALYSIS" && (
              <div className="flex flex-col gap-3">
                <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                  <ScanSearch className="w-3.5 h-3.5 text-indigo-400" /> Analysis Findings
                </div>
                {message.payload?.summary && (
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80">
                    {message.payload.summary}
                  </p>
                )}
                {!message.payload?.summary && message.payload && (
                  <div className="flex flex-col gap-2">
                    {Object.entries(message.payload).map(([section, data]) =>
                      data && data.summary ? (
                        <div key={section} className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80">
                          <p className="text-[10px] uppercase tracking-wider text-indigo-400 font-bold mb-1">{section}</p>
                          <p className="text-xs text-slate-200 leading-relaxed">{data.summary}</p>
                        </div>
                      ) : null
                    )}
                  </div>
                )}
                <details className="text-[10px] text-slate-500">
                  <summary className="cursor-pointer hover:text-slate-300">Raw measurement data</summary>
                  <pre className="mt-2 bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-indigo-300 overflow-auto max-h-48">
                    {JSON.stringify(message.payload, null, 2)}
                  </pre>
                </details>
              </div>
            )}

            {/* 4. Error Message */}
            {message.type === "ERROR" && (
              <div className="text-xs text-rose-300 bg-rose-950/30 border border-rose-900/50 p-3 rounded-xl">
                <p className="font-semibold text-rose-400 mb-0.5">Execution Failed</p>
                <p>{message.error}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-slate-300 shrink-0 border border-slate-700">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
