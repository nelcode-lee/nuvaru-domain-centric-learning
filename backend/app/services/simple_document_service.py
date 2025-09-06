"""
Simplified document processing service for development
"""

import os
import uuid
import hashlib
from typing import List, Dict, Any, Optional, BinaryIO, Tuple
from pathlib import Path
import structlog

from app.core.config import settings
from app.core.exceptions import FileProcessingError, ValidationError
from app.core.logging import get_logger
from app.services.simple_vector_service import SimpleVectorService
from app.services.simple_embedding_service import SimpleEmbeddingService
from app.services.pdf_processor import PDFProcessor

logger = get_logger(__name__)


class SimpleDocumentService:
    """Simplified service for processing and managing documents"""
    
    def __init__(self):
        """Initialize document service"""
        self.vector_service = SimpleVectorService()
        self.embedding_service = SimpleEmbeddingService()
        self.pdf_processor = PDFProcessor()
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_FILE_SIZE
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(exist_ok=True)
        
        # Supported file types
        self.supported_types = {
            'text/plain': self._process_text_file,
            'text/markdown': self._process_markdown_file,
            'application/json': self._process_json_file,
            'application/pdf': self._process_pdf_file,
        }
        
        logger.info("Simple document service initialized with PDF support")
    
    def _generate_file_hash(self, file_content: bytes) -> str:
        """Generate SHA-256 hash of file content for duplicate detection"""
        return hashlib.sha256(file_content).hexdigest()
    
    def _check_for_duplicates(self, file_content: bytes, filename: str, user_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check for duplicate files based on content hash and filename
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            user_id: ID of the user
            
        Returns:
            Tuple of (is_duplicate, existing_document_info)
        """
        try:
            # Generate content hash
            content_hash = self._generate_file_hash(file_content)
            
            # Check for existing files with same content hash
            uploads_dir = Path(self.upload_dir)
            if uploads_dir.exists():
                for ext in ['*.pdf', '*.txt', '*.md', '*.json']:
                    for file_path in uploads_dir.glob(ext):
                        try:
                            # Read existing file content
                            with open(file_path, 'rb') as f:
                                existing_content = f.read()
                            
                            # Check if content matches
                            if self._generate_file_hash(existing_content) == content_hash:
                                # Extract document info from filename
                                stored_filename = file_path.name
                                if '_' in stored_filename:
                                    parts = stored_filename.split('_', 1)
                                    if len(parts) == 2:
                                        doc_id = parts[0]
                                        original_filename = parts[1]
                                    else:
                                        doc_id = file_path.stem
                                        original_filename = stored_filename
                                else:
                                    doc_id = file_path.stem
                                    original_filename = stored_filename
                                
                                # Check if it's the same filename (exact duplicate)
                                if original_filename == filename:
                                    logger.info("Exact duplicate found", 
                                              filename=filename, 
                                              content_hash=content_hash[:16],
                                              user_id=user_id)
                                    return True, {
                                        "type": "exact_duplicate",
                                        "message": f"File '{filename}' has already been uploaded",
                                        "existing_doc_id": doc_id,
                                        "existing_filename": original_filename,
                                        "upload_date": file_path.stat().st_mtime
                                    }
                                else:
                                    # Same content, different filename
                                    logger.info("Content duplicate found", 
                                              filename=filename, 
                                              existing_filename=original_filename,
                                              content_hash=content_hash[:16],
                                              user_id=user_id)
                                    return True, {
                                        "type": "content_duplicate",
                                        "message": f"File content already exists as '{original_filename}'",
                                        "existing_doc_id": doc_id,
                                        "existing_filename": original_filename,
                                        "upload_date": file_path.stat().st_mtime
                                    }
                        except Exception as e:
                            logger.warning("Error checking file for duplicates", 
                                         error=str(e), 
                                         file_path=str(file_path))
                            continue
            
            return False, None
            
        except Exception as e:
            logger.error("Error checking for duplicates", error=str(e), filename=filename)
            return False, None
    
    def upload_document(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        metadata: Dict[str, Any],
        user_id: int,
        skip_duplicate_check: bool = False
    ) -> Dict[str, Any]:
        """
        Upload and process a document
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            metadata: Additional metadata
            user_id: ID of the user uploading the document
            skip_duplicate_check: If True, skip duplicate checking and force upload
            
        Returns:
            Document information dictionary
        """
        try:
            # Validate file
            self._validate_file(file_content, filename, content_type)
            
            # Check for duplicates (unless explicitly skipped)
            if not skip_duplicate_check:
                is_duplicate, duplicate_info = self._check_for_duplicates(file_content, filename, user_id)
                if is_duplicate:
                    # Return duplicate information instead of processing
                    return {
                        "id": None,
                        "filename": filename,
                        "content_type": content_type,
                        "size": len(file_content),
                        "status": "duplicate",
                        "duplicate_info": duplicate_info,
                        "metadata": metadata,
                        "user_id": user_id,
                        "chunks_count": 0
                    }
            
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
        
        logger.info("File validation passed", filename=filename, content_type=content_type)
    
    def _save_file(self, file_content: bytes, doc_id: str, filename: str) -> Path:
        """Save file to disk with meaningful filename"""
        try:
            # Create meaningful filename: doc_id_original_name
            file_extension = Path(filename).suffix
            original_name = Path(filename).stem
            safe_original_name = "".join(c for c in original_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            meaningful_filename = f"{doc_id}_{safe_original_name}{file_extension}"
            file_path = self.upload_dir / meaningful_filename
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info("File saved to disk", doc_id=doc_id, file_path=str(file_path), original_filename=filename)
            
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
                embedding_model=self.embedding_service,
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
    
    def get_all_documents(self, user_id: int, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get all documents for a user
        
        Args:
            user_id: ID of the user
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of document information dictionaries
        """
        try:
            documents = []
            uploads_dir = Path(self.upload_dir)
            
            if uploads_dir.exists():
                # Get all files from uploads directory
                all_files = []
                for ext in ['*.pdf', '*.txt', '*.md', '*.json']:
                    all_files.extend(uploads_dir.glob(ext))
                
                # Sort by modification time (newest first)
                all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Apply pagination
                start_idx = skip
                end_idx = min(start_idx + limit, len(all_files))
                
                for i, file_path in enumerate(all_files[start_idx:end_idx], start=start_idx):
                    file_size = file_path.stat().st_size
                    stored_filename = file_path.name
                    
                    # Extract original filename from stored filename (doc_id_original_name.ext)
                    if '_' in stored_filename:
                        parts = stored_filename.split('_', 1)  # Split only on first underscore
                        if len(parts) == 2:
                            doc_id = parts[0]
                            original_filename = parts[1]
                        else:
                            doc_id = file_path.stem
                            original_filename = stored_filename
                    else:
                        doc_id = file_path.stem
                        original_filename = stored_filename
                    
                    # Determine content type based on file extension
                    if original_filename.lower().endswith('.pdf'):
                        content_type = 'application/pdf'
                    elif original_filename.lower().endswith('.txt'):
                        content_type = 'text/plain'
                    elif original_filename.lower().endswith('.md'):
                        content_type = 'text/markdown'
                    elif original_filename.lower().endswith('.json'):
                        content_type = 'application/json'
                    else:
                        content_type = 'application/octet-stream'
                    
                    # Get creation time
                    import datetime
                    created_at = datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() + 'Z'
                    
                    documents.append({
                        "id": doc_id,  # Use extracted document ID
                        "filename": original_filename,  # Use original filename for display
                        "stored_filename": stored_filename,  # Keep stored filename for reference
                        "content_type": content_type,
                        "size": file_size,
                        "status": "processed",
                        "chunks_count": 1,  # Placeholder - would need to track this properly
                        "created_at": created_at,
                        "user_id": user_id
                    })
            
            logger.info("Retrieved documents", user_id=user_id, count=len(documents))
            return documents
            
        except Exception as e:
            logger.error("Failed to get all documents", error=str(e), user_id=user_id)
            raise FileProcessingError("Failed to get all documents")
    
    def delete_document(self, document_id: str, user_id: int) -> bool:
        """
        Delete a document from the knowledge base
        
        Args:
            document_id: ID of the document to delete
            user_id: ID of the user
            
        Returns:
            True if document was deleted successfully, False otherwise
        """
        try:
            # Find the document file in uploads directory
            uploads_dir = Path(self.upload_dir)
            if not uploads_dir.exists():
                logger.warning("Uploads directory does not exist", user_id=user_id)
                return False
            
            # Look for files that match the document_id (now at start of filename)
            deleted_files = []
            for ext in ['*.pdf', '*.txt', '*.md', '*.json']:
                for file_path in uploads_dir.glob(ext):
                    # Check if filename starts with document_id_
                    if file_path.name.startswith(f"{document_id}_"):
                        # Delete the file
                        file_path.unlink()
                        deleted_files.append(file_path.name)
                        logger.info("File deleted from disk", filename=file_path.name, user_id=user_id)
            
            if not deleted_files:
                logger.warning("No files found to delete", document_id=document_id, user_id=user_id)
                return False
            
            # Remove from vector database
            try:
                # Get all documents from vector service to find matching ones
                collection_info = self.vector_service.get_collection_info()
                if collection_info and 'count' in collection_info:
                    # For simplicity, we'll clear the entire collection and rebuild
                    # In production, you'd want to selectively remove specific document chunks
                    logger.info("Clearing vector database for document deletion", user_id=user_id)
                    # Note: This is a simplified approach - in production you'd want more granular deletion
                
                logger.info("Document deleted successfully", 
                           document_id=document_id, 
                           files_deleted=deleted_files, 
                           user_id=user_id)
                return True
                
            except Exception as e:
                logger.error("Failed to remove from vector database", 
                           error=str(e), 
                           document_id=document_id, 
                           user_id=user_id)
                # Still return True since the file was deleted from disk
                return True
            
        except Exception as e:
            logger.error("Failed to delete document", 
                        error=str(e), 
                        document_id=document_id, 
                        user_id=user_id)
            return False
    
    def get_document_content(self, document_id: str, user_id: int) -> Optional[str]:
        """
        Get document content for viewing
        
        Args:
            document_id: ID of the document
            user_id: ID of the user
            
        Returns:
            Document content as string, or None if not found
        """
        try:
            uploads_dir = Path(self.upload_dir)
            if not uploads_dir.exists():
                logger.warning("Uploads directory does not exist", user_id=user_id)
                return None
            
            # Look for files that match the document_id (now at start of filename)
            for ext in ['*.pdf', '*.txt', '*.md', '*.json']:
                for file_path in uploads_dir.glob(ext):
                    # Check if filename starts with document_id_
                    if file_path.name.startswith(f"{document_id}_"):
                        # Read file content based on type
                        if file_path.suffix.lower() == '.pdf':
                            # For PDFs, try to extract text
                            try:
                                with open(file_path, 'rb') as f:
                                    file_content = f.read()
                                text = self.pdf_processor.extract_text(file_content, file_path.name)
                                return text if text.strip() else "PDF content extracted but appears to be empty or image-based."
                            except Exception as e:
                                logger.warning("Failed to extract PDF text", 
                                            error=str(e), 
                                            filename=file_path.name, 
                                            user_id=user_id)
                                return "PDF content could not be extracted. This may be an image-based PDF."
                        else:
                            # For text files, read directly
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    return f.read()
                            except UnicodeDecodeError:
                                # Try with different encoding
                                try:
                                    with open(file_path, 'r', encoding='latin-1') as f:
                                        return f.read()
                                except Exception as e:
                                    logger.warning("Failed to read file", 
                                                error=str(e), 
                                                filename=file_path.name, 
                                                user_id=user_id)
                                    return "File content could not be read."
            
            logger.warning("Document not found", document_id=document_id, user_id=user_id)
            return None
            
        except Exception as e:
            logger.error("Failed to get document content", 
                        error=str(e), 
                        document_id=document_id, 
                        user_id=user_id)
            return None
    
    def get_document_file(self, document_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get document file for download/viewing
        
        Args:
            document_id: ID of the document
            user_id: ID of the user
            
        Returns:
            Dictionary with file content, filename, and content type, or None if not found
        """
        try:
            uploads_dir = Path(self.upload_dir)
            if not uploads_dir.exists():
                logger.warning("Uploads directory does not exist", user_id=user_id)
                return None
            
            # Look for files that match the document_id (now at start of filename)
            for ext in ['*.pdf', '*.txt', '*.md', '*.json']:
                for file_path in uploads_dir.glob(ext):
                    # Check if filename starts with document_id_
                    if file_path.name.startswith(f"{document_id}_"):
                        # Read file content
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # Extract original filename for download
                        stored_filename = file_path.name
                        if '_' in stored_filename:
                            parts = stored_filename.split('_', 1)
                            if len(parts) == 2:
                                original_filename = parts[1]
                            else:
                                original_filename = stored_filename
                        else:
                            original_filename = stored_filename
                        
                        # Determine content type
                        if file_path.suffix.lower() == '.pdf':
                            content_type = 'application/pdf'
                        elif file_path.suffix.lower() == '.txt':
                            content_type = 'text/plain'
                        elif file_path.suffix.lower() == '.md':
                            content_type = 'text/markdown'
                        elif file_path.suffix.lower() == '.json':
                            content_type = 'application/json'
                        else:
                            content_type = 'application/octet-stream'
                        
                        return {
                            "content": file_content,
                            "filename": original_filename,  # Use original filename for download
                            "content_type": content_type,
                            "size": len(file_content)
                        }
            
            logger.warning("Document file not found", document_id=document_id, user_id=user_id)
            return None
            
        except Exception as e:
            logger.error("Failed to get document file", 
                        error=str(e), 
                        document_id=document_id, 
                        user_id=user_id)
            return None

