"""
OpenAI service for AI chat functionality
"""

import os
from typing import List, Dict, Any, Optional
import structlog
from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        """Initialize OpenAI service"""
        self.client = None
        self.model = "gpt-3.5-turbo"  # Default model
        self.max_tokens = 1000
        self.temperature = 0.7
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            # For development, you can set a placeholder
            # In production, this should be properly configured
            api_key = "your-openai-api-key-here"
        
        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI service initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenAI service", error=str(e))
            raise LLMError("Failed to initialize OpenAI service")
    
    def generate_response(
        self,
        message: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate AI response using OpenAI API
        
        Args:
            message: User's message
            context: Retrieved context from knowledge base
            conversation_history: Previous conversation messages
            system_prompt: Custom system prompt
            
        Returns:
            AI generated response
        """
        try:
            if not self.client:
                raise LLMError("OpenAI client not initialized")
            
            # Default system prompt
            if not system_prompt:
                system_prompt = """You are a helpful AI assistant for a domain-centric learning system. 
                You have access to a knowledge base of documents and should provide accurate, helpful responses 
                based on the available information. Always cite your sources when possible and be honest about 
                the limitations of your knowledge."""
            
            # Build messages array
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add context if available
            if context and "No relevant documents found" not in context:
                context_message = f"Based on the following information from the knowledge base:\n\n{context}\n\n"
                messages.append({"role": "user", "content": context_message + message})
            else:
                messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract response content
            ai_response = response.choices[0].message.content
            
            logger.info(
                "OpenAI response generated successfully",
                response_length=len(ai_response),
                model=self.model
            )
            
            return ai_response
            
        except Exception as e:
            logger.error("Failed to generate OpenAI response", error=str(e))
            raise LLMError(f"Failed to generate AI response: {str(e)}")
    
    def set_model(self, model: str):
        """Set the OpenAI model to use"""
        self.model = model
        logger.info("OpenAI model updated", model=model)
    
    def set_parameters(self, max_tokens: int = None, temperature: float = None):
        """Set model parameters"""
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
        
        logger.info(
            "OpenAI parameters updated",
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            if not self.client:
                return []
            
            models = self.client.models.list()
            model_names = [model.id for model in models.data]
            
            # Filter for chat completion models
            chat_models = [name for name in model_names if 'gpt' in name.lower()]
            
            logger.info("Available OpenAI models retrieved", count=len(chat_models))
            return chat_models
            
        except Exception as e:
            logger.error("Failed to get available models", error=str(e))
            return []
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            if not self.client:
                return False
            
            # Simple test call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            logger.info("OpenAI connection test successful")
            return True
            
        except Exception as e:
            logger.error("OpenAI connection test failed", error=str(e))
            return False

