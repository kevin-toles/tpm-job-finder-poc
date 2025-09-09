"""
BM25TFIDFMatcher: Utility for BM25 and TF-IDF keyword relevance scoring
"""
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class BM25TFIDFMatcher:
    def __init__(self, corpus: List[str]):
        self.corpus = corpus
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.avgdl = np.mean([len(doc.split()) for doc in corpus])
        self.k1 = 1.5
        self.b = 0.75

    def score(self, query: str) -> Dict[str, float]:
        # TF-IDF cosine similarity
        query_vec = self.vectorizer.transform([query])
        cosine_sim = np.dot(self.tfidf_matrix, query_vec.T).toarray().flatten()
        # BM25 scoring
        bm25_scores = [self._bm25(query, doc) for doc in self.corpus]
        return {
            "tfidf_max": float(np.max(cosine_sim)),
            "tfidf_mean": float(np.mean(cosine_sim)),
            "bm25_max": float(np.max(bm25_scores)),
            "bm25_mean": float(np.mean(bm25_scores))
        }

    def _bm25(self, query: str, doc: str) -> float:
        # Simple BM25 implementation
        query_terms = query.lower().split()
        doc_terms = doc.lower().split()
        score = 0.0
        doc_len = len(doc_terms)
        for term in query_terms:
            tf = doc_terms.count(term)
            df = sum(1 for d in self.corpus if term in d.lower().split())
            idf = np.log((len(self.corpus) - df + 0.5) / (df + 0.5) + 1)
            denom = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            score += idf * ((tf * (self.k1 + 1)) / (denom + 1e-6))
        return score

# Example usage:
# matcher = BM25TFIDFMatcher(["Led agile teams", "Managed teams and delivered projects"])
# scores = matcher.score("agile project management")
# print(scores)
