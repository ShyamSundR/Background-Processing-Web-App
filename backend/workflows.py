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
# import httpx
import re
import urllib.request

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


class ContentAnalysisWorkflow:
    @workflow.run
    async def run(self, url: str) -> dict:
        """
        Main workflow execution method for content analysis
        """
        workflow_id = workflow.info().workflow_id

@activity.defn
async def extract_page_content_activity(url: str) -> dict:
    """
    Activity to extract comprehensive page content using Browserbase + Playwright
    
    Extracts text, headings, metadata, and structure for AI analysis
    """
    start_time = time.time()
    
    print(f"[CONTENT_EXTRACT] Starting content extraction for URL: {url}")
    
    # Validate URL
    if not url or not url.strip():
        print("[CONTENT_EXTRACT] Error: URL cannot be empty")
        raise ValueError("URL cannot be empty")
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"[CONTENT_EXTRACT] Added protocol: {url}")
    
    # Get API credentials
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        print("[CONTENT_EXTRACT] Error: Browserbase credentials not configured")
        raise ValueError("Browserbase credentials not configured")
    
    try:
        from playwright.async_api import async_playwright
        import httpx
        
        print("[CONTENT_EXTRACT] ✅ Creating browser session for content extraction...")
        
        # Create session via REST API
        async with httpx.AsyncClient(timeout=30.0) as client:
            session_response = await client.post(
                "https://api.browserbase.com/v1/sessions",
                headers={
                    "X-BB-API-Key": api_key,
                    "Content-Type": "application/json"
                },
                json={"projectId": project_id}
            )
            
            if session_response.status_code not in [200, 201]:
                raise ValueError(f"Failed to create browser session: {session_response.status_code}")
            
            session_data = session_response.json()
            connect_url = session_data["connectUrl"]
            session_id = session_data["id"]
            
            print(f"[CONTENT_EXTRACT] Session created: {session_id}")
        
        # Extract content using Playwright
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            browser = await chromium.connect_over_cdp(connect_url)
            context = browser.contexts[0]
            page = context.pages[0]
            
            try:
                print(f"[CONTENT_EXTRACT] Navigating to {url}")
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for dynamic content to load
                await page.wait_for_timeout(2000)
                
                # Extract comprehensive page content
                # REPLACE WITH THIS:
                content_data = await page.evaluate("""
                    () => {
                        const title = document.title || '';
                        const description = document.querySelector('meta[name="description"]')?.content || '';
                        const keywords = document.querySelector('meta[name="keywords"]')?.content || '';
                        
                        // Extract ALL text content in proper reading order
                        const walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_TEXT,
                            {
                                acceptNode: function(node) {
                                    const parent = node.parentElement;
                                    if (!parent) return NodeFilter.FILTER_REJECT;
                                    
                                    const style = window.getComputedStyle(parent);
                                    if (style.display === 'none' || style.visibility === 'hidden') {
                                        return NodeFilter.FILTER_REJECT;
                                    }
                                    
                                    const tagName = parent.tagName.toLowerCase();
                                    if (['script', 'style', 'noscript', 'nav', 'header', 'footer'].includes(tagName)) {
                                        return NodeFilter.FILTER_REJECT;
                                    }
                                    
                                    return NodeFilter.FILTER_ACCEPT;
                                }
                            }
                        );
                        
                        // Collect text in reading order
                        const textNodes = [];
                        let node;
                        while (node = walker.nextNode()) {
                            const text = node.textContent.trim();
                            if (text.length > 3) {
                                textNodes.push(text);
                            }
                        }
                        
                        const fullContent = textNodes.join(' ');
                        
                        // Extract headings with more detail
                        const headings = [];
                        ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {
                            document.querySelectorAll(tag).forEach((heading, index) => {
                                const text = heading.textContent.trim();
                                if (text) {
                                    headings.push({
                                        level: parseInt(tag.substring(1)),
                                        text: text,
                                        index: index
                                    });
                                }
                            });
                        });
                        
                        // Extract paragraphs separately for better content structure
                        const paragraphs = Array.from(document.querySelectorAll('p'))
                            .map(p => p.textContent.trim())
                            .filter(text => text.length > 20)
                            .slice(0, 10);
                        
                        // Extract links (keep your existing logic)
                        const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
                            text: a.textContent.trim(),
                            href: a.href
                        })).filter(link => link.text && link.text.length > 2).slice(0, 20);
                        
                        // Extract images (keep your existing logic)
                        const images = Array.from(document.querySelectorAll('img[alt]')).map(img => ({
                            alt: img.alt,
                            src: img.src
                        })).filter(img => img.alt).slice(0, 10);
                        
                        // Get page structure info (keep your existing logic)
                        const structure = {
                            hasNav: !!document.querySelector('nav'),
                            hasMain: !!document.querySelector('main'),
                            hasArticle: !!document.querySelector('article'),
                            hasAside: !!document.querySelector('aside'),
                            paragraphCount: document.querySelectorAll('p').length,
                            linkCount: document.querySelectorAll('a').length,
                            imageCount: document.querySelectorAll('img').length
                        };
                        
                        return {
                            title,
                            description,
                            keywords,
                            headings,
                            paragraphs,  // NEW: Separate paragraphs array
                            mainContent: fullContent.substring(0, 15000), // Increased limit
                            links,
                            images,
                            structure,
                            wordCount: fullContent.split(/\s+/).length,
                            url: window.location.href
                        };
                    }
                """)
                
                print(f"[CONTENT_EXTRACT] Extracted {content_data['wordCount']} words")
                print(f"[CONTENT_EXTRACT] Found {len(content_data['headings'])} headings")
                
                processing_time = time.time() - start_time
                content_data["processing_time_seconds"] = round(processing_time, 3)
                content_data["session_id"] = session_id
                content_data["extraction_timestamp"] = time.time()
                
                return content_data
                
            finally:
                print("[CONTENT_EXTRACT] Cleaning up browser session...")
                await page.close()
                await browser.close()
        
    except Exception as e:
        error_msg = f"Content extraction failed: {str(e)}"
        print(f"[CONTENT_EXTRACT] Error: {error_msg}")
        raise ValueError(error_msg)

@activity.defn
async def analyze_content_with_ai_activity(content_data: dict) -> dict:
    """
    Enhanced AI analysis with multiple fallback strategies for summary generation
    """
    start_time = time.time()
    
    print(f"[AI_ANALYSIS] Starting AI analysis of content...")
    
    # Get HuggingFace token
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not hf_token:
        print("[AI_ANALYSIS] No HuggingFace token, using rule-based analysis only")
        return create_rule_based_analysis(content_data, start_time)
    
    try:
        import httpx
        
        # Prepare content for analysis
        text_to_analyze = content_data.get('mainContent', '')
        title = content_data.get('title', '')
        headings = content_data.get('headings', [])
        
        # Create structured text for AI analysis
        structured_text = f"Title: {title}\n"
        if headings:
            structured_text += "Headings: " + " | ".join([h['text'] for h in headings[:10]]) + "\n"
        structured_text += f"Content: {text_to_analyze[:2000]}"  # Shorter for better API success
        
        print(f"[AI_ANALYSIS] Analyzing {len(structured_text)} characters...")
        
        # Generate summary with multiple fallbacks
        summary_text = await generate_summary_with_fallbacks(structured_text, hf_token)
        
        # Generate topics with fallbacks
        main_topics = await generate_topics_with_fallbacks(structured_text, hf_token)
        
        # Rule-based analysis (always works)
        key_info = extract_key_information(content_data)
        page_purpose = determine_page_purpose(content_data, main_topics)
        readability_score = calculate_readability_score(content_data)
        
        # Compile analysis results
        analysis_result = {
            "summary": summary_text,
            "main_topics": main_topics,
            "page_purpose": page_purpose,
            "key_information": key_info,
            "content_metrics": {
                "word_count": content_data.get("wordCount", 0),
                "heading_count": len(content_data.get("headings", [])),
                "link_count": len(content_data.get("links", [])),
                "image_count": len(content_data.get("images", []))
            },
            "readability_score": readability_score,
            "analysis_timestamp": time.time(),
            "processing_time_seconds": round(time.time() - start_time, 3)
        }
        
        print(f"[AI_ANALYSIS] ✅ Analysis complete")
        print(f"[AI_ANALYSIS] Summary: {summary_text[:100]}...")
        print(f"[AI_ANALYSIS] Topics: {main_topics}")
        print(f"[AI_ANALYSIS] Purpose: {page_purpose}")
        
        return analysis_result
        
    except Exception as e:
        error_msg = f"AI analysis failed: {str(e)}"
        print(f"[AI_ANALYSIS] ❌ Error: {error_msg}")
        print(f"[AI_ANALYSIS] 🔄 Falling back to rule-based analysis")
        return create_rule_based_analysis(content_data, start_time)

