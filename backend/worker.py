# Temporal worker process for executing workflows and activities
# Worker setup pattern adapted from: https://github.com/temporalio/samples-python/blob/main/hello/run_worker.py
# Configuration patterns from Temporal Python documentation

import asyncio
import os
import signal
import sys
from temporalio.client import Client
from temporalio.worker import Worker
from dotenv import load_dotenv

# Import workflows and activities
from workflows import (
    ReverseWorkflow, 
    ScreenshotWorkflow,
    reverse_string_activity, 
    log_processing_activity, 
    capture_screenshot_activity
)

# Load environment variables
load_dotenv()

class WorkerManager:
    """
    Manages the Temporal worker lifecycle
    
    Encapsulates worker setup, graceful shutdown, and error handling
    Pattern adapted from production Temporal worker examples
    """
    
    def __init__(self):
        self.worker = None
        self.client = None
        self.shutdown_event = asyncio.Event()
    
    async def setup_client(self):
        """Establish connection to Temporal server"""
        temporal_host = os.getenv("TEMPORAL_HOST", "localhost")
        temporal_port = os.getenv("TEMPORAL_PORT", "7233")
        temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
        
        connection_string = f"{temporal_host}:{temporal_port}"
        
        print(f"🔗 Connecting to Temporal server at {connection_string}")
        print(f"📦 Using namespace: {temporal_namespace}")
        
        try:
            # Connect to Temporal server
            # Connection pattern from Temporal client documentation
            self.client = await Client.connect(
                connection_string,
                namespace=temporal_namespace
            )
            print("✅ Successfully connected to Temporal server")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Temporal server: {e}")
            print("   Make sure Temporal server is running (docker-compose up temporal)")
            return False
    
    async def setup_worker(self):
        """Configure and create the Temporal worker"""
        if not self.client:
            raise Exception("Client not initialized. Call setup_client() first.")
        
        # Define task queue name consistently
        task_queue = "string-processing-queue"
        
        # Create worker with workflows and activities
        self.worker = Worker(
            self.client,
            task_queue=task_queue,
            workflows=[ReverseWorkflow, ScreenshotWorkflow],
            activities=[reverse_string_activity, log_processing_activity, capture_screenshot_activity],
            max_concurrent_activities=10
        )
        
        print("🔧 Worker configured with:")
        print(f"   - Task Queue: {task_queue}")
        print("   - Workflows: ReverseWorkflow, ScreenshotWorkflow")
        print("   - Activities: reverse_string_activity, log_processing_activity, capture_screenshot_activity")
        print("   - Max Concurrent Activities: 10")
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers for SIGINT and SIGTERM"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()
        
        # Handle Ctrl+C and docker stop
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main worker execution loop with graceful shutdown"""
        print("✅ Starting Temporal worker...")
        print("🎯 Press Ctrl+C to stop gracefully")
        print("🚀 Worker is ready to process workflows.")
        print("-" * 50)
        
        try:
            # Start the worker (this will block)
            await self.worker.run()
        except asyncio.CancelledError:
            print("Worker stopped gracefully")
        except Exception as e:
            print(f"❌ Worker error: {e}")
            raise
    
    async def start(self):
        """Complete worker startup sequence"""
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Connect to Temporal
        if not await self.setup_client():
            sys.exit(1)
        
        # Setup worker
        await self.setup_worker()
        
        # Create shutdown task
        shutdown_task = asyncio.create_task(self.wait_for_shutdown())
        worker_task = asyncio.create_task(self.run())
        
        # Wait for either shutdown signal or worker completion
        done, pending = await asyncio.wait(
            [shutdown_task, worker_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel any remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self.shutdown_event.wait()
        print("Shutdown signal received, stopping worker...")

async def main():
    """
    Main entry point for the worker process
    
    Handles worker lifecycle management and error handling
    """
    print("=" * 60)
    print("🏭 MOCKSI TEMPORAL WORKER")
    print("=" * 60)
    
    # Create and start worker manager
    worker_manager = WorkerManager()
    
    try:
        await worker_manager.start()
    except KeyboardInterrupt:
        print("\n✋ Worker interrupted by user")
    except Exception as e:
        print(f"❌ Fatal worker error: {e}")
        sys.exit(1)
    
    print("👋 Worker shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Failed to start worker: {e}")
        sys.exit(1)