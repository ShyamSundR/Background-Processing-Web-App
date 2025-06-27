# Temporal workflows for string processing
# Workflow patterns adapted from: https://github.com/temporalio/samples-python/tree/main/hello
# Activity patterns from: https://docs.temporal.io/python/activities

from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from datetime import timedelta
import asyncio
import time
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