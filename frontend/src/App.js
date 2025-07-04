// React frontend for Mocksi 
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

// API configuration
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  // State management for reverse string functionality
  const [reverseInput, setReverseInput] = useState('');
  const [reverseTask, setReverseTask] = useState(null);
  const [reverseResult, setReverseResult] = useState(null);
  const [reverseLoading, setReverseLoading] = useState(false);
  
  // State management for summarization
  const [summarizeInput, setSummarizeInput] = useState('');
  const [summarizeStyle, setSummarizeStyle] = useState('concise');
  const [summarizeResult, setSummarizeResult] = useState(null);
  const [summarizeLoading, setSummarizeLoading] = useState(false);
  
  // Error handling
  const [error, setError] = useState('');
  
  // Service status
  const [serviceStatus, setServiceStatus] = useState(null);

  // Check service health on component mount
  useEffect(() => {
    checkServiceHealth();
  }, []);

  // Polling effect for reverse task status
  useEffect(() => {
    let interval;
    if (reverseTask && !reverseResult) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE}/reverse/${reverseTask.task_id}`);
          const data = response.data;
          
          // Check for terminal states
          if (data.status === 'completed' || data.status === 'failed') {
            setReverseResult(data);
            setReverseTask(null);
            setReverseLoading(false);
            
            if (data.status === 'failed' && data.error) {
              setError(data.error);
            }
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Error polling task status:', err);
          setError('Failed to get task status');
          setReverseLoading(false);
          clearInterval(interval);
        }
      }, 1000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [reverseTask, reverseResult]);

  const checkServiceHealth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      setServiceStatus(response.data);
    } catch (err) {
      console.error('Health check failed:', err);
      setServiceStatus({ app: 'unhealthy' });
    }
  }, []);

  // Handle string reversal submission
  const handleReverseSubmit = async (e) => {
    e.preventDefault();
    if (!reverseInput.trim()) {
      setError('Please enter text to reverse');
      return;
    }

    setReverseLoading(true);
    setError('');
    setReverseResult(null);
    
    try {
      const response = await axios.post(`${API_BASE}/reverse`, {
        text: reverseInput
      });
      setReverseTask(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start reverse task');
      setReverseLoading(false);
    }
  };

  // Handle text summarization submission
  const handleSummarizeSubmit = async (e) => {
    e.preventDefault();
    if (!summarizeInput.trim()) {
      setError('Please enter text to summarize');
      return;
    }

    setSummarizeLoading(true);
    setError('');
    setSummarizeResult(null);
    
    try {
      const response = await axios.post(`${API_BASE}/summarize`, {
        text: summarizeInput,
        style: summarizeStyle
      });
      setSummarizeResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to summarize text');
    } finally {
      setSummarizeLoading(false);
    }
  };

  // Clear all results and reset form
  const handleClearAll = () => {
    setReverseInput('');
    setReverseTask(null);
    setReverseResult(null);
    setReverseLoading(false);
    setSummarizeInput('');
    setSummarizeResult(null);
    setSummarizeLoading(false);
    setError('');
  };

  // Helper function to get status class
  const getStatusClass = (status) => {
    if (status === 'healthy' || status === 'connected') return 'healthy';
    if (status === 'configured' || status === 'available') return 'warning';
    return 'error';
  };

  // Helper function to get display text
  const getDisplayStatus = (status) => {
    if (status === 'connected') return 'connected';
    if (status === 'configured but unreachable') return 'API issue';
    if (status === 'configured but error') return 'API error';
    if (status === 'error') return 'connection error';
    if (status === 'available') return 'working';
    if (status === 'not configured') return 'not configured';
    return status;
  };

  return (
    <div className="App">
      {/* Header with Mocksi branding */}
      <header className="mocksi-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="mocksi-logo">
              <span className="logo-icon">🚀</span>
              <span className="logo-text">mocksi</span>
            </div>
          </div>
          <div className="header-actions">
            <button className="btn-secondary">Book a demo</button>
            <button className="btn-primary">Join the waitlist</button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Less prep, better demos,<br />
            more wins faster
          </h1>
          <p className="hero-subtitle">
            Deliver high-quality, customized demos at the speed of<br />
            opportunity—without the technical bottlenecks that slow deals
          </p>
          
          {/* Service Status Indicators - Updated to match new health format */}
          {serviceStatus && (
            <div className="service-status">
              <div className={`status-indicator ${getStatusClass(serviceStatus.app)}`}>
                <span className="status-dot"></span>
                API: {serviceStatus.app}
              </div>
              <div className={`status-indicator ${getStatusClass(serviceStatus.temporal?.status)}`}>
                <span className="status-dot"></span>
                Temporal: {getDisplayStatus(serviceStatus.temporal?.status)}
              </div>
              <div className={`status-indicator ${getStatusClass(serviceStatus.huggingface?.status)}`}>
                <span className="status-dot"></span>
                AI: {getDisplayStatus(serviceStatus.huggingface?.status)}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Main Demo Section */}
      <main className="demo-section">
        <div className="demo-container">
          
          {/* Error Display */}
          {error && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
              <button onClick={() => setError('')} className="close-error">×</button>
            </div>
          )}

          {/* Demo Cards */}
          <div className="demo-grid">
            
            {/* String Reversal Demo */}
            <div className="demo-card">
              <div className="card-header">
                <h3>🔄 Background Processing</h3>
                <p>Temporal workflow demonstration</p>
              </div>
              
              <form onSubmit={handleReverseSubmit} className="demo-form">
                <div className="input-group">
                  <label>Enter text to reverse:</label>
                  <textarea
                    value={reverseInput}
                    onChange={(e) => setReverseInput(e.target.value)}
                    placeholder="Type your message here..."
                    rows="3"
                    disabled={reverseLoading}
                    className="demo-input"
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={reverseLoading || !reverseInput.trim()}
                  className="demo-btn primary"
                >
                  {reverseLoading ? (
                    <>
                      <span className="spinner"></span>
                      Processing...
                    </>
                  ) : (
                    'Start Workflow'
                  )}
                </button>
              </form>

              {/* Task Progress */}
              {reverseTask && !reverseResult && (
                <div className="task-progress">
                  <div className="progress-header">
                    <span>Workflow Running</span>
                    <span className="task-id">ID: {reverseTask.task_id.slice(0, 8)}...</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill"></div>
                  </div>
                </div>
              )}

              {/* Results */}
              {reverseResult && (
                <div className="result-panel">
                  <div className="result-header">
                    <span className={`result-status ${reverseResult.status}`}>
                      {reverseResult.status === 'completed' ? ' Complete' : 'Failed'}
                    </span>
                    {reverseResult.processing_time_seconds && (
                      <span className="processing-time">
                        {reverseResult.processing_time_seconds}s
                      </span>
                    )}
                  </div>
                  
                  <div className="result-content">
                    <div className="result-item">
                      <label>Original:</label>
                      <div className="result-text original">{reverseResult.original_text}</div>
                    </div>
                    
                    {reverseResult.reversed_text && (
                      <div className="result-item">
                        <label>Reversed:</label>
                        <div className="result-text reversed">{reverseResult.reversed_text}</div>
                      </div>
                    )}
                    
                    {reverseResult.error && (
                      <div className="result-item error">
                        <label>Error:</label>
                        <div className="result-text">{reverseResult.error}</div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* AI Summarization Demo */}
            <div className="demo-card">
              <div className="card-header">
                <h3>🤖 AI Processing</h3>
                <p>Text summarization with Hugging Face API</p>
              </div>
              
              <form onSubmit={handleSummarizeSubmit} className="demo-form">
                <div className="input-group">
                  <label>Enter text to summarize:</label>
                  <textarea
                    value={summarizeInput}
                    onChange={(e) => setSummarizeInput(e.target.value)}
                    placeholder="Paste a long article or text here..."
                    rows="4"
                    disabled={summarizeLoading}
                    className="demo-input"
                  />
                </div>
                
                <div className="input-group">
                  <label>Summary style:</label>
                  <select
                    value={summarizeStyle}
                    onChange={(e) => setSummarizeStyle(e.target.value)}
                    disabled={summarizeLoading}
                    className="demo-select"
                  >
                    <option value="concise">Concise (2-3 sentences)</option>
                    <option value="detailed">Detailed (4-5 sentences)</option>
                  </select>
                </div>
                
                <button 
                  type="submit" 
                  disabled={summarizeLoading || !summarizeInput.trim()}
                  className="demo-btn primary"
                >
                  {summarizeLoading ? (
                    <>
                      <span className="spinner"></span>
                      Processing...
                    </>
                  ) : (
                    'Generate Summary'
                  )}
                </button>
              </form>

              {/* AI Results */}
              {summarizeResult && (
                <div className="result-panel">
                  <div className="result-header">
                    <span className="result-status completed">✨ Summary Generated</span>
                    <span className="ai-badge">{summarizeResult.style}</span>
                  </div>
                  
                  <div className="result-content">
                    <div className="result-item">
                      <label>Original Text:</label>
                      <div className="result-text original">{summarizeResult.original_text}</div>
                    </div>
                    
                    <div className="result-item">
                      <label>AI Summary:</label>
                      <div className="result-text summary">{summarizeResult.summary_text}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Demo Controls */}
          <div className="demo-controls">
            <button onClick={handleClearAll} className="demo-btn secondary">
              Clear All Results
            </button>
            <button onClick={checkServiceHealth} className="demo-btn secondary">
              Refresh Status
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mocksi-footer">
        <div className="footer-content">
          <p>Built with FastAPI, Temporal, React, and Hugging Face API • Mocksi Demo Environment</p>
          <div className="footer-links">
            <a href="http://localhost:8080" target="_blank" rel="noopener noreferrer">
              Temporal Dashboard
            </a>
            <span>•</span>
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
              API Documentation
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
