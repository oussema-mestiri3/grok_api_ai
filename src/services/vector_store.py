import os
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import uuid

class VectorStore:
    def __init__(self, openai_api_key: str = None, persist_directory: str = "./chroma_db"):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required for embeddings")
        
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
    def add_document(self, text: str, metadata: Dict[str, Any]) -> str:
        try:
            doc_id = str(uuid.uuid4())
            
            self.db.add_texts(
                texts=[text],
                metadatas=[{**metadata, "document_id": doc_id}],
                ids=[doc_id]
            )
            
            self.db.persist()
            
            return doc_id
        except Exception as e:
            raise Exception(f"Error adding document to vector store: {str(e)}")
    
    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.db.similarity_search_with_score(query, k=limit)
            
            processed_results = []
            for doc, score in results:
                processed_results.append({
                    "document_id": doc.metadata.get("document_id"),
                    "score": score,
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
                
            return processed_results
        except Exception as e:
            raise Exception(f"Error searching vector store: {str(e)}")