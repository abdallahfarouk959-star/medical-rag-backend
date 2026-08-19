"""
Structure-Aware Clinical PDF Ingestion
--------------------------------------
- Layout-aware parsing (PyMuPDF dict-mode + native table finder)
- TABLE-ATOMIC chunking: dosage tables are never split mid-row
- Section-aware hierarchical breadcrumbs (H1 > H2 > H3)
- Token sizing with the EXACT tokenizer of the embedding model (no silent truncation)
- Deterministic, globally-unique, collision-free chunk_id
- Repeated header/footer furniture removal
- Precise Bounding Box (bbox) and Snippet extraction for Front-end Highlighting
- Optional unstructured.io backend (hackathon-recommended) via ENGINE flag
"""
from __future__ import annotations

import hashlib
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Optional

import pymupdf
from transformers import AutoTokenizer

# ---------------------------------------------------------------- config
EMBED_MODEL_NAME = "pritamdeka/S-PubMedBert-MS-MARCO"
MODEL_MAX_TOKENS = 512          # hard ceiling of the BERT backbone
CONTEXT_HEADER_BUDGET = 48      # reserved for the contextual prefix
TARGET_TOKENS = 400             # hackathon target band: 300-500
MIN_CHUNK_TOKENS = 45
OVERLAP_RATIO = 0.12            # hackathon target band: 10-15%
HEADER_BAND = 0.075             # top 7.5% of the page
FOOTER_BAND = 0.925             # bottom 7.5% of the page
INGESTION_ENGINE = os.getenv("INGESTION_ENGINE", "pymupdf")  # pymupdf | unstructured

_TOKENIZER = None


def _tok():
    global _TOKENIZER
    if _TOKENIZER is None:
        _TOKENIZER = AutoTokenizer.from_pretrained(EMBED_MODEL_NAME)
    return _TOKENIZER


def count_tokens(text: str) -> int:
    """Counts tokens with the SAME WordPiece tokenizer used by the encoder."""
    return len(_tok().encode(text, add_special_tokens=False))


def _hard_truncate(text: str, limit: int) -> str:
    ids = _tok().encode(text, add_special_tokens=False)
    if len(ids) <= limit:
        return text
    return _tok().decode(ids[:limit], skip_special_tokens=True)


# ---------------------------------------------------------------- elements
@dataclass
class Element:
    kind: str            # "heading" | "text" | "table"
    text: str
    page: str            # printed page label or 1-based index string
    y: float
    level: int = 99
    size: float = 0.0
    bbox: tuple = (0.0, 0.0, 0.0, 0.0)  # Added to track coordinates for UI highlighting
    meta: dict = field(default_factory=dict)


_BOLD_FLAG = 1 << 4
_NUMBERED = re.compile(r"^(\d+(\.\d+){0,3})[\.\)]?\s+\S")
_SENT_SPLIT = re.compile(r"(?<=[\.\;\:\!\?])\s+(?=[A-Z0-9\(\u2022\-])")
_PAGE_NUM_ONLY = re.compile(r"^[\s\-–—ivxlcIVXLC\.\|]*\d{0,4}[\s\-–—\.\|]*$")


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _furniture_signatures(doc) -> set[str]:
    """Lines that repeat in the header/footer bands across >=50% of pages."""
    counter, n_pages = Counter(), len(doc)
    for page in doc:
        h = page.rect.height or 1.0
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") != 0:
                continue
            rel = block["bbox"][1] / h
            if rel > HEADER_BAND and rel < FOOTER_BAND:
                continue
            raw = _normalize(" ".join(
                sp["text"] for ln in block["lines"] for sp in ln["spans"]))
            if raw:
                counter[re.sub(r"\d+", "#", raw.lower())] += 1
    threshold = max(2, int(n_pages * 0.5))
    return {sig for sig, c in counter.items() if c >= threshold}


def _body_font_size(doc) -> float:
    weights = Counter()
    for page in doc:
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") != 0:
                continue
            for ln in block["lines"]:
                for sp in ln["spans"]:
                    weights[round(sp["size"], 1)] += len(sp["text"])
    return weights.most_common(1)[0][0] if weights else 10.0


