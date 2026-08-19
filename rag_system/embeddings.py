import os, time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from rag_system.embedder import get_embedder

# استيراد مكتبة BM25 للبحث اللفظي (الكلمات المفتاحية)
try:
    from pinecone_text.sparse import BM25Encoder
except ImportError:
    raise ImportError("Please install pinecone-text to use Hybrid Search: pip install pinecone-text")

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "medical-rag-hackathon"
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "guidelines")
_pc = None
_bm25 = None

def get_bm25_encoder():
    """تحميل موديل الكلمات المفتاحية مرة واحدة في الذاكرة"""
    global _bm25
    if _bm25 is None:
        # تحميل الأوزان الافتراضية للغة الإنجليزية (جاهزة للاستخدام الطبي السريع)
        _bm25 = BM25Encoder().default()
    return _bm25

def get_index():
    global _pc
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY missing in .env")
    if _pc is None:
        _pc = Pinecone(api_key=PINECONE_API_KEY)
    
    if INDEX_NAME not in _pc.list_indexes().names():
        # ملاحظة هامة: Hybrid Search يتطلب metric="dotproduct" بدلاً من cosine
        _pc.create_index(
            name=INDEX_NAME, 
            dimension=get_embedder().dimension,
            metric="dotproduct", 
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        for _ in range(60):                    # wait until the index is ready
            if _pc.describe_index(INDEX_NAME).status.get("ready"):
                break
            time.sleep(1)
    return _pc.Index(INDEX_NAME)

def embed_and_store_chunks(chunks: list[dict], batch_size: int = 64) -> dict:
    if not chunks:
        return {"upserted": 0}
    
    index = get_index()
    embedder = get_embedder()
    bm25 = get_bm25_encoder()
    
    total = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        # استخراج النصوص لعمليات التضمين
        texts = [c["embed_text"] for c in batch]
        
        # 1. توليد الأرقام الدلالية - Dense Vectors (Semantic)
        dense_vectors = embedder.embed_documents(texts)
        
        # 2. توليد أرقام الكلمات المفتاحية - Sparse Vectors (Keyword)
        sparse_vectors = bm25.encode_documents(texts)
        
        # دمج النوعين في عملية الرفع
        index.upsert(
            vectors=[{
                "id": c["metadata"]["chunk_id"],   
                "values": dv,                      # Dense (Semantic)
                "sparse_values": sv,               # Sparse (Keyword)
                "metadata": {**c["metadata"], "text": c["text"]},
            } for c, dv, sv in zip(batch, dense_vectors, sparse_vectors)],
            namespace=NAMESPACE,
        )
        total += len(batch)
        
    return {"upserted": total, "namespace": NAMESPACE,
            "document_id": chunks[0]["metadata"]["document_id"]}