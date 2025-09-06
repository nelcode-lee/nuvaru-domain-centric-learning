"""
Ollama service for local LLM integration
"""

import requests
import json
from typing import Dict, Any, Optional, List
import structlog

from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self):
        """Initialize Ollama service"""
        self.base_url = f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}"
        self.model = settings.OLLAMA_MODEL
        self.timeout = 30  # seconds
        
        # Test connection
        self._test_connection()
        
        logger.info(
            "Ollama service initialized",
            base_url=self.base_url,
            model=self.model
        )
    
    def _test_connection(self) -> None:
        """Test connection to Ollama service"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            logger.info("Ollama connection test successful")
            
        except Exception as e:
            logger.error("Failed to connect to Ollama service", error=str(e))
            raise LLMError("Failed to connect to Ollama service")
    
    def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response using Ollama LLM
        
        Args:
            prompt: Input prompt
            model: Model to use (defaults to configured model)
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            if model is None:
                model = self.model
            
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            generated_text = result.get("response", "")
            
            logger.info(
                "Response generated successfully",
                model=model,
                prompt_length=len(prompt),
                response_length=len(generated_text)
            )
            
            return generated_text
            
        except requests.exceptions.RequestException as e:
            logger.error("Ollama request failed", error=str(e))
            raise LLMError("Failed to generate response from Ollama")
        except Exception as e:
            logger.error("Failed to generate response", error=str(e))
            raise LLMError("Failed to generate response")
    
    def generate_streaming_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> List[str]:
        """
        Generate streaming response using Ollama LLM
        
        Args:
            prompt: Input prompt
            model: Model to use (defaults to configured model)
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            List of response chunks
        """
        try:
            if model is None:
                model = self.model
            
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            # Make streaming request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Process streaming response
            chunks = []
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            chunks.append(data['response'])
                    except json.JSONDecodeError:
                        continue
            
            logger.info(
                "Streaming response generated successfully",
                model=model,
                chunks_count=len(chunks)
            )
            
            return chunks
            
        except requests.exceptions.RequestException as e:
            logger.error("Ollama streaming request failed", error=str(e))
            raise LLMError("Failed to generate streaming response from Ollama")
        except Exception as e:
            logger.error("Failed to generate streaming response", error=str(e))
            raise LLMError("Failed to generate streaming response")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models in Ollama
        
        Returns:
            List of available models
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            
            result = response.json()
            models = result.get("models", [])
            
            logger.info("Models listed successfully", count=len(models))
            
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to list models", error=str(e))
            raise LLMError("Failed to list Ollama models")
        except Exception as e:
            logger.error("Failed to list models", error=str(e))
            raise LLMError("Failed to list models")
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            Pull status information
        """
        try:
            payload = {
                "name": model_name,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=300  # 5 minutes for model download
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Model pulled successfully", model=model_name)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to pull model", error=str(e), model=model_name)
            raise LLMError(f"Failed to pull model {model_name}")
        except Exception as e:
            logger.error("Failed to pull model", error=str(e), model=model_name)
            raise LLMError(f"Failed to pull model {model_name}")
    
    def delete_model(self, model_name: str) -> Dict[str, Any]:
        """
        Delete a model from Ollama
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            Deletion status information
        """
        try:
            payload = {
                "name": model_name
            }
            
            response = requests.delete(
                f"{self.base_url}/api/delete",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("Model deleted successfully", model=model_name)
            
            return {"message": f"Model {model_name} deleted successfully"}
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to delete model", error=str(e), model=model_name)
            raise LLMError(f"Failed to delete model {model_name}")
        except Exception as e:
            logger.error("Failed to delete model", error=str(e), model=model_name)
            raise LLMError(f"Failed to delete model {model_name}")
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model (defaults to configured model)
            
        Returns:
            Model information
        """
        try:
            if model_name is None:
                model_name = self.model
            
            payload = {
                "name": model_name
            }
            
            response = requests.post(
                f"{self.base_url}/api/show",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("Model info retrieved successfully", model=model_name)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get model info", error=str(e), model=model_name)
            raise LLMError(f"Failed to get model info for {model_name}")
        except Exception as e:
            logger.error("Failed to get model info", error=str(e), model=model_name)
            raise LLMError(f"Failed to get model info for {model_name}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Ollama service
        
        Returns:
            Health status information
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            # Get model info
            models = self.list_models()
            current_model_info = None
            
            for model in models:
                if model.get("name") == self.model:
                    current_model_info = model
                    break
            
            health_status = {
                "status": "healthy",
                "base_url": self.base_url,
                "model": self.model,
                "model_available": current_model_info is not None,
                "total_models": len(models),
                "timestamp": "2024-01-01T00:00:00Z"  # Placeholder
            }
            
            if current_model_info:
                health_status["model_info"] = current_model_info
            
            logger.info("Health check completed", status="healthy")
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "base_url": self.base_url,
                "model": self.model
            }
    
    def create_custom_prompt(
        self,
        base_prompt: str,
        context: str,
        user_instructions: str
    ) -> str:
        """
        Create a custom prompt for specific use cases
        
        Args:
            base_prompt: Base prompt template
            context: Context information
            user_instructions: Specific user instructions
            
        Returns:
            Formatted prompt
        """
        try:
            custom_prompt = f"""
{base_prompt}

Context:
{context}

User Instructions:
{user_instructions}

Please provide a helpful response based on the context and instructions above.
"""
            
            logger.info("Custom prompt created", prompt_length=len(custom_prompt))
            
            return custom_prompt
            
        except Exception as e:
            logger.error("Failed to create custom prompt", error=str(e))
            raise LLMError("Failed to create custom prompt")



