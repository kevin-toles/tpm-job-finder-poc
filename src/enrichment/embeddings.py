"""
Embeddings: Utility for semantic similarity between resume bullets and JD sections
Uses SentenceTransformers (e.g., all-MiniLM-L6-v2)
"""
from typing import List

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None
    util = None

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformer:
            self.model = SentenceTransformer(model_name)
        else:
            self.model = None

    def get_embeddings(self, texts: List[str]):
        if not self.model:
            raise ImportError("sentence-transformers not installed")
        return self.model.encode(texts, convert_to_tensor=True)

    def similarity(self, text_a: str, text_b: str) -> float:
        if not self.model:
            raise ImportError("sentence-transformers not installed")
        emb_a = self.model.encode([text_a], convert_to_tensor=True)
        emb_b = self.model.encode([text_b], convert_to_tensor=True)
        return float(util.pytorch_cos_sim(emb_a, emb_b)[0][0])

# Example usage:
# engine = EmbeddingEngine()
# sim = engine.similarity("Led agile teams", "lead projects")
