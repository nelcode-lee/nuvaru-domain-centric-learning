"""
Document processing service for handling document ingestion and processing
"""

import os
import uuid
from typing import List, Dict, Any, Optional, BinaryIO
from pathlib import Path
import mimetypes
import structlog

from app.core.config import settings
from app.core.exceptions import FileProcessingError, ValidationError
from app.core.logging import get_logger
from app.services.vector_service import VectorService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_processor import PDFProcessor

logger = get_logger(__name__)


class DocumentService:
    """Service for processing and managing documents"""
    
    def __init__(self):
        """Initialize document service"""
        self.vector_service = VectorService()
        self.embedding_service = EmbeddingService()
        self.pdf_processor = PDFProcessor()
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_FILE_SIZE
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(exist_ok=True)
        
        # Supported file types
        self.supported_types = {
            'text/plain': self._process_text_file,
            'application/pdf': self._process_pdf_file,
            'text/markdown': self._process_markdown_file,
            'application/json': self._process_json_file,
            'text/csv': self._process_csv_file,
        }
        
        logger.info("Document service initialized with PDF support")
    
    def upload_document(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        metadata: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Upload and process a document
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            metadata: Additional metadata
            user_id: ID of the user uploading the document
            
        Returns:
            Document information dictionary
        """
        try:
            # Validate file
            self._validate_file(file_content, filename, content_type)
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Save file to disk
            file_path = self._save_file(file_content, doc_id, filename)
            
            # Process document
            processed_doc = self._process_document(
                file_path, content_type, metadata, user_id, doc_id
            )
            
            # Store in vector database
            self._store_in_vector_db(processed_doc)
            
            logger.info(
                "Document uploaded and processed successfully",
                doc_id=doc_id,
                filename=filename,
                user_id=user_id,
                size=len(file_content)
            )
            
            return {
                "id": doc_id,
                "filename": filename,
                "content_type": content_type,
                "size": len(file_content),
                "status": "processed",
                "metadata": metadata,
                "user_id": user_id,
                "chunks_count": len(processed_doc["chunks"])
            }
            
        except Exception as e:
            logger.error("Failed to upload document", error=str(e), filename=filename)
            raise FileProcessingError("Failed to upload document")
    
    def _validate_file(self, file_content: bytes, filename: str, content_type: str) -> None:
        """Validate uploaded file"""
        # Check file size
        if len(file_content) > self.max_file_size:
            raise ValidationError(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
        
        # Check if content type is supported
        if content_type not in self.supported_types:
            raise ValidationError(f"Unsupported file type: {content_type}")
        
        # Additional validation based on file type
        if content_type == 'application/pdf':
            if not file_content.startswith(b'%PDF'):
                raise ValidationError("Invalid PDF file")
        
        logger.info("File validation passed", filename=filename, content_type=content_type)
    
    def _save_file(self, file_content: bytes, doc_id: str, filename: str) -> Path:
        """Save file to disk"""
        try:
            # Create file path
            file_extension = Path(filename).suffix
            file_path = self.upload_dir / f"{doc_id}{file_extension}"
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info("File saved to disk", doc_id=doc_id, file_path=str(file_path))
            
            return file_path
            
        except Exception as e:
            logger.error("Failed to save file", error=str(e), doc_id=doc_id)
            raise FileProcessingError("Failed to save file")
    
    def _process_document(
        self,
        file_path: Path,
        content_type: str,
        metadata: Dict[str, Any],
        user_id: int,
        doc_id: str
    ) -> Dict[str, Any]:
        """Process document based on its type"""
        try:
            # Get the appropriate processor
            processor = self.supported_types[content_type]
            
            # Process the document
            text_content = processor(file_path)
            
            # Add metadata
            doc_metadata = metadata.copy()
            doc_metadata.update({
                "doc_id": doc_id,
                "user_id": user_id,
                "content_type": content_type,
                "file_path": str(file_path),
                "processed_at": str(uuid.uuid4())  # Timestamp placeholder
            })
            
            # Process with embedding service
            processed_chunks = self.embedding_service.process_document(
                text_content, doc_metadata
            )
            
            logger.info(
                "Document processed successfully",
                doc_id=doc_id,
                content_length=len(text_content),
                chunks_count=len(processed_chunks)
            )
            
            return {
                "doc_id": doc_id,
                "text_content": text_content,
                "metadata": doc_metadata,
                "chunks": processed_chunks
            }
            
        except Exception as e:
            logger.error("Failed to process document", error=str(e), doc_id=doc_id)
            raise FileProcessingError("Failed to process document")
    
    def _process_text_file(self, file_path: Path) -> str:
        """Process plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _process_pdf_file(self, file_path: Path) -> str:
        """Process PDF file"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Extract text from PDF
            text_content = self.pdf_processor.extract_text(file_content, file_path.name)
            
            logger.info("PDF processed successfully", file_path=str(file_path), text_length=len(text_content))
            return text_content
            
        except Exception as e:
            logger.error("Failed to process PDF", error=str(e), file_path=str(file_path))
            raise FileProcessingError("Failed to process PDF file")
    
    def _process_markdown_file(self, file_path: Path) -> str:
        """Process markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error("Failed to process markdown", error=str(e), file_path=str(file_path))
            raise FileProcessingError("Failed to process markdown file")
    
    def _process_json_file(self, file_path: Path) -> str:
        """Process JSON file"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception as e:
            logger.error("Failed to process JSON", error=str(e), file_path=str(file_path))
            raise FileProcessingError("Failed to process JSON file")
    
    def _process_csv_file(self, file_path: Path) -> str:
        """Process CSV file"""
        try:
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                return "\n".join([",".join(row) for row in rows])
        except Exception as e:
            logger.error("Failed to process CSV", error=str(e), file_path=str(file_path))
            raise FileProcessingError("Failed to process CSV file")
    
    def _store_in_vector_db(self, processed_doc: Dict[str, Any]) -> None:
        """Store processed document in vector database"""
        try:
            chunks = processed_doc["chunks"]
            
            # Extract data for vector database
            documents = [chunk["text"] for chunk in chunks]
            embeddings = [chunk["embedding"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [f"{processed_doc['doc_id']}_chunk_{i}" for i in range(len(chunks))]
            
            # Store in vector database
            self.vector_service.add_documents(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(
                "Document stored in vector database",
                doc_id=processed_doc["doc_id"],
                chunks_count=len(chunks)
            )
            
        except Exception as e:
            logger.error("Failed to store document in vector database", error=str(e))
            raise FileProcessingError("Failed to store document in vector database")
    
    def search_documents(
        self,
        query: str,
        user_id: int,
        knowledge_base_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search documents using vector similarity
        
        Args:
            query: Search query
            user_id: ID of the user performing the search
            knowledge_base_id: Optional knowledge base filter
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            # Create metadata filter
            where_filter = {"user_id": user_id}
            if knowledge_base_id:
                where_filter["knowledge_base_id"] = knowledge_base_id
            
            # Search in vector database
            similar_docs = self.vector_service.search_similar(
                query_text=query,
                embedding_model=self.embedding_service.model,
                n_results=limit,
                where=where_filter
            )
            
            logger.info(
                "Document search completed",
                query=query,
                user_id=user_id,
                results_count=len(similar_docs)
            )
            
            return similar_docs
            
        except Exception as e:
            logger.error("Failed to search documents", error=str(e))
            raise FileProcessingError("Failed to search documents")
    
    def get_document(self, doc_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific document
        
        Args:
            doc_id: Document ID
            user_id: ID of the user requesting the document
            
        Returns:
            Document information or None if not found
        """
        try:
            # Get document from vector database
            doc = self.vector_service.get_document_by_id(doc_id)
            
            if doc and doc["metadata"].get("user_id") == user_id:
                return doc
            
            return None
            
        except Exception as e:
            logger.error("Failed to get document", error=str(e), doc_id=doc_id)
            raise FileProcessingError("Failed to get document")
    
    def delete_document(self, doc_id: str, user_id: int) -> bool:
        """
        Delete a document
        
        Args:
            doc_id: Document ID
            user_id: ID of the user deleting the document
            
        Returns:
            True if successful
        """
        try:
            # Get document to verify ownership
            doc = self.get_document(doc_id, user_id)
            if not doc:
                return False
            
            # Delete from vector database
            # Note: This is a simplified approach. In production, you'd need to
            # find all chunk IDs for the document
            self.vector_service.delete_documents([doc_id])
            
            # Delete file from disk
            file_path = Path(doc["metadata"]["file_path"])
            if file_path.exists():
                file_path.unlink()
            
            logger.info("Document deleted successfully", doc_id=doc_id, user_id=user_id)
            
            return True
            
        except Exception as e:
            logger.error("Failed to delete document", error=str(e), doc_id=doc_id)
            raise FileProcessingError("Failed to delete document")
    
    def get_user_documents(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all documents for a user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of documents to return
            
        Returns:
            List of user documents
        """
        try:
            # This is a simplified implementation
            # In production, you'd maintain a separate document index
            # or query the vector database with proper filtering
            
            logger.info("User documents retrieved", user_id=user_id, limit=limit)
            
            return []  # Placeholder - implement based on your needs
            
        except Exception as e:
            logger.error("Failed to get user documents", error=str(e), user_id=user_id)
            raise FileProcessingError("Failed to get user documents")

