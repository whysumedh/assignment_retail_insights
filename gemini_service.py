"""
Gemini API service wrapper for Retail Insights Assistant.
Handles API calls, error handling, and rate limiting.
"""

import os
from typing import Optional, Dict, Any
from google import genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()


class GeminiService:
    """Service class for interacting with Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key. If None, loads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Set API key in environment for the client
        os.environ['GEMINI_API_KEY'] = self.api_key
        self.client = genai.Client()
        self.model = "gemini-2.5-flash"
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum seconds between requests (rate limiting)
    
    def generate_content(
        self, 
        prompt: str, 
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> str:
        """
        Generate content using Gemini API with error handling and retries.
        
        Args:
            prompt: The prompt to send to Gemini
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If all retries fail
        """
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        for attempt in range(max_retries):
            try:
                self.last_request_time = time.time()
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                return response.text
            
            except Exception as e:
                error_msg = str(e)
                print(f"Attempt {attempt + 1} failed: {error_msg}")
                
                # Check if it's a rate limit error
                if "rate limit" in error_msg.lower() or "429" in error_msg:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                # Check if it's a quota error
                if "quota" in error_msg.lower():
                    raise Exception("API quota exceeded. Please check your Gemini API quota.")
                
                # For other errors, retry with delay
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    raise Exception(f"Failed to generate content after {max_retries} attempts: {error_msg}")
        
        raise Exception("Failed to generate content after all retries")
    
    def chat_with_context(
        self,
        user_question: str,
        context_data: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response with context data (for RAG-like behavior).
        
        Args:
            user_question: User's question
            context_data: Relevant data context to include
            system_prompt: Optional system prompt for instructions
            
        Returns:
            Generated response
        """
        full_prompt = ""
        
        if system_prompt:
            full_prompt += f"{system_prompt}\n\n"
        
        full_prompt += f"Context Data:\n{context_data}\n\n"
        full_prompt += f"User Question: {user_question}\n\n"
        full_prompt += "Please provide a helpful and accurate answer based on the context data provided."
        
        return self.generate_content(full_prompt)
    
    def summarize_data(self, data_summary: Dict[str, Any]) -> str:
        """
        Generate a summary of the dataset.
        
        Args:
            data_summary: Dictionary containing data summary statistics
            
        Returns:
            Formatted summary text
        """
        summary_text = f"""
        Dataset Summary:
        - Total Products: {data_summary.get('total_products', 'N/A')}
        - Total SKUs: {data_summary.get('total_skus', 'N/A')}
        - Total Styles: {data_summary.get('total_styles', 'N/A')}
        - Categories: {', '.join(data_summary.get('categories', {}).keys())}
        - Price Range: ₹{data_summary.get('price_statistics', {}).get('min_price_overall', 'N/A')} - ₹{data_summary.get('price_statistics', {}).get('max_price_overall', 'N/A')}
        - Average Price: ₹{data_summary.get('price_statistics', {}).get('avg_price_overall', 'N/A'):.2f}
        """
        
        prompt = f"""Please provide a comprehensive, business-friendly summary of this retail pricing dataset.
        
        {summary_text}
        
        Include insights about:
        1. Product diversity and categorization
        2. Pricing patterns and ranges
        3. Platform availability
        4. Key observations that would be useful for business decision-making
        
        Format the response in a clear, professional manner suitable for business stakeholders."""
        
        return self.generate_content(prompt)


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create the singleton GeminiService instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

