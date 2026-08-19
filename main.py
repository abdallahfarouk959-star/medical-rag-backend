from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    from rag_system.embedder import get_embedder
    # تسخين الموديل في البداية عشان ميكونش الاستعلام الأول بطيء
    get_embedder().embed_query("warmup")
    yield

app = FastAPI(
    title="Medical RAG System API",
    description="Backend API for the AI Hackathon Medical RAG System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Medical RAG System API is running successfully!"}