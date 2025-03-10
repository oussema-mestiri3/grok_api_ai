# src/main.py
import os
import tempfile
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uuid

from src.models.tender_models import (
    HealthCheck, TenderAnalysisResponse, SearchRequest, SearchResponse
)
from src.services.pdf_extraction import PDFExtractor
from src.services.analyse import TenderAnalyzer
from src.services.vector_store import VectorStore

load_dotenv()

pdf_extractor = PDFExtractor()
ai_analyzer = TenderAnalyzer()  # Uses XAI_API_KEY from .env
vector_store = VectorStore()

app = FastAPI(
    title="Tender Analysis API",
    description="AI-powered tender document analysis microservice with Grok"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-tender", response_model=TenderAnalysisResponse)
async def upload_tender(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()

        # Extract text from PDF
        text = pdf_extractor.extract_text_from_pdf(temp_file_path)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        metadata = pdf_extractor.extract_metadata(temp_file_path)
        
        analysis = ai_analyzer.analyze_tender(text)
        
        # Store document in vector database
        document_id = vector_store.add_document(
            text=text,
            metadata={
                "filename": file.filename,
                "title": metadata.get("title", ""),
                "analysis_summary": analysis.get("structured_data", {}).get("TENDER SUMMARY", "")
            }
        )
        
        structured_data = analysis.get("structured_data", {})
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        key_requirements = []
        if "KEY REQUIREMENTS" in structured_data:
            for line in structured_data["KEY REQUIREMENTS"].split("\n"):
                if line.strip().startswith("- "):
                    key_requirements.append(line.strip()[2:])
        
        eligibility_criteria = []
        evaluation_criteria = []
        required_documents = []
        compliance_checklist = []
        risks_and_mitigations = []
        
        basic_info = {}
        if structured_data.get("BASIC_INFORMATION"):
            lines = structured_data["BASIC_INFORMATION"].split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    basic_info[key.strip().lower().replace(" ", "_")] = value.strip()
        
        return TenderAnalysisResponse(
            document_id=document_id,
            summary=structured_data.get("TENDER SUMMARY", ""),
            basic_info=basic_info,
            key_requirements=key_requirements,
            eligibility_criteria=eligibility_criteria,
            evaluation_criteria=evaluation_criteria,
            required_documents=required_documents,
            compliance_checklist=compliance_checklist,
            winning_strategy=structured_data.get("WINNING STRATEGY", ""),
            risks_and_mitigations=risks_and_mitigations,
            metadata=metadata,
            full_analysis=analysis.get("full_analysis", "")
        )
    
    except Exception as e:
        if 'temp_file_path' in locals():
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-tenders", response_model=SearchResponse)
async def search_tenders(request: SearchRequest):
    try:
        results = vector_store.search_similar(request.query, request.limit)
        
        search_results = []
        for result in results:
            search_results.append({
                "document_id": result["document_id"],
                "score": result["score"],
                "title": result["metadata"].get("title", ""),
                "summary": result["metadata"].get("analysis_summary", "")
            })
        
        return SearchResponse(results=search_results)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tender-analysis/{document_id}", response_model=TenderAnalysisResponse)
async def get_tender_analysis(document_id: str):
    raise HTTPException(status_code=501, detail="Endpoint not yet implemented")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)