def _table_to_markdown(table) -> str:
    try:
        md = table.to_markdown()
        if md and md.strip():
            return md.strip()
    except Exception:
        pass
    rows = [[(c or "").replace("\n", " ").strip() for c in r]
            for r in (table.extract() or [])]
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    out = ["| " + " | ".join(head) + " |",
           "| " + " | ".join(["---"] * len(head)) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in body]
    return "\n".join(out)


def _parse_pymupdf(doc, toc_map: dict[int, str]) -> list[Element]:
    furniture = _furniture_signatures(doc)
    body_size = _body_font_size(doc)
    elements: list[Element] = []

    for pno in range(len(doc)):
        page = doc.load_page(pno)
        page_h = page.rect.height or 1.0

        page_label = page.get_label()
        actual_page = page_label if page_label else str(pno + 1)

        # --- 1. tables first, so their area can be masked out of the text flow
        table_rects: list[pymupdf.Rect] = []
        try:
            for tb in page.find_tables().tables:
                rect = pymupdf.Rect(tb.bbox)
                md = _table_to_markdown(tb)
                if md:
                    table_rects.append(rect)
                    elements.append(Element("table", md, actual_page, rect.y0,
                                            bbox=(rect.x0, rect.y0, rect.x1, rect.y1),
                                            meta={"n_rows": tb.row_count,
                                                  "n_cols": tb.col_count}))
        except Exception:
            pass

        # --- 2. narrative text, excluding anything inside a table bbox
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") != 0:
                continue
            brect = pymupdf.Rect(block["bbox"])
            if brect.get_area() > 0 and any(
                    (brect & tr).get_area() / brect.get_area() > 0.45
                    for tr in table_rects):
                continue

            rel = brect.y0 / page_h
            buf, max_size, is_bold = [], 0.0, True
            for ln in block["lines"]:
                for sp in ln["spans"]:
                    buf.append(sp["text"])
                    max_size = max(max_size, sp["size"])
                    is_bold &= bool(sp["flags"] & _BOLD_FLAG)
            text = _normalize(" ".join(buf))
            if not text or _PAGE_NUM_ONLY.match(text):
                continue
            if (rel <= HEADER_BAND or rel >= FOOTER_BAND) and \
                    re.sub(r"\d+", "#", text.lower()) in furniture:
                continue

            looks_heading = (
                len(text) <= 145
                and not text.endswith((".", ";", ","))
                and (max_size >= body_size + 0.7
                     or (is_bold and len(text) <= 110)
                     or bool(_NUMBERED.match(text)))
            )
            elements.append(Element(
                "heading" if looks_heading else "text",
                text, actual_page, brect.y0, size=round(max_size, 1),
                bbox=(brect.x0, brect.y0, brect.x1, brect.y1)))

        # --- 3. TOC fallback if the page opens a known section
        if pno + 1 in toc_map and not any(
                e.page == actual_page and e.kind == "heading" for e in elements):
            elements.append(Element("heading", toc_map[pno + 1],
                                    actual_page, -1.0, size=body_size + 3,
                                    bbox=(0.0, 0.0, 0.0, 0.0)))

    elements.sort(key=lambda e: (e.page, e.y))

    # --- 4. rank heading font sizes -> hierarchy levels (H1/H2/H3)
    sizes = sorted({e.size for e in elements if e.kind == "heading"},
                   reverse=True)[:3]
    for e in elements:
        if e.kind == "heading":
            e.level = (sizes.index(e.size) + 1) if e.size in sizes else 3
    return elements


