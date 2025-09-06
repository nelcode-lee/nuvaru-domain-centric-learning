"""
Embedding service for generating vector embeddings
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import structlog

from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        """Initialize the embedding model"""
        try:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.model_name = settings.EMBEDDING_MODEL
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            
            logger.info(
                "Embedding service initialized",
                model=self.model_name,
                dimension=self.embedding_dimension
            )
            
        except Exception as e:
            logger.error("Failed to initialize embedding service", error=str(e))
            raise LLMError("Failed to initialize embedding service")
    
    def encode_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to encode
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
            
        except Exception as e:
            logger.error("Failed to encode text", error=str(e), text_length=len(text))
            raise LLMError("Failed to encode text")
    
    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts to encode
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
            
        except Exception as e:
            logger.error("Failed to encode texts", error=str(e), count=len(texts))
            raise LLMError("Failed to encode texts")
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for large batches of texts
        
        Args:
            texts: List of input texts to encode
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_tensor=False
            )
            
            logger.info(
                "Batch embeddings generated",
                count=len(texts),
                batch_size=batch_size
            )
            
            return embeddings.tolist()
            
        except Exception as e:
            logger.error("Failed to encode batch", error=str(e), count=len(texts))
            raise LLMError("Failed to encode batch")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        
        Returns:
            Embedding dimension
        """
        return self.embedding_dimension
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model
        
        Returns:
            Model information dictionary
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "max_sequence_length": self.model.max_seq_length
        }
    
    def compute_similarity(
        self,
        text1: str,
        text2: str,
        metric: str = "cosine"
    ) -> float:
        """
        Compute similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            metric: Similarity metric ("cosine", "euclidean", "dot")
            
        Returns:
            Similarity score
        """
        try:
            embeddings = self.encode_texts([text1, text2])
            
            if metric == "cosine":
                # Compute cosine similarity
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
            elif metric == "euclidean":
                # Compute euclidean distance (inverted for similarity)
                distance = np.linalg.norm(np.array(embeddings[0]) - np.array(embeddings[1]))
                similarity = 1 / (1 + distance)
            elif metric == "dot":
                # Compute dot product
                similarity = np.dot(embeddings[0], embeddings[1])
            else:
                raise ValueError(f"Unsupported similarity metric: {metric}")
            
            return float(similarity)
            
        except Exception as e:
            logger.error("Failed to compute similarity", error=str(e))
            raise LLMError("Failed to compute similarity")
    
    def find_most_similar(
        self,
        query_text: str,
        candidate_texts: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar texts from a list of candidates
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            top_k: Number of top similar texts to return
            
        Returns:
            List of similar texts with similarity scores
        """
        try:
            # Encode query and candidates
            query_embedding = self.encode_text(query_text)
            candidate_embeddings = self.encode_texts(candidate_texts)
            
            # Compute similarities
            similarities = []
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = np.dot(query_embedding, candidate_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(candidate_embedding)
                )
                similarities.append({
                    "text": candidate_texts[i],
                    "index": i,
                    "similarity": float(similarity)
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.info(
                "Most similar texts found",
                query_length=len(query_text),
                candidates_count=len(candidate_texts),
                top_k=top_k
            )
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error("Failed to find most similar texts", error=str(e))
            raise LLMError("Failed to find most similar texts")
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[str]:
        """
        Split text into chunks for processing
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk (default from settings)
            chunk_overlap: Overlap between chunks (default from settings)
            
        Returns:
            List of text chunks
        """
        try:
            if chunk_size is None:
                chunk_size = settings.CHUNK_SIZE
            if chunk_overlap is None:
                chunk_overlap = settings.CHUNK_OVERLAP
            
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                chunks.append(chunk)
                
                # Move start position with overlap
                start = end - chunk_overlap
                
                # Prevent infinite loop
                if start >= len(text):
                    break
            
            logger.info(
                "Text chunked",
                original_length=len(text),
                chunk_count=len(chunks),
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            return chunks
            
        except Exception as e:
            logger.error("Failed to chunk text", error=str(e))
            raise LLMError("Failed to chunk text")
    
    def process_document(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[Dict[str, Any]]:
        """
        Process a document by chunking and generating embeddings
        
        Args:
            text: Document text
            metadata: Document metadata
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of processed chunks with embeddings and metadata
        """
        try:
            # Chunk the text
            chunks = self.chunk_text(text, chunk_size, chunk_overlap)
            
            # Generate embeddings for chunks
            embeddings = self.encode_texts(chunks)
            
            # Create processed chunks
            processed_chunks = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "chunk_size": len(chunk)
                })
                
                processed_chunks.append({
                    "text": chunk,
                    "embedding": embedding,
                    "metadata": chunk_metadata
                })
            
            logger.info(
                "Document processed",
                original_length=len(text),
                chunk_count=len(processed_chunks)
            )
            
            return processed_chunks
            
        except Exception as e:
            logger.error("Failed to process document", error=str(e))
            raise LLMError("Failed to process document")



