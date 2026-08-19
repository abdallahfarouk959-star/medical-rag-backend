"""Tiered guardrail: deterministic red flags -> semantic scope -> LLM fallback."""
from __future__ import annotations
import os, re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GUARD_MODEL = os.getenv("GUARD_MODEL")

# L0: Prompt Injections
PROMPT_INJECTION = re.compile(r"(?i)\b(ignore previous instructions|system prompt|disregard|you are now|bypass)\b")

# L0: Immediate Emergencies
EMERGENCY = re.compile(r"""(?ix)
 \b(crushing|severe|sudden)\s+(chest|head)\s*(pain|ache)
|\bheart\s*attack|myocardial\s+infarction\s+now|\bstroke\s+(now|symptoms)
|\bcan(?:'|no)?t\s+breathe|\bnot\s+breathing|\banaphyla|\bunresponsive
|\bseizure\s+(now|ongoing)|\bactive\s+bleeding|\bcall\s+(911|999|112|ambulance)
""")

# L1: Comprehensive Clinical Lexicon
CLINICAL_LEX = re.compile(r"""(?ix)\b(
  guideline|recommend|dose|dosage|dosing|mg|therapy|treatment|screening|diagnos|diagnostic|
  patient|adult|paediatric|pediatric|pregnan|physical\s+activity|sedentary|risk|evidence|
  contraindicat|prophylax|mortality|prevalence|management|indication|who|nice|uspstf|
  diabetes|diabetic|glucose|plasma|fasting|ogtt|hba1c|sugar|glycaemia|glycemia|
  metformin|glibenclamide|tolbutamide|insulin|retinopathy|nephropathy|neuropathy|foot|feet|
  blood\s+pressure|cholesterol|triglycerides|bmi|hypertension|albuminuria|creatinine
)\b""")

# L1: Obvious Non-medical / Out-of-scope topics
OUT_OF_SCOPE = re.compile(r"(?i)\b(capital of|weather|football|soccer|basketball|fifa|world cup|match|player|python|javascript|programming|recipe|cookie|baking|movie|poem|stock price|who won|translate|math|calculate|sum of|equation)\b|[\+\-\*\/\=]")

_llm = None

def _classify_with_llm(query: str) -> str:
    global _llm
    if not GROQ_API_KEY:
        return "Allowed"
    
    try:
        if _llm is None:
            _llm = ChatGroq(
                groq_api_key=GROQ_API_KEY,
                model_name=GUARD_MODEL,
                temperature=0.0,
                max_tokens=10  # تم تكبير المساحة ليسمح للموديل بالتفكير
            )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Classify the query for a clinical medical guidelines system. "
                       "Answer with ONE word only at the very end: 'CLINICAL' if it is related to diseases, symptoms, treatments, medications, or guidelines, "
                       "or 'OFFTOPIC' for general knowledge, sports, math, entertainment, coding, etc."),
            ("user", "{q}")
        ])
        # تم تصحيح _prompt إلى prompt هنا
        res = (prompt | _llm).invoke({"q": query[:300]}).content.strip().upper()
        return "Refuse" if "OFFTOPIC" in res or "CLINICAL" not in res else "Allowed"
    except Exception as e:
        print(f"[Guardrail LLM Error]: {e}")
        # في حال حدوث أي خطأ في الـ Guard LLM، يتم تمرير السؤال للـ Pipeline
        return "Allowed"


def check_query_safety(query: str) -> dict:
    q = (query or "").strip()
    if len(q) < 3:
        return {"allowed": False, "category": "Invalid", "reason": "Query is too short."}

    # 1. فحص محاولات الـ Injection
    if PROMPT_INJECTION.search(q):
        return {"allowed": False, "category": "Adversarial", "reason": "Query contains invalid system instructions."}

    # 2. فحص حالات الطوارئ القصوى
    if EMERGENCY.search(q):
        return {
            "allowed": False,
            "category": "Emergency",
            "reason": "Potential medical emergency detected. Please contact emergency services immediately."
        }

    # 3. فحص الكلمات الطبية الصريحة (تجاوز فوري للـ Pipeline بـ 0ms)
    if CLINICAL_LEX.search(q) and not OUT_OF_SCOPE.search(q):
        return {"allowed": True, "category": "Allowed", "reason": "In-scope clinical query."}

    # 4. فحص المواضيع غير الطبية الصريحة
    if OUT_OF_SCOPE.search(q) and not CLINICAL_LEX.search(q):
        return {"allowed": False, "category": "OutOfScope", "reason": "Outside the clinical guidelines domain."}

    # 5. للحالات الغامضة فقط (LLM classification)
    verdict = _classify_with_llm(q)
    is_allowed = (verdict == "Allowed")
    return {
        "allowed": is_allowed,
        "category": "Allowed" if is_allowed else "OutOfScope",
        "reason": "In-scope clinical query." if is_allowed else "Outside indexed clinical scope."
    }