def _parse_unstructured(file_path: str) -> Optional[list[Element]]:
    """Hackathon-recommended backend. Requires `unstructured[pdf]` + poppler."""
    try:
        from unstructured.partition.pdf import partition_pdf
    except Exception:
        return None
    try:
        raw = partition_pdf(filename=file_path, strategy="hi_res",
                            infer_table_structure=True)
    except Exception:
        return None

    out, level_of = {"Title": 1, "Header": 1, "SectionHeader": 2}
    for i, el in enumerate(raw):
        cat = type(el).__name__
        page = getattr(el.metadata, "page_number", None) or 1
        
        # Extract coordinates if available
        bbox = (0.0, 0.0, 0.0, 0.0)
        if hasattr(el.metadata, "coordinates") and el.metadata.coordinates:
            pts = el.metadata.coordinates.points
            if len(pts) >= 4:
                bbox = (pts[0][0], pts[0][1], pts[2][0], pts[2][1])

        if cat == "Table":
            html = getattr(el.metadata, "text_as_html", "") or el.text
            out.append(Element("table", html.strip(), str(page), i, bbox=bbox,
                               meta={"format": "html"}))
        elif cat in level_of:
            out.append(Element("heading", _normalize(el.text), str(page), i,
                               level=level_of[cat], bbox=bbox))
        elif cat in ("NarrativeText", "ListItem", "UncategorizedText"):
            if el.text and el.text.strip():
                out.append(Element("text", _normalize(el.text), str(page), i, bbox=bbox))
    return out or None


# ---------------------------------------------------------------- chunking
def _split_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in _SENT_SPLIT.split(text) if p.strip()]
    return parts or ([text] if text.strip() else [])


def _pack(sentences: list[str], budget: int, overlap_tokens: int) -> list[list[str]]:
    """Greedy sentence packing with sentence-aligned overlap."""
    chunks, cur, cur_tok = [], [], 0
    for sent in sentences:
        st = count_tokens(sent)
        if st > budget:                       # monster sentence -> hard split
            if cur:
                chunks.append(cur); cur, cur_tok = [], 0
            ids = _tok().encode(sent, add_special_tokens=False)
            step = budget - int(budget * OVERLAP_RATIO)
            for i in range(0, len(ids), step):
                chunks.append([_tok().decode(ids[i:i + budget],
                                             skip_special_tokens=True)])
            continue
        if cur_tok + st > budget and cur:
            chunks.append(cur)
            tail, tail_tok = [], 0
            for s in reversed(cur):           # build the overlap window
                t = count_tokens(s)
                if tail_tok + t > overlap_tokens:
                    break
                tail.insert(0, s); tail_tok += t
            cur, cur_tok = list(tail), tail_tok
        cur.append(sent); cur_tok += st
    if cur:
        chunks.append(cur)
    return chunks


def _split_table(md: str, budget: int) -> list[str]:
    """Splits an oversized table by ROWS, repeating the header on every part."""
    if count_tokens(md) <= budget:
        return [md]
    lines = md.split("\n")
    header = lines[:2] if len(lines) > 2 and set(lines[1]) <= set("|- :") \
        else lines[:1]
    body, parts, cur = lines[len(header):], [], list(header)
    for row in body:
        if count_tokens("\n".join(cur + [row])) > budget and len(cur) > len(header):
            parts.append("\n".join(cur)); cur = list(header)
        cur.append(row)
    if len(cur) > len(header):
        parts.append("\n".join(cur))
    total = len(parts)
    return [f"{p}\n\n_(table part {i+1} of {total})_" for i, p in enumerate(parts)]


