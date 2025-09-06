import os
from typing import List, Dict, Any, Optional
from app.core.logging import get_logger
from app.services.chromadb_service import ChromaDBService
from app.services.simple_vector_service import SimpleVectorService

logger = get_logger(__name__)

class ProductionVectorService:
    def __init__(self, collection_name: str = "nuvaru_knowledge"):
        self.vector_db_type = os.getenv("VECTOR_DB_TYPE", "chromadb")
        self.collection_name = collection_name
        
        if self.vector_db_type == "chromadb":
            try:
                self.vector_service = ChromaDBService(collection_name=collection_name)
                logger.info("Production vector service initialized with ChromaDB")
            except Exception as e:
                logger.warning(f"Failed to initialize ChromaDB, falling back to simple vector service: {e}")
                self.vector_service = SimpleVectorService(collection_name=collection_name)
                self.vector_db_type = "simple"
        else:
            self.vector_service = SimpleVectorService(collection_name=collection_name)
            logger.info("Production vector service initialized with simple vector service")

    def add_documents(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add documents to the vector database"""
        return self.vector_service.add_documents(embeddings, metadatas, ids)

    def query_documents(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Query documents from the vector database"""
        return self.vector_service.query_documents(query_embedding, n_results)

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        return self.vector_service.get_document(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        return self.vector_service.delete_document(doc_id)

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        info = self.vector_service.get_collection_info()
        info["vector_db_type"] = self.vector_db_type
        return info

    def update_document(self, doc_id: str, embedding: List[float], metadata: Dict[str, Any], document: str) -> bool:
        """Update a document in the collection"""
        if hasattr(self.vector_service, 'update_document'):
            return self.vector_service.update_document(doc_id, embedding, metadata, document)
        else:
            # Fallback for simple vector service
            logger.warning("Update document not supported in simple vector service")
            return False

    def search_by_metadata(self, where: Dict[str, Any], n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents by metadata filters"""
        if hasattr(self.vector_service, 'search_by_metadata'):
            return self.vector_service.search_by_metadata(where, n_results)
        else:
            # Fallback for simple vector service
            logger.warning("Metadata search not supported in simple vector service")
            return []


