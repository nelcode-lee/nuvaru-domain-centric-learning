"""
Learning engine service for RAG (Retrieval-Augmented Generation)
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple
import structlog
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import LLMError, VectorDatabaseError
from app.core.logging import get_logger
from app.services.vector_service import VectorService
from app.services.embedding_service import EmbeddingService
from app.services.ollama_service import OllamaService

logger = get_logger(__name__)


class LearningService:
    """Service for RAG-based learning and AI interactions"""
    
    def __init__(self):
        """Initialize learning service"""
        self.vector_service = VectorService()
        self.embedding_service = EmbeddingService()
        self.ollama_service = OllamaService()
        
        logger.info("Learning service initialized successfully")
    
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
            
            # Step 3: Generate AI response using Ollama
            ai_response = self._generate_ai_response(
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
                embedding_model=self.embedding_service.model,
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
                return "No relevant documents found."
            
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
    
    def _generate_ai_response(
        self,
        message: str,
        context: str,
        conversation_context: Optional[str] = None
    ) -> str:
        """Generate AI response using Ollama LLM"""
        try:
            # Build prompt for RAG
            prompt = self._build_rag_prompt(message, context, conversation_context)
            
            # Generate response using Ollama
            response = self.ollama_service.generate_response(
                prompt=prompt,
                model=settings.OLLAMA_MODEL
            )
            
            logger.info("AI response generated successfully", response_length=len(response))
            
            return response
            
        except Exception as e:
            logger.error("Failed to generate AI response", error=str(e))
            raise LLMError("Failed to generate AI response")
    
    def _build_rag_prompt(
        self,
        message: str,
        context: str,
        conversation_context: Optional[str] = None
    ) -> str:
        """Build prompt for RAG-based response generation"""
        
        system_prompt = """You are a helpful AI assistant for the Nuvaru Domain-Centric Learning Platform. 
Your role is to provide accurate, helpful responses based on the provided context documents.

Guidelines:
1. Use only the information provided in the context documents
2. If the context doesn't contain relevant information, say so clearly
3. Cite specific sources when possible
4. Provide accurate, factual responses
5. Be helpful and professional
6. If asked about topics not covered in the context, explain the limitations

Context Documents:
{context}

User Question: {message}

Please provide a helpful response based on the context documents above."""

        # Add conversation context if provided
        if conversation_context:
            system_prompt += f"\n\nPrevious conversation context: {conversation_context}"
        
        prompt = system_prompt.format(
            context=context,
            message=message
        )
        
        return prompt
    
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
                "knowledge_bases": self.vector_service.list_knowledge_bases(),
                "last_updated": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            
            logger.info("Knowledge base stats retrieved", user_id=user_id)
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get knowledge base stats", error=str(e), user_id=user_id)
            raise LLMError("Failed to get knowledge base stats")
    
    def improve_knowledge_base(
        self,
        user_id: int,
        knowledge_base_id: str,
        feedback_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Improve knowledge base based on user feedback
        
        Args:
            user_id: ID of the user
            knowledge_base_id: Knowledge base ID
            feedback_data: List of feedback entries
            
        Returns:
            Improvement confirmation
        """
        try:
            # TODO: Implement knowledge base improvement
            # This could include:
            # 1. Re-ranking documents based on feedback
            # 2. Updating embedding models
            # 3. Adding new documents
            # 4. Removing irrelevant documents
            # 5. Fine-tuning retrieval parameters
            
            logger.info(
                "Knowledge base improvement initiated",
                user_id=user_id,
                knowledge_base_id=knowledge_base_id,
                feedback_count=len(feedback_data)
            )
            
            return {
                "message": "Knowledge base improvement initiated",
                "knowledge_base_id": knowledge_base_id,
                "improvements_applied": len(feedback_data),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to improve knowledge base", error=str(e), user_id=user_id)
            raise LLMError("Failed to improve knowledge base")