# ---------------------------------------------------------------- public API
def process_and_chunk_pdf(file_path: str, filename: str) -> list[dict[str, Any]]:
    with open(file_path, "rb") as fh:
        doc_id = hashlib.sha1(fh.read()).hexdigest()[:10]

    doc = pymupdf.open(file_path)
    toc_map: dict[int, str] = {}
    try:
        for _lvl, title, pg in (doc.get_toc() or []):
            if pg >= 1:
                toc_map.setdefault(int(pg), _normalize(title))
    except Exception:
        pass

    elements = (_parse_unstructured(file_path)
                if INGESTION_ENGINE == "unstructured" else None)
    engine = "unstructured.io"
    if not elements:
        elements = _parse_pymupdf(doc, toc_map)
        engine = "pymupdf-layout"
    doc.close()

    doc_title = os.path.splitext(filename)[0].replace("_", " ")[:80]
    budget = min(TARGET_TOKENS, MODEL_MAX_TOKENS - CONTEXT_HEADER_BUDGET)
    overlap = max(24, int(budget * OVERLAP_RATIO))

    chunks: list[dict[str, Any]] = []
    breadcrumb: list[str] = []
    buffer: list[Element] = []
    counter = 0

    def flush():
        """Emits the accumulated narrative buffer as section-aware chunks."""
        nonlocal buffer, counter
        if not buffer:
            return
        section_path = " > ".join(breadcrumb) if breadcrumb else "General"
        section_title = breadcrumb[-1] if breadcrumb else "General"
        sentences, owner = [], {}
        
        for el in buffer:
            for s in _split_sentences(el.text):
                # Save page and original bbox for every sentence
                owner[len(sentences)] = {"page": el.page, "bbox": el.bbox}
                sentences.append(s)
        
        idx = 0
        for group in _pack(sentences, budget, overlap):
            body = " ".join(group)
            if count_tokens(body) < MIN_CHUNK_TOKENS and chunks and \
                    chunks[-1]["metadata"]["section_path"] == section_path:
                chunks[-1]["text"] += " " + body          # absorb orphan tails
                continue
                
            start = sentences.index(group[0]) if group[0] in sentences else 0
            
            # Map chunk to corresponding pages and extract the primary BBox
            pages = sorted({owner.get(start + i, {"page": buffer[0].page})["page"] for i in range(len(group))})
            primary_bbox = owner.get(start, {"bbox": buffer[0].bbox}).get("bbox", (0.0, 0.0, 0.0, 0.0))
            
            counter += 1
            chunks.append(_make(doc_id, doc_title, filename, body, "narrative",
                                section_title, section_path, pages, counter,
                                engine, bbox=primary_bbox))
            idx += 1
        buffer = []

    for el in elements:
        if el.kind == "heading":
            flush()
            lvl = max(1, min(el.level, 3))
            breadcrumb = breadcrumb[:lvl - 1] + [el.text]
        elif el.kind == "table":
            flush()
            section_path = " > ".join(breadcrumb) if breadcrumb else "General"
            section_title = breadcrumb[-1] if breadcrumb else "General"
            for part in _split_table(el.text, budget):
                counter += 1
                chunks.append(_make(doc_id, doc_title, filename, part, "table",
                                    section_title, section_path, [el.page],
                                    counter, engine, bbox=el.bbox, extra=el.meta))
        else:
            buffer.append(el)
            if sum(count_tokens(b.text) for b in buffer) >= budget * 1.6:
                flush()
    flush()
    return chunks


def _make(doc_id, doc_title, filename, text, ctype, section_title,
          section_path, pages, counter, engine, bbox=(0.0, 0.0, 0.0, 0.0), extra=None) -> dict:
    page = pages[0]
    sec_hash = hashlib.md5(section_path.encode()).hexdigest()[:5]
    # Page can be a string, sanitize for chunk_id
    safe_page = re.sub(r'[^a-zA-Z0-9]', '', str(page))[:4]
    chunk_id = f"{doc_id}-p{safe_page}-{sec_hash}-c{counter:04d}"

    # Contextual prefix: proven to lift retrieval on hierarchical guidelines.
    prefix = f"[{doc_title} | {section_path} | Page {page}]"
    embed_text = _hard_truncate(f"{prefix}\n{text}",
                                MODEL_MAX_TOKENS - 4)      # NEVER truncated later

    md = {
        "document_id": doc_id,
        "document_name": filename,
        "document_title": doc_title,
        "section_title": section_title,
        "section_path": section_path,
        "page_number": page,
        "page_start": pages[0],
        "page_end": pages[-1],
        "chunk_id": chunk_id,
        "content_type": ctype,           # narrative | table
        "token_count": count_tokens(text),
        "parser_engine": engine,
        "source_url": "local_upload",
        # Added Snippet and BBox for Front-end Evidence Panel Highlighting
        "snippet": text[:200] + ("..." if len(text) > 200 else ""),
        "bbox": [str(x) for x in bbox],
    }
    if extra:
        md.update({f"table_{k}": v for k, v in extra.items()})
    return {"text": text, "embed_text": embed_text, "metadata": md}