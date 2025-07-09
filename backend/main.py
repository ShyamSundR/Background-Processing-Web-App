from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from temporalio.client import Client
import uuid
import os
from dotenv import load_dotenv
import asyncio
from typing import Optional
import httpx

# Import workflows
from workflows import ReverseWorkflow, ScreenshotWorkflow, ContentAnalysisWorkflow, TechnicalSpecificationWorkflow, WebsiteGenerationWorkflow



# Load environment variables
load_dotenv()

class WebsiteGenerationRequest(BaseModel):
    url: str

class WebsiteGenerationResponse(BaseModel):
    task_id: str
    status: str
    url: str
    screenshot: Optional[dict] = None
    content_analysis: Optional[dict] = None
    technical_specification: Optional[dict] = None
    generated_code: Optional[dict] = None
    total_processing_time_seconds: Optional[float] = None
    error: Optional[str] = None

class TechSpecRequest(BaseModel):
    url: str

class TechSpecResponse(BaseModel):
    task_id: str
    status: str
    url: str
    specification: Optional[dict] = None
    complexity_level: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None

class ContentAnalysisRequest(BaseModel):
    url: str

class ContentAnalysisResponse(BaseModel):
    task_id: str
    status: str
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    main_topics: Optional[list] = None
    page_purpose: Optional[str] = None
    key_information: Optional[dict] = None
    content_metrics: Optional[dict] = None
    readability_score: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None
# Pydantic models
class ReverseRequest(BaseModel):
    text: str

class ReverseResponse(BaseModel):
    task_id: str
    status: str
    original_text: str
    reversed_text: Optional[str] = None
    error: Optional[str] = None

class SummarizeRequest(BaseModel):
    text: str
    style: str = "concise"

class SummarizeResponse(BaseModel):
    original_text: str
    summary_text: str
    style: str

class ScreenshotRequest(BaseModel):
    url: str

class ScreenshotResponse(BaseModel):
    task_id: str
    status: str
    url: str
    page_title: Optional[str] = None
    screenshot_data: Optional[str] = None
    replay_url: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(title="Mocksi API - Complete Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
temporal_client: Optional[Client] = None
hf_token = None
task_results = {}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global temporal_client, hf_token
    
    print("🚀 STARTING MOCKSI BACKEND - COMPLETE VERSION")
    
    # Connect to Temporal server
    try:
        temporal_host = os.getenv("TEMPORAL_HOST", "127.0.0.1")
        temporal_port = os.getenv("TEMPORAL_PORT", "7233")
        temporal_client = await Client.connect(f"{temporal_host}:{temporal_port}")
        print(f"✅ Connected to Temporal at {temporal_host}:{temporal_port}")
    except Exception as e:
        print(f"❌ Failed to connect to Temporal: {e}")
        
    # Get Hugging Face token
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if hf_token:
        print(f"✅ Hugging Face API token configured: {hf_token[:10]}...")
        try:
            await test_hf_api()
            print("✅ Hugging Face API connection verified!")
        except Exception as e:
            print(f"⚠️ Hugging Face API test failed: {e}")
    else:
        print("⚠️ HUGGINGFACE_API_TOKEN not found in environment!")

    # Check Browserbase credentials
    browserbase_key = os.getenv("BROWSERBASE_API_KEY")
    browserbase_project = os.getenv("BROWSERBASE_PROJECT_ID")
    if browserbase_key and browserbase_project:
        print(f"✅ Browserbase credentials configured")
        print(f"   API Key: {browserbase_key[:10]}...")
        print(f"   Project ID: {browserbase_project}")
    else:
        print("⚠️ Browserbase credentials not found - screenshot feature will be limited")

async def test_hf_api():
    """Test Hugging Face API connection"""
    if not hf_token:
        return False
    
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(api_url, headers=headers)
        print(f"🔍 HF API test response: {response.status_code}")
        return response.status_code == 200

async def test_temporal_connection():
    """Simple Temporal health check"""
    try:
        if not temporal_client:
            return False
        
        # Test if we can get workflow service info
        service_info = temporal_client.workflow_service
        return service_info is not None
    except Exception as e:
        print(f"Temporal health check error: {e}")
        return False

async def call_huggingface_api(text: str, style: str) -> str:
    """Call Hugging Face API for summarization"""
    print(f"🤖 Calling Hugging Face API for {style} summary...")
    print(f"📝 Input text (first 100 chars): {text[:100]}...")
    
    if not hf_token:
        raise Exception("Hugging Face API token not configured")
    
    # Make sure text is long enough to summarize
    if len(text.split()) < 20:
        print("⚠️ Text too short for summarization, returning as-is")
        return text
    
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    
    # Better parameters for summarization
    if style == "concise":
        max_length = 50
        min_length = 20
    else:
        max_length = 100
        min_length = 40
    
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_length,
            "min_length": min_length,
            "do_sample": False,
            "early_stopping": True
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  
            print(f"📤 Sending request to HF API with max_length={max_length}, min_length={min_length}")
            response = await client.post(api_url, headers=headers, json=payload)
            print(f"📥 HF API response status: {response.status_code}")
            
            if response.status_code == 503:
                print("⏳ Model is loading on HF servers, waiting 20 seconds...")
                await asyncio.sleep(20)
                response = await client.post(api_url, headers=headers, json=payload)
                print(f"🔄 HF API retry response status: {response.status_code}")
            
            if response.status_code == 429:
                print("⏳ Rate limited, waiting 30 seconds...")
                await asyncio.sleep(30)
                response = await client.post(api_url, headers=headers, json=payload)
                print(f"🔄 HF API rate limit retry response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            print(f"📋 HF API raw result: {result}")
            
            if isinstance(result, list) and len(result) > 0:
                summary = result[0].get("summary_text", "")
                if summary and summary.strip() and summary != text:
                    print(f"✅ Generated summary: {summary}")
                    return summary
                else:
                    print(f"⚠️ Summary same as input or empty: {summary}")
            
            # If we get here, summarization didn't work properly
            print("⚠️ No valid summary from HF API, creating manual summary")
            return create_manual_summary(text, style)
            
    except Exception as e:
        print(f"❌ HF API error: {e}")
        print("🔄 Falling back to manual summarization")
        return create_manual_summary(text, style)

def create_manual_summary(text: str, style: str) -> str:
    """Create a better manual summary when HF API fails"""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) <= 2:
        return text
    
    if style == "concise":
        # Take first sentence and most important middle sentence
        if len(sentences) >= 3:
            summary = f"{sentences[0]}. {sentences[len(sentences)//2]}."
        else:
            summary = f"{sentences[0]}."
    else:
        # Take first, middle, and last sentences
        if len(sentences) >= 3:
            middle_idx = len(sentences) // 2
            summary = f"{sentences[0]}. {sentences[middle_idx]}. {sentences[-1]}."
        else:
            summary = ". ".join(sentences)
    
    return f"[Auto-Summary] {summary}"

@app.get("/")
async def root():
    return {
        "message": "Mocksi API - Complete Version with Screenshots",
        "hf_token_configured": bool(hf_token),
        "temporal_connected": bool(temporal_client),
        "browserbase_configured": bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
    }

@app.post("/reverse", response_model=ReverseResponse)
async def reverse_string(request: ReverseRequest):
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    task_id = str(uuid.uuid4())
    
    try:
        handle = await temporal_client.start_workflow(
            ReverseWorkflow.run,
            request.text,
            id=task_id,
            task_queue="string-processing-queue",
        )
        
        task_results[task_id] = {
            "task_id": task_id,
            "status": "running",
            "original_text": request.text,
            "reversed_text": None,
            "error": None
        }
        
        return ReverseResponse(
            task_id=task_id,
            status="running",
            original_text=request.text
        )
        
    except Exception as e:
        print(f"❌ Error starting reverse workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.get("/reverse/{task_id}", response_model=ReverseResponse)
async def get_reverse_status(task_id: str):
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    try:
        handle = temporal_client.get_workflow_handle(task_id)
        
        try:
            result = await asyncio.wait_for(handle.result(), timeout=0.1)
            return ReverseResponse(
                task_id=task_id,
                status="completed",
                original_text=result["original_text"],
                reversed_text=result["reversed_text"]
            )
        except asyncio.TimeoutError:
            return ReverseResponse(
                task_id=task_id,
                status="running",
                original_text=task_results.get(task_id, {}).get("original_text", "")
            )
            
    except Exception as e:
        print(f"❌ Error getting task status: {e}")
        raise HTTPException(status_code=404, detail="Task not found")

@app.post("/screenshot", response_model=ScreenshotResponse)
async def capture_screenshot(request: ScreenshotRequest):
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    # Check Browserbase credentials
    if not os.getenv("BROWSERBASE_API_KEY") or not os.getenv("BROWSERBASE_PROJECT_ID"):
        raise HTTPException(status_code=503, detail="Browserbase not configured")
    
    task_id = str(uuid.uuid4())
    
    try:
        handle = await temporal_client.start_workflow(
            ScreenshotWorkflow.run,
            request.url,
            id=task_id,
            task_queue="string-processing-queue",
        )
        
        task_results[task_id] = {
            "task_id": task_id,
            "status": "running",
            "url": request.url,
            "screenshot_data": None,
            "error": None
        }
        
        return ScreenshotResponse(
            task_id=task_id,
            status="running",
            url=request.url
        )
        
    except Exception as e:
        print(f"❌ Error starting screenshot workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.get("/screenshot/{task_id}", response_model=ScreenshotResponse)
async def get_screenshot_status(task_id: str):
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    try:
        handle = temporal_client.get_workflow_handle(task_id)
        
        try:
            result = await asyncio.wait_for(handle.result(), timeout=0.1)
            return ScreenshotResponse(
                task_id=task_id,
                status=result["status"],
                url=result["url"],
                page_title=result.get("page_title"),
                screenshot_data=result.get("screenshot_data"),
                replay_url=result.get("replay_url"),
                processing_time_seconds=result.get("processing_time_seconds"),
                error=result.get("error")
            )
        except asyncio.TimeoutError:
            return ScreenshotResponse(
                task_id=task_id,
                status="running",
                url=task_results.get(task_id, {}).get("url", "")
            )
            
    except Exception as e:
        print(f"❌ Error getting screenshot status: {e}")
        raise HTTPException(status_code=404, detail="Task not found")

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    print(f"📝 Received summarize request: {request.text[:100]}...")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Always try HF API first
        summary = await call_huggingface_api(request.text, request.style)
        
        return SummarizeResponse(
            original_text=request.text,
            summary_text=summary,
            style=request.style
        )
        
    except Exception as e:
        print(f"❌ Complete summarization failure: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
    
@app.post("/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(request: ContentAnalysisRequest):
    """Start comprehensive content analysis for a webpage"""
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    # Check dependencies
    if not os.getenv("BROWSERBASE_API_KEY") or not os.getenv("BROWSERBASE_PROJECT_ID"):
        raise HTTPException(status_code=503, detail="Browserbase not configured")
    
    if not os.getenv("HUGGINGFACE_API_TOKEN"):
        raise HTTPException(status_code=503, detail="HuggingFace API not configured")
    
    task_id = str(uuid.uuid4())
    
    try:
        handle = await temporal_client.start_workflow(
            ContentAnalysisWorkflow.run,
            request.url,
            id=task_id,
            task_queue="string-processing-queue",
        )
        
        task_results[task_id] = {
            "task_id": task_id,
            "status": "running",
            "url": request.url,
            "analysis": None,
            "error": None
        }
        
        return ContentAnalysisResponse(
            task_id=task_id,
            status="running",
            url=request.url
        )
        
    except Exception as e:
        print(f"❌ Error starting content analysis workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.get("/analyze/{task_id}", response_model=ContentAnalysisResponse)
async def get_analysis_status(task_id: str):
    """Get the status and results of a content analysis task"""
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    try:
        handle = temporal_client.get_workflow_handle(task_id)
        
        try:
            result = await asyncio.wait_for(handle.result(), timeout=0.1)
            
            if result["status"] == "completed":
                analysis = result.get("analysis", {})
                content = result.get("content_data", {})
                
                return ContentAnalysisResponse(
                    task_id=task_id,
                    status="completed",
                    url=result["url"],
                    title=content.get("title"),
                    summary=analysis.get("summary"),
                    main_topics=analysis.get("main_topics"),
                    page_purpose=analysis.get("page_purpose"),
                    key_information=analysis.get("key_information"),
                    content_metrics=analysis.get("content_metrics"),
                    readability_score=analysis.get("readability_score"),
                    processing_time_seconds=result.get("total_processing_time"),
                    error=result.get("error")
                )
            else:
                return ContentAnalysisResponse(
                    task_id=task_id,
                    status="failed",
                    url=result["url"],
                    error=result.get("error")
                )
                
        except asyncio.TimeoutError:
            return ContentAnalysisResponse(
                task_id=task_id,
                status="running",
                url=task_results.get(task_id, {}).get("url", "")
            )
            
    except Exception as e:
        print(f"❌ Error getting analysis status: {e}")
        raise HTTPException(status_code=404, detail="Task not found")


# Add new API endpoints
@app.post("/tech-spec", response_model=TechSpecResponse)
async def generate_tech_spec(request: TechSpecRequest):
    """Generate comprehensive technical specification for rebuilding a webpage"""
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    # Check dependencies
    if not os.getenv("BROWSERBASE_API_KEY") or not os.getenv("BROWSERBASE_PROJECT_ID"):
        raise HTTPException(status_code=503, detail="Browserbase not configured")
    
    task_id = str(uuid.uuid4())
    
    try:
        handle = await temporal_client.start_workflow(
            TechnicalSpecificationWorkflow.run,
            request.url,
            id=task_id,
            task_queue="string-processing-queue",
        )
        
        task_results[task_id] = {
            "task_id": task_id,
            "status": "running",
            "url": request.url,
            "specification": None,
            "error": None
        }
        
        return TechSpecResponse(
            task_id=task_id,
            status="running",
            url=request.url
        )
        
    except Exception as e:
        print(f"❌ Error starting tech spec workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.get("/tech-spec/{task_id}", response_model=TechSpecResponse)
async def get_tech_spec_status(task_id: str):
    """Get the status and results of a technical specification task"""
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    try:
        handle = temporal_client.get_workflow_handle(task_id)
        
        try:
            result = await asyncio.wait_for(handle.result(), timeout=0.1)
            
            if result["status"] == "completed":
                tech_spec = result.get("technical_specification", {})
                specification = tech_spec.get("specification", {})
                
                # Extract complexity level
                complexity = (specification.get("technical_requirements", {})
                            .get("dependencies", {})
                            .get("estimated_complexity", "Unknown"))
                
                return TechSpecResponse(
                    task_id=task_id,
                    status="completed",
                    url=result["url"],
                    specification=specification,
                    complexity_level=complexity,
                    processing_time_seconds=tech_spec.get("processing_time_seconds"),
                    error=result.get("error")
                )
            else:
                return TechSpecResponse(
                    task_id=task_id,
                    status="failed",
                    url=result["url"],
                    error=result.get("error")
                )
                
        except asyncio.TimeoutError:
            return TechSpecResponse(
                task_id=task_id,
                status="running",
                url=task_results.get(task_id, {}).get("url", "")
            )
            
    except Exception as e:
        print(f"❌ Error getting tech spec status: {e}")
        raise HTTPException(status_code=404, detail="Task not found")

@app.post("/generate-website", response_model=WebsiteGenerationResponse)
async def generate_website(request: WebsiteGenerationRequest):
    """
    Comprehensive website generation - combines all steps:
    1. Screenshot capture
    2. Content analysis 
    3. Technical specification
    4. Frontend code generation
    """
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    # Check all required dependencies
    missing_deps = []
    if not os.getenv("BROWSERBASE_API_KEY"):
        missing_deps.append("BROWSERBASE_API_KEY")
    if not os.getenv("BROWSERBASE_PROJECT_ID"):
        missing_deps.append("BROWSERBASE_PROJECT_ID")
    if not os.getenv("HUGGINGFACE_API_TOKEN"):
        missing_deps.append("HUGGINGFACE_API_TOKEN")
    
    if missing_deps:
        raise HTTPException(
            status_code=503, 
            detail=f"Missing required environment variables: {', '.join(missing_deps)}"
        )
    
    task_id = str(uuid.uuid4())
    
    try:
        handle = await temporal_client.start_workflow(
            WebsiteGenerationWorkflow.run,
            request.url,
            id=task_id,
            task_queue="string-processing-queue",
        )
        
        task_results[task_id] = {
            "task_id": task_id,
            "status": "running",
            "url": request.url,
            "result": None,
            "error": None
        }
        
        return WebsiteGenerationResponse(
            task_id=task_id,
            status="running",
            url=request.url
        )
        
    except Exception as e:
        print(f"❌ Error starting website generation workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.get("/generate-website/{task_id}", response_model=WebsiteGenerationResponse)
async def get_website_generation_status(task_id: str):
    """Get the status and results of a comprehensive website generation task"""
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    try:
        handle = temporal_client.get_workflow_handle(task_id)
        
        try:
            result = await asyncio.wait_for(handle.result(), timeout=0.1)
            
            if result["status"] == "completed":
                return WebsiteGenerationResponse(
                    task_id=task_id,
                    status="completed",
                    url=result["url"],
                    screenshot=result.get("screenshot"),
                    content_analysis=result.get("content_analysis"),
                    technical_specification=result.get("technical_specification"),
                    generated_code=result.get("generated_code"),
                    total_processing_time_seconds=result.get("total_processing_time_seconds"),
                    error=result.get("error")
                )
            else:
                return WebsiteGenerationResponse(
                    task_id=task_id,
                    status="failed",
                    url=result["url"],
                    error=result.get("error")
                )
                
        except asyncio.TimeoutError:
            return WebsiteGenerationResponse(
                task_id=task_id,
                status="running",
                url=task_results.get(task_id, {}).get("url", "")
            )
            
    except Exception as e:
        print(f"❌ Error getting website generation status: {e}")
        raise HTTPException(status_code=404, detail="Task not found")

# ADD A UTILITY ENDPOINT FOR DOWNLOADING GENERATED CODE:

@app.get("/download-code/{task_id}")
async def download_generated_code(task_id: str):
    """Download the generated HTML, CSS, and JavaScript files as a ZIP"""
    if not temporal_client:
        raise HTTPException(status_code=503, detail="Temporal service unavailable")
    
    try:
        handle = temporal_client.get_workflow_handle(task_id)
        result = await asyncio.wait_for(handle.result(), timeout=0.1)
        
        if result["status"] != "completed":
            raise HTTPException(status_code=400, detail="Task not completed yet")
        
        generated_code = result.get("generated_code")
        if not generated_code:
            raise HTTPException(status_code=404, detail="No generated code found")
        
        # Return the code as JSON for now (frontend can handle file creation)
        return {
            "files": {
                "index.html": generated_code.get("html", ""),
                "styles.css": generated_code.get("css", ""),
                "script.js": generated_code.get("javascript", "")
            },
            "url": result["url"],
            "timestamp": result.get("total_processing_time_seconds")
        }
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=400, detail="Task still running")
    except Exception as e:
        print(f"❌ Error downloading code: {e}")
        raise HTTPException(status_code=404, detail="Task not found or failed")


@app.get("/health")
async def health_check():
    """Complete health check for all services"""
    
    # Test Temporal connection
    temporal_status = "disconnected"
    if temporal_client:
        temporal_healthy = await test_temporal_connection()
        temporal_status = "connected" if temporal_healthy else "error"
    
    # Test HF API
    hf_status = "not configured"
    if hf_token:
        try:
            hf_healthy = await test_hf_api()
            hf_status = "connected" if hf_healthy else "configured but unreachable"
        except:
            hf_status = "configured but error"
    
    # Test Browserbase config
    browserbase_status = "not configured"
    if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"):
        browserbase_status = "configured"
    
    content_analysis_status = "unavailable"
    if temporal_client and os.getenv("BROWSERBASE_API_KEY") and os.getenv("HUGGINGFACE_API_TOKEN"):
        content_analysis_status = "available"
    elif not temporal_client:
        content_analysis_status = "temporal unavailable"
    elif not os.getenv("BROWSERBASE_API_KEY"):
        content_analysis_status = "browserbase not configured"
    elif not os.getenv("HUGGINGFACE_API_TOKEN"):
        content_analysis_status = "huggingface not configured"
    tech_spec_status = "unavailable"
    if temporal_client and os.getenv("BROWSERBASE_API_KEY"):
        tech_spec_status = "available"
    elif not temporal_client:
        tech_spec_status = "temporal unavailable"
    elif not os.getenv("BROWSERBASE_API_KEY"):
        tech_spec_status = "browserbase not configured"
    
    return {
        "app": "healthy",
        "temporal": {
            "status": temporal_status,
            "host": os.getenv("TEMPORAL_HOST", "localhost"),
            "port": os.getenv("TEMPORAL_PORT", "7233")
        },
        "huggingface": {
            "status": hf_status,
            "model": "facebook/bart-large-cnn",
            "token_configured": bool(hf_token)
        },
        "browserbase": {
            "status": browserbase_status,
            "api_key_configured": bool(os.getenv("BROWSERBASE_API_KEY")),
            "project_id_configured": bool(os.getenv("BROWSERBASE_PROJECT_ID"))
        },
        "features": {
            "string_reversal": "available" if temporal_client else "unavailable", 
            "ai_summarization": "available" if hf_token else "unavailable",
            "screenshot_capture": "available" if (temporal_client and os.getenv("BROWSERBASE_API_KEY")) else "unavailable",
            "content_analysis": content_analysis_status,
            "technical_specification": tech_spec_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)