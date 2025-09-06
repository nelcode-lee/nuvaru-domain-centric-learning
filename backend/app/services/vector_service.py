"""
Vector database service for ChromaDB integration
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import structlog

from app.core.config import settings
from app.core.exceptions import VectorDatabaseError
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorService:
    """Service for managing vector database operations"""
    
    def __init__(self):
        """Initialize ChromaDB client"""
        try:
            self.client = chromadb.Client(Settings(
                chroma_host=settings.CHROMA_HOST,
                chroma_port=settings.CHROMA_PORT,
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host="0.0.0.0",
                chroma_server_http_port=8001
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Nuvaru knowledge base collection"}
            )
            
            logger.info("Vector database service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize vector database", error=str(e))
            raise VectorDatabaseError("Failed to initialize vector database")
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector database
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(
                "Documents added to vector database",
                count=len(documents),
                collection=settings.CHROMA_COLLECTION_NAME
            )
            
            return ids
            
        except Exception as e:
            logger.error("Failed to add documents to vector database", error=str(e))
            raise VectorDatabaseError("Failed to add documents to vector database")
    
    def query_documents(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Query documents from the vector database
        
        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            where: Optional metadata filter
            include: Optional list of fields to include
            
        Returns:
            Query results dictionary
        """
        try:
            if include is None:
                include = ["documents", "metadatas", "distances"]
            
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=include
            )
            
            logger.info(
                "Documents queried from vector database",
                query_count=len(query_embeddings),
                results_count=len(results.get("ids", [])),
                collection=settings.CHROMA_COLLECTION_NAME
            )
            
            return results
            
        except Exception as e:
            logger.error("Failed to query documents from vector database", error=str(e))
            raise VectorDatabaseError("Failed to query documents from vector database")
    
    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Update documents in the vector database
        
        Args:
            ids: List of document IDs to update
            documents: Optional list of updated document texts
            embeddings: Optional list of updated embedding vectors
            metadatas: Optional list of updated metadata dictionaries
            
        Returns:
            True if successful
        """
        try:
            self.collection.update(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(
                "Documents updated in vector database",
                count=len(ids),
                collection=settings.CHROMA_COLLECTION_NAME
            )
            
            return True
            
        except Exception as e:
            logger.error("Failed to update documents in vector database", error=str(e))
            raise VectorDatabaseError("Failed to update documents in vector database")
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents from the vector database
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=ids)
            
            logger.info(
                "Documents deleted from vector database",
                count=len(ids),
                collection=settings.CHROMA_COLLECTION_NAME
            )
            
            return True
            
        except Exception as e:
            logger.error("Failed to delete documents from vector database", error=str(e))
            raise VectorDatabaseError("Failed to delete documents from vector database")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection
        
        Returns:
            Collection information dictionary
        """
        try:
            count = self.collection.count()
            
            info = {
                "name": self.collection.name,
                "count": count,
                "metadata": self.collection.metadata
            }
            
            logger.info(
                "Retrieved collection information",
                collection=settings.CHROMA_COLLECTION_NAME,
                count=count
            )
            
            return info
            
        except Exception as e:
            logger.error("Failed to get collection information", error=str(e))
            raise VectorDatabaseError("Failed to get collection information")
    
    def search_similar(
        self,
        query_text: str,
        embedding_model,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using text query
        
        Args:
            query_text: Text query to search for
            embedding_model: Model to generate embeddings
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of similar documents with metadata
        """
        try:
            # Generate embedding for query text
            query_embedding = embedding_model.encode([query_text])
            
            # Query the vector database
            results = self.query_documents(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            similar_docs = []
            if results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    similar_docs.append({
                        "id": doc_id,
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
                    })
            
            logger.info(
                "Similar documents found",
                query=query_text,
                results_count=len(similar_docs)
            )
            
            return similar_docs
            
        except Exception as e:
            logger.error("Failed to search similar documents", error=str(e))
            raise VectorDatabaseError("Failed to search similar documents")
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results["ids"] and results["ids"][0]:
                return {
                    "id": results["ids"][0],
                    "document": results["documents"][0],
                    "metadata": results["metadatas"][0]
                }
            
            return None
            
        except Exception as e:
            logger.error("Failed to get document by ID", error=str(e), doc_id=doc_id)
            raise VectorDatabaseError("Failed to get document by ID")
    
    def create_knowledge_base(self, kb_name: str, description: str = "") -> str:
        """
        Create a new knowledge base collection
        
        Args:
            kb_name: Name of the knowledge base
            description: Description of the knowledge base
            
        Returns:
            Collection name
        """
        try:
            collection_name = f"{kb_name}_{uuid.uuid4().hex[:8]}"
            
            collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "description": description,
                    "created_at": str(uuid.uuid4()),
                    "kb_name": kb_name
                }
            )
            
            logger.info(
                "Knowledge base created",
                kb_name=kb_name,
                collection_name=collection_name
            )
            
            return collection_name
            
        except Exception as e:
            logger.error("Failed to create knowledge base", error=str(e), kb_name=kb_name)
            raise VectorDatabaseError("Failed to create knowledge base")
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """
        List all knowledge bases
        
        Returns:
            List of knowledge base information
        """
        try:
            collections = self.client.list_collections()
            
            knowledge_bases = []
            for collection in collections:
                if collection.metadata and "kb_name" in collection.metadata:
                    knowledge_bases.append({
                        "name": collection.name,
                        "kb_name": collection.metadata.get("kb_name"),
                        "description": collection.metadata.get("description", ""),
                        "count": collection.count()
                    })
            
            logger.info("Knowledge bases listed", count=len(knowledge_bases))
            
            return knowledge_bases
            
        except Exception as e:
            logger.error("Failed to list knowledge bases", error=str(e))
            raise VectorDatabaseError("Failed to list knowledge bases")



