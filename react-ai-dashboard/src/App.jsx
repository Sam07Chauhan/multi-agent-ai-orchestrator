import { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [file, setFile] = useState(null);
  const [schema, setSchema] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
    }
  };

  const clearAttachment = () => {
    setFile(null);
    setPreviewUrl('');
  };

  const handleOrchestration = async () => {
    if (!query.trim()) return;

    setLoading(true);
    const currentUserQuery = query;
    setQuery(''); // Resetting input like a true chat terminal

    const formData = new FormData();
    formData.append('userQuery', currentUserQuery);
    if (file) formData.append('file', file);
    if (schema) formData.append('schema', schema);

    try {
      const response = await fetch('http://localhost:5137/api/orchestrator/run', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error("Orchestrator dropped connection");

      const result = await response.json();

      // Append exchange to live feed history
      setHistory(prev => [
        {
          id: Date.now(),
          userPrompt: currentUserQuery,
          attachedImage: previewUrl,
          engine: result.actionPerformed,
          type: result.dataType,
          data: result.content
        },
        ...prev
      ]);

      // Clear attachments after success
      clearAttachment();
    } catch (error) {
      console.error(error);
      alert("Error: Core Orchestrator engine response dropped.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Dynamic Glassmorphic Sidebar Console */}
      <aside className="control-sidebar">
        <div className="brand-header">
          <div className="pulse-icon"></div>
          <h2>M4 AI Nexus Core</h2>
        </div>
        <p className="system-subtitle">3-Tier Intelligent Routing Architecture</p>

        <hr className="divider" />

        {/* Attachment Hub */}
        <div className="sidebar-section">
          <h3>📁 Input Modalities</h3>
          <div className="file-uploader">
            <label className="upload-btn">
              {file ? "🔄 Change Attachment" : "📸 Upload Context Image"}
              <input type="file" accept="image/*" onChange={handleFileChange} style={{ display: 'none' }} />
            </label>
            {previewUrl && (
              <div className="preview-frame">
                <img src={previewUrl} alt="Context Preview" />
                <button className="clear-btn" onClick={clearAttachment}>✕ Remove</button>
              </div>
            )}
          </div>
        </div>

        {/* Technical Context Terminal */}
        <div className="sidebar-section">
          <h3>🗄️ Relational Context Data</h3>
          <textarea
            value={schema}
            onChange={(e) => setSchema(e.target.value)}
            placeholder="Inject metadata structure here... e.g. Table: Users(ID, Name, Role)"
            className="schema-terminal"
            rows={4}
          />
        </div>
      </aside>

      {/* Main Streaming Chat Workspace */}
      <main className="chat-workspace">
        <div className="chat-history">
          {history.length === 0 && !loading ? (
            <div className="empty-state">
              <div className="ai-logo">🧠</div>
              <h2>How can I assist your workflow today, Shivam?</h2>
              <p>Type a natural language request. Llama 3 will map the intent, compute pipelines via M4 hardware, and render outputs natively.</p>
            </div>
          ) : (
            <div className="feed-stream">
              {/* Loader placeholder */}
              {loading && (
                <div className="chat-card dynamic-loading">
                  <div className="loader-pulse"></div>
                  <p>Orchestrating system agents, compiling local inference tasks...</p>
                </div>
              )}

              {/* Feed mapping loops */}
              {history.map((interaction) => (
                <div key={interaction.id} className="chat-card row-layout">
                  <div className="user-query-block">
                    <span className="user-badge">USER</span>
                    <p className="prompt-txt">{interaction.userPrompt}</p>
                    {interaction.attachedImage && (
                      <div className="query-img">
                        <small>Context image pinned:</small>
                        <img src={interaction.attachedImage} alt="user attach" />
                      </div>
                    )}
                  </div>

                  <div className="ai-response-block">
                    <div className="engine-meta">
                      <span className="ai-badge">NEXUS CORE</span>
                      <span className="route-tag">Agent: {interaction.engine}</span>
                    </div>

                    <div className="response-payload">
                      {/* Scenario 1: Base64 Diffusion Image Outputs */}
                      {interaction.type === 'IMAGE_BASE64' && (
                        <div className="image-result-wrapper">
                          <img src={interaction.data} alt="AI output" className="compiled-render" />
                        </div>
                      )}

                      {/* Scenario 2: System Text Responses */}
                      {interaction.type === 'TEXT' && (
                        <div className="text-result-wrapper">
                          <p>{interaction.data}</p>
                        </div>
                      )}

                      {/* Scenario 3: SQL Data Engine Mapping */}
                      {(interaction.type === 'JSON_TABLE' || interaction.type === 'JSON') && (
                        <div className="json-result-wrapper">
                          {interaction.data.query && (
                            <pre className="code-block"><code>{interaction.data.query}</code></pre>
                          )}
                          <pre className="json-raw">
                            <code>{JSON.stringify(interaction.data.rows || interaction.data, null, 2)}</code>
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Global Input Bar Layer */}
        <footer className="workspace-footer">
          <div className="input-bar-container">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleOrchestration()}
              placeholder="Message Nexus AI Core..."
              disabled={loading}
              className="global-input-box"
            />
            <button 
              onClick={handleOrchestration} 
              disabled={loading || !query.trim()} 
              className="send-arrow-btn"
            >
              ➔
            </button>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;