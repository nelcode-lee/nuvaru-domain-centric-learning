"""
Simplified vector service for development without ChromaDB
"""

import json
import os
from typing import List, Dict, Any, Optional
import structlog

from app.core.config import settings
from app.core.exceptions import VectorDatabaseError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SimpleVectorService:
    """Simplified vector service using file-based storage"""
    
    def __init__(self):
        """Initialize simple vector service"""
        self.data_dir = "data/vector_db"
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        self.collection_file = os.path.join(self.data_dir, f"{self.collection_name}.json")
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data
        self.collection_data = self._load_collection()
        
        logger.info("Simple vector service initialized", collection=self.collection_name)
    
    def _load_collection(self) -> Dict[str, Any]:
        """Load collection data from file"""
        try:
            if os.path.exists(self.collection_file):
                with open(self.collection_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "documents": [],
                    "embeddings": [],
                    "metadatas": [],
                    "ids": [],
                    "metadata": {"description": "Nuvaru knowledge base collection"}
                }
        except Exception as e:
            logger.error("Failed to load collection", error=str(e))
            return {
                "documents": [],
                "embeddings": [],
                "metadatas": [],
                "ids": [],
                "metadata": {"description": "Nuvaru knowledge base collection"}
            }
    
    def _save_collection(self) -> None:
        """Save collection data to file"""
        try:
            with open(self.collection_file, 'w') as f:
                json.dump(self.collection_data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save collection", error=str(e))
            raise VectorDatabaseError("Failed to save collection")
    
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
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Add to collection
            self.collection_data["documents"].extend(documents)
            self.collection_data["embeddings"].extend(embeddings)
            self.collection_data["metadatas"].extend(metadatas)
            self.collection_data["ids"].extend(ids)
            
            # Save to file
            self._save_collection()
            
            logger.info(
                "Documents added to vector database",
                count=len(documents),
                collection=self.collection_name
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
            
            # Simple similarity search using cosine similarity
            results = {
                "ids": [[] for _ in query_embeddings],
                "documents": [[] for _ in query_embeddings],
                "metadatas": [[] for _ in query_embeddings],
                "distances": [[] for _ in query_embeddings]
            }
            
            for query_idx, query_embedding in enumerate(query_embeddings):
                similarities = []
                
                for i, doc_embedding in enumerate(self.collection_data["embeddings"]):
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    
                    # Apply metadata filter if provided
                    if where:
                        metadata = self.collection_data["metadatas"][i]
                        if not self._matches_filter(metadata, where):
                            continue
                    
                    similarities.append((i, similarity))
                
                # Sort by similarity (descending)
                similarities.sort(key=lambda x: x[1], reverse=True)
                
                # Take top n_results
                for i, (doc_idx, similarity) in enumerate(similarities[:n_results]):
                    results["ids"][query_idx].append(self.collection_data["ids"][doc_idx])
                    results["documents"][query_idx].append(self.collection_data["documents"][doc_idx])
                    results["metadatas"][query_idx].append(self.collection_data["metadatas"][doc_idx])
                    results["distances"][query_idx].append(1 - similarity)  # Convert to distance
            
            logger.info(
                "Documents queried from vector database",
                query_count=len(query_embeddings),
                results_count=len(results["ids"][0]) if results["ids"] else 0,
                collection=self.collection_name
            )
            
            return results
            
        except Exception as e:
            logger.error("Failed to query documents from vector database", error=str(e))
            raise VectorDatabaseError("Failed to query documents from vector database")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))
            
            # Avoid division by zero
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            logger.error("Failed to calculate cosine similarity", error=str(e))
            return 0.0
    
    def _matches_filter(self, metadata: Dict[str, Any], where: Dict[str, Any]) -> bool:
        """Check if metadata matches the filter"""
        try:
            for key, value in where.items():
                if key not in metadata or metadata[key] != value:
                    return False
            return True
        except Exception as e:
            logger.error("Failed to check filter", error=str(e))
            return False
    
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
            query_embedding = embedding_model.encode_text(query_text)
            
            # Query the vector database
            results = self.query_documents(
                query_embeddings=[query_embedding],
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
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection
        
        Returns:
            Collection information dictionary
        """
        try:
            count = len(self.collection_data["documents"])
            
            info = {
                "name": self.collection_name,
                "count": count,
                "metadata": self.collection_data["metadata"]
            }
            
            logger.info(
                "Retrieved collection information",
                collection=self.collection_name,
                count=count
            )
            
            return info
            
        except Exception as e:
            logger.error("Failed to get collection information", error=str(e))
            raise VectorDatabaseError("Failed to get collection information")
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            if doc_id in self.collection_data["ids"]:
                idx = self.collection_data["ids"].index(doc_id)
                return {
                    "id": self.collection_data["ids"][idx],
                    "document": self.collection_data["documents"][idx],
                    "metadata": self.collection_data["metadatas"][idx]
                }
            
            return None
            
        except Exception as e:
            logger.error("Failed to get document by ID", error=str(e), doc_id=doc_id)
            raise VectorDatabaseError("Failed to get document by ID")



