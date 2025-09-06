#!/usr/bin/env python3
"""
Test script for vector database functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.vector_service import VectorService
from app.services.embedding_service import EmbeddingService
from app.core.config import settings
import structlog

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def test_vector_database():
    """Test vector database functionality"""
    try:
        print("🚀 Testing Vector Database Integration...")
        
        # Initialize services
        print("📦 Initializing services...")
        vector_service = VectorService()
        embedding_service = EmbeddingService()
        
        # Test data
        test_documents = [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Vector databases are essential for AI applications.",
            "ChromaDB is an open-source vector database.",
            "Natural language processing uses vector embeddings."
        ]
        
        test_metadata = [
            {"source": "test", "type": "sentence", "index": i}
            for i in range(len(test_documents))
        ]
        
        print("🔤 Generating embeddings...")
        # Generate embeddings
        embeddings = embedding_service.encode_texts(test_documents)
        
        print("💾 Storing documents in vector database...")
        # Store documents
        doc_ids = vector_service.add_documents(
            documents=test_documents,
            embeddings=embeddings,
            metadatas=test_metadata
        )
        
        print(f"✅ Stored {len(doc_ids)} documents")
        
        # Test search
        print("🔍 Testing similarity search...")
        query = "What is machine learning?"
        query_embedding = embedding_service.encode_text(query)
        
        results = vector_service.query_documents(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        print("📊 Search Results:")
        for i, (doc_id, distance) in enumerate(zip(results["ids"][0], results["distances"][0])):
            doc_text = results["documents"][0][i]
            similarity = 1 - distance
            print(f"  {i+1}. Similarity: {similarity:.3f}")
            print(f"     Text: {doc_text}")
            print(f"     ID: {doc_id}")
            print()
        
        # Test collection info
        print("📈 Collection Information:")
        info = vector_service.get_collection_info()
        print(f"  Name: {info['name']}")
        print(f"  Document Count: {info['count']}")
        print(f"  Metadata: {info['metadata']}")
        
        print("✅ Vector database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error("Vector database test failed", error=str(e))
        return False
    
    return True


def test_embedding_service():
    """Test embedding service functionality"""
    try:
        print("🧠 Testing Embedding Service...")
        
        embedding_service = EmbeddingService()
        
        # Test single text
        text = "This is a test sentence for embedding."
        embedding = embedding_service.encode_text(text)
        print(f"✅ Generated embedding for single text (dimension: {len(embedding)})")
        
        # Test multiple texts
        texts = ["First text", "Second text", "Third text"]
        embeddings = embedding_service.encode_texts(texts)
        print(f"✅ Generated embeddings for {len(texts)} texts")
        
        # Test similarity
        similarity = embedding_service.compute_similarity(
            "Machine learning is great",
            "AI and ML are fascinating topics"
        )
        print(f"✅ Computed similarity: {similarity:.3f}")
        
        # Test model info
        info = embedding_service.get_model_info()
        print(f"✅ Model info: {info}")
        
        print("✅ Embedding service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        logger.error("Embedding service test failed", error=str(e))
        return False
    
    return True


def main():
    """Main test function"""
    print("🧪 Nuvaru Vector Database Test Suite")
    print("=" * 50)
    
    # Test embedding service first
    if not test_embedding_service():
        print("❌ Embedding service test failed. Exiting.")
        return
    
    print("\n" + "=" * 50)
    
    # Test vector database
    if not test_vector_database():
        print("❌ Vector database test failed. Exiting.")
        return
    
    print("\n🎉 All tests passed successfully!")
    print("🚀 Vector database integration is working correctly!")


if __name__ == "__main__":
    main()



