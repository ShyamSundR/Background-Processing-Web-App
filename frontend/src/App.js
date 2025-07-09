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
  
  // Add to state management (after existing state)
  const [screenshotUrl, setScreenshotUrl] = useState('');
  const [screenshotTask, setScreenshotTask] = useState(null);
  const [screenshotResult, setScreenshotResult] = useState(null);
  const [screenshotLoading, setScreenshotLoading] = useState(false);

  const [showScreenshotModal, setShowScreenshotModal] = useState(false);

  const [analysisUrl, setAnalysisUrl] = useState('');
  const [analysisTask, setAnalysisTask] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  
  const [techSpecUrl, setTechSpecUrl] = useState('');
  const [techSpecTask, setTechSpecTask] = useState(null);
  const [techSpecResult, setTechSpecResult] = useState(null);
  const [techSpecLoading, setTechSpecLoading] = useState(false);

  const [websiteGenUrl, setWebsiteGenUrl] = useState('');
  const [websiteGenTask, setWebsiteGenTask] = useState(null);
  const [websiteGenResult, setWebsiteGenResult] = useState(null);
  const [websiteGenLoading, setWebsiteGenLoading] = useState(false);
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

  useEffect(() => {
    let interval;
    if (screenshotTask && !screenshotResult) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE}/screenshot/${screenshotTask.task_id}`);
          const data = response.data;
          
          if (data.status === 'completed' || data.status === 'failed') {
            setScreenshotResult(data);
            setScreenshotTask(null);
            setScreenshotLoading(false);
            
            if (data.status === 'failed' && data.error) {
              setError(data.error);
            }
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Error polling screenshot status:', err);
          setError('Failed to get screenshot status');
          setScreenshotLoading(false);
          clearInterval(interval);
        }
      }, 2000); // Longer interval for screenshots
    }    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [screenshotTask, screenshotResult]);
  // Add polling effect for content analysis (add after existing polling effects)
  useEffect(() => {
    let interval;
    if (analysisTask && !analysisResult) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE}/analyze/${analysisTask.task_id}`);
          const data = response.data;
          
          if (data.status === 'completed' || data.status === 'failed') {
            setAnalysisResult(data);
            setAnalysisTask(null);
            setAnalysisLoading(false);
            
            if (data.status === 'failed' && data.error) {
              setError(data.error);
            }
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Error polling analysis status:', err);
          setError('Failed to get analysis status');
          setAnalysisLoading(false);
          clearInterval(interval);
        }
      }, 3000); // Longer interval for complex analysis
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [analysisTask, analysisResult]);

  // Add polling effect for tech spec (add after existing polling effects)
  useEffect(() => {
    let interval;
    if (techSpecTask && !techSpecResult) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE}/tech-spec/${techSpecTask.task_id}`);
          const data = response.data;
          
          console.log('Tech spec status:', data.status);
          
          if (data.status === 'completed' || data.status === 'failed') {
            setTechSpecResult(data);
            setTechSpecTask(null);
            setTechSpecLoading(false);
            
            if (data.status === 'failed' && data.error) {
              setError(`Technical specification failed: ${data.error}`);
            }
            
            if (data.status === 'completed') {
              console.log('✅ Technical specification completed successfully');
            }
            
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Error polling tech spec status:', err);
          setError('Failed to get technical specification status');
          setTechSpecLoading(false);
          clearInterval(interval);
        }
      }, 4000); // 4 second intervals for complex analysis
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [techSpecTask, techSpecResult]);

  useEffect(() => {
    let interval;
    if (websiteGenTask && !websiteGenResult) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE}/generate-website/${websiteGenTask.task_id}`);
          const data = response.data;
          
          console.log('Website generation status:', data.status);
          
          if (data.status === 'completed' || data.status === 'failed') {
            setWebsiteGenResult(data);
            setWebsiteGenTask(null);
            setWebsiteGenLoading(false);
            
            if (data.status === 'failed' && data.error) {
              setError(`Website generation failed: ${data.error}`);
            }
            
            if (data.status === 'completed') {
              console.log('✅ Website generation completed successfully');
            }
            
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Error polling website generation status:', err);
          setError('Failed to get website generation status');
          setWebsiteGenLoading(false);
          clearInterval(interval);
        }
      }, 5000); // 5 second intervals for comprehensive workflow
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [websiteGenTask, websiteGenResult]);
  

  // Add screenshot submit handler
  const handleScreenshotSubmit = async (e) => {
    e.preventDefault();
    if (!screenshotUrl.trim()) {
      setError('Please enter a URL');
      return;
    }
  
    setScreenshotLoading(true);
    setError('');
    setScreenshotResult(null);
    
    try {
      const response = await axios.post(`${API_BASE}/screenshot`, {
        url: screenshotUrl
      });
      setScreenshotTask(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start screenshot capture');
      setScreenshotLoading(false);
    }
  };

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

  // Add analysis submit handler
  const handleAnalysisSubmit = async (e) => {
    e.preventDefault();
    if (!analysisUrl.trim()) {
      setError('Please enter a URL to analyze');
      return;
    }

    setAnalysisLoading(true);
    setError('');
    setAnalysisResult(null);
    
    try {
      const response = await axios.post(`${API_BASE}/analyze`, {
        url: analysisUrl
      });
      setAnalysisTask(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start content analysis');
      setAnalysisLoading(false);
    }
  };

  // Add tech spec submit handler
  const handleTechSpecSubmit = async (e) => {
    e.preventDefault();
    
    if (!techSpecUrl.trim()) {
      setError('Please enter a URL to analyze');
      return;
    }
    
    // URL validation
    const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    if (!urlPattern.test(techSpecUrl)) {
      setError('Please enter a valid URL (e.g., https://example.com)');
      return;
    }

    setTechSpecLoading(true);
    setError('');
    setTechSpecResult(null);
    
    try {
      console.log('🔧 Starting technical specification for:', techSpecUrl);
      
      const response = await axios.post(`${API_BASE}/tech-spec`, {
        url: techSpecUrl
      });
      
      console.log('✅ Tech spec task created:', response.data.task_id);
      setTechSpecTask(response.data);
      
    } catch (err) {
      console.error('❌ Tech spec submission failed:', err);
      
      if (err.response?.status === 503) {
        setError('Technical specification service unavailable - check if Browserbase is configured');
      } else if (err.response?.status === 400) {
        setError('Invalid URL provided - please check the format');
      } else if (err.response?.data?.detail) {
        setError(`Failed to start analysis: ${err.response.data.detail}`);
      } else {
        setError('Failed to start technical specification - please try again');
      }
      
      setTechSpecLoading(false);
    }
  };
  const handleWebsiteGenSubmit = async (e) => {
    e.preventDefault();
    
    if (!websiteGenUrl.trim()) {
      setError('Please enter a URL to analyze');
      return;
    }
    
    // URL validation
    const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    if (!urlPattern.test(websiteGenUrl)) {
      setError('Please enter a valid URL (e.g., https://example.com)');
      return;
    }
  
    setWebsiteGenLoading(true);
    setError('');
    setWebsiteGenResult(null);
    
    try {
      console.log('🚀 Starting comprehensive website generation for:', websiteGenUrl);
      
      const response = await axios.post(`${API_BASE}/generate-website`, {
        url: websiteGenUrl
      });
      
      console.log('✅ Website generation task created:', response.data.task_id);
      setWebsiteGenTask(response.data);
      
    } catch (err) {
      console.error('❌ Website generation submission failed:', err);
      
      if (err.response?.status === 503) {
        if (err.response.data.detail.includes('BROWSERBASE')) {
          setError('Browserbase not configured - contact administrator');
        } else if (err.response.data.detail.includes('HUGGINGFACE')) {
          setError('AI service not configured - contact administrator');
        } else {
          setError('Required services unavailable - check configuration');
        }
      } else if (err.response?.status === 400) {
        setError('Invalid URL provided - please check the format');
      } else if (err.response?.data?.detail) {
        setError(`Failed to start generation: ${err.response.data.detail}`);
      } else {
        setError('Failed to start website generation - please try again');
      }
      
      setWebsiteGenLoading(false);
    }
  };

  // REPLACE the handleDownloadCode function with this fixed version:
  const handleDownloadCode = async (taskId) => {
    try {
      console.log('Downloading code for task:', taskId);
      
      // Use the correct task ID from the result, not the old task
      const actualTaskId = websiteGenResult?.task_id || taskId;
      
      const response = await axios.get(`${API_BASE}/download-code/${actualTaskId}`);
      const files = response.data.files;
      
      if (!files || Object.keys(files).length === 0) {
        setError('No code files available for download');
        return;
      }
      
      // Create and download each file
      Object.entries(files).forEach(([filename, content]) => {
        if (content && content.trim()) {
          const blob = new Blob([content], { 
            type: filename.endsWith('.html') ? 'text/html' : 
                  filename.endsWith('.css') ? 'text/css' :
                  filename.endsWith('.js') ? 'text/javascript' : 'text/plain'
          });
          
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          link.style.display = 'none';
          
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
          
          console.log(`✅ Downloaded: ${filename}`);
        }
      });
      
      console.log('✅ All code files downloaded successfully');
      
    } catch (err) {
      console.error('❌ Failed to download code:', err);
      
      if (err.response?.status === 404) {
        setError('Code files not found - task may not be completed yet');
      } else if (err.response?.status === 400) {
        setError('Task not ready for download yet');
      } else {
        setError('Failed to download generated code files');
      }
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
    setScreenshotUrl('');
    setScreenshotTask(null);
    setScreenshotResult(null);
    setScreenshotLoading(false);
    setAnalysisUrl('');
    setAnalysisTask(null);
    setAnalysisResult(null);
    setAnalysisLoading(false);
    setTechSpecUrl('');
    setTechSpecTask(null);
    setTechSpecResult(null);
    setTechSpecLoading(false);
    setWebsiteGenUrl('');          // ADD THIS
    setWebsiteGenTask(null);       // ADD THIS
    setWebsiteGenResult(null);     // ADD THIS
    setWebsiteGenLoading(false);   // ADD THIS
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
              {serviceStatus?.browserbase && (
                <div className={`status-indicator ${getStatusClass(serviceStatus.browserbase.status)}`}>
                  <span className="status-dot"></span>
                  Screenshots: {getDisplayStatus(serviceStatus.browserbase.status)}
                </div>
              )}
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
          {/* Screenshot Capture Demo */}
          <div className="demo-card">
            <div className="card-header">
              <h3>📸 Screenshot Capture</h3>
              <p>Browser automation with Browserbase + Playwright</p>
            </div>
            
            <form onSubmit={handleScreenshotSubmit} className="demo-form">
              <div className="input-group">
                <label>Enter website URL:</label>
                <input
                  type="text"
                  value={screenshotUrl}
                  onChange={(e) => setScreenshotUrl(e.target.value)}
                  placeholder="https://example.com"
                  disabled={screenshotLoading}
                  className="demo-input"
                />
              </div>
              <button 
                type="submit" 
                disabled={screenshotLoading || !screenshotUrl.trim()}
                className="demo-btn primary"
              >
                {screenshotLoading ? (
                  <>
                    <span className="spinner"></span>
                    Capturing...
                  </>
                ) : (
                  'Get Screenshot'
                )}
              </button>
            </form>

            {/* Task Progress */}
            {screenshotTask && !screenshotResult && (
              <div className="task-progress">
                <div className="progress-header">
                  <span>Capturing Screenshot</span>
                  <span className="task-id">ID: {screenshotTask.task_id.slice(0, 8)}...</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill"></div>
                </div>
              </div>
            )}

            {/* Results */}
            {screenshotResult && (
              <div className="result-panel">
                <div className="result-header">
                  <span className={`result-status ${screenshotResult.status}`}>
                    {screenshotResult.status === 'completed' ? '📸 Captured' : 'Failed'}
                  </span>
                  {screenshotResult.processing_time_seconds && (
                    <span className="processing-time">
                      {screenshotResult.processing_time_seconds}s
                    </span>
                  )}
                </div>
                
                <div className="result-content">
                  <div className="result-item">
                    <label>Website:</label>
                    <div className="result-text original">{screenshotResult.url}</div>
                  </div>
                  
                  {screenshotResult.page_title && (
                    <div className="result-item">
                      <label>Page Title:</label>
                      <div className="result-text">{screenshotResult.page_title}</div>
                    </div>
                  )}
                  
                  {screenshotResult.screenshot_data && (
                    <div className="result-item">
                      <label>Screenshot:</label>
                      <div className="screenshot-container">
                        <img 
                          src={`data:image/png;base64,${screenshotResult.screenshot_data}`}
                          alt="Website screenshot"
                          className="screenshot-image"
                          onClick={() => setShowScreenshotModal(true)}
                          style={{ cursor: 'pointer' }}
                          title="Click to view full size"
                        />
                      </div>
                    </div>
                  )}

                  {/* Add this modal at the end of your component, before the closing </div> */}
                  {showScreenshotModal && (
                    <div 
                      className="screenshot-modal-overlay" 
                      onClick={() => setShowScreenshotModal(false)}
                      style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                        cursor: 'pointer'
                      }}
                    >
                      <div style={{ position: 'relative', maxWidth: '90vw', maxHeight: '90vh' }}>
                        <img 
                          src={`data:image/png;base64,${screenshotResult.screenshot_data}`}
                          alt="Full size screenshot"
                          style={{
                            maxWidth: '100%',
                            maxHeight: '100%',
                            objectFit: 'contain',
                            borderRadius: '8px'
                          }}
                        />
                        <button
                          onClick={() => setShowScreenshotModal(false)}
                          style={{
                            position: 'absolute',
                            top: '10px',
                            right: '10px',
                            background: 'rgba(0, 0, 0, 0.7)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '50%',
                            width: '30px',
                            height: '30px',
                            cursor: 'pointer',
                            fontSize: '18px'
                          }}
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {screenshotResult.replay_url && (
                    <div className="result-item">
                      <label>Session Replay:</label>
                      <a 
                        href={screenshotResult.replay_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="replay-link"
                      >
                        View Browser Session →
                      </a>
                    </div>
                  )}
                  
                  {screenshotResult.error && (
                    <div className="result-item error">
                      <label>Error:</label>
                      <div className="result-text">{screenshotResult.error}</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          {/* Content Analysis Demo */}
            <div className="demo-card">
              <div className="card-header">
                <h3>🧠 Content Analysis</h3>
                <p>AI-powered page analysis with insights and summaries</p>
              </div>
              
              <form onSubmit={handleAnalysisSubmit} className="demo-form">
                <div className="input-group">
                  <label>Enter website URL to analyze:</label>
                  <input
                    type="text"
                    value={analysisUrl}
                    onChange={(e) => setAnalysisUrl(e.target.value)}
                    placeholder="https://example.com"
                    disabled={analysisLoading}
                    className="demo-input"
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={analysisLoading || !analysisUrl.trim()}
                  className="demo-btn primary"
                >
                  {analysisLoading ? (
                    <>
                      <span className="spinner"></span>
                      Analyzing...
                    </>
                  ) : (
                    'Analyze Content'
                  )}
                </button>
              </form>

              {/* Task Progress */}
              {analysisTask && !analysisResult && (
                <div className="task-progress">
                  <div className="progress-header">
                    <span>Analyzing Content</span>
                    <span className="task-id">ID: {analysisTask.task_id.slice(0, 8)}...</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill"></div>
                  </div>
                  <div className="progress-steps">
                    <small>Extracting content → AI analysis → Generating insights</small>
                  </div>
                </div>
              )}

              {/* Analysis Results */}
              {analysisResult && (
                <div className="result-panel">
                  <div className="result-header">
                    <span className={`result-status ${analysisResult.status}`}>
                      {analysisResult.status === 'completed' ? '🧠 Analysis Complete' : 'Failed'}
                    </span>
                    {analysisResult.processing_time_seconds && (
                      <span className="processing-time">
                        {analysisResult.processing_time_seconds}s
                      </span>
                    )}
                  </div>
                  
                  <div className="result-content">
                    {/* Page Title */}
                    {analysisResult.title && (
                      <div className="result-item">
                        <label>Page Title:</label>
                        <div className="result-text">{analysisResult.title}</div>
                      </div>
                    )}
                    
                    {/* AI Summary */}
                    {analysisResult.summary && (
                      <div className="result-item">
                        <label>AI Summary:</label>
                        <div className="result-text summary">{analysisResult.summary}</div>
                      </div>
                    )}
                    
                    {/* Main Topics */}
                    {analysisResult.main_topics && analysisResult.main_topics.length > 0 && (
                      <div className="result-item">
                        <label>Main Topics:</label>
                        <div className="topics-container">
                          {analysisResult.main_topics.map((topic, index) => (
                            <span key={index} className="topic-tag">{topic}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Page Purpose */}
                    {analysisResult.page_purpose && (
                      <div className="result-item">
                        <label>Page Purpose:</label>
                        <div className="result-text purpose">{analysisResult.page_purpose}</div>
                      </div>
                    )}
                    
                    {/* Key Information */}
                    {analysisResult.key_information && (
                      <div className="result-item">
                        <label>Key Information:</label>
                        <div className="key-info-container">
                          
                          {/* Key Points */}
                          {analysisResult.key_information.key_points && analysisResult.key_information.key_points.length > 0 && (
                            <div className="key-info-section">
                              <h5>Key Points:</h5>
                              <ul className="key-points-list">
                                {analysisResult.key_information.key_points.slice(0, 5).map((point, index) => (
                                  <li key={index}>
                                    <span className="heading-level">{point.type}</span>
                                    {point.text}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {/* Important Links */}
                          {analysisResult.key_information.important_links && analysisResult.key_information.important_links.length > 0 && (
                            <div className="key-info-section">
                              <h5>Important Links:</h5>
                              <div className="important-links">
                                {analysisResult.key_information.important_links.map((link, index) => (
                                  <span key={index} className="link-tag">{link}</span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Contact Info */}
                          {analysisResult.key_information.has_contact_info && (
                            <div className="key-info-section">
                              <h5>Contact Information Found:</h5>
                              <div className="contact-info">
                                {analysisResult.key_information.contact_info.emails.length > 0 && (
                                  <div>📧 {analysisResult.key_information.contact_info.emails.length} email(s)</div>
                                )}
                                {analysisResult.key_information.contact_info.phones.length > 0 && (
                                  <div>📞 {analysisResult.key_information.contact_info.phones.length} phone(s)</div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {/* Content Metrics */}
                    {analysisResult.content_metrics && (
                      <div className="result-item">
                        <label>Content Metrics:</label>
                        <div className="metrics-container">
                          <div className="metric">
                            <span className="metric-value">{analysisResult.content_metrics.word_count}</span>
                            <span className="metric-label">Words</span>
                          </div>
                          <div className="metric">
                            <span className="metric-value">{analysisResult.content_metrics.heading_count}</span>
                            <span className="metric-label">Headings</span>
                          </div>
                          <div className="metric">
                            <span className="metric-value">{analysisResult.content_metrics.link_count}</span>
                            <span className="metric-label">Links</span>
                          </div>
                          <div className="metric">
                            <span className="metric-value">{analysisResult.content_metrics.image_count}</span>
                            <span className="metric-label">Images</span>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {/* Readability Score */}
                    {analysisResult.readability_score && (
                      <div className="result-item">
                        <label>Readability:</label>
                        <div className="readability-badge">{analysisResult.readability_score}</div>
                      </div>
                    )}
                    
                    {/* Error Display */}
                    {analysisResult.error && (
                      <div className="result-item error">
                        <label>Error:</label>
                        <div className="result-text">{analysisResult.error}</div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          {/* Technical Specification Demo */}
            <div className="demo-card">
              <div className="card-header">
                <h3>🔧 Technical Specification</h3>
                <p>Generate comprehensive rebuild documentation with HTML, CSS, and JavaScript specs</p>
              </div>
              
              <form onSubmit={handleTechSpecSubmit} className="demo-form">
                <div className="input-group">
                  <label>Enter website URL for technical analysis:</label>
                  <input
                    type="text"
                    value={techSpecUrl}
                    onChange={(e) => setTechSpecUrl(e.target.value)}
                    placeholder="https://example.com"
                    disabled={techSpecLoading}
                    className="demo-input"
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={techSpecLoading || !techSpecUrl.trim()}
                  className="demo-btn primary"
                >
                  {techSpecLoading ? (
                    <>
                      <span className="spinner"></span>
                      Generating Spec...
                    </>
                  ) : (
                    'Generate Technical Spec'
                  )}
                </button>
              </form>

              {/* Task Progress */}
              {techSpecTask && !techSpecResult && (
                <div className="task-progress">
                  <div className="progress-header">
                    <span>Generating Technical Specification</span>
                    <span className="task-id">ID: {techSpecTask.task_id.slice(0, 8)}...</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill"></div>
                  </div>
                  <div className="progress-steps">
                    <small>Analyzing structure → Extracting styles → Documenting functionality → Generating guide</small>
                  </div>
                </div>
              )}

              {/* Technical Specification Results */}
              {techSpecResult && (
                <div className="result-panel">
                  <div className="result-header">
                    <span className={`result-status ${techSpecResult.status}`}>
                      {techSpecResult.status === 'completed' ? '🔧 Specification Generated' : 'Failed'}
                    </span>
                    <div className="spec-metadata">
                      {techSpecResult.complexity_level && (
                        <span className="complexity-badge">{techSpecResult.complexity_level}</span>
                      )}
                      {techSpecResult.processing_time_seconds && (
                        <span className="processing-time">
                          {techSpecResult.processing_time_seconds}s
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="result-content">
                    {techSpecResult.specification && (
                      <div className="tech-spec-container">
                        
                        {/* HTML Structure Requirements */}
                        {techSpecResult.specification.html_structure && (
                          <div className="spec-section">
                            <h4 className="spec-title">📄 HTML Structure Requirements</h4>
                            <div className="spec-content">
                              <div className="spec-item">
                                <strong>Document Type:</strong> {techSpecResult.specification.html_structure.document_type}
                              </div>
                              <div className="spec-item">
                                <strong>Language:</strong> {techSpecResult.specification.html_structure.language}
                              </div>
                              <div className="spec-item">
                                <strong>Title:</strong> {techSpecResult.specification.html_structure.title}
                              </div>
                              {techSpecResult.specification.html_structure.semantic_elements && (
                                <div className="spec-item">
                                  <strong>Semantic Elements:</strong>
                                  <div className="tag-list">
                                    {techSpecResult.specification.html_structure.semantic_elements.map((tag, index) => (
                                      <span key={index} className="html-tag">&lt;{tag}&gt;</span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* CSS Requirements */}
                        {techSpecResult.specification.css_requirements && (
                          <div className="spec-section">
                            <h4 className="spec-title">🎨 CSS Styling Requirements</h4>
                            <div className="spec-content">
                              <div className="spec-item">
                                <strong>Layout System:</strong> {techSpecResult.specification.css_requirements.layout_system?.primary}
                              </div>
                              {techSpecResult.specification.css_requirements.color_palette && (
                                <div className="spec-item">
                                  <strong>Color Palette:</strong>
                                  <div className="color-palette">
                                    {techSpecResult.specification.css_requirements.color_palette.background_colors?.slice(0, 6).map((color, index) => (
                                      <div key={index} className="color-swatch" style={{backgroundColor: color}} title={color}></div>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {techSpecResult.specification.css_requirements.responsive_design && (
                                <div className="spec-item">
                                  <strong>Responsive Breakpoints:</strong>
                                  <ul className="breakpoint-list">
                                    {techSpecResult.specification.css_requirements.responsive_design.breakpoints?.map((bp, index) => (
                                      <li key={index}>{bp}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* JavaScript Functionality */}
                        {techSpecResult.specification.javascript_functionality && (
                          <div className="spec-section">
                            <h4 className="spec-title">⚡ JavaScript Functionality</h4>
                            <div className="spec-content">
                              {techSpecResult.specification.javascript_functionality.framework_requirements && (
                                <div className="spec-item">
                                  <strong>Detected Frameworks:</strong>
                                  <div className="framework-list">
                                    {techSpecResult.specification.javascript_functionality.framework_requirements.detected_frameworks?.map((fw, index) => (
                                      <span key={index} className="framework-tag">{fw}</span>
                                    ))}
                                    {techSpecResult.specification.javascript_functionality.framework_requirements.detected_frameworks?.length === 0 && (
                                      <span className="framework-tag">Vanilla JavaScript</span>
                                    )}
                                  </div>
                                </div>
                              )}
                              {techSpecResult.specification.javascript_functionality.form_handling?.length > 0 && (
                                <div className="spec-item">
                                  <strong>Forms Found:</strong> {techSpecResult.specification.javascript_functionality.form_handling.length}
                                  <div className="forms-list">
                                    {techSpecResult.specification.javascript_functionality.form_handling.map((form, index) => (
                                      <div key={index} className="form-spec">
                                        Form {index + 1}: {form.fields?.length || 0} fields ({form.method})
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Implementation Guide */}
                        {techSpecResult.specification.step_by_step_guide && (
                          <div className="spec-section">
                            <h4 className="spec-title">📋 Step-by-Step Implementation Guide</h4>
                            <div className="implementation-guide">
                              {techSpecResult.specification.step_by_step_guide.slice(0, 6).map((step, index) => (
                                <div key={index} className="implementation-step">
                                  <div className="step-header">
                                    <span className="step-number">{step.step}</span>
                                    <h5>{step.title}</h5>
                                  </div>
                                  <p className="step-description">{step.description}</p>
                                  <ul className="task-list">
                                    {step.tasks?.slice(0, 4).map((task, taskIndex) => (
                                      <li key={taskIndex}>{task}</li>
                                    ))}
                                  </ul>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Technical Requirements */}
                        {techSpecResult.specification.technical_requirements && (
                          <div className="spec-section">
                            <h4 className="spec-title">⚙️ Technical Requirements</h4>
                            <div className="spec-content">
                              {techSpecResult.specification.technical_requirements.browser_support && (
                                <div className="spec-item">
                                  <strong>Browser Support:</strong>
                                  <div className="browser-list">
                                    {techSpecResult.specification.technical_requirements.browser_support.map((browser, index) => (
                                      <span key={index} className="browser-tag">{browser}</span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {techSpecResult.specification.technical_requirements.dependencies && (
                                <div className="spec-item">
                                  <strong>Dependencies:</strong>
                                  <div className="dependencies-info">
                                    <span>External Stylesheets: {techSpecResult.specification.technical_requirements.dependencies.external_stylesheets || 0}</span>
                                    <span>External Scripts: {techSpecResult.specification.technical_requirements.dependencies.external_scripts || 0}</span>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Content Specification */}
                        {techSpecResult.specification.content_specification && (
                          <div className="spec-section">
                            <h4 className="spec-title">📝 Content Specification</h4>
                            <div className="spec-content">
                              {techSpecResult.specification.content_specification.content_types && (
                                <div className="spec-item">
                                  <strong>Content Types Found:</strong>
                                  <div className="content-types">
                                    {techSpecResult.specification.content_specification.content_types.map((type, index) => (
                                      <span key={index} className="content-type-tag">{type}</span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {techSpecResult.specification.content_specification.content_guidelines && (
                                <div className="spec-item">
                                  <strong>Content Guidelines:</strong>
                                  <ul className="guidelines-list">
                                    {techSpecResult.specification.content_specification.content_guidelines.slice(0, 3).map((guideline, index) => (
                                      <li key={index}>{guideline}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                      </div>
                    )}
                    
                    {/* Error Display */}
                    {techSpecResult.error && (
                      <div className="result-item error">
                        <label>Error:</label>
                        <div className="result-text">{techSpecResult.error}</div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            {/* Comprehensive Website Generation Demo */}
              <div className="demo-card featured-card">
                <div className="card-header">
                  <h3>🚀 Complete Website Generation</h3>
                  <p>All-in-one: Screenshot + Analysis + Technical Spec + Code Generation</p>
                </div>
                
                <form onSubmit={handleWebsiteGenSubmit} className="demo-form">
                  <div className="input-group">
                    <label>Enter website URL for complete generation:</label>
                    <input
                      type="text"
                      value={websiteGenUrl}
                      onChange={(e) => setWebsiteGenUrl(e.target.value)}
                      placeholder="https://example.com"
                      disabled={websiteGenLoading}
                      className="demo-input"
                    />
                  </div>
                  <button 
                    type="submit" 
                    disabled={websiteGenLoading || !websiteGenUrl.trim()}
                    className="demo-btn primary featured"
                  >
                    {websiteGenLoading ? (
                      <>
                        <span className="spinner"></span>
                        Generating Website...
                      </>
                    ) : (
                      '🚀 Generate Complete Website'
                    )}
                  </button>
                </form>

                {/* Task Progress */}
                {websiteGenTask && !websiteGenResult && (
                  <div className="task-progress featured-progress">
                    <div className="progress-header">
                      <span>🚀 Comprehensive Website Generation</span>
                      <span className="task-id">ID: {websiteGenTask.task_id.slice(0, 8)}...</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill"></div>
                    </div>
                    <div className="progress-steps">
                      <small>📸 Screenshot → 🧠 Content Analysis → 🔧 Technical Spec → 💻 Code Generation</small>
                    </div>
                  </div>
                )}

                {/* Comprehensive Results */}
                {websiteGenResult && (
                  <div className="result-panel featured-result">
                    <div className="result-header">
                      <span className={`result-status ${websiteGenResult.status}`}>
                        {websiteGenResult.status === 'completed' ? '🎉 Complete Website Generated' : 'Failed'}
                      </span>
                      <div className="result-actions">
                        {websiteGenResult.status === 'completed' && (
                          <button 
                            onClick={() => handleDownloadCode(websiteGenResult.task_id)}
                            className="download-btn"
                          >
                            📥 Download Code
                          </button>
                        )}
                        {websiteGenResult.total_processing_time_seconds && (
                          <span className="processing-time">
                            {websiteGenResult.total_processing_time_seconds.toFixed(2)}s total
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="comprehensive-results">
                      
                      {/* Screenshot Section */}
                      {websiteGenResult.screenshot && (
                        <div className="result-section">
                          <h4 className="section-title">📸 Screenshot Capture</h4>
                          <div className="section-content">
                            <div className="screenshot-preview">
                              <img 
                                src={`data:image/png;base64,${websiteGenResult.screenshot.screenshot_data}`}
                                alt="Website screenshot"
                                className="mini-screenshot"
                                title="Click to view full size"
                              />
                              <div className="screenshot-info">
                                <div><strong>Title:</strong> {websiteGenResult.screenshot.page_title}</div>
                                {websiteGenResult.screenshot.replay_url && (
                                  <a href={websiteGenResult.screenshot.replay_url} target="_blank" rel="noopener noreferrer">
                                    🎥 View Session Replay →
                                  </a>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Content Analysis Section */}
                      {websiteGenResult.content_analysis && (
                        <div className="result-section">
                          <h4 className="section-title">🧠 Content Analysis</h4>
                          <div className="section-content">
                            {websiteGenResult.content_analysis.title && (
                              <div className="analysis-item">
                                <strong>Page Title:</strong> {websiteGenResult.content_analysis.title}
                              </div>
                            )}
                            <div className="analysis-item">
                              <strong>Content:</strong> {websiteGenResult.content_analysis.wordCount} words, 
                              {websiteGenResult.content_analysis.headings?.length || 0} headings
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Technical Specification Section */}
                      {websiteGenResult.technical_specification && (
                        <div className="result-section">
                          <h4 className="section-title">🔧 Technical Specification</h4>
                          <div className="section-content">
                            {websiteGenResult.technical_specification.specification && (
                              <div className="tech-summary">
                                <div className="tech-item">
                                  <strong>Complexity:</strong> 
                                  {websiteGenResult.technical_specification.specification.technical_requirements?.dependencies?.estimated_complexity || 'Analyzed'}
                                </div>
                                <div className="tech-item">
                                  <strong>Framework:</strong> 
                                  {websiteGenResult.technical_specification.specification.javascript_functionality?.framework_requirements?.detected_frameworks?.join(', ') || 'Vanilla JS'}
                                </div>
                                <div className="tech-item">
                                  <strong>Layout:</strong> 
                                  {websiteGenResult.technical_specification.specification.css_requirements?.layout_system?.primary || 'Standard'}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Generated Code Section */}
                      {websiteGenResult.generated_code && (
                        <div className="result-section">
                          <h4 className="section-title">💻 Generated Code</h4>
                          <div className="section-content">
                            <div className="code-summary">
                              <div className="code-files">
                                {websiteGenResult.generated_code.files?.map((file, index) => (
                                  <span key={index} className="file-tag">{file}</span>
                                ))}
                              </div>
                              <div className="code-preview">
                                <div className="code-stats">
                                  <div>📄 HTML: {websiteGenResult.generated_code.html?.length || 0} chars</div>
                                  <div>🎨 CSS: {websiteGenResult.generated_code.css?.length || 0} chars</div>
                                  <div>⚡ JS: {websiteGenResult.generated_code.javascript?.length || 0} chars</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {/* Error Display */}
                      {websiteGenResult.error && (
                        <div className="result-item error">
                          <label>Error:</label>
                          <div className="result-text">{websiteGenResult.error}</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
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