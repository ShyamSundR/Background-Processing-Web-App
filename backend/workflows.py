# Temporal workflows for string processing and screenshots
# Workflow patterns adapted from: https://github.com/temporalio/samples-python/tree/main/hello
# Activity patterns from: https://docs.temporal.io/python/activities
# Browserbase pattern from interviewer's requirements

from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from datetime import timedelta
import asyncio
import time
import os
import base64
from typing import Optional

class StringProcessingError(Exception):
    """Custom exception for string processing errors"""
    pass

@activity.defn
async def reverse_string_activity(text: str) -> dict:
    """
    Activity to reverse a string with proper Unicode handling
    
    Args:
        text: The string to be reversed
        
    Returns:
        dict: Result containing original text, reversed text, and metadata
        
    Raises:
        StringProcessingError: If the input is invalid or processing fails
    """
    # Start timing
    start_time = time.time()
    
    # Input validation with detailed logging
    print(f"[REVERSE] Received input text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    print(f"[REVERSE] Input text length: {len(text)} characters")
    
    if text is None:
        print("[REVERSE] Error: Input text is None")
        raise StringProcessingError("Input text cannot be None")
    
    if not isinstance(text, str):
        print(f"[REVERSE] Error: Input is not a string, got {type(text)}")
        raise StringProcessingError("Input must be a string")
    
    if not text.strip():
        print("[REVERSE] Error: Input text is empty or whitespace")
        raise StringProcessingError("Input text cannot be empty or whitespace only")
    
    # Check reasonable length limit (e.g., 1MB of text)
    text_bytes = text.encode('utf-8')
    text_size = len(text_bytes)
    print(f"[REVERSE] Input text size: {text_size} bytes")
    
    if text_size > 1_048_576:  # 1MB limit
        print(f"[REVERSE] Error: Input text too large ({text_size} bytes)")
        raise StringProcessingError("Input text is too large (max 1MB)")
    
    try:
        # Convert string to list of characters (properly handling Unicode)
        chars = list(text)
        print(f"[REVERSE] Split into {len(chars)} characters")
        
        # Reverse the list
        chars.reverse()
        
        # Join back to string
        reversed_text = ''.join(chars)
        print(f"[REVERSE] Reversed text length: {len(reversed_text)} characters")
        print(f"[REVERSE] First 50 chars of reversed text: '{reversed_text[:50]}{'...' if len(reversed_text) > 50 else ''}'")
        
        # Verify the reversal
        if len(text) != len(reversed_text):
            print("[REVERSE] Error: Length mismatch after reversal!")
            raise StringProcessingError("Length mismatch after reversal")
        
        # Calculate actual processing time
        processing_time = time.time() - start_time
        
        # Simulate some minimal processing time for demo purposes
        if processing_time < 0.1:  # If processed too quickly
            await asyncio.sleep(0.1 - processing_time)
            processing_time = 0.1
        
        result = {
            "original_text": text,
            "reversed_text": reversed_text,
            "processing_time_seconds": round(processing_time, 3),
            "original_length": len(text),
            "reversed_length": len(reversed_text)
        }
        
        print(f"[REVERSE] Processing completed in {result['processing_time_seconds']} seconds")
        return result
        
    except Exception as e:
        error_msg = f"Failed to reverse string: {str(e)}"
        print(f"[REVERSE] Error: {error_msg}")
        raise StringProcessingError(error_msg)

@activity.defn
async def capture_screenshot_activity(url: str) -> dict:
    """
    Activity to capture screenshot using Browserbase + Playwright (ASYNC VERSION)
    
    Following the interviewer's exact pattern but adapted for async Temporal activities:
    
    from playwright.sync_api import Playwright, sync_playwright
    from browserbase import Browserbase
    import os

    bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

    def run(playwright: Playwright) -> None:
        # Create a session on Browserbase
        session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
        # Connect to the remote session
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]
        try:
            # Execute Playwright actions on the remote browser tab
            page.goto("https://news.ycombinator.com/")
            page_title = page.title()
            print(f"Page title: {page_title}")
            page.screenshot(path="screenshot.png")
        finally:
            page.close()
            browser.close()
        print(f"Done! View replay at https://browserbase.com/sessions/{session.id}")

    if __name__ == "__main__":
        with sync_playwright() as playwright:
            run(playwright)
    
    Args:
        url: The website URL to capture
        
    Returns:
        dict: Result containing screenshot data and metadata
        
    Raises:
        ValueError: If the input is invalid or capture fails
    """
    start_time = time.time()
    
    print(f"[SCREENSHOT] Starting capture for URL: {url}")
    
    # Validate URL
    if not url or not url.strip():
        print("[SCREENSHOT] Error: URL cannot be empty")
        raise ValueError("URL cannot be empty")
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"[SCREENSHOT] Added protocol: {url}")
    
    # Get API credentials (following interviewer's pattern)
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        print("[SCREENSHOT] Error: Browserbase credentials not configured")
        raise ValueError("Browserbase credentials not configured")
    
    try:
        # Import async versions (adapted from interviewer's sync pattern)
        from playwright.async_api import async_playwright
        from browserbase import Browserbase
        
        print("[SCREENSHOT] ✅ Async Playwright and Browserbase imports successful")
        
        # Following interviewer's pattern: bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
        bb = Browserbase(api_key=api_key)
        
        # Async version of interviewer's run function
        async def run_async_playwright():
            print(f"[SCREENSHOT] Creating Browserbase session...")
            # Following interviewer's pattern: session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
            session = bb.sessions.create(project_id=project_id)
            print(f"[SCREENSHOT] Session created: {session.id}")
            
            async with async_playwright() as playwright:
                # Following interviewer's pattern: chromium = playwright.chromium
                chromium = playwright.chromium
                # Following interviewer's pattern: browser = chromium.connect_over_cdp(session.connect_url)
                browser = await chromium.connect_over_cdp(session.connect_url)
                # Following interviewer's pattern: context = browser.contexts[0]
                context = browser.contexts[0]
                # Following interviewer's pattern: page = context.pages[0]
                page = context.pages[0]
                
                try:
                    print(f"[SCREENSHOT] Navigating to {url}")
                    # Following interviewer's pattern: page.goto("https://news.ycombinator.com/")
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    
                    # Following interviewer's pattern: page_title = page.title()
                    page_title = await page.title()
                    # Following interviewer's pattern: print(f"Page title: {page_title}")
                    print(f"[SCREENSHOT] Page title: {page_title}")
                    
                    # Following interviewer's pattern: page.screenshot(path="screenshot.png")
                    # But capturing bytes instead of saving to file
                    print("[SCREENSHOT] Taking screenshot...")
                    screenshot_bytes = await page.screenshot(full_page=True)
                    print(f"[SCREENSHOT] Screenshot captured: {len(screenshot_bytes)} bytes")
                    
                    # Convert to base64 for JSON response
                    screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
                    print(f"[SCREENSHOT] Base64 encoded: {len(screenshot_b64)} characters")
                    
                    result = {
                        "url": url,
                        "page_title": page_title,
                        "screenshot_data": screenshot_b64,
                        "session_id": session.id,
                        # Following interviewer's pattern: print(f"Done! View replay at https://browserbase.com/sessions/{session.id}")
                        "replay_url": f"https://browserbase.com/sessions/{session.id}"
                    }
                    
                    return result
                    
                finally:
                    print("[SCREENSHOT] Cleaning up browser session...")
                    # Following interviewer's pattern: page.close(); browser.close()
                    await page.close()
                    await browser.close()
        
        # Execute async playwright (adapted from interviewer's sync pattern)
        result = await run_async_playwright()
        
        processing_time = time.time() - start_time
        result["processing_time_seconds"] = round(processing_time, 3)
        
        # Following interviewer's pattern: print(f"Done! View replay at https://browserbase.com/sessions/{session.id}")
        print(f"[SCREENSHOT] Done! View replay at {result['replay_url']}")
        print(f"[SCREENSHOT] Completed in {processing_time:.3f}s")
        return result
        
    except ImportError as e:
        error_msg = f"Screenshot dependencies not installed: {str(e)}"
        print(f"[SCREENSHOT] Import Error: {error_msg}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Screenshot capture failed: {str(e)}"
        print(f"[SCREENSHOT] Error: {error_msg}")
        raise ValueError(error_msg)

@activity.defn
async def log_processing_activity(message: str, task_id: str) -> None:
    """
    Activity for logging workflow progress
    
    Useful for debugging and monitoring workflow execution
    """
    print(f"[WORKFLOW {task_id}] {message}")

@workflow.defn
class ReverseWorkflow:
    """
    Temporal workflow for string reversal with logging and error handling
    
    Workflow structure adapted from Temporal Python samples with enhanced error handling
    and proper activity failure management.
    """
    
    @workflow.run
    async def run(self, input_text: str) -> dict:
        """
        Main workflow execution method
        
        Args:
            input_text: The string to be reversed
            
        Returns:
            dict: Result containing original text, reversed text, and metadata
            
        The workflow handles various failure scenarios and provides detailed error information
        """
        workflow_id = workflow.info().workflow_id
        
        try:
            # Input validation at workflow level
            if not isinstance(input_text, str):
                raise ValueError(f"Expected string input, got {type(input_text)}")
            
            if not input_text.strip():
                raise ValueError("Input text cannot be empty")
            
            # Log workflow start with input details
            log_message = f"Starting string reversal - Input length: {len(input_text)} chars, First 50 chars: '{input_text[:50]}{'...' if len(input_text) > 50 else ''}'"
            await workflow.execute_activity(
                log_processing_activity,
                args=(log_message, workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Execute the main reversal activity with retry policy
            try:
                result = await workflow.execute_activity(
                    reverse_string_activity,
                    args=(input_text,),
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=10),
                        maximum_attempts=3,
                        non_retryable_error_types=["StringProcessingError", "ValueError", "TypeError"]
                    )
                )
                
                # Validate result
                if not result.get("reversed_text"):
                    raise ValueError("Reversal produced empty result")
                
                if len(result["original_text"]) != len(result["reversed_text"]):
                    raise ValueError(f"Length mismatch: original={len(result['original_text'])}, reversed={len(result['reversed_text'])}")
                
                # Log successful completion with details
                completion_message = (
                    f"Workflow completed - Original length: {len(result['original_text'])} chars, "
                    f"Reversed length: {len(result['reversed_text'])} chars, "
                    f"Processing time: {result['processing_time_seconds']}s"
                )
                await workflow.execute_activity(
                    log_processing_activity,
                    args=(completion_message, workflow_id),
                    start_to_close_timeout=timedelta(seconds=10)
                )
                
                # Return comprehensive result
                return {
                    "original_text": result["original_text"],
                    "reversed_text": result["reversed_text"],
                    "processing_time_seconds": result["processing_time_seconds"],
                    "original_length": len(result["original_text"]),
                    "reversed_length": len(result["reversed_text"]),
                    "workflow_id": workflow_id,
                    "status": "completed"
                }
                
            except Exception as e:
                error_msg = f"String reversal failed: {str(e)}"
                # Log activity failure with details
                await workflow.execute_activity(
                    log_processing_activity,
                    args=(error_msg, workflow_id),
                    start_to_close_timeout=timedelta(seconds=10)
                )
                
                # Return error result
                return {
                    "original_text": input_text,
                    "reversed_text": None,
                    "error": error_msg,
                    "workflow_id": workflow_id,
                    "status": "failed"
                }
                
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            # Handle workflow-level failures
            return {
                "original_text": input_text,
                "reversed_text": None,
                "error": error_msg,
                "workflow_id": workflow_id,
                "status": "failed"
            }

@activity.defn
async def capture_screenshot_activity(url: str) -> dict:
    """
    Activity to capture screenshot using CORRECT Browserbase REST API + Playwright
    
    Fixed API endpoint and headers based on official Browserbase documentation:
    - Correct URL: https://api.browserbase.com/v1/sessions (not www.browserbase.com)
    - Correct header: X-BB-API-Key (not Authorization: Bearer)
    """
    start_time = time.time()
    
    print(f"[SCREENSHOT] Starting capture for URL: {url}")
    
    # Validate URL
    if not url or not url.strip():
        print("[SCREENSHOT] Error: URL cannot be empty")
        raise ValueError("URL cannot be empty")
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"[SCREENSHOT] Added protocol: {url}")
    
    # Get API credentials
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        print("[SCREENSHOT] Error: Browserbase credentials not configured")
        raise ValueError("Browserbase credentials not configured")
    
    try:
        from playwright.async_api import async_playwright
        import httpx
        
        print("[SCREENSHOT] ✅ Using CORRECT Browserbase REST API")
        
        # Step 1: Create session via CORRECT REST API endpoint
        print(f"[SCREENSHOT] Creating session via correct API endpoint...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # FIXED: Correct API endpoint and headers from official docs
            session_response = await client.post(
                "https://api.browserbase.com/v1/sessions",  # FIXED: api.browserbase.com not www.browserbase.com
                headers={
                    "X-BB-API-Key": api_key,  # FIXED: X-BB-API-Key not Authorization: Bearer
                    "Content-Type": "application/json"
                },
                json={
                    "projectId": project_id
                }
            )
            
            print(f"[SCREENSHOT] Session API response: {session_response.status_code}")
            
            if session_response.status_code == 429:
                print("[SCREENSHOT] Rate limited - waiting 60 seconds...")
                import asyncio
                await asyncio.sleep(60)
                
                # Retry after rate limit
                session_response = await client.post(
                    "https://api.browserbase.com/v1/sessions",
                    headers={
                        "X-BB-API-Key": api_key,
                        "Content-Type": "application/json"
                    },
                    json={"projectId": project_id}
                )
                print(f"[SCREENSHOT] Retry response: {session_response.status_code}")
            
            # Check for specific error codes
            if session_response.status_code == 401:
                print("[SCREENSHOT] 401 Unauthorized - Check your API key")
                raise ValueError("Invalid Browserbase API key")
            elif session_response.status_code == 403:
                print("[SCREENSHOT] 403 Forbidden - Check your project ID and permissions")
                raise ValueError("Invalid project ID or insufficient permissions")
            elif session_response.status_code not in [200, 201]:
                error_text = session_response.text
                print(f"[SCREENSHOT] API Error {session_response.status_code}: {error_text}")
                raise ValueError(f"Browserbase API error: {session_response.status_code} - {error_text}")
            
            session_data = session_response.json()
            
            print(f"[SCREENSHOT] ✅ Session created successfully!")
            print(f"[SCREENSHOT] Session ID: {session_data['id']}")
            
            connect_url = session_data["connectUrl"]
            session_id = session_data["id"]
            
            print(f"[SCREENSHOT] Connect URL: {connect_url[:50]}...")
        
        # Step 2: Use Playwright with the session (following interviewer's exact pattern)
        async with async_playwright() as playwright:
            print(f"[SCREENSHOT] Connecting to browserbase session...")
            
            # Following interviewer's pattern: chromium = playwright.chromium
            chromium = playwright.chromium
            # Following interviewer's pattern: browser = chromium.connect_over_cdp(session.connect_url)
            browser = await chromium.connect_over_cdp(connect_url)
            # Following interviewer's pattern: context = browser.contexts[0]
            context = browser.contexts[0]
            # Following interviewer's pattern: page = context.pages[0]
            page = context.pages[0]
            
            try:
                print(f"[SCREENSHOT] Navigating to {url}")
                # Following interviewer's pattern: page.goto("https://news.ycombinator.com/")
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Following interviewer's pattern: page_title = page.title()
                page_title = await page.title()
                # Following interviewer's pattern: print(f"Page title: {page_title}")
                print(f"[SCREENSHOT] Page title: {page_title}")
                
                # Following interviewer's pattern: page.screenshot(path="screenshot.png")
                # But capturing bytes instead of saving to file
                print("[SCREENSHOT] Taking screenshot...")
                screenshot_bytes = await page.screenshot(full_page=True)
                print(f"[SCREENSHOT] Screenshot captured: {len(screenshot_bytes)} bytes")
                
                # Convert to base64 for JSON response
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
                print(f"[SCREENSHOT] Base64 encoded: {len(screenshot_b64)} characters")
                
                result = {
                    "url": url,
                    "page_title": page_title,
                    "screenshot_data": screenshot_b64,
                    "session_id": session_id,
                    # Following interviewer's pattern: print(f"Done! View replay at https://browserbase.com/sessions/{session.id}")
                    "replay_url": f"https://browserbase.com/sessions/{session_id}"
                }
                
                processing_time = time.time() - start_time
                result["processing_time_seconds"] = round(processing_time, 3)
                
                # Following interviewer's pattern: print(f"Done! View replay at https://browserbase.com/sessions/{session.id}")
                print(f"[SCREENSHOT] Done! View replay at {result['replay_url']}")
                print(f"[SCREENSHOT] Completed in {processing_time:.3f}s")
                return result
                
            finally:
                print("[SCREENSHOT] Cleaning up browser session...")
                # Following interviewer's pattern: page.close(); browser.close()
                await page.close()
                await browser.close()
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            error_msg = "Rate limited by Browserbase - please wait before trying again"
        elif e.response.status_code == 401:
            error_msg = "Invalid Browserbase API key - please check your credentials"
        elif e.response.status_code == 403:
            error_msg = "Invalid project ID or insufficient permissions"
        else:
            error_msg = f"Browserbase API error: {e.response.status_code} - {e.response.text}"
        print(f"[SCREENSHOT] API Error: {error_msg}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Screenshot capture failed: {str(e)}"
        print(f"[SCREENSHOT] Error: {error_msg}")
        raise ValueError(error_msg)
    
@workflow.defn
class ScreenshotWorkflow:
    """
    Temporal workflow for website screenshot capture
    
    Handles browser automation using Browserbase + Playwright with comprehensive error handling
    Following the interviewer's exact requirements and patterns
    """
    
    @workflow.run
    async def run(self, url: str) -> dict:
        """
        Main workflow execution method for screenshot capture
        
        Args:
            url: The website URL to capture
            
        Returns:
            dict: Result containing screenshot data and metadata
        """
        workflow_id = workflow.info().workflow_id
        
        try:
            # Input validation at workflow level
            if not isinstance(url, str):
                raise ValueError(f"Expected string URL, got {type(url)}")
            
            if not url.strip():
                raise ValueError("URL cannot be empty")
            
            # Log workflow start
            await workflow.execute_activity(
                log_processing_activity,
                args=(f"Starting screenshot capture for: {url}", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Execute the main screenshot activity with retry policy
            try:
                result = await workflow.execute_activity(
                    capture_screenshot_activity,
                    args=(url,),
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=2),
                        maximum_interval=timedelta(seconds=20),
                        maximum_attempts=3,
                        non_retryable_error_types=["ValueError", "TypeError"]
                    )
                )
                
                # Validate result
                if not result.get("screenshot_data"):
                    raise ValueError("Screenshot capture produced no data")
                
                # Log successful completion
                await workflow.execute_activity(
                    log_processing_activity,
                    args=(f"Screenshot captured successfully: {result['page_title']}", workflow_id),
                    start_to_close_timeout=timedelta(seconds=10)
                )
                
                # Return comprehensive result
                return {
                    "url": result["url"],
                    "page_title": result["page_title"],
                    "screenshot_data": result["screenshot_data"],
                    "session_id": result["session_id"],
                    "replay_url": result["replay_url"],
                    "processing_time_seconds": result["processing_time_seconds"],
                    "workflow_id": workflow_id,
                    "status": "completed"
                }
                
            except Exception as e:
                error_msg = f"Screenshot capture failed: {str(e)}"
                # Log activity failure
                await workflow.execute_activity(
                    log_processing_activity,
                    args=(error_msg, workflow_id),
                    start_to_close_timeout=timedelta(seconds=10)
                )
                
                # Return error result
                return {
                    "url": url,
                    "page_title": None,
                    "screenshot_data": None,
                    "error": error_msg,
                    "workflow_id": workflow_id,
                    "status": "failed"
                }
                
        except Exception as e:
            error_msg = f"Screenshot workflow failed: {str(e)}"
            # Handle workflow-level failures
            return {
                "url": url,
                "page_title": None,
                "screenshot_data": None,
                "error": error_msg,
                "workflow_id": workflow_id,
                "status": "failed"
            }