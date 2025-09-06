import os
import chromadb
from typing import List, Dict, Any, Optional
from uuid import uuid4
from app.core.logging import get_logger

logger = get_logger(__name__)

class ChromaDBService:
    def __init__(self, collection_name: str = "nuvaru_knowledge", persist_directory: str = "data/chromadb"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Connected to existing ChromaDB collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Nuvaru Domain-Centric Learning Knowledge Base"}
            )
            logger.info(f"Created new ChromaDB collection: {collection_name}")
        
        logger.info(f"ChromaDB service initialized collection={collection_name} persist_dir={persist_directory}")

    def add_documents(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add documents to the collection"""
        if ids is None:
            ids = [str(uuid4()) for _ in embeddings]
        
        # Prepare documents for ChromaDB
        documents = [metadata.get("content", "") for metadata in metadatas]
        
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Documents added to ChromaDB collection={self.collection_name} count={len(embeddings)}")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise

    def query_documents(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Query documents from the collection"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results for consistency with other services
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": doc,
                        "metadata": results['metadatas'][0][i],
                        "similarity": 1 - results['distances'][0][i] if 'distances' in results else 0.0
                    })
            
            logger.info(f"Documents queried from ChromaDB collection={self.collection_name} query_count=1 results_count={len(formatted_results)}")
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying documents from ChromaDB: {e}")
            return []

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        try:
            results = self.collection.get(ids=[doc_id])
            if results['documents'] and results['documents'][0]:
                return {
                    "id": results['ids'][0],
                    "document": results['documents'][0],
                    "metadata": results['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document from ChromaDB: {e}")
            return None

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Document deleted from ChromaDB collection={self.collection_name} doc_id={doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document from ChromaDB: {e}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        try:
            count = self.collection.count()
            logger.info(f"Retrieved collection information collection={self.collection_name} count={count}")
            return {
                "name": self.collection_name,
                "count": count,
                "type": "chromadb"
            }
        except Exception as e:
            logger.error(f"Error getting collection info from ChromaDB: {e}")
            return {"name": self.collection_name, "count": 0, "type": "chromadb"}

    def update_document(self, doc_id: str, embedding: List[float], metadata: Dict[str, Any], document: str) -> bool:
        """Update a document in the collection"""
        try:
            self.collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata]
            )
            logger.info(f"Document updated in ChromaDB collection={self.collection_name} doc_id={doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document in ChromaDB: {e}")
            return False

    def search_by_metadata(self, where: Dict[str, Any], n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents by metadata filters"""
        try:
            results = self.collection.query(
                where=where,
                n_results=n_results
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": doc,
                        "metadata": results['metadatas'][0][i],
                        "similarity": 1 - results['distances'][0][i] if 'distances' in results else 0.0
                    })
            
            logger.info(f"Metadata search in ChromaDB collection={self.collection_name} results_count={len(formatted_results)}")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching by metadata in ChromaDB: {e}")
            return []


