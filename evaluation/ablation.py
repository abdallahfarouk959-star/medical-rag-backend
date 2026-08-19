import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from evaluation.RAG_evaluator import DATASET
from rag_system.retriever import get_relevant_chunks
import rag_system.retriever as retriever_module

EXPERIMENTS = [
    {"name": "Baseline", "CANDIDATE_POOL": 30, "HYBRID_ALPHA": 0.5},
    {"name": "Exp 1 (Semantic Heavy)", "CANDIDATE_POOL": 30, "HYBRID_ALPHA": 0.8},
    {"name": "Exp 2 (Keyword Heavy)", "CANDIDATE_POOL": 30, "HYBRID_ALPHA": 0.2},
    {"name": "Exp 3 (Small Pool)", "CANDIDATE_POOL": 10, "HYBRID_ALPHA": 0.5}
]

def run_ablation():
    print("Running Ablation Experiments...")
    print(f"{'Experiment':<25} | {'Top-1':<10} | {'Hit@5':<10}")
    print("-" * 50)

    for exp in EXPERIMENTS:
        # Override retriever config
        retriever_module.CANDIDATE_POOL = exp["CANDIDATE_POOL"]
        retriever_module.HYBRID_ALPHA = exp["HYBRID_ALPHA"]
        retriever_module.RELEVANCE_FLOOR = 0.001

        top1_hits = 0
        hit5_hits = 0

        for data in DATASET:
            # We only evaluate retrieval, so we don't need the generator
            chunks = get_relevant_chunks(data["q"], top_k=5)
            context_text = " ".join([c.get('snippet', '') + " " + c.get('text', '') for c in chunks]).lower()

            if chunks and any(kw.lower() in (chunks[0].get('snippet', '') + " " + chunks[0].get('text', '')).lower() for kw in data['expected_keywords']):
                top1_hits += 1

            if any(kw.lower() in context_text for kw in data['expected_keywords']):
                hit5_hits += 1

        top1_score = (top1_hits / len(DATASET)) * 100
        hit5_score = (hit5_hits / len(DATASET)) * 100

        print(f"{exp['name']:<25} | {top1_score:>6.2f}%   | {hit5_score:>6.2f}%")

if __name__ == "__main__":
    run_ablation()