async def generate_summary_with_fallbacks(text: str, hf_token: str) -> str:
    """Generate summary with multiple fallback strategies"""
    
    print(f"[SUMMARY] Attempting AI summary generation...")
    
    # Strategy 1: Try BART CNN model
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            summary_response = await client.post(
                "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
                headers={
                    "Authorization": f"Bearer {hf_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": text,
                    "parameters": {
                        "max_length": 100,
                        "min_length": 30,
                        "do_sample": False
                    },
                    "options": {
                        "wait_for_model": True
                    }
                }
            )
            
            print(f"[SUMMARY] BART response: {summary_response.status_code}")
            
            if summary_response.status_code == 200:
                summary_result = summary_response.json()
                if isinstance(summary_result, list) and len(summary_result) > 0:
                    ai_summary = summary_result[0].get("summary_text", "")
                    if ai_summary and len(ai_summary) > 20:
                        print(f"[SUMMARY] ✅ BART success: {ai_summary[:50]}...")
                        return ai_summary
            
            elif summary_response.status_code == 503:
                print(f"[SUMMARY] BART model loading, trying alternative...")
                
    except Exception as e:
        print(f"[SUMMARY] BART failed: {e}")
    
    # Strategy 2: Try T5 small model (faster, more reliable)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            t5_response = await client.post(
                "https://api-inference.huggingface.co/models/t5-small",
                headers={
                    "Authorization": f"Bearer {hf_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": f"summarize: {text[:800]}",  # T5 needs prefix
                    "parameters": {
                        "max_length": 80,
                        "min_length": 20
                    }
                }
            )
            
            print(f"[SUMMARY] T5 response: {t5_response.status_code}")
            
            if t5_response.status_code == 200:
                t5_result = t5_response.json()
                if isinstance(t5_result, list) and len(t5_result) > 0:
                    t5_summary = t5_result[0].get("generated_text", "")
                    if t5_summary and len(t5_summary) > 15:
                        print(f"[SUMMARY] ✅ T5 success: {t5_summary[:50]}...")
                        return t5_summary
                        
    except Exception as e:
        print(f"[SUMMARY] T5 failed: {e}")
    
    # Strategy 3: Rule-based summary extraction
    print(f"[SUMMARY] 🔄 Using rule-based summary generation")
    return create_extractive_summary(text)

async def generate_topics_with_fallbacks(text: str, hf_token: str) -> list:
    """Generate topics with fallbacks"""
    
    print(f"[TOPICS] Attempting topic classification...")
    
    # Try zero-shot classification
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            topics_response = await client.post(
                "https://api-inference.huggingface.co/models/facebook/bart-large-mnli",
                headers={
                    "Authorization": f"Bearer {hf_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": text[:500],
                    "parameters": {
                        "candidate_labels": [
                            "business", "technology", "education", "news", "entertainment", 
                            "health", "science", "sports", "politics", "finance", 
                            "travel", "food", "lifestyle", "marketing", "documentation",
                            "software", "website", "company", "product", "service"
                        ]
                    }
                }
            )
            
            print(f"[TOPICS] Classification response: {topics_response.status_code}")
            
            if topics_response.status_code == 200:
                topics_result = topics_response.json()
                if "labels" in topics_result and "scores" in topics_result:
                    # Get top 3 topics with confidence > 0.1
                    main_topics = [
                        topics_result["labels"][i] 
                        for i in range(min(3, len(topics_result["labels"]))) 
                        if topics_result["scores"][i] > 0.1
                    ]
                    if main_topics:
                        print(f"[TOPICS] ✅ AI topics: {main_topics}")
                        return main_topics
                        
    except Exception as e:
        print(f"[TOPICS] AI classification failed: {e}")
    
    # Fallback: Rule-based topic extraction
    print(f"[TOPICS] 🔄 Using rule-based topic extraction")
    return extract_topics_from_keywords(text)

def create_extractive_summary(text: str) -> str:
    """Create summary by extracting key sentences"""
    
    # Split into sentences
    sentences = [s.strip() for s in text.split('.') if s.strip() and len(s.strip()) > 20]
    
    if len(sentences) == 0:
        return "Content analysis completed - unable to generate summary."
    
    if len(sentences) <= 2:
        return ". ".join(sentences) + "."
    
    # Score sentences based on position and key indicators
    scored_sentences = []
    for i, sentence in enumerate(sentences[:10]):  # Only first 10 sentences
        score = 0
        
        # First sentences are more important
        if i == 0:
            score += 10
        elif i < 3:
            score += 5
        
        # Sentences with key indicators
        key_words = ['main', 'important', 'key', 'primary', 'focuses', 'provides', 'offers', 'specializes']
        score += sum(2 for word in key_words if word in sentence.lower())
        
        # Prefer medium-length sentences
        word_count = len(sentence.split())
        if 10 <= word_count <= 25:
            score += 3
        
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    # Take top 2-3 sentences
    summary_sentences = [sent[1] for sent in scored_sentences[:2]]
    
    summary = ". ".join(summary_sentences) + "."
    
    # Add prefix to indicate it's extractive
    return f"{summary}"

def extract_topics_from_keywords(text: str) -> list:
    """Extract topics using keyword matching"""
    
    text_lower = text.lower()
    
    topic_keywords = {
        "technology": ["software", "app", "platform", "digital", "tech", "development", "programming", "code", "system"],
        "business": ["company", "business", "service", "solution", "client", "customer", "enterprise", "corporate"],
        "education": ["learn", "education", "course", "training", "tutorial", "guide", "teaching", "student"],
        "healthcare": ["health", "medical", "care", "treatment", "doctor", "patient", "wellness"],
        "finance": ["finance", "money", "investment", "banking", "payment", "financial", "cost", "price"],
        "marketing": ["marketing", "brand", "campaign", "advertising", "promotion", "social media"],
        "news": ["news", "article", "report", "announcement", "update", "press"],
        "entertainment": ["game", "entertainment", "music", "video", "movie", "fun"],
        "travel": ["travel", "trip", "vacation", "hotel", "flight", "destination"],
        "food": ["food", "restaurant", "recipe", "cooking", "meal", "dining"]
    }
    
    topic_scores = {}
    
    for topic, keywords in topic_keywords.items():
        score = sum(text_lower.count(keyword) for keyword in keywords)
        if score > 0:
            topic_scores[topic] = score
    
    # Return top 3 topics
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, score in sorted_topics[:3]] if sorted_topics else ["general"]

