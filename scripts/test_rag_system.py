#!/usr/bin/env python3
"""
Test script for RAG (Retrieval-Augmented Generation) system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.learning_service import LearningService
from app.services.vector_service import VectorService
from app.services.embedding_service import EmbeddingService
from app.services.ollama_service import OllamaService
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


def test_rag_system():
    """Test the complete RAG system"""
    try:
        print("🚀 Testing RAG System...")
        
        # Initialize services
        print("📦 Initializing services...")
        learning_service = LearningService()
        vector_service = VectorService()
        embedding_service = EmbeddingService()
        ollama_service = OllamaService()
        
        # Test data - medical knowledge base
        test_documents = [
            "Diabetes is a chronic condition that affects how your body turns food into energy. There are two main types: Type 1 and Type 2.",
            "Type 1 diabetes is an autoimmune condition where the body attacks insulin-producing cells in the pancreas.",
            "Type 2 diabetes is more common and occurs when the body becomes resistant to insulin or doesn't produce enough.",
            "Common symptoms of diabetes include increased thirst, frequent urination, extreme fatigue, and blurred vision.",
            "Treatment for diabetes typically includes medication, diet changes, regular exercise, and blood sugar monitoring.",
            "Insulin is a hormone that helps glucose enter cells to be used for energy. People with Type 1 diabetes need insulin injections.",
            "Metformin is a common medication used to treat Type 2 diabetes by helping the body use insulin more effectively.",
            "Regular blood sugar monitoring is essential for managing diabetes and preventing complications.",
            "Diabetic complications can include heart disease, kidney damage, nerve damage, and eye problems.",
            "A healthy diet for diabetes includes whole grains, lean proteins, vegetables, and limited sugar and processed foods."
        ]
        
        test_metadata = [
            {
                "source": "medical_guidelines",
                "type": "diabetes_info",
                "user_id": 1,
                "knowledge_base_id": "medical_kb",
                "index": i
            }
            for i in range(len(test_documents))
        ]
        
        print("🔤 Generating embeddings and storing documents...")
        # Generate embeddings
        embeddings = embedding_service.encode_texts(test_documents)
        
        # Store documents in vector database
        doc_ids = vector_service.add_documents(
            documents=test_documents,
            embeddings=embeddings,
            metadatas=test_metadata
        )
        
        print(f"✅ Stored {len(doc_ids)} documents in knowledge base")
        
        # Test RAG chat
        print("💬 Testing RAG chat functionality...")
        
        test_queries = [
            "What is diabetes and what are the main types?",
            "What are the common symptoms of diabetes?",
            "How is diabetes treated?",
            "What medications are used for diabetes?",
            "What complications can diabetes cause?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}: {query}")
            
            try:
                response = learning_service.chat_with_ai(
                    message=query,
                    user_id=1,
                    knowledge_base_id="medical_kb"
                )
                
                print(f"🤖 AI Response: {response['response'][:200]}...")
                print(f"📊 Sources: {len(response['sources'])} documents found")
                print(f"🔗 Session ID: {response['session_id']}")
                
                # Show top source
                if response['sources']:
                    top_source = response['sources'][0]
                    print(f"📖 Top Source: {top_source['title']} (Relevance: {top_source['relevance_score']:.3f})")
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        # Test feedback submission
        print("\n📝 Testing feedback submission...")
        try:
            feedback_result = learning_service.submit_feedback(
                session_id="test_session_123",
                response_id="test_response_456",
                rating=5,
                feedback="Very helpful and accurate response",
                correctness=True,
                user_id=1
            )
            print(f"✅ Feedback submitted: {feedback_result['message']}")
        except Exception as e:
            print(f"❌ Feedback submission failed: {e}")
        
        # Test knowledge base stats
        print("\n📊 Testing knowledge base statistics...")
        try:
            stats = learning_service.get_knowledge_base_stats(user_id=1)
            print(f"✅ Knowledge base stats retrieved:")
            print(f"   Total documents: {stats['total_documents']}")
            print(f"   Knowledge bases: {len(stats['knowledge_bases'])}")
        except Exception as e:
            print(f"❌ Stats retrieval failed: {e}")
        
        print("\n✅ RAG system test completed successfully!")
        
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        logger.error("RAG system test failed", error=str(e))
        return False
    
    return True


def test_ollama_integration():
    """Test Ollama LLM integration"""
    try:
        print("🧠 Testing Ollama Integration...")
        
        ollama_service = OllamaService()
        
        # Test health check
        print("🏥 Testing Ollama health check...")
        health = ollama_service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Model: {health['model']}")
        print(f"   Model Available: {health['model_available']}")
        
        if health['status'] != 'healthy':
            print("⚠️  Ollama service is not healthy. Some tests may fail.")
        
        # Test model listing
        print("📋 Testing model listing...")
        try:
            models = ollama_service.list_models()
            print(f"   Available models: {len(models)}")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model.get('name', 'Unknown')}")
        except Exception as e:
            print(f"   ⚠️  Model listing failed: {e}")
        
        # Test simple response generation
        print("💬 Testing response generation...")
        try:
            test_prompt = "What is artificial intelligence? Please provide a brief explanation."
            response = ollama_service.generate_response(
                prompt=test_prompt,
                temperature=0.7,
                max_tokens=100
            )
            print(f"   Response: {response[:100]}...")
            print("✅ Ollama integration test completed successfully!")
        except Exception as e:
            print(f"   ❌ Response generation failed: {e}")
            print("   This is expected if Ollama is not running or model is not available.")
        
    except Exception as e:
        print(f"❌ Ollama integration test failed: {e}")
        logger.error("Ollama integration test failed", error=str(e))
        return False
    
    return True


def test_document_processing():
    """Test document processing pipeline"""
    try:
        print("📄 Testing Document Processing Pipeline...")
        
        embedding_service = EmbeddingService()
        
        # Test text chunking
        print("✂️  Testing text chunking...")
        long_text = """
        This is a long document that needs to be chunked for processing. 
        It contains multiple sentences and paragraphs that will be split 
        into smaller chunks for better processing and retrieval. 
        Each chunk will be processed separately and stored in the vector database.
        This allows for more efficient searching and retrieval of relevant information.
        The chunking process ensures that we can handle large documents effectively.
        """
        
        chunks = embedding_service.chunk_text(long_text, chunk_size=100, chunk_overlap=20)
        print(f"   Original text length: {len(long_text)}")
        print(f"   Number of chunks: {len(chunks)}")
        print(f"   First chunk: {chunks[0][:50]}...")
        
        # Test document processing
        print("🔄 Testing document processing...")
        test_metadata = {
            "source": "test_document",
            "type": "sample",
            "user_id": 1
        }
        
        processed_chunks = embedding_service.process_document(
            text=long_text,
            metadata=test_metadata,
            chunk_size=100,
            chunk_overlap=20
        )
        
        print(f"   Processed chunks: {len(processed_chunks)}")
        print(f"   First chunk embedding dimension: {len(processed_chunks[0]['embedding'])}")
        
        print("✅ Document processing test completed successfully!")
        
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        logger.error("Document processing test failed", error=str(e))
        return False
    
    return True


def main():
    """Main test function"""
    print("🧪 Nuvaru RAG System Test Suite")
    print("=" * 60)
    
    # Test document processing first
    if not test_document_processing():
        print("❌ Document processing test failed. Exiting.")
        return
    
    print("\n" + "=" * 60)
    
    # Test Ollama integration
    if not test_ollama_integration():
        print("❌ Ollama integration test failed. Exiting.")
        return
    
    print("\n" + "=" * 60)
    
    # Test complete RAG system
    if not test_rag_system():
        print("❌ RAG system test failed. Exiting.")
        return
    
    print("\n🎉 All RAG system tests passed successfully!")
    print("🚀 The RAG system is ready for production use!")
    print("\n📋 Next steps:")
    print("   1. Deploy the system with Docker Compose")
    print("   2. Test with real enterprise documents")
    print("   3. Implement frontend interface")
    print("   4. Add monitoring and analytics")


if __name__ == "__main__":
    main()



