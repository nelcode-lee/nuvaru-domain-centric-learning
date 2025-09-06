"""
Simplified learning service for development without heavy dependencies
"""

import uuid
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import LLMError, VectorDatabaseError
from app.core.logging import get_logger
from app.services.simple_vector_service import SimpleVectorService
from app.services.simple_embedding_service import SimpleEmbeddingService
from app.services.openai_service import OpenAIService

logger = get_logger(__name__)


class SimpleLearningService:
    """Simplified learning service for RAG-based learning and AI interactions"""
    
    def __init__(self):
        """Initialize learning service"""
        self.vector_service = SimpleVectorService()
        self.embedding_service = SimpleEmbeddingService()
        self.openai_service = OpenAIService()
        
        logger.info("Simple learning service initialized successfully")
    
    def chat_with_ai(
        self,
        message: str,
        user_id: int,
        knowledge_base_id: Optional[str] = None,
        context: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with AI using RAG (Retrieval-Augmented Generation)
        
        Args:
            message: User's message/query
            user_id: ID of the user
            knowledge_base_id: Optional knowledge base filter
            context: Optional context for the conversation
            session_id: Optional session ID for conversation continuity
            
        Returns:
            AI response with sources and metadata
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Step 1: Retrieve relevant documents using vector search
            relevant_docs = self._retrieve_relevant_documents(
                query=message,
                user_id=user_id,
                knowledge_base_id=knowledge_base_id,
                limit=5
            )
            
            # Step 2: Build context from retrieved documents
            context_text = self._build_context_from_documents(relevant_docs)
            
            # Step 3: Generate AI response using OpenAI
            ai_response = self._generate_openai_response(
                message=message,
                context=context_text,
                conversation_context=context
            )
            
            # Step 4: Prepare response with sources
            response = {
                "response": ai_response,
                "sources": self._format_sources(relevant_docs),
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "user_id": user_id,
                    "knowledge_base_id": knowledge_base_id,
                    "sources_count": len(relevant_docs),
                    "context_length": len(context_text)
                }
            }
            
            logger.info(
                "AI chat completed successfully",
                user_id=user_id,
                session_id=session_id,
                sources_count=len(relevant_docs)
            )
            
            return response
            
        except Exception as e:
            logger.error("Failed to process AI chat", error=str(e), user_id=user_id)
            raise LLMError("Failed to process AI chat")
    
    def _retrieve_relevant_documents(
        self,
        query: str,
        user_id: int,
        knowledge_base_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using vector similarity search"""
        try:
            # Create metadata filter
            where_filter = {"user_id": user_id}
            if knowledge_base_id:
                where_filter["knowledge_base_id"] = knowledge_base_id
            
            # Search for similar documents
            similar_docs = self.vector_service.search_similar(
                query_text=query,
                embedding_model=self.embedding_service,
                n_results=limit,
                where=where_filter
            )
            
            logger.info(
                "Relevant documents retrieved",
                query_length=len(query),
                results_count=len(similar_docs)
            )
            
            return similar_docs
            
        except Exception as e:
            logger.error("Failed to retrieve relevant documents", error=str(e))
            raise VectorDatabaseError("Failed to retrieve relevant documents")
    
    def _build_context_from_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents"""
        try:
            if not documents:
                return "No relevant documents found in the knowledge base."
            
            context_parts = []
            for i, doc in enumerate(documents, 1):
                # Extract relevant information
                doc_text = doc.get("document", "")
                metadata = doc.get("metadata", {})
                similarity = doc.get("similarity", 0)
                
                # Build context entry
                context_entry = f"Source {i} (Relevance: {similarity:.2f}):\n{doc_text}\n"
                context_parts.append(context_entry)
            
            context = "\n".join(context_parts)
            
            # Truncate if too long
            max_context_length = settings.MAX_CONTEXT_LENGTH - 500  # Leave room for prompt
            if len(context) > max_context_length:
                context = context[:max_context_length] + "..."
            
            logger.info("Context built from documents", context_length=len(context))
            
            return context
            
        except Exception as e:
            logger.error("Failed to build context from documents", error=str(e))
            raise LLMError("Failed to build context from documents")
    
    def _generate_openai_response(
        self,
        message: str,
        context: str,
        conversation_context: Optional[str] = None
    ) -> str:
        """Generate AI response using OpenAI API"""
        try:
            # Use OpenAI service to generate response
            ai_response = self.openai_service.generate_response(
                message=message,
                context=context,
                conversation_history=None,  # TODO: Implement conversation history
                system_prompt=None  # Use default system prompt
            )
            
            logger.info("OpenAI response generated", response_length=len(ai_response))
            
            return ai_response
            
        except Exception as e:
            logger.error("Failed to generate OpenAI response", error=str(e))
            # Fallback to simple response if OpenAI fails
            return self._generate_fallback_response(message, context)
    
    def _generate_fallback_response(
        self,
        message: str,
        context: str
    ) -> str:
        """Generate fallback response if OpenAI fails"""
        try:
            if "No relevant documents found" in context:
                response = f"I don't have specific information about '{message}' in the knowledge base. Please upload relevant documents to get better answers."
            else:
                # Extract key information from context
                context_summary = self._extract_key_information(context)
                
                response = f"Based on the available information:\n\n{context_summary}\n\nThis information is relevant to your question: '{message}'. For more detailed answers, please ensure you have uploaded comprehensive documents to the knowledge base."
            
            logger.info("Fallback AI response generated", response_length=len(response))
            
            return response
            
        except Exception as e:
            logger.error("Failed to generate fallback response", error=str(e))
            return "I apologize, but I'm unable to process your request at the moment. Please try again later."
    
    def _extract_key_information(self, context: str) -> str:
        """Extract key information from context"""
        try:
            # Simple extraction - take first few sentences from each source
            lines = context.split('\n')
            key_info = []
            
            for line in lines:
                if line.startswith('Source') and ':' in line:
                    # This is a source header, skip
                    continue
                elif line.strip() and not line.startswith('Source'):
                    # This is content, take first sentence
                    sentences = line.split('.')
                    if sentences:
                        first_sentence = sentences[0].strip()
                        if first_sentence and len(first_sentence) > 10:
                            key_info.append(f"• {first_sentence}.")
            
            return '\n'.join(key_info[:3])  # Limit to 3 key points
            
        except Exception as e:
            logger.error("Failed to extract key information", error=str(e))
            return "Key information extracted from available sources."
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for response"""
        sources = []
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            source = {
                "document_id": metadata.get("doc_id", "unknown"),
                "title": metadata.get("original_filename", "Unknown Document"),
                "relevance_score": doc.get("similarity", 0),
                "excerpt": doc.get("document", "")[:200] + "..." if len(doc.get("document", "")) > 200 else doc.get("document", ""),
                "metadata": {
                    "content_type": metadata.get("content_type", "unknown"),
                    "uploaded_at": metadata.get("processed_at", "unknown"),
                    "chunk_index": metadata.get("chunk_index", 0)
                }
            }
            sources.append(source)
        
        return sources
    
    def submit_feedback(
        self,
        session_id: str,
        response_id: str,
        rating: int,
        feedback: str,
        correctness: bool,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Submit feedback for learning improvement
        
        Args:
            session_id: Session ID
            response_id: Response ID
            rating: Rating (1-5)
            feedback: Text feedback
            correctness: Whether the response was correct
            user_id: ID of the user
            
        Returns:
            Feedback confirmation
        """
        try:
            # Store feedback (in production, this would go to a database)
            feedback_data = {
                "session_id": session_id,
                "response_id": response_id,
                "rating": rating,
                "feedback": feedback,
                "correctness": correctness,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # TODO: Store feedback in database for learning improvement
            # This could be used to:
            # 1. Improve retrieval algorithms
            # 2. Fine-tune response generation
            # 3. Update document relevance scores
            # 4. Train custom models
            
            logger.info(
                "Feedback submitted successfully",
                session_id=session_id,
                rating=rating,
                user_id=user_id
            )
            
            return {
                "message": "Feedback submitted successfully",
                "feedback_id": str(uuid.uuid4()),
                "timestamp": feedback_data["timestamp"]
            }
            
        except Exception as e:
            logger.error("Failed to submit feedback", error=str(e), user_id=user_id)
            raise LLMError("Failed to submit feedback")
    
    def get_learning_sessions(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get learning sessions for a user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return
            
        Returns:
            List of learning sessions
        """
        try:
            # TODO: Implement session storage and retrieval
            # For now, return placeholder data
            
            sessions = [
                {
                    "session_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "started_at": datetime.utcnow().isoformat(),
                    "ended_at": None,
                    "message_count": 0,
                    "satisfaction_score": None,
                    "knowledge_base_id": None
                }
            ]
            
            logger.info("Learning sessions retrieved", user_id=user_id, count=len(sessions))
            
            return sessions
            
        except Exception as e:
            logger.error("Failed to get learning sessions", error=str(e), user_id=user_id)
            raise LLMError("Failed to get learning sessions")
    
    def get_knowledge_base_stats(
        self,
        user_id: int,
        knowledge_base_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for knowledge base usage
        
        Args:
            user_id: ID of the user
            knowledge_base_id: Optional knowledge base filter
            
        Returns:
            Knowledge base statistics
        """
        try:
            # Get collection info
            collection_info = self.vector_service.get_collection_info()
            
            # TODO: Implement more detailed statistics
            # - Query frequency
            # - Most accessed documents
            # - User satisfaction scores
            # - Response accuracy metrics
            
            stats = {
                "total_documents": collection_info.get("count", 0),
                "knowledge_bases": [],  # TODO: Implement knowledge base listing
                "last_updated": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            
            logger.info("Knowledge base stats retrieved", user_id=user_id)
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get knowledge base stats", error=str(e), user_id=user_id)
            raise LLMError("Failed to get knowledge base stats")
    
    def test_openai_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection"""
        try:
            is_connected = self.openai_service.test_connection()
            
            return {
                "openai_connected": is_connected,
                "model": self.openai_service.model,
                "available_models": self.openai_service.get_available_models() if is_connected else [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to test OpenAI connection", error=str(e))
            return {
                "openai_connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def configure_openai(
        self,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None
    ) -> Dict[str, Any]:
        """Configure OpenAI parameters"""
        try:
            if model:
                self.openai_service.set_model(model)
            
            if max_tokens is not None or temperature is not None:
                self.openai_service.set_parameters(max_tokens, temperature)
            
            return {
                "message": "OpenAI configuration updated successfully",
                "model": self.openai_service.model,
                "max_tokens": self.openai_service.max_tokens,
                "temperature": self.openai_service.temperature,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to configure OpenAI", error=str(e))
            raise LLMError("Failed to configure OpenAI")