def create_rule_based_analysis(content_data: dict, start_time: float) -> dict:
    """Create analysis using only rule-based methods when AI fails"""
    
    print(f"[AI_ANALYSIS] 🔄 Creating rule-based analysis...")
    
    text = content_data.get('mainContent', '')
    title = content_data.get('title', '')
    
    # Create simple summary from title and first content
    if title:
        summary = f"{title}. "
        if text:
            first_sentence = text.split('.')[0] if '.' in text else text[:100]
            summary += first_sentence + "."
    else:
        summary = "Analysis completed - page content extracted successfully."
    
    # Extract topics from keywords
    topics = extract_topics_from_keywords(text + " " + title)
    
    return {
        "summary": summary[:200],  # Limit length
        "main_topics": topics,
        "page_purpose": determine_page_purpose(content_data, topics),
        "key_information": extract_key_information(content_data),
        "content_metrics": {
            "word_count": content_data.get("wordCount", 0),
            "heading_count": len(content_data.get("headings", [])),
            "link_count": len(content_data.get("links", [])),
            "image_count": len(content_data.get("images", []))
        },
        "readability_score": calculate_readability_score(content_data),
        "analysis_timestamp": time.time(),
        "processing_time_seconds": round(time.time() - start_time, 3),
        "fallback_used": "rule-based analysis"
    }

def extract_key_information(content_data: dict) -> dict:
    """Extract key information using rule-based analysis"""
    
    headings = content_data.get('headings', [])
    main_content = content_data.get('mainContent', '')
    links = content_data.get('links', [])
    
    # Extract key points from headings
    key_points = []
    for heading in headings[:10]:  # Top 10 headings
        if heading['text'] and len(heading['text']) > 5:
            key_points.append({
                "type": f"H{heading['level']}",
                "text": heading['text']
            })
    
    # Extract important links (navigation, main actions)
    important_links = []
    action_keywords = ['contact', 'about', 'services', 'products', 'pricing', 'buy', 'download', 'signup', 'login']
    for link in links:
        if any(keyword in link['text'].lower() for keyword in action_keywords):
            important_links.append(link['text'])
    
    # Simple entity extraction (emails, phones, addresses)
    import re
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', main_content)
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', main_content)
    
    return {
        "key_points": key_points,
        "important_links": important_links[:5],
        "contact_info": {
            "emails": emails[:3],
            "phones": phones[:3]
        },
        "has_contact_info": len(emails) > 0 or len(phones) > 0
    }

def determine_page_purpose(content_data: dict, topics: list) -> str:
    """Determine the main purpose of the page"""
    
    title = content_data.get('title', '').lower()
    headings = [h['text'].lower() for h in content_data.get('headings', [])]
    structure = content_data.get('structure', {})
    
    # Check for specific page types
    if any(word in title for word in ['blog', 'article', 'news', 'post']):
        return "Content/Blog Article"
    elif any(word in title for word in ['about', 'company', 'team']):
        return "Company Information"
    elif any(word in title for word in ['product', 'service', 'pricing', 'buy']):
        return "Product/Service Page"
    elif any(word in title for word in ['contact', 'support', 'help']):
        return "Contact/Support Page"
    elif any(word in title for word in ['home', 'welcome']) or title.count(' ') <= 2:
        return "Homepage/Landing Page"
    elif structure.get('hasArticle'):
        return "Article/Content Page"
    elif 'documentation' in topics or any(word in title for word in ['docs', 'api', 'guide']):
        return "Documentation"
    elif 'business' in topics:
        return "Business/Corporate Page"
    elif 'education' in topics:
        return "Educational Content"
    else:
        return "General Information Page"

def calculate_readability_score(content_data: dict) -> str:
    """Simple readability assessment"""
    
    word_count = content_data.get('wordCount', 0)
    heading_count = len(content_data.get('headings', []))
    paragraph_count = content_data.get('structure', {}).get('paragraphCount', 0)
    
    if word_count == 0:
        return "No content"
    
    # Simple heuristics
    avg_words_per_paragraph = word_count / max(paragraph_count, 1)
    heading_to_content_ratio = heading_count / max(word_count / 100, 1)
    
    if avg_words_per_paragraph > 200:
        return "Dense/Technical"
    elif avg_words_per_paragraph < 50:
        return "Easy/Scan-friendly"
    elif heading_to_content_ratio > 3:
        return "Well-structured"
    else:
        return "Moderate"

