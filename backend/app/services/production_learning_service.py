from typing import List, Dict, Any, Optional
from uuid import uuid4
from app.core.logging import get_logger
from app.services.simple_embedding_service import SimpleEmbeddingService
from app.services.production_vector_service import ProductionVectorService
from app.services.external_llm_service import ExternalLLMService

logger = get_logger(__name__)

class ProductionLearningService:
    def __init__(self):
        self.embedding_service = SimpleEmbeddingService()
        self.vector_service = ProductionVectorService()
        self.llm_service = ExternalLLMService()
        logger.info("Production learning service initialized successfully")

    async def chat_with_ai(self, user_id: int, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Chat with AI using RAG and external LLM services"""
        if session_id is None:
            session_id = str(uuid4())
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.encode_text(query)
            
            # Retrieve relevant documents
            retrieved_docs = self.vector_service.query_documents(query_embedding, n_results=3)
            
            # Build context from retrieved documents
            context = "\n".join([doc["document"] for doc in retrieved_docs])
            sources = [{"id": doc["id"], "content_snippet": doc["document"][:100]} for doc in retrieved_docs]
            
            # Generate AI response using external LLM
            llm_response = await self.llm_service.generate_response(query, context, user_id)
            
            logger.info(f"AI chat completed successfully session_id={session_id} user_id={user_id} sources_count={len(sources)} provider={llm_response.get('provider', 'unknown')}")
            
            return {
                "session_id": session_id,
                "response": llm_response["response"],
                "sources": sources,
                "feedback_needed": True,
                "provider": llm_response.get("provider", "demo"),
                "model": llm_response.get("model", "demo-mode"),
                "tokens_used": llm_response.get("tokens_used", 0)
            }
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return {
                "session_id": session_id,
                "response": f"I encountered an error processing your question: '{query}'. Please try again or contact support if the issue persists.",
                "sources": [],
                "feedback_needed": True,
                "provider": "error",
                "model": "error-mode",
                "tokens_used": 0
            }

    def submit_feedback(self, session_id: str, user_id: int, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Submit feedback for learning improvement"""
        logger.info(f"Feedback submitted session_id={session_id} user_id={user_id} feedback={feedback}")
        return {
            "message": "Feedback received. Thank you for helping improve the learning model!",
            "session_id": session_id
        }

    def get_learning_sessions(self, user_id: int, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get learning sessions for user"""
        # In a real implementation, this would query the database
        return []

    def get_knowledge_base_stats(self, user_id: int) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        collection_info = self.vector_service.get_collection_info()
        return {
            "total_documents": collection_info["count"],
            "total_chunks": collection_info["count"],
            "average_chunk_size": 0,
            "embedding_model": "simple-hash-embedding",
            "vector_database": "file-based-json",
            "llm_provider": self.llm_service.provider
        }

    def improve_knowledge_base(self, user_id: int, document_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Improve knowledge base based on feedback"""
        logger.info(f"Knowledge base improvement requested document_id={document_id} user_id={user_id} feedback={feedback}")
        return {
            "message": f"Improvement for document {document_id} noted. This feature is under development.",
            "document_id": document_id
        }
