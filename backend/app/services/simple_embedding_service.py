"""
Simplified embedding service for development without heavy dependencies
"""

import hashlib
import re
from typing import List, Dict, Any, Optional
import structlog

from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SimpleEmbeddingService:
    """Simplified embedding service for development"""
    
    def __init__(self):
        """Initialize the simple embedding service"""
        self.embedding_dimension = 384  # Standard dimension for simple embeddings
        self.model_name = "simple-hash-embedding"
        
        logger.info(
            "Simple embedding service initialized",
            model=self.model_name,
            dimension=self.embedding_dimension
        )
    
    def encode_text(self, text: str) -> List[float]:
        """
        Generate simple hash-based embedding for a single text
        
        Args:
            text: Input text to encode
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            # Create a simple hash-based embedding
            # This is not a real embedding but works for development
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            
            # Convert hash to vector
            embedding = []
            for i in range(0, len(text_hash), 2):
                # Convert hex pairs to float values between -1 and 1
                hex_pair = text_hash[i:i+2]
                value = int(hex_pair, 16) / 255.0 * 2 - 1
                embedding.append(value)
            
            # Pad or truncate to desired dimension
            while len(embedding) < self.embedding_dimension:
                embedding.append(0.0)
            
            embedding = embedding[:self.embedding_dimension]
            
            return embedding
            
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
            embeddings = []
            for text in texts:
                embedding = self.encode_text(text)
                embeddings.append(embedding)
            
            logger.info("Texts encoded successfully", count=len(texts))
            
            return embeddings
            
        except Exception as e:
            logger.error("Failed to encode texts", error=str(e), count=len(texts))
            raise LLMError("Failed to encode texts")
    
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
            "max_sequence_length": 512,
            "type": "simple_hash_based"
        }
    
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



