"""Single shared encoder instance. Import this everywhere — never re-instantiate."""
from __future__ import annotations
import threading
from sentence_transformers import SentenceTransformer

EMBED_MODEL_NAME = "pritamdeka/S-PubMedBert-MS-MARCO"
_lock = threading.Lock()
_instance = None


class LocalPubMedEmbeddings:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL_NAME)
        # Guarantee the tokenizer ceiling matches the ingestion assumption.
        self.model.max_seq_length = min(getattr(self.model, "max_seq_length", 512), 512)

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed_documents(self, texts, batch_size: int = 32):
        return self.model.encode(texts, batch_size=batch_size,
                                 normalize_embeddings=True,
                                 convert_to_numpy=True,
                                 show_progress_bar=False).tolist()

    def embed_query(self, text: str):
        return self.model.encode([text], normalize_embeddings=True,
                                 convert_to_numpy=True)[0].tolist()


def get_embedder() -> LocalPubMedEmbeddings:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = LocalPubMedEmbeddings()
    return _instance