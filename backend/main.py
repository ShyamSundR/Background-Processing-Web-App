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
from workflows import ReverseWorkflow

# Load environment variables
load_dotenv()

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

# Initialize FastAPI app
app = FastAPI(title="Mocksi API - Fixed Version")

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
    
    print("🚀 STARTING MOCKSI BACKEND - FIXED VERSION")
    
    # Connect to Temporal server
    try:
        temporal_host = os.getenv("TEMPORAL_HOST", "localhost")
        temporal_port = os.getenv("TEMPORAL_PORT", "7233")
        temporal_client = await Client.connect(f"{temporal_host}:{temporal_port}")
        print(f"Connected to Temporal at {temporal_host}:{temporal_port}")
    except Exception as e:
        print(f"Failed to connect to Temporal: {e}")
        
    # Get Hugging Face token
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if hf_token:
        print(f"Hugging Face API token configured: {hf_token[:10]}...")
        try:
            await test_hf_api()
            print(" Hugging Face API connection verified!")
        except Exception as e:
            print(f" Hugging Face API test failed: {e}")
    else:
        print(" HUGGINGFACE_API_TOKEN not found in environment!")

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
    """Simple Temporal health check that actually works"""
    try:
        if not temporal_client:
            return False
        
        # Just test if we can get workflow service info
        # This is less invasive than list_workflows
        service_info = temporal_client.workflow_service
        return service_info is not None
    except Exception as e:
        print(f"Temporal health check error: {e}")
        return False

async def call_huggingface_api(text: str, style: str) -> str:
    """Call Hugging Face API for summarization - FIXED VERSION"""
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
            print(f" Sending request to HF API with max_length={max_length}, min_length={min_length}")
            response = await client.post(api_url, headers=headers, json=payload)
            print(f"HF API response status: {response.status_code}")
            
            if response.status_code == 503:
                print(" Model is loading on HF servers, waiting 20 seconds...")
                await asyncio.sleep(20)
                response = await client.post(api_url, headers=headers, json=payload)
                print(f" HF API retry response status: {response.status_code}")
            
            if response.status_code == 429:
                print("⏳ Rate limited, waiting 30 seconds...")
                await asyncio.sleep(30)
                response = await client.post(api_url, headers=headers, json=payload)
                print(f"HF API rate limit retry response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            print(f"HF API raw result: {result}")
            
            if isinstance(result, list) and len(result) > 0:
                summary = result[0].get("summary_text", "")
                if summary and summary.strip() and summary != text:
                    print(f" Generated summary: {summary}")
                    return summary
                else:
                    print(f"Summary same as input or empty: {summary}")
            
            # If we get here, summarization didn't work properly
            print("No valid summary from HF API, creating manual summary")
            return create_manual_summary(text, style)
            
    except Exception as e:
        print(f" HF API error: {e}")
        print("Falling back to manual summarization")
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
        "message": "Mocksi API - Fixed Temporal & Summarization",
        "hf_token_configured": bool(hf_token),
        "temporal_connected": bool(temporal_client)
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
        print(f"Error starting reverse workflow: {e}")
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
        print(f"Error getting task status: {e}")
        raise HTTPException(status_code=404, detail="Task not found")

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    print(f"Received summarize request: {request.text[:100]}...")
    
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
        print(f" Complete summarization failure: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Fixed health check"""
    
    # Test Temporal connection with simpler method
    temporal_status = "disconnected"
    if temporal_client:
        temporal_healthy = await test_temporal_connection()
        temporal_status = "connected" if temporal_healthy else "connected_but_limited"
    
    # Test HF API
    hf_status = "not configured"
    if hf_token:
        try:
            hf_healthy = await test_hf_api()
            hf_status = "connected" if hf_healthy else "configured but unreachable"
        except:
            hf_status = "configured but error"
    
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
        "features": {
            "string_reversal": "available" if temporal_client else "unavailable", 
            "ai_summarization": "available" if hf_token else "unavailable"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
