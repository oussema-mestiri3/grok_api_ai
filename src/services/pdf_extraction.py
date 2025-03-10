import os
import tempfile
from typing import List, Dict, Any
import PyPDF2

class PDFExtractor:
    def __init__(self):
        pass
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            text_content = ""
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            return text_content
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
            
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                metadata = pdf_reader.metadata
                return {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "creation_date": metadata.get("/CreationDate", ""),
                    "page_count": len(pdf_reader.pages)
                }
        except Exception as e:
            raise Exception(f"Error extracting metadata from PDF: {str(e)}")