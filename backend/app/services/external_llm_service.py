import os
import httpx
from typing import Dict, Any, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)

class ExternalLLMService:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        logger.info(f"External LLM service initialized provider={self.provider}")

    async def generate_response(self, query: str, context: str = "", user_id: int = 1) -> Dict[str, Any]:
        """Generate AI response using external LLM service"""
        try:
            if self.provider == "openai" and self.openai_api_key:
                return await self._call_openai(query, context)
            elif self.provider == "anthropic" and self.anthropic_api_key:
                return await self._call_anthropic(query, context)
            else:
                # Fallback to demo response
                return self._generate_demo_response(query, context)
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._generate_demo_response(query, context)

    async def _call_openai(self, query: str, context: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        prompt = self._build_prompt(query, context)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.openai_model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant for the Nuvaru Domain-Centric Learning Platform. Provide accurate, helpful responses based on the provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data["choices"][0]["message"]["content"],
                    "provider": "openai",
                    "model": self.openai_model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                }
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return self._generate_demo_response(query, context)

    async def _call_anthropic(self, query: str, context: str) -> Dict[str, Any]:
        """Call Anthropic API"""
        prompt = self._build_prompt(query, context)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.anthropic_model,
                    "max_tokens": 500,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data["content"][0]["text"],
                    "provider": "anthropic",
                    "model": self.anthropic_model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                }
            else:
                logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                return self._generate_demo_response(query, context)

    def _build_prompt(self, query: str, context: str) -> str:
        """Build prompt for LLM"""
        if context:
            return f"""Context from your knowledge base:
{context}

User question: {query}

Please provide a helpful response based on the context above. If the context doesn't contain relevant information, let the user know and suggest they upload more relevant documents."""
        else:
            return f"""User question: {query}

Please provide a helpful response. Note that no specific context from documents was found, so you may want to suggest the user upload relevant documents to get more specific answers."""

    def _generate_demo_response(self, query: str, context: str) -> Dict[str, Any]:
        """Generate demo response when external services are not available"""
        if context:
            response = f"""Based on the provided context, I can help you with your question about "{query}". 

The context contains relevant information that I can use to provide a more specific answer. However, I'm currently running in demo mode without access to external LLM services.

To get full AI-powered responses, please configure your API keys in the environment variables:
- OPENAI_API_KEY for OpenAI services
- ANTHROPIC_API_KEY for Anthropic services

Context available: {len(context)} characters of relevant information."""
        else:
            response = f"""I understand you're asking about "{query}". 

I'm currently running in demo mode without access to external LLM services. To get full AI-powered responses, please:

1. Configure your API keys in the environment variables
2. Upload relevant documents to provide context for better answers

Available providers:
- OpenAI (set OPENAI_API_KEY)
- Anthropic (set ANTHROPIC_API_KEY)"""

        return {
            "response": response,
            "provider": "demo",
            "model": "demo-mode",
            "tokens_used": 0
        }


