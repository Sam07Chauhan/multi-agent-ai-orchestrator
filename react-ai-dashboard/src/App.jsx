import React, { useState, useRef, useEffect } from "react";
import { Loader2, Bot } from "lucide-react";
import { Header } from "./components/Header";
import { ChatEmptyState } from "./components/ChatEmptyState";
import { ChatMessage } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";
import { processOrchestratorRequest } from "./services/api";

function App() {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState("auto");
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll on new message or loading state change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      if (mode === "data") {
        setMode("image");
      }
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClearChat = () => {
    setMessages([]);
    handleClearFile();
    setPrompt("");
  };

  const handleSelectPreset = (presetMode, presetPrompt) => {
    setMode(presetMode);
    setPrompt(presetPrompt);
  };

  const handlePipelineExecution = async (e) => {
    e?.preventDefault();
    if (!prompt.trim() && !selectedFile) return;

    const currentPrompt = prompt;
    const currentMode = mode;
    const currentPreview = previewUrl;
    const currentFile = selectedFile;

    // 1. Append User Message
    const userMessage = {
      id: Date.now().toString(),
      sender: "user",
      text: currentPrompt,
      mode: currentMode,
      imagePreview: currentPreview,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setPrompt("");
    setLoading(true);

    try {
      // 2. Call Modular Service Layer
      const data = await processOrchestratorRequest({
        prompt: currentPrompt,
        mode: currentMode,
        file: currentFile,
      });

      // 3. Append Assistant Response Message
      const botMessage = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        type: data.type,
        taskId: data.task_id,
        payload: data.payload,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("UI Gateway Error:", err);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        type: "ERROR",
        error: err.message || "Failed to establish proxy connection to AI service layer.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30">
      {/* 1. Header Component */}
      <Header hasMessages={messages.length > 0} onClearChat={handleClearChat} />

      {/* 2. Main Chat Conversation Feed */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-4 sm:p-6 flex flex-col justify-between overflow-hidden">
        <div className="flex-1 overflow-y-auto space-y-6 pr-2 mb-4">
          {messages.length === 0 ? (
            <ChatEmptyState onSelectPreset={handleSelectPreset} />
          ) : (
            messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                copiedId={copiedId}
                onCopy={handleCopy}
              />
            ))
          )}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex gap-3 justify-start animate-fadeIn">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shrink-0 animate-pulse">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-900 border border-slate-850 rounded-2xl rounded-tl-sm p-4 shadow-xl flex items-center gap-3">
                <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                <span className="text-xs text-slate-400">Synthesizing multi-agent pipeline response...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 3. Input Console Component */}
        <ChatInput
          prompt={prompt}
          setPrompt={setPrompt}
          mode={mode}
          setMode={setMode}
          selectedFile={selectedFile}
          previewUrl={previewUrl}
          onFileChange={handleFileChange}
          onClearFile={handleClearFile}
          onSubmit={handlePipelineExecution}
          loading={loading}
        />
      </main>
    </div>
  );
}

export default App;
