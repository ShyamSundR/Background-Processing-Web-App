# LLM service for text summarization using Hugging Face Inference API 
# Hugging Face integration patterns adapted from: https://huggingface.co/docs/api-inference/quicktour
# HTTP client patterns from: https://docs.python-requests.org/

import os
import httpx
import asyncio
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from transformers import pipeline
import logging

load_dotenv()

class LLMService:
    """
    Service class for handling Hugging Face text summarization (FREE)
    
    Uses Hugging Face's free Inference API with:
    - BART for summarization (facebook/bart-large-cnn)
    
    No payment required - just need a free HF account and API token
    """
    
    def __init__(self):
        """Initialize the LLM service with required models"""
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            logging.info("LLM Service initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize LLM Service: {e}")
            raise

    def is_configured(self) -> bool:
        """Check if the service is properly configured with API token"""
        return bool(self.api_token)
    
    async def summarize_text(self, text: str, style: str = "concise") -> str:
        """
        Summarize text using the BART model
        
        Args:
            text (str): Text to summarize
            style (str): Style of summary ("concise" or "detailed")
            
        Returns:
            str: Summarized text
        """
        try:
            # Set max length based on style
            max_length = 60 if style == "concise" else 100
            min_length = 30 if style == "concise" else 60
            
            # Generate summary
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]['summary_text']
            
            return summary
            
        except Exception as e:
            logging.error(f"Error in summarize_text: {e}")
            raise

# Example usage and testing
async def main():
    """Test function for LLM service"""
    service = LLMService()
    
    if not service.is_configured():
        print("LLM service not configured.")
        print("Setup steps:")
        print("1. Install transformers and torch")
        print("2. Run the script again")
        return
    
    # Test different styles
    test_text = "The weather today is quite nice and I think we should go outside for a walk."
    styles = ["concise", "detailed"]
    
    print(f"Original: {test_text}\n")
    
    for style in styles:
        try:
            result = await service.summarize_text(test_text, style)
            print(f"{style.upper()}: {result}\n")
        except Exception as e:
            print(f"Error with {style}: {e}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())