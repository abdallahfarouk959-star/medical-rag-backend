from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import os
import shutil
import time
import json

# استدعاء جميع أجزاء النظام
from rag_system.ingestion import process_and_chunk_pdf
from rag_system.embeddings import embed_and_store_chunks, get_index, NAMESPACE
from rag_system.retriever import get_relevant_chunks
from rag_system.guardrails import check_query_safety
from rag_system.generator import generate_grounded_response

router = APIRouter()
UPLOAD_DIR = "data"
CACHE_FILE = os.path.join(UPLOAD_DIR, "demo_cache.json")

def get_cached(question):
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        return cache.get(question.strip().lower())
    except Exception:
        return None

def cache_query(question, result):
    try:
        cache = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}
        cache[question.strip().lower()] = result
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    safe_name = os.path.basename(file.filename or "")
    if not safe_name.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed.")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        chunks = process_and_chunk_pdf(file_path, safe_name)
        stats = embed_and_store_chunks(chunks)
        
        return {
            "status": "success", 
            "filename": safe_name,
            "chunks_created": len(chunks),
            "tables_preserved": sum(1 for c in chunks if c["metadata"]["content_type"] == "table"),
            "avg_tokens": round(sum(c["metadata"]["token_count"] for c in chunks) / max(len(chunks), 1), 1),
            **stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/query")
def ask_question(request: QueryRequest):
    t0 = time.perf_counter()
    
    if os.getenv("OFFLINE_DEMO", "false").lower() == "true":
        cached = get_cached(request.question)
        if cached:
            cached["latency_ms"] = round((time.perf_counter() - t0) * 1000)
            return cached

    try:
        safety = check_query_safety(request.question)
        if not safety["allowed"]:
            res = {
                "status": "refused", 
                "category": safety["category"],
                "message": safety["reason"], 
                "recommendation": safety["reason"],
                "citations": [], 
                "confidence": "Low"
            }
            cache_query(request.question, res)
            return res
            
        chunks = get_relevant_chunks(request.question, request.top_k)
        result = generate_grounded_response(request.question, chunks)
        
        if safety.get("personal_advice_flag"):
            result["recommendation"] = (
                "> ⚠️ **This system provides guideline summaries, not personal "
                "medical advice. Consult a healthcare professional.**\n\n"
                + result.get("recommendation", "")
            )
        
        final_result = {
            "status": "success", 
            "question": request.question, 
            **result,
            "evidence_panel": chunks,
            "latency_ms": round((time.perf_counter() - t0) * 1000)
        }
        
        cache_query(request.question, final_result)
        return final_result
    except Exception as e:
        cached = get_cached(request.question)
        if cached:
            cached["latency_ms"] = round((time.perf_counter() - t0) * 1000)
            return cached
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")


@router.post("/clear")
def clear_database():
    try:
        index = get_index()
        # مسح الـ namespace الخاص بالـ Guidelines في Pinecone
        index.delete(delete_all=True, namespace=NAMESPACE)
        
        # تنظيف مجلد الملفات المرفوعة محلياً إذا وجد
        if os.path.exists(UPLOAD_DIR):
            for f in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, f)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception:
                    pass
                    
        return {"status": "success", "message": f"Namespace '{NAMESPACE}' and local files cleared successfully."}
    except Exception as e:
        # تفادي الـ 500 لو الـ namespace كان فارغاً بالفعل
        return {"status": "success", "message": f"Database already clear or namespace empty: {str(e)}"}