"""Two-stage clinical retrieval: recall-oriented ANN (HYBRID) -> precision-oriented rerank."""
from __future__ import annotations
import os, threading, json
from dotenv import load_dotenv
from rag_system.embedder import get_embedder
from rag_system.embeddings import get_index, NAMESPACE, get_bm25_encoder  # استيراد BM25 من ملف الـ embeddings

load_dotenv()

config_path = os.path.join(os.path.dirname(__file__), "retrieval_config.json")
try:
    with open(config_path, "r") as f:
        _cfg = json.load(f)
except Exception:
    _cfg = {}

CANDIDATE_POOL = int(_cfg.get("CANDIDATE_POOL", 30))
RERANK_MODEL = _cfg.get("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RELEVANCE_FLOOR = float(_cfg.get("RELEVANCE_FLOOR", 0.35))  # sigmoid-normalised
HYBRID_ALPHA = float(_cfg.get("HYBRID_ALPHA", 0.5))         # 0.5 means 50% Semantic, 50% Keyword
_reranker, _rlock = None, threading.Lock()


def _get_reranker():
    """MedCPT is stronger on biomedical text; MiniLM is ~6x faster on CPU."""
    global _reranker
    if _reranker is None:
        with _rlock:
            if _reranker is None:
                from sentence_transformers import CrossEncoder
                _reranker = CrossEncoder(RERANK_MODEL, max_length=512)
    return _reranker


def _sigmoid(x: float) -> float:
    import math
    return 1.0 / (1.0 + math.exp(-x))


def get_relevant_chunks(query: str, top_k: int = 5,
                        document_id: str | None = None) -> list[dict]:
    index = get_index()
    
    # 1. توليد الأرقام الدلالية (Dense / Semantic)
    dense_vec = get_embedder().embed_query(query)
    
    # 2. توليد أرقام الكلمات المفتاحية (Sparse / Keyword)
    bm25 = get_bm25_encoder()
    sparse_vec = bm25.encode_queries(query)
    
    # 3. دمج الأوزان (Alpha Scaling)
    # Alpha = 1.0 (Semantic Only), Alpha = 0.0 (Keyword Only), Alpha = 0.5 (Balanced Hybrid)
    dense_vec_scaled = [v * HYBRID_ALPHA for v in dense_vec]
    sparse_vec_scaled = {
        "indices": sparse_vec["indices"],
        "values": [v * (1.0 - HYBRID_ALPHA) for v in sparse_vec["values"]]
    }

    flt = {"document_id": {"$eq": document_id}} if document_id else None

    # 4. البحث الهجين في Pinecone
    res = index.query(
        vector=dense_vec_scaled,
        sparse_vector=sparse_vec_scaled,  # السطر السحري لتفعيل الـ Hybrid
        top_k=CANDIDATE_POOL, 
        include_metadata=True,
        namespace=NAMESPACE, 
        filter=flt
    )
    
    matches = res.get("matches", []) or []
    if not matches:
        return []

    candidates, seen = [], set()
    for m in matches:
        md = dict(m.get("metadata") or {})
        text = md.pop("text", "")
        cid = md.get("chunk_id") or m["id"]
        if cid in seen or not text.strip():
            continue
        seen.add(cid)
        candidates.append({"text": text, "metadata": md,
                           "dense_score": float(m.get("score", 0.0))})

    # ---- Stage 2: cross-encoder re-ranking (full query-passage attention)
    try:
        scores = _get_reranker().predict(
            [(query, f"{c['metadata'].get('section_path','')}. {c['text']}")
             for c in candidates])
        for c, s in zip(candidates, scores):
            c["rerank_score"] = round(_sigmoid(float(s)), 4)
    except Exception:                              # graceful degradation
        for c in candidates:
            c["rerank_score"] = round(c["dense_score"], 4)

    candidates.sort(key=lambda c: c["rerank_score"], reverse=True)
    kept = [c for c in candidates if c["rerank_score"] >= RELEVANCE_FLOOR][:top_k]

    # Keep the single best hit even below the floor, so the generator can
    # explicitly declare "Insufficient Evidence" against real (weak) context.
    if not kept and candidates:
        kept = [candidates[0]]
    return kept