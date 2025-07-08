Mocksi 

Hey there! This is my submission for the Mocksi background processing assignment. I built a web app that reverses strings using Temporal workflows and summarizes text with Hugging Face's AI models.
What it does

Type in some text → it gets reversed in the background using Temporal
Paste longer text → it gets summarized by AI
Everything runs locally with Docker
Real-time updates so you can watch it work

The whole thing is styled to look like Mocksi's actual website (dark theme, clean design, etc.).
Quick start
First, you'll need Docker running on your machine. Then:
bashgit clone <this-repo>
cd mocksi

# Copy the env file and add your Hugging Face token
cp .env.example .env
Edit .env and add your Hugging Face API token:
HUGGINGFACE_API_TOKEN=hf_your_token_here
Don't have a token? Get one free at huggingface.co/settings/tokens - just sign up and create a "Read" token.
Then spin everything up:
bashdocker-compose up --build
Give it a couple minutes to start (the AI models need to load), then check out:

Main app: http://localhost:3000
API docs: http://localhost:8000/docs
Temporal dashboard: http://localhost:8080

How I built this
Backend (FastAPI):

Two main endpoints: /reverse for string workflows and /summarize for AI
Connects to Temporal for background job processing
Uses Hugging Face API for the text summarization (no local model downloads)
Proper error handling and health checks

Frontend (React):

Clean interface matching Mocksi's website design
Real-time polling to show workflow progress
Service status indicators so you know what's working
Mobile-friendly responsive design

Temporal Setup:

One workflow: ReverseWorkflow that handles string reversal
Background worker processes the jobs
All running in Docker containers with PostgreSQL

Architecture:
React Frontend (port 3000)
    |
FastAPI Backend (port 8000)
    |
Temporal Worker ← → Temporal Server (port 7233)
    |
PostgreSQL Database
Plus the Hugging Face API calls for AI features.




API_KEY = "bb_live_QjT9KXxOoxwUnQvnKhwdrC_4zTc"
PROJECT_ID = "10a92df2-2269-40f1-9260-6b88cda2bcc0"