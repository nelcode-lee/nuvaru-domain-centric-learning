"""
PDF document processing utilities
"""

import io
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from app.core.logging import get_logger
from app.core.exceptions import FileProcessingError

logger = get_logger(__name__)


class PDFProcessor:
    """PDF document processor for extracting text content"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
        logger.info("PDF processor initialized")
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            file_content: PDF file content as bytes
            filename: Original filename
            
        Returns:
            Extracted text content
        """
        try:
            # Create a file-like object from bytes
            pdf_file = io.BytesIO(file_content)
            
            # Read PDF
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += page_text
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not text_content.strip():
                # If no text found, create a placeholder with filename
                text_content = f"PDF Document: {filename}\n\nThis PDF document could not be processed for text extraction. The file may be image-based, password-protected, or corrupted. Filename: {filename}"
                logger.warning(f"No text content found in PDF, using placeholder: {filename}")
            
            logger.info(f"PDF text extracted successfully filename={filename} pages={len(pdf_reader.pages)} text_length={len(text_content)}")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {filename}: {e}")
            raise FileProcessingError(f"Failed to process PDF file: {e}")
    
    def get_metadata(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        
        Args:
            file_content: PDF file content as bytes
            filename: Original filename
            
        Returns:
            PDF metadata dictionary
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            
            metadata = {
                "filename": filename,
                "file_type": "pdf",
                "page_count": len(pdf_reader.pages),
                "title": "",
                "author": "",
                "subject": "",
                "creator": "",
                "producer": "",
                "creation_date": "",
                "modification_date": ""
            }
            
            # Extract PDF metadata if available
            if pdf_reader.metadata:
                pdf_metadata = pdf_reader.metadata
                metadata.update({
                    "title": pdf_metadata.get("/Title", ""),
                    "author": pdf_metadata.get("/Author", ""),
                    "subject": pdf_metadata.get("/Subject", ""),
                    "creator": pdf_metadata.get("/Creator", ""),
                    "producer": pdf_metadata.get("/Producer", ""),
                    "creation_date": str(pdf_metadata.get("/CreationDate", "")),
                    "modification_date": str(pdf_metadata.get("/ModDate", ""))
                })
            
            logger.info(f"PDF metadata extracted filename={filename} page_count={metadata['page_count']}")
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata {filename}: {e}")
            return {
                "filename": filename,
                "file_type": "pdf",
                "page_count": 0,
                "title": "",
                "author": "",
                "subject": "",
                "creator": "",
                "producer": "",
                "creation_date": "",
                "modification_date": ""
            }
    
    def is_supported(self, filename: str) -> bool:
        """
        Check if file is supported by this processor
        
        Args:
            filename: File name to check
            
        Returns:
            True if supported, False otherwise
        """
        if not filename:
            return False
        
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in self.supported_extensions)
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions
        
        Returns:
            List of supported extensions
        """
        return self.supported_extensions.copy()