@workflow.defn
class ContentAnalysisWorkflow:
    """
    Temporal workflow for comprehensive page content analysis
    
    Combines content extraction and AI analysis for complete page insights
    """
    
    @workflow.run
    async def run(self, url: str) -> dict:
        """
        Main workflow execution method for content analysis
        
        Args:
            url: The website URL to analyze
            
        Returns:
            dict: Complete analysis including content, summary, topics, and insights
        """
        workflow_id = workflow.info().workflow_id
        
        try:
            # Input validation
            if not isinstance(url, str) or not url.strip():
                raise ValueError("URL cannot be empty")
            
            # Log workflow start
            await workflow.execute_activity(
                log_processing_activity,
                args=(f"Starting content analysis for: {url}", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Step 1: Extract page content
            content_data = await workflow.execute_activity(
                extract_page_content_activity,
                args=(url,),
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=20),
                    maximum_attempts=3,
                    non_retryable_error_types=["ValueError", "TypeError"]
                )
            )
            
            # Step 2: Analyze content with AI
            analysis_result = await workflow.execute_activity(
                analyze_content_with_ai_activity,
                args=(content_data,),
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=3),
                    maximum_interval=timedelta(seconds=30),
                    maximum_attempts=2
                )
            )
            
            # Combine results
            final_result = {
                "url": url,
                "content_data": content_data,
                "analysis": analysis_result,
                "workflow_id": workflow_id,
                "status": "completed",
                "total_processing_time": content_data.get("processing_time_seconds", 0) + analysis_result.get("processing_time_seconds", 0)
            }
            
            # Log completion
            await workflow.execute_activity(
                log_processing_activity,
                args=(f"Content analysis completed for: {content_data.get('title', url)}", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return final_result
            
        except Exception as e:
            error_msg = f"Content analysis workflow failed: {str(e)}"
            await workflow.execute_activity(
                log_processing_activity,
                args=(error_msg, workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return {
                "url": url,
                "content_data": None,
                "analysis": None,
                "error": error_msg,
                "workflow_id": workflow_id,
                "status": "failed"
            }

# Add to workflows.py - Technical Specification Generator

@activity.defn
async def generate_technical_specification_activity(url: str) -> dict:
    """
    Activity to generate comprehensive technical specifications for rebuilding a webpage
    
    Analyzes HTML structure, CSS styles, JavaScript functionality, and content
    """
    start_time = time.time()
    
    print(f"[TECH_SPEC] Starting technical specification generation for URL: {url}")
    
    # Validate URL
    if not url or not url.strip():
        print("[TECH_SPEC] Error: URL cannot be empty")
        raise ValueError("URL cannot be empty")
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"[TECH_SPEC] Added protocol: {url}")
    
    # Get API credentials
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        print("[TECH_SPEC] Error: Browserbase credentials not configured")
        raise ValueError("Browserbase credentials not configured")
    
    try:
        from playwright.async_api import async_playwright
        import httpx
        
        print("[TECH_SPEC] ✅ Creating browser session for technical analysis...")
        
        # Create session via REST API
        async with httpx.AsyncClient(timeout=30.0) as client:
            session_response = await client.post(
                "https://api.browserbase.com/v1/sessions",
                headers={
                    "X-BB-API-Key": api_key,
                    "Content-Type": "application/json"
                },
                json={"projectId": project_id}
            )
            
            if session_response.status_code not in [200, 201]:
                raise ValueError(f"Failed to create browser session: {session_response.status_code}")
            
            session_data = session_response.json()
            connect_url = session_data["connectUrl"]
            session_id = session_data["id"]
            
            print(f"[TECH_SPEC] Session created: {session_id}")
        
        # Perform comprehensive technical analysis
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            browser = await chromium.connect_over_cdp(connect_url)
            context = browser.contexts[0]
            page = context.pages[0]
            
            try:
                print(f"[TECH_SPEC] Navigating to {url}")
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for dynamic content and JavaScript execution
                await page.wait_for_timeout(3000)
                
                # Extract comprehensive technical data
                tech_data = await page.evaluate("""
                    () => {
                        // Helper function to get computed styles
                        function getComputedStylesForElement(element) {
                            const computedStyle = window.getComputedStyle(element);
                            const importantStyles = {};
                            
                            // Key CSS properties for layout and design
                            const keyProperties = [
                                'display', 'position', 'top', 'right', 'bottom', 'left',
                                'width', 'height', 'margin', 'padding', 'border',
                                'background', 'background-color', 'background-image',
                                'color', 'font-family', 'font-size', 'font-weight',
                                'line-height', 'text-align', 'text-decoration',
                                'flex-direction', 'justify-content', 'align-items',
                                'grid-template-columns', 'grid-template-rows',
                                'z-index', 'opacity', 'transform', 'transition'
                            ];
                            
                            keyProperties.forEach(prop => {
                                const value = computedStyle.getPropertyValue(prop);
                                if (value && value !== 'auto' && value !== 'normal' && value !== 'none') {
                                    importantStyles[prop] = value;
                                }
                            });
                            
                            return importantStyles;
                        }
                        
                        // Analyze HTML structure
                        function analyzeElement(element, depth = 0) {
                            if (depth > 10) return null; // Prevent infinite recursion
                            
                            const tagName = element.tagName.toLowerCase();
                            const elementData = {
                                tag: tagName,
                                attributes: {},
                                styles: getComputedStylesForElement(element),
                                content: '',
                                children: [],
                                hasText: false,
                                isInteractive: false
                            };
                            
                            // Get attributes
                            for (let attr of element.attributes) {
                                elementData.attributes[attr.name] = attr.value;
                            }
                            
                            // Check if element has direct text content
                            const directText = Array.from(element.childNodes)
                                .filter(node => node.nodeType === Node.TEXT_NODE)
                                .map(node => node.textContent.trim())
                                .join(' ');
                            
                            if (directText) {
                                elementData.content = directText;
                                elementData.hasText = true;
                            }
                            
                            // Check if interactive
                            const interactiveTags = ['button', 'a', 'input', 'select', 'textarea', 'form'];
                            const hasClickHandler = element.onclick || element.addEventListener;
                            elementData.isInteractive = interactiveTags.includes(tagName) || !!hasClickHandler;
                            
                            // Analyze children (limited depth)
                            if (depth < 5) {
                                for (let child of element.children) {
                                    const childData = analyzeElement(child, depth + 1);
                                    if (childData) {
                                        elementData.children.push(childData);
                                    }
                                }
                            }
                            
                            return elementData;
                        }
                        
                        // Get page metadata
                        const metadata = {
                            title: document.title,
                            description: document.querySelector('meta[name="description"]')?.content || '',
                            keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                            viewport: document.querySelector('meta[name="viewport"]')?.content || '',
                            charset: document.querySelector('meta[charset]')?.getAttribute('charset') || 'UTF-8',
                            lang: document.documentElement.lang || 'en'
                        };
                        
                        // Analyze CSS architecture
                        const cssAnalysis = {
                            stylesheets: [],
                            inlineStyles: 0,
                            cssVariables: [],
                            mediaQueries: []
                        };
                        
                        // Count stylesheets
                        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                            cssAnalysis.stylesheets.push(link.href);
                        });
                        
                        // Count inline styles
                        cssAnalysis.inlineStyles = document.querySelectorAll('[style]').length;
                        
                        // Extract CSS variables from :root
                        const rootElement = document.documentElement;
                        const rootStyles = window.getComputedStyle(rootElement);
                        for (let i = 0; i < rootStyles.length; i++) {
                            const prop = rootStyles[i];
                            if (prop.startsWith('--')) {
                                cssAnalysis.cssVariables.push({
                                    name: prop,
                                    value: rootStyles.getPropertyValue(prop)
                                });
                            }
                        }
                        
                        // Analyze JavaScript
                        const jsAnalysis = {
                            externalScripts: [],
                            inlineScripts: 0,
                            eventListeners: 0,
                            frameworks: []
                        };
                        
                        // Count external scripts
                        document.querySelectorAll('script[src]').forEach(script => {
                            jsAnalysis.externalScripts.push(script.src);
                        });
                        
                        // Count inline scripts
                        jsAnalysis.inlineScripts = document.querySelectorAll('script:not([src])').length;
                        
                        // Detect frameworks
                        if (window.React) jsAnalysis.frameworks.push('React');
                        if (window.Vue) jsAnalysis.frameworks.push('Vue');
                        if (window.Angular) jsAnalysis.frameworks.push('Angular');
                        if (window.jQuery || window.$) jsAnalysis.frameworks.push('jQuery');
                        
                        // Analyze layout structure
                        const layoutAnalysis = {
                            hasHeader: !!document.querySelector('header, .header, #header'),
                            hasNav: !!document.querySelector('nav, .nav, .navigation'),
                            hasMain: !!document.querySelector('main, .main, #main'),
                            hasAside: !!document.querySelector('aside, .aside, .sidebar'),
                            hasFooter: !!document.querySelector('footer, .footer, #footer'),
                            layoutType: 'unknown',
                            gridAreas: [],
                            flexContainers: 0
                        };
                        
                        // Detect layout type
                        const body = document.body;
                        const bodyStyles = window.getComputedStyle(body);
                        if (bodyStyles.display === 'grid') {
                            layoutAnalysis.layoutType = 'CSS Grid';
                        } else if (bodyStyles.display === 'flex') {
                            layoutAnalysis.layoutType = 'Flexbox';
                        } else {
                            layoutAnalysis.layoutType = 'Traditional';
                        }
                        
                        // Count flex containers
                        layoutAnalysis.flexContainers = document.querySelectorAll('*').length;
                        let flexCount = 0;
                        document.querySelectorAll('*').forEach(el => {
                            if (window.getComputedStyle(el).display.includes('flex')) {
                                flexCount++;
                            }
                        });
                        layoutAnalysis.flexContainers = flexCount;
                        
                        // Analyze forms
                        const formsAnalysis = [];
                        document.querySelectorAll('form').forEach((form, index) => {
                            const formData = {
                                id: form.id || `form-${index}`,
                                method: form.method || 'GET',
                                action: form.action || '',
                                fields: []
                            };
                            
                            form.querySelectorAll('input, select, textarea').forEach(field => {
                                formData.fields.push({
                                    type: field.type || field.tagName.toLowerCase(),
                                    name: field.name,
                                    id: field.id,
                                    required: field.required,
                                    placeholder: field.placeholder
                                });
                            });
                            
                            formsAnalysis.push(formData);
                        });
                        
                        // Get color scheme
                        const colorScheme = {
                            primaryColors: [],
                            backgroundColors: [],
                            textColors: []
                        };
                        
                        // Sample elements for color analysis
                        const sampleElements = [
                            document.body,
                            ...Array.from(document.querySelectorAll('h1, h2, h3, p, a, button')).slice(0, 20)
                        ];
                        
                        sampleElements.forEach(el => {
                            if (el) {
                                const styles = window.getComputedStyle(el);
                                const bgColor = styles.backgroundColor;
                                const textColor = styles.color;
                                
                                if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                                    if (!colorScheme.backgroundColors.includes(bgColor)) {
                                        colorScheme.backgroundColors.push(bgColor);
                                    }
                                }
                                
                                if (textColor && textColor !== 'rgba(0, 0, 0, 0)') {
                                    if (!colorScheme.textColors.includes(textColor)) {
                                        colorScheme.textColors.push(textColor);
                                    }
                                }
                            }
                        });
                        
                        // Analyze main content structure
                        const mainStructure = analyzeElement(document.body, 0);
                        
                        return {
                            url: window.location.href,
                            metadata,
                            cssAnalysis,
                            jsAnalysis,
                            layoutAnalysis,
                            formsAnalysis,
                            colorScheme,
                            mainStructure: mainStructure,
                            viewport: {
                                width: window.innerWidth,
                                height: window.innerHeight
                            },
                            performance: {
                                domElements: document.querySelectorAll('*').length,
                                images: document.querySelectorAll('img').length,
                                links: document.querySelectorAll('a').length
                            }
                        };
                    }
                """)
                
                print(f"[TECH_SPEC] Extracted technical data - DOM elements: {tech_data['performance']['domElements']}")
                
                # Generate comprehensive technical specification
                specification = generate_comprehensive_spec(tech_data)
                
                processing_time = time.time() - start_time
                
                result = {
                    "url": url,
                    "technical_data": tech_data,
                    "specification": specification,
                    "session_id": session_id,
                    "processing_time_seconds": round(processing_time, 3),
                    "generation_timestamp": time.time()
                }
                
                print(f"[TECH_SPEC] ✅ Technical specification generated in {processing_time:.2f}s")
                return result
                
            finally:
                print("[TECH_SPEC] Cleaning up browser session...")
                await page.close()
                await browser.close()
        
    except Exception as e:
        error_msg = f"Technical specification generation failed: {str(e)}"
        print(f"[TECH_SPEC] ❌ Error: {error_msg}")
        raise ValueError(error_msg)

def generate_comprehensive_spec(tech_data: dict) -> dict:
    """Generate comprehensive technical specification from analyzed data"""
    
    metadata = tech_data.get('metadata', {})
    css_analysis = tech_data.get('cssAnalysis', {})
    js_analysis = tech_data.get('jsAnalysis', {})
    layout_analysis = tech_data.get('layoutAnalysis', {})
    forms_analysis = tech_data.get('formsAnalysis', [])
    color_scheme = tech_data.get('colorScheme', {})
    main_structure = tech_data.get('mainStructure', {})
    
    specification = {
        "html_structure": generate_html_structure_spec(main_structure, metadata),
        "css_requirements": generate_css_requirements_spec(css_analysis, layout_analysis, color_scheme),
        "javascript_functionality": generate_js_functionality_spec(js_analysis, forms_analysis),
        "content_specification": generate_content_spec(main_structure),
        "step_by_step_guide": generate_implementation_guide(tech_data),
        "technical_requirements": generate_technical_requirements(tech_data),
        "responsive_design": generate_responsive_spec(tech_data),
        "accessibility_requirements": generate_accessibility_spec(main_structure)
    }
    
    return specification

def generate_html_structure_spec(structure: dict, metadata: dict) -> dict:
    """Generate HTML structure requirements"""
    
    def analyze_structure_recursively(element, level=0):
        if not element or level > 8:
            return []
        
        requirements = []
        tag = element.get('tag', 'div')
        attrs = element.get('attributes', {})
        children = element.get('children', [])
        
        # Create requirement for this element
        requirement = {
            "tag": tag,
            "purpose": determine_element_purpose(tag, attrs, element),
            "attributes": list(attrs.keys()),
            "required_attributes": get_required_attributes(tag, attrs),
            "accessibility": get_accessibility_requirements(tag, attrs),
            "nesting_level": level
        }
        
        requirements.append(requirement)
        
        # Analyze children
        for child in children[:10]:  # Limit to prevent huge specs
            requirements.extend(analyze_structure_recursively(child, level + 1))
        
        return requirements
    
    structure_requirements = analyze_structure_recursively(structure)
    
    return {
        "document_type": "HTML5",
        "language": metadata.get('lang', 'en'),
        "charset": metadata.get('charset', 'UTF-8'),
        "viewport": metadata.get('viewport', 'width=device-width, initial-scale=1'),
        "title": metadata.get('title', ''),
        "meta_description": metadata.get('description', ''),
        "structure_requirements": structure_requirements[:50],  # Limit for readability
        "semantic_elements": extract_semantic_elements(structure),
        "required_sections": identify_required_sections(structure)
    }

def generate_css_requirements_spec(css_analysis: dict, layout_analysis: dict, color_scheme: dict) -> dict:
    """Generate CSS styling requirements"""
    
    return {
        "css_methodology": "Component-based CSS with utility classes",
        "layout_system": {
            "primary": layout_analysis.get('layoutType', 'Flexbox'),
            "grid_areas": layout_analysis.get('gridAreas', []),
            "flex_containers": layout_analysis.get('flexContainers', 0)
        },
        "color_palette": {
            "background_colors": color_scheme.get('backgroundColors', [])[:10],
            "text_colors": color_scheme.get('textColors', [])[:10],
            "usage_notes": "Extract exact color values for brand consistency"
        },
        "typography": {
            "font_loading": "Use web fonts or system font stack",
            "hierarchy": "Establish clear heading hierarchy (H1-H6)",
            "responsive_scaling": "Implement fluid typography with clamp()"
        },
        "responsive_design": {
            "breakpoints": ["mobile: 480px", "tablet: 768px", "desktop: 1024px", "large: 1200px"],
            "approach": "Mobile-first responsive design",
            "units": "Use rem/em for scalability, px for borders"
        },
        "css_organization": {
            "external_stylesheets": len(css_analysis.get('stylesheets', [])),
            "css_variables": len(css_analysis.get('cssVariables', [])),
            "inline_styles": css_analysis.get('inlineStyles', 0),
            "recommendations": [
                "Use CSS custom properties for consistent theming",
                "Implement BEM methodology for class naming",
                "Organize CSS into logical modules/components"
            ]
        }
    }

def generate_js_functionality_spec(js_analysis: dict, forms_analysis: list) -> dict:
    """Generate JavaScript functionality requirements"""
    
    frameworks = js_analysis.get('frameworks', [])
    external_scripts = js_analysis.get('externalScripts', [])
    
    functionality_spec = {
        "framework_requirements": {
            "detected_frameworks": frameworks,
            "recommendations": get_framework_recommendations(frameworks, external_scripts)
        },
        "core_functionality": [],
        "form_handling": [],
        "interactive_elements": [],
        "external_dependencies": external_scripts[:10]
    }
    
    # Analyze forms
    for form in forms_analysis:
        form_spec = {
            "form_id": form.get('id', 'unnamed'),
            "method": form.get('method', 'POST'),
            "validation_required": True,
            "fields": form.get('fields', []),
            "javascript_requirements": [
                "Form validation before submission",
                "Error message display",
                "Loading states during submission"
            ]
        }
        functionality_spec["form_handling"].append(form_spec)
    
    return functionality_spec

def generate_content_spec(structure: dict) -> dict:
    """Generate content specification"""
    
    def extract_content_recursively(element, content_list=None):
        if content_list is None:
            content_list = []
        
        if not element:
            return content_list
        
        tag = element.get('tag', '')
        content = element.get('content', '')
        attrs = element.get('attributes', {})
        
        if content.strip():
            content_item = {
                "element_type": tag,
                "content": content[:200],  # Limit length
                "context": determine_content_context(tag, attrs),
                "formatting": determine_content_formatting(tag)
            }
            content_list.append(content_item)
        
        # Process children
        for child in element.get('children', []):
            extract_content_recursively(child, content_list)
        
        return content_list
    
    content_items = extract_content_recursively(structure)
    
    return {
        "content_inventory": content_items[:30],  # Limit for readability
        "content_types": list(set(item['element_type'] for item in content_items)),
        "content_guidelines": [
            "Maintain exact text content for brand consistency",
            "Preserve content hierarchy and structure",
            "Ensure all interactive text is preserved",
            "Include alt text for images",
            "Maintain link text and destinations"
        ]
    }

def generate_implementation_guide(tech_data: dict) -> list:
    """Generate step-by-step implementation guide"""
    
    layout_type = tech_data.get('layoutAnalysis', {}).get('layoutType', 'Traditional')
    has_forms = len(tech_data.get('formsAnalysis', [])) > 0
    has_js = len(tech_data.get('jsAnalysis', {}).get('externalScripts', [])) > 0
    
    steps = [
        {
            "step": 1,
            "title": "Project Setup",
            "description": "Initialize the project structure",
            "tasks": [
                "Create project directory structure",
                "Set up HTML5 boilerplate",
                "Initialize CSS and JavaScript files",
                "Configure development environment"
            ]
        },
        {
            "step": 2,
            "title": "HTML Structure",
            "description": "Build the semantic HTML foundation",
            "tasks": [
                "Create HTML5 document structure",
                "Add meta tags and document head",
                "Build semantic layout containers",
                "Add content elements with proper nesting"
            ]
        },
        {
            "step": 3,
            "title": "CSS Layout System",
            "description": f"Implement {layout_type} layout system",
            "tasks": [
                f"Set up {layout_type} containers",
                "Define CSS custom properties",
                "Implement responsive breakpoints",
                "Add base typography styles"
            ]
        },
        {
            "step": 4,
            "title": "Component Styling",
            "description": "Style individual components",
            "tasks": [
                "Style header and navigation",
                "Implement main content area",
                "Style sidebar/aside elements",
                "Add footer styling"
            ]
        }
    ]
    
    if has_forms:
        steps.append({
            "step": 5,
            "title": "Form Implementation",
            "description": "Build and style forms with validation",
            "tasks": [
                "Create form HTML structure",
                "Add form styling and layout",
                "Implement client-side validation",
                "Add form submission handling"
            ]
        })
    
    if has_js:
        steps.append({
            "step": 6,
            "title": "JavaScript Functionality",
            "description": "Add interactive features",
            "tasks": [
                "Include required JavaScript libraries",
                "Implement interactive components",
                "Add event listeners",
                "Test all functionality"
            ]
        })
    
    steps.extend([
        {
            "step": len(steps) + 1,
            "title": "Responsive Testing",
            "description": "Test across devices and browsers",
            "tasks": [
                "Test on mobile devices",
                "Verify tablet layouts",
                "Check desktop responsiveness",
                "Cross-browser compatibility testing"
            ]
        },
        {
            "step": len(steps) + 2,
            "title": "Optimization & Launch",
            "description": "Final optimizations and deployment",
            "tasks": [
                "Optimize images and assets",
                "Minify CSS and JavaScript",
                "Run accessibility audit",
                "Deploy to production"
            ]
        }
    ])
    
    return steps

def generate_technical_requirements(tech_data: dict) -> dict:
    """Generate technical requirements and constraints"""
    
    return {
        "browser_support": [
            "Chrome 90+",
            "Firefox 88+", 
            "Safari 14+",
            "Edge 90+"
        ],
        "performance_targets": {
            "first_contentful_paint": "< 1.5s",
            "largest_contentful_paint": "< 2.5s",
            "cumulative_layout_shift": "< 0.1"
        },
        "dependencies": {
            "external_stylesheets": len(tech_data.get('cssAnalysis', {}).get('stylesheets', [])),
            "external_scripts": len(tech_data.get('jsAnalysis', {}).get('externalScripts', [])),
            "estimated_complexity": determine_complexity_level(tech_data)
        }
    }

def generate_responsive_spec(tech_data: dict) -> dict:
    """Generate responsive design specifications"""
    
    viewport = tech_data.get('viewport', {})
    
    return {
        "current_viewport": f"{viewport.get('width', 'unknown')}x{viewport.get('height', 'unknown')}",
        "breakpoint_strategy": "Mobile-first approach",
        "responsive_requirements": [
            "Implement fluid grid system",
            "Use flexible images and media",
            "Optimize touch interactions for mobile",
            "Ensure readable text on all devices"
        ]
    }

def generate_accessibility_spec(structure: dict) -> dict:
    """Generate accessibility requirements"""
    
    return {
        "wcag_level": "AA compliance recommended",
        "key_requirements": [
            "Semantic HTML elements for screen readers",
            "Sufficient color contrast ratios",
            "Keyboard navigation support",
            "Alt text for all images",
            "Form labels and error messages",
            "Focus management for interactive elements"
        ]
    }

# Helper functions
def determine_element_purpose(tag: str, attrs: dict, element: dict) -> str:
    """Determine the purpose of an HTML element"""
    
    if tag == 'header':
        return "Page or section header"
    elif tag == 'nav':
        return "Navigation menu"
    elif tag == 'main':
        return "Main content area"
    elif tag == 'aside':
        return "Sidebar or complementary content"
    elif tag == 'footer':
        return "Page or section footer"
    elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        return f"Heading level {tag[1]}"
    elif tag == 'form':
        return "User input form"
    elif tag == 'button':
        return "Interactive button"
    elif tag == 'a':
        return "Link or navigation"
    elif element.get('isInteractive'):
        return "Interactive element"
    elif element.get('hasText'):
        return "Content container"
    else:
        return "Layout/structural element"

def get_required_attributes(tag: str, attrs: dict) -> list:
    """Get required attributes for specific HTML elements"""
    
    required = []
    
    if tag == 'img':
        required.extend(['src', 'alt'])
    elif tag == 'a' and 'href' in attrs:
        required.append('href')
    elif tag == 'form':
        required.extend(['method', 'action'])
    elif tag == 'input':
        required.extend(['type', 'name'])
    elif tag == 'label':
        required.append('for')
    elif tag == 'meta':
        required.extend(['name', 'content'])
    
    return required

def get_accessibility_requirements(tag: str, attrs: dict) -> list:
    """Get accessibility requirements for elements"""
    
    requirements = []
    
    if tag == 'img':
        requirements.append("Alt text required")
    elif tag == 'button':
        requirements.append("Accessible button text")
    elif tag == 'a':
        requirements.append("Descriptive link text")
    elif tag == 'form':
        requirements.append("Form labels and error handling")
    elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        requirements.append("Proper heading hierarchy")
    
    return requirements

def extract_semantic_elements(structure: dict) -> list:
    """Extract semantic HTML5 elements used"""
    
    semantic_tags = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
    found_elements = []
    
    def find_semantic_recursively(element):
        if not element:
            return
        
        tag = element.get('tag', '')
        if tag in semantic_tags and tag not in found_elements:
            found_elements.append(tag)
        
        for child in element.get('children', []):
            find_semantic_recursively(child)
    
    find_semantic_recursively(structure)
    return found_elements

def identify_required_sections(structure: dict) -> list:
    """Identify required page sections"""
    
    sections = []
    
    def find_sections_recursively(element):
        if not element:
            return
        
        tag = element.get('tag', '')
        attrs = element.get('attributes', {})
        
        if tag in ['header', 'nav', 'main', 'aside', 'footer']:
            sections.append({
                "tag": tag,
                "purpose": determine_element_purpose(tag, attrs, element),
                "required": True
            })
        
        for child in element.get('children', []):
            find_sections_recursively(child)
    
    find_sections_recursively(structure)
    return sections

def get_framework_recommendations(frameworks: list, external_scripts: list) -> list:
    """Get framework recommendations based on detected usage"""
    
    recommendations = []
    
    if 'React' in frameworks:
        recommendations.append("Use React 18+ for component architecture")
    elif 'Vue' in frameworks:
        recommendations.append("Use Vue 3+ with Composition API")
    elif 'jQuery' in frameworks:
        recommendations.append("Consider migrating to vanilla JS or modern framework")
    else:
        recommendations.append("Use vanilla JavaScript for simple interactions")
    
    if len(external_scripts) > 5:
        recommendations.append("Bundle and optimize JavaScript dependencies")
    
    return recommendations

def determine_content_context(tag: str, attrs: dict) -> str:
    """Determine the context of content"""
    
    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        return f"Heading content - level {tag[1]}"
    elif tag == 'p':
        return "Paragraph text content"
    elif tag == 'a':
        return "Link text"
    elif tag == 'button':
        return "Button label"
    elif tag == 'span':
        return "Inline text content"
    elif tag == 'div':
        return "Block content container"
    else:
        return f"Content in {tag} element"

def determine_content_formatting(tag: str) -> list:
    """Determine content formatting requirements"""
    
    formatting = []
    
    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        formatting.extend(["Bold/semibold weight", "Larger font size", "Margin spacing"])
    elif tag == 'p':
        formatting.extend(["Regular weight", "Line height 1.5+", "Paragraph spacing"])
    elif tag == 'a':
        formatting.extend(["Underline or color differentiation", "Hover states"])
    elif tag == 'button':
        formatting.extend(["Button styling", "Hover/focus states", "Padding"])
    elif tag in ['strong', 'b']:
        formatting.append("Bold font weight")
    elif tag in ['em', 'i']:
        formatting.append("Italic font style")
    
    return formatting

def determine_complexity_level(tech_data: dict) -> str:
    """Determine overall complexity level of the page"""
    
    dom_elements = tech_data.get('performance', {}).get('domElements', 0)
    external_scripts = len(tech_data.get('jsAnalysis', {}).get('externalScripts', []))
    forms_count = len(tech_data.get('formsAnalysis', []))
    
    complexity_score = 0
    
    # DOM complexity
    if dom_elements > 500:
        complexity_score += 3
    elif dom_elements > 200:
        complexity_score += 2
    elif dom_elements > 50:
        complexity_score += 1
    
    # JavaScript complexity
    if external_scripts > 10:
        complexity_score += 3
    elif external_scripts > 5:
        complexity_score += 2
    elif external_scripts > 0:
        complexity_score += 1
    
    # Forms complexity
    complexity_score += forms_count
    
    if complexity_score >= 7:
        return "High - Complex application with many interactive elements"
    elif complexity_score >= 4:
        return "Medium - Standard website with some interactive features"
    else:
        return "Low - Simple static or mostly static website"

@workflow.defn
class TechnicalSpecificationWorkflow:
    """
    Temporal workflow for generating comprehensive technical specifications
    
    Analyzes webpage structure and creates detailed rebuild documentation
    """
    
    @workflow.run
    async def run(self, url: str) -> dict:
        """
        Main workflow execution method for technical specification generation
        
        Args:
            url: The website URL to analyze
            
        Returns:
            dict: Complete technical specification with rebuild instructions
        """
        workflow_id = workflow.info().workflow_id
        
        try:
            # Input validation
            if not isinstance(url, str) or not url.strip():
                raise ValueError("URL cannot be empty")
            
            # Log workflow start
            await workflow.execute_activity(
                log_processing_activity,
                args=(f"Starting technical specification for: {url}", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Generate technical specification
            spec_result = await workflow.execute_activity(
                generate_technical_specification_activity,
                args=(url,),
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=3),
                    maximum_interval=timedelta(seconds=30),
                    maximum_attempts=3,
                    non_retryable_error_types=["ValueError", "TypeError"]
                )
            )
            
            # Log completion
            complexity = spec_result.get("specification", {}).get("technical_requirements", {}).get("dependencies", {}).get("estimated_complexity", "unknown")
            await workflow.execute_activity(
                log_processing_activity,
                args=(f"Technical specification completed - Complexity: {complexity}", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return {
                "url": url,
                "technical_specification": spec_result,
                "workflow_id": workflow_id,
                "status": "completed"
            }
            
        except Exception as e:
            error_msg = f"Technical specification workflow failed: {str(e)}"
            await workflow.execute_activity(
                log_processing_activity,
                args=(error_msg, workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return {
                "url": url,
                "technical_specification": None,
                "error": error_msg,
                "workflow_id": workflow_id,
                "status": "failed"
            }
# ONLY ADD THESE NEW ITEMS TO YOUR EXISTING workflows.py FILE
# (Don't duplicate what's already there)

# ADD THIS NEW ACTIVITY (this is the only missing piece for code generation)
@activity.defn
async def generate_frontend_code_activity(tech_data: dict, content_data: dict) -> dict:
    """Activity to generate HTML, CSS, and JavaScript code for rebuilding the website"""
    start_time = time.time()
    
    print(f"[CODE_GEN] Starting frontend code generation...")
    
    try:
        # Generate HTML
        html_code = generate_html_code(tech_data, content_data)
        
        # Generate CSS
        css_code = generate_css_code(tech_data)
        
        # Generate JavaScript (if needed)
        js_code = generate_javascript_code(tech_data)
        
        processing_time = time.time() - start_time
        
        return {
            "html_code": html_code,
            "css_code": css_code,
            "javascript_code": js_code,
            "files_generated": ["index.html", "styles.css", "script.js"],
            "processing_time_seconds": round(processing_time, 3)
        }
        
    except Exception as e:
        raise ValueError(f"Frontend code generation failed: {str(e)}")

# ADD THESE HELPER FUNCTIONS (for code generation)
def generate_html_code(tech_data: dict, content_data: dict) -> str:
    """Generate improved HTML code with actual content"""
    
    metadata = tech_data.get("metadata", {})
    layout = tech_data.get("layoutAnalysis", {})
    title = content_data.get("title", "Generated Page")
    headings = content_data.get("headings", [])
    paragraphs = content_data.get("paragraphs", [])
    main_content = content_data.get("mainContent", "")
    
    html = f"""<!DOCTYPE html>
<html lang="{metadata.get('lang', 'en')}">
<head>
    <meta charset="{metadata.get('charset', 'UTF-8')}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{metadata.get('description', '')}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>"""
    
    # Add header if detected
    if layout.get("hasHeader"):
        html += f"""
    <header class="site-header">
        <div class="container">
            <h1 class="site-title">{title}</h1>
        </div>
    </header>"""
    
    # Add navigation if detected
    if layout.get("hasNav"):
        html += """
    <nav class="site-nav">
        <div class="container">
            <ul class="nav-menu">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#content">Content</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </div>
    </nav>"""
    
    # Add main content with actual extracted content
    html += """
    <main class="main-content">
        <div class="container">"""
    
    # Add extracted headings and content strategically
    content_sections = []
    
    # Group content into sections (limit to 3-5 sections)
    if headings:
        # Take first 3-5 headings as section markers
        main_headings = [h for h in headings if h['level'] <= 2][:4]
        
        for i, heading in enumerate(main_headings):
            content_sections.append({
                'title': heading['text'],
                'content': paragraphs[i] if i < len(paragraphs) else f"Content related to {heading['text']}"
            })
    
    # If no good headings, create sections from paragraphs
    if not content_sections and paragraphs:
        content_sections = [
            {'title': 'Introduction', 'content': paragraphs[0] if len(paragraphs) > 0 else ''},
            {'title': 'Main Content', 'content': paragraphs[1] if len(paragraphs) > 1 else ''},
            {'title': 'Details', 'content': paragraphs[2] if len(paragraphs) > 2 else ''}
        ]
    
    # Generate sections
    for i, section in enumerate(content_sections[:4]):  # Limit to 4 sections
        if section['title'] and section['content']:
            level = 2 if i == 0 else 3
            html += f"""
            <section class="content-section">
                <h{level}>{section['title']}</h{level}>
                <p>{section['content'][:500]}{'...' if len(section['content']) > 500 else ''}</p>
            </section>"""
    
    # Add a summary section if we have main content
    if main_content and len(main_content) > 100:
        # Create a brief summary from the beginning of the content
        summary = main_content[:300] + "..." if len(main_content) > 300 else main_content
        html += f"""
            <section class="content-section">
                <h3>Summary</h3>
                <p>{summary}</p>
            </section>"""
    
    html += """
        </div>
    </main>"""
    
    # Add footer if detected
    if layout.get("hasFooter"):
        html += f"""
    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2024 {title}. Generated from original content.</p>
        </div>
    </footer>"""
    
    html += """
    <script src="script.js"></script>
</body>
</html>"""
    
    return html

def generate_css_code(tech_data: dict) -> str:
    """Generate CSS code based on analyzed styles"""
    
    layout = tech_data.get("layoutAnalysis", {})
    
    css = """/* Generated CSS based on analyzed website */

/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header styles */
.site-header {
    background-color: #f8f9fa;
    padding: 1rem 0;
    border-bottom: 1px solid #e9ecef;
}

.site-title {
    font-size: 2rem;
    font-weight: 600;
    color: #2c3e50;
}

/* Navigation styles */
.site-nav {
    background-color: #2c3e50;
    padding: 0.75rem 0;
}

.nav-menu {
    list-style: none;
    display: flex;
    gap: 2rem;
}

.nav-menu a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

.nav-menu a:hover {
    color: #3498db;
}

/* Main content styles */
.main-content {
    padding: 2rem 0;
    min-height: 60vh;
}

.main-content h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
}

.main-content h2 {
    font-size: 2rem;
    margin: 1.5rem 0 1rem;
    color: #34495e;
}

.main-content h3 {
    font-size: 1.5rem;
    margin: 1.25rem 0 0.75rem;
    color: #34495e;
}

.main-content p {
    margin-bottom: 1rem;
    line-height: 1.7;
}
/* ADD these section styles to the CSS generation: */

.content-section {
    margin-bottom: 2rem;
    padding: 1.5rem 0;
    border-bottom: 1px solid #eee;
}

.content-section:last-child {
    border-bottom: none;
}

.content-section h2 {
    color: #2c3e50;
    margin-bottom: 1rem;
    font-size: 2rem;
}

.content-section h3 {
    color: #34495e;
    margin-bottom: 0.75rem;
    font-size: 1.5rem;
}

.content-section p {
    line-height: 1.8;
    color: #555;
    margin-bottom: 1rem;
}

/* Footer styles */
.site-footer {
    background-color: #2c3e50;
    color: white;
    text-align: center;
    padding: 1.5rem 0;
    margin-top: 2rem;
}

/* Responsive design */
@media (max-width: 768px) {
    .container {
        padding: 0 15px;
    }
    
    .nav-menu {
        flex-direction: column;
        gap: 1rem;
    }
    
    .site-title {
        font-size: 1.5rem;
    }
    
    .main-content h1 {
        font-size: 2rem;
    }
}"""
    
    return css

def generate_javascript_code(tech_data: dict) -> str:
    """Generate JavaScript code based on detected functionality"""
    
    frameworks = tech_data.get("jsAnalysis", {}).get("frameworks", [])
    
    js = """// Generated JavaScript based on analyzed website

document.addEventListener('DOMContentLoaded', function() {
    console.log('Website loaded and ready');
    
    // Add smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add mobile menu toggle if needed
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu && window.innerWidth <= 768) {
        // Mobile menu functionality would go here
        console.log('Mobile layout detected');
    }
    
    // Add any interactive elements
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Button clicked:', this.textContent);
        });
    });
});

// Utility functions
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Export for use in other scripts if needed
window.siteUtils = {
    showMessage
};"""
    
    return js

# ADD THIS NEW COMPREHENSIVE WORKFLOW (this is the main addition)
@workflow.defn
class WebsiteGenerationWorkflow:
    """
    Comprehensive workflow that combines all steps:
    1. Screenshots the website
    2. Extracts content and analyzes with AI
    3. Generates technical specification  
    4. Produces frontend code for rebuilding
    """
    
    @workflow.run
    async def run(self, url: str) -> dict:
        workflow_id = workflow.info().workflow_id
        
        try:
            if not isinstance(url, str) or not url.strip():
                raise ValueError("URL cannot be empty")
            
            await workflow.execute_activity(
                log_processing_activity,
                args=(f"Starting comprehensive website generation for: {url}", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Step 1: Capture screenshot
            await workflow.execute_activity(
                log_processing_activity,
                args=("Step 1: Capturing screenshot", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            screenshot_result = await workflow.execute_activity(
                capture_screenshot_activity,
                args=(url,),
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=20),
                    maximum_attempts=3
                )
            )
            
            # Step 2: Extract and analyze content
            await workflow.execute_activity(
                log_processing_activity,
                args=("Step 2: Extracting and analyzing content", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            content_data = await workflow.execute_activity(
                extract_page_content_activity,
                args=(url,),
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=20),
                    maximum_attempts=3
                )
            )
            
            # Step 3: Generate technical specification
            await workflow.execute_activity(
                log_processing_activity,
                args=("Step 3: Generating technical specification", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            tech_spec = await workflow.execute_activity(
                generate_technical_specification_activity,
                args=(url,),
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=3),
                    maximum_interval=timedelta(seconds=30),
                    maximum_attempts=3
                )
            )
            
            # Step 4: Generate frontend code
            await workflow.execute_activity(
                log_processing_activity,
                args=("Step 4: Generating frontend code", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            frontend_code = await workflow.execute_activity(
                generate_frontend_code_activity,
                args=(tech_spec["technical_data"], content_data),
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=20),
                    maximum_attempts=2
                )
            )
            
            # Calculate total processing time
            total_time = (
                screenshot_result.get("processing_time_seconds", 0) +
                content_data.get("processing_time_seconds", 0) +
                tech_spec.get("processing_time_seconds", 0) +
                frontend_code.get("processing_time_seconds", 0)
            )
            
            await workflow.execute_activity(
                log_processing_activity,
                args=(f"Website generation completed in {total_time:.2f}s", workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return {
                "url": url,
                "screenshot": {
                    "page_title": screenshot_result["page_title"],
                    "screenshot_data": screenshot_result["screenshot_data"],
                    "session_id": screenshot_result["session_id"],
                    "replay_url": screenshot_result["replay_url"]
                },
                "content_analysis": content_data,
                "technical_specification": tech_spec,
                "generated_code": {
                    "html": frontend_code["html_code"],
                    "css": frontend_code["css_code"],
                    "javascript": frontend_code["javascript_code"],
                    "files": frontend_code["files_generated"]
                },
                "workflow_id": workflow_id,
                "status": "completed",
                "total_processing_time_seconds": total_time
            }
            
        except Exception as e:
            error_msg = f"Website generation workflow failed: {str(e)}"
            await workflow.execute_activity(
                log_processing_activity,
                args=(error_msg, workflow_id),
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            return {
                "url": url,
                "screenshot": None,
                "content_analysis": None,
                "technical_specification": None,
                "generated_code": None,
                "error": error_msg,
                "workflow_id": workflow_id,
                "status": "failed"
            }