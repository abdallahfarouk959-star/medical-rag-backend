import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag_system.retriever import get_relevant_chunks

IN_SCOPE = [
    "What is the fasting plasma glucose level required for diagnosing diabetes?",
    "What is the drug of first choice for normal weight diabetic patients (BMI < 25)?",
    "What is the recommended starting dose for Glibenclamide?",
    "Which drug is indicated as first line pharmacological therapy in overweight patients (BMI ≥ 25)?",
    "What is the maximum daily dose for Metformin?",
    "What percentage of energy intake should come from carbohydrates in a diabetic diet?",
    "What is the earliest manifestation of diabetic nephropathy?",
    "What is the target blood pressure for diabetic patients to prevent nephropathy progression?",
    "Which class of drugs is recommended as primary treatment for hypertensive diabetics with microalbuminuria?",
    "How should diabetic patients cut their nails?",
    "What should diabetic patients use for dry feet, and where should they avoid applying it?",
    "How can fungal infections between toes be treated?",
    "How long should the warm-up period be before starting exercise?",
    "What types of exercises should be avoided by patients with retinopathy?",
    "When should a diabetic patient be referred to an ophthalmologist?",
    "How can excessive sweating be controlled in patients with autonomic neuropathy?",
    "What drugs are most commonly used for painful diabetic neuropathies?",
    "What is the optimal target for Fasting Plasma Glucose in mmol/L?"
]

OUT_OF_SCOPE = [
    "What is the capital of France?",
    "How do I write a binary search in Python?",
    "What is the weather like in New York today?",
    "Who won the 2022 World Cup?",
    "What are the rules for playing basketball?",
    "How do you bake a chocolate cake?",
    "What is the stock price of Apple?",
    "Write a poem about the sea.",
    "When did the Roman Empire fall?",
    "What are the main differences between Java and JavaScript?"
]

import requests

def run_calibration():
    print("Running Calibration (In-Scope vs Out-Of-Scope)...")
    in_scope_scores = []
    out_of_scope_scores = []

    print("\n--- In-Scope Queries ---")
    for q in IN_SCOPE:
        try:
            r = requests.post("http://127.0.0.1:8000/query", json={"question": q, "top_k": 1})
            chunks = r.json().get("evidence_panel", []) if r.status_code == 200 else []
            score = chunks[0].get("rerank_score", 0.0) if chunks else 0.0
        except Exception:
            score = 0.0
        in_scope_scores.append(score)
        print(f"[{score:.4f}] {q}")

    print("\n--- Out-of-Scope Queries ---")
    for q in OUT_OF_SCOPE:
        try:
            r = requests.post("http://127.0.0.1:8000/query", json={"question": q, "top_k": 1})
            chunks = r.json().get("evidence_panel", []) if r.status_code == 200 else []
            score = chunks[0].get("rerank_score", 0.0) if chunks else 0.0
        except Exception:
            score = 0.0
        out_of_scope_scores.append(score)
        print(f"[{score:.4f}] {q}")

    min_in = min(in_scope_scores) if in_scope_scores else 0.0
    max_out = max(out_of_scope_scores) if out_of_scope_scores else 0.0

    print("\n" + "=" * 50)
    print("CALIBRATION RESULTS")
    print("=" * 50)
    print(f"Lowest In-Scope Score:  {min_in:.4f}")
    print(f"Highest Out-Scope Score:{max_out:.4f}")
    if min_in > max_out:
        print(f"GAP DETECTED: {min_in - max_out:.4f}")
        print(f"RECOMMENDED THRESHOLD: {(min_in + max_out) / 2:.4f}")
    else:
        print("NO GAP! Overlap detected. Trade-off required.")

if __name__ == "__main__":
    run_calibration()
