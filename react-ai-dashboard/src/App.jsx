import React, { useState } from "react";
import { Sparkles, Database, Image as ImageIcon, Cpu, Loader2, Code } from "lucide-react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState("auto"); // Options: auto, image, data
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [responseData, setResponseData] = useState(null);
  const [error, setError] = useState(null);

  // 1. Handling input image upload matrix
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      // Processing safe safeguard layer - if user uploads an image, naturally switch to image mode if on data mode
      if (mode === "data") {
        setMode("image");
      }
    }
  };

  // 2. Dispatch payload data block directly to .NET Gateway Endpoint
  const handlePipelineExecution = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError("Please enter a structured command or instruction query.");
      return;
    }

    setLoading(true);
    setError(null);
    setResponseData(null);

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("mode", mode);
    if (selectedFile) {
      formData.append("file", selectedFile);
    }

    try {
      // .NET Gateway Engine Base Port Call Injection
      const response = await fetch("http://localhost:5137/api/orchestrator/process", {
        method: "POST",
        body: formData, // Automatic Boundary setup handled by standard fetch core
      });

      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.error || "Execution gateway processing exception.");
      }

      const data = await response.json();
      setResponseData(data);
    } catch (err) {
      console.error("UI Gateway Error Layer caught:", err);
      setError(err.message || "Failed to establish proxy connection to AI service layer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30">
      {/* Premium Header Architecture */}
      <header className="border-b border-slate-900 bg-slate-900/40 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-indigo-600 to-violet-500 p-2 rounded-xl text-white shadow-lg shadow-indigo-500/20">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              M4 AI Orchestrator
            </h1>
            <p className="text-xs text-indigo-400 font-medium">3-Tier Hybrid Local Microservice Stack</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800 text-xs text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          FastAPI Engine Status: Active
        </div>
      </header>

      {/* Main Container Control Workstation Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 p-6">
        
        {/* Left Control Column: Input Parameters Matrix */}
        <section className="lg:col-span-5 bg-slate-900/60 border border-slate-900 rounded-2xl p-5 flex flex-col gap-5 h-fit">
          <h2 className="text-sm font-semibold tracking-wider uppercase text-slate-400 flex items-center gap-2">
            Execution Parameters Blueprint
          </h2>

          <form onSubmit={handlePipelineExecution} className="flex flex-col gap-4">
            {/* Mode Select Tabs - Addresses Dynamic Agent Routing Switch */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-400">Orchestration Intent Pathway</label>
              <div className="grid grid-cols-3 gap-2 bg-slate-950 p-1 rounded-xl border border-slate-900">
                <button
                  type="button"
                  onClick={() => setMode("auto")}
                  className={`flex items-center justify-center gap-1.5 py-2 text-xs font-medium rounded-lg transition-all ${
                    mode === "auto" ? "bg-indigo-600/90 text-white shadow-md shadow-indigo-600/10" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5" /> Auto Agent
                </button>
                <button
                  type="button"
                  onClick={() => setMode("image")}
                  className={`flex items-center justify-center gap-1.5 py-2 text-xs font-medium rounded-lg transition-all ${
                    mode === "image" ? "bg-indigo-600/90 text-white shadow-md shadow-indigo-600/10" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <ImageIcon className="w-3.5 h-3.5" /> AI Canvas
                </button>
                <button
                  type="button"
                  onClick={() => setMode("data")}
                  className={`flex items-center justify-center gap-1.5 py-2 text-xs font-medium rounded-lg transition-all ${
                    mode === "data" ? "bg-indigo-600/90 text-white shadow-md shadow-indigo-600/10" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Database className="w-3.5 h-3.5" /> DB Engine
                </button>
              </div>
            </div>

            {/* Conditional File Upload Block - Needed for Inpainting processing */}
            {mode !== "data" && (
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-400">Target Structural Matrix (Image)</label>
                <div className="border border-dashed border-slate-800 rounded-xl bg-slate-950 p-4 transition-colors hover:border-indigo-500/40 relative flex flex-col items-center justify-center text-center group min-h-[140px]">
                  {previewUrl ? (
                    <div className="relative w-full h-full flex flex-col items-center gap-2">
                      <img src={previewUrl} alt="Matrix Upload Preview" className="max-h-32 object-contain rounded-lg border border-slate-800" />
                      <button 
                        type="button" 
                        onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                        className="text-[10px] text-rose-400 bg-rose-950/40 hover:bg-rose-950/80 px-2 py-0.5 rounded-md border border-rose-900/60"
                      >
                        Purge Matrix
                      </button>
                    </div>
                  ) : (
                    <>
                      <ImageIcon className="w-6 h-6 text-slate-500 mb-2 group-hover:text-indigo-400 transition-colors" />
                      <p className="text-xs font-medium text-slate-400">Drag or drop input asset layer here</p>
                      <p className="text-[10px] text-slate-600 mt-1">PNG, JPG or JPEG up to 10MB dimensions</p>
                      <input type="file" accept="image/*" onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer" />
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Prompt Instruction String Entrypoint */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-400">Instruction Context Sequence</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                placeholder={
                  mode === "data"
                    ? "e.g., Generate a performance report showing all premium users with transactions exceeding 500 units last month..."
                    : "e.g., Transform the current casual dress texture layout into an elegant formal navy blue blazer with fine silk contours..."
                }
                className="w-full bg-slate-950 border border-slate-900 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors resize-none leading-relaxed shadow-inner"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:from-slate-900 disabled:to-slate-900 disabled:text-slate-600 disabled:border-slate-800 text-white text-xs font-semibold py-3 px-4 rounded-xl shadow-lg shadow-indigo-600/10 active:scale-[0.99] transition-all border border-indigo-500/20 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                  Synthesizing Operations Pipeline...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Compile & Execute Request
                </>
              )}
            </button>
          </form>
        </section>

        {/* Right Output Column: Dynamic Render Matrix Dashboard Workspace */}
        <section className="lg:col-span-7 bg-slate-900/40 border border-slate-900/60 rounded-2xl p-5 flex flex-col min-h-[450px]">
          <h2 className="text-sm font-semibold tracking-wider uppercase text-slate-400 mb-4">
            Render Node Display Monitor
          </h2>

          <div className="flex-1 bg-slate-950 rounded-xl border border-slate-900/80 flex flex-col items-center justify-center p-4 relative overflow-hidden shadow-2xl">
            
            {/* Status Indicators Layer */}
            {!loading && !responseData && !error && (
              <div className="text-center p-6 flex flex-col items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-850 flex items-center justify-center text-slate-600 shadow-inner">
                  <Cpu className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-400">System Standing By for Dispatch Orders</p>
                  <p className="text-[10px] text-slate-600 mt-1">Execution output vectors will map onto this diagnostic view monitor grid.</p>
                </div>
              </div>
            )}

            {/* Loading Indicator Core Screen */}
            {loading && (
              <div className="text-center flex flex-col items-center gap-4 bg-slate-950/80 absolute inset-0 justify-center backdrop-blur-sm z-10">
                <div className="relative flex items-center justify-center">
                  <div className="w-14 h-14 rounded-full border border-indigo-500/20 border-t-indigo-500 animate-spin" />
                  <Sparkles className="w-5 h-5 text-indigo-400 absolute animate-pulse" />
                </div>
                <div className="flex flex-col gap-1 max-w-xs">
                  <p className="text-xs font-semibold text-slate-300">Assembling Multi-Agent State Machine</p>
                  <p className="text-[10px] text-slate-500 leading-relaxed">
                    {mode === "data" 
                      ? "Fetching structural schema catalog metadata and executing local Llama LLM Text-to-SQL logic block..."
                      : "Triggering YOLOv8 subject segmentation, calculating face mesh shields, and passing vectors to Diffusion pipelines..."}
                  </p>
                </div>
              </div>
            )}

            {/* Error Message Layout Display */}
            {error && (
              <div className="max-w-md text-center p-4 border border-rose-900/50 bg-rose-950/20 rounded-xl text-rose-300 flex flex-col items-center gap-2">
                <span className="text-xs font-semibold tracking-wide uppercase text-rose-400">Pipeline Crash Encountered</span>
                <p className="text-xs font-mono leading-relaxed break-words bg-slate-950 p-2 rounded border border-slate-900 w-full text-left">{error}</p>
              </div>
            )}

            {/* Dynamic Content Generation Renderer - Handles dynamic polymorphic payload responses */}
            {responseData && !loading && (
              <div className="w-full h-full flex flex-col animate-fadeIn">
                
                {/* Header Metadata Ribbon */}
                <div className="flex items-center justify-between border-b border-slate-900 pb-3 mb-3 text-[10px] font-mono text-indigo-400 w-full">
                  <span>Task Token: {responseData.task_id}</span>
                  <span className="bg-indigo-950/60 border border-indigo-900 px-2 py-0.5 rounded text-indigo-300 font-bold uppercase tracking-widest">
                    {responseData.type}
                  </span>
                </div>

                {/* Polymorphic Switch Render Layer */}
                {responseData.type === "IMAGE_BASE64" && (
                  <div className="flex-1 flex flex-col items-center justify-center overflow-hidden">
                    <img
                      src={`data:image/jpeg;base64,${responseData.payload}`}
                      alt="AI Orchestration Generated Output Pipeline Result"
                      className="max-h-[380px] w-auto object-contain rounded-lg border border-slate-900 shadow-2xl transition-transform hover:scale-[1.01]"
                    />
                  </div>
                )}

                {responseData.type === "DATABASE_SQL" && (
                  <div className="flex-1 w-full flex flex-col gap-2">
                    <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                      <Code className="w-3.5 h-3.5 text-indigo-400" /> Executable Text-to-SQL Structured Output Syntax
                    </div>
                    <pre className="flex-1 w-full bg-slate-900/50 border border-slate-900 font-mono text-xs text-emerald-400 p-4 rounded-xl overflow-auto select-all leading-relaxed whitespace-pre-wrap text-left shadow-inner border-t-2 border-t-emerald-600/30">
                      {responseData.payload}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;