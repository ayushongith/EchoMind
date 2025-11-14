import os
import requests
import json
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIProcessor:
    def __init__(self, api_key: str = None, model: str = "openai/gpt-3.5-turbo"):
        """
        Initialize the AI processor with API key and model.
        
        Args:
            api_key (str): OpenRouter API key. If None, will try to get from environment variable.
            model (str): The AI model to use. Default is 'openai/gpt-3.5-turbo'.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://echomind-ai.vercel.app",  # Optional, for tracking
            "X-Title": "EchoMind AI Assistant"  # Optional, shown in rankings on openrouter.ai
        }
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """
        Generate a response using the OpenRouter API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
                     Example: [{"role": "user", "content": "Hello!"}]
            **kwargs: Additional parameters to pass to the API (temperature, max_tokens, etc.)
            
        Returns:
            str: Generated response text, or None if the request failed.
        """
        # Default parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop": None
        }
        
        # Update with any additional parameters
        params.update(kwargs)
        
        try:
            self.logger.info(f"Sending request to {self.model}...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=params,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making API request: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    self.logger.error(f"API Error Details: {json.dumps(error_detail, indent=2)}")
                except:
                    self.logger.error(f"API Error Response: {e.response.text}")
            return None
    
    def process_conversation(self, user_input: str, conversation_history: List[Dict[str, str]] = None, 
                           system_prompt: str = None) -> str:
        """
        Process a conversation turn with optional history and system prompt.
        
        Args:
            user_input: The user's input text.
            conversation_history: List of previous messages in the conversation.
            system_prompt: Optional system message to set the assistant's behavior.
            
        Returns:
            str: The AI's response text.
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        # Generate response
        return self.generate_response(messages)

# Example usage
if __name__ == "__main__":
    # Initialize with your API key and model
    ai = AIProcessor(model="openai/gpt-3.5-turbo")
    
    # Example conversation
    response = ai.process_conversation(
        "Hello, how are you?",
        system_prompt="You are a helpful AI assistant."
    )
    
    print(f"AI: {response}")
