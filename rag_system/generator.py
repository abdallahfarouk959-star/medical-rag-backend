"""Grounded generation with post-hoc citation verification for Day 3."""
from __future__ import annotations
import json
import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEN_MODEL = os.getenv("GEN_MODEL")

SYSTEM_PROMPT = """You are an evidence-grounded Clinical Decision Support synthesiser.
You summarise retrieved clinical-guideline passages for a licensed clinician.

## ABSOLUTE CONSTRAINTS:
1. Answer strictly using ONLY the provided CONTEXT. Do not use outside medical knowledge.
2. If the context contains the answer, summarize the direct recommendation and quote the verbatim evidence.
3. Extract accurate citation details (document name, section, and page number) matching the source context.
4. If the context is missing the answer, set "insufficient_evidence": true and "confidence": "insufficient".

## REQUIRED OUTPUT FORMAT (Return JSON ONLY):
{{
  "recommendation": "<Direct answer clinical in language plain>",
  "evidence": "<Verbatim context excerpt from recommendation supporting the>",
  "citations": [
    {{
      "document": "<Document name>",
      "section": "<Section title/path>",
      "page": <Page as integer number>
    }}
  ],
  "confidence": "high | medium | low | insufficient",
  "insufficient_evidence": false
}}

## CONTEXT:
{context}"""


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for idx, c in enumerate(chunks):
        md = c.get("metadata", {}) or {}
        page = md.get("page_number", md.get("page_start", 1))
        doc = md.get("document_name", md.get("document_title", "Medical Guideline"))
        sec = md.get("section_title", md.get("section_path", "General"))
        text = c.get("text", "")

        try:
            page_int = int(float(page))
        except (ValueError, TypeError):
            page_int = 1

        parts.append(
            f"--- SOURCE [{idx+1}] ---\n"
            f"DOCUMENT: {doc}\n"
            f"SECTION: {sec}\n"
            f"PAGE: {page_int}\n"
            f"TEXT: {text}\n"
            f"--- END SOURCE [{idx+1}] ---\n"
        )
    return "\n".join(parts)


def generate_grounded_response(
    query: str, retrieved_chunks: list[dict]
) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured in .env")

    if not retrieved_chunks:
        return {
            "recommendation": (
                "I couldn't find enough information in the indexed guidelines to"
                " answer this question."
            ),
            "evidence": "",
            "citations": [],
            "confidence": "insufficient",
            "insufficient_evidence": True,
        }

    context_str = _build_context(retrieved_chunks)

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GEN_MODEL,
        temperature=0.0,
        max_tokens=4096,  # 1. زيادة مساحة التوليد
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "CLINICAL QUESTION: {query}"),
    ])

    try:
        response = (prompt | llm).invoke(
            {"context": context_str, "query": query}
        ).content
        
        # 2. إزالة بلوك التفكير <think> بالكامل
        clean_response = re.sub(r"<think>.*?</think>\s*", "", response, flags=re.IGNORECASE | re.DOTALL)
        
        # تنظيف الرد من الـ Markdown لو الموديل بعته
        clean_response = re.sub(r"^```(?:json)?\s*", "", clean_response.strip(), flags=re.IGNORECASE)
        clean_response = re.sub(r"\s*```$", "", clean_response)
        
        data = json.loads(clean_response)

        raw_citations = data.get("citations", [])
        clean_citations = []
        for cit in raw_citations:
            try:
                p = int(float(cit.get("page", 1)))
            except (ValueError, TypeError):
                p = 1
            clean_citations.append({
                "document": str(cit.get("document", "Medical Guidelines")),
                "section": str(cit.get("section", "General")),
                "page": p,
            })

        confidence = data.get("confidence", "high").lower()
        insufficient = bool(data.get("insufficient_evidence", False))

        if confidence in ["high", "medium"] and not clean_citations:
            confidence = "insufficient"
            insufficient = True

        return {
            "recommendation": data.get("recommendation", ""),
            "evidence": data.get("evidence", ""),
            "citations": clean_citations,
            "confidence": confidence,
            "insufficient_evidence": insufficient,
        }

    except Exception as e:
        print(f"\n[DEBUG ERROR in generator.py]: {str(e)}\n")
        print(f"Raw Model Output was: {response if 'response' in locals() else 'None'}\n")
        return {
            "recommendation": (
                "An error occurred while generating the verified answer."
            ),
            "evidence": "",
            "citations": [],
            "confidence": "insufficient",
            "insufficient_evidence": True,
        }