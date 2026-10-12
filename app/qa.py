"""Q&A pipeline: retrieve -> (answer with sources + checklist) OR hand off.

Flow (mirrors the Evolus Workflow block design):
  1. Retrieve top-k chunks locally (BM25) — or from the Evolus Knowledge
     Library when USE_EVOLUS is on.
  2. Confidence gate: if the best chunk scores below HANDOFF_THRESHOLD the
     documents cannot support an answer, so we return an escalation summary
     for a human instead of guessing. Honest uncertainty is a feature.
  3. Answer generation:
       - evolus mode: the Workflow block produces answer/checklist/handoff.
       - llm mode: an OpenAI-compatible chat endpoint (later: our own vLLM
         server on AMD Developer Cloud) writes the answer from the chunks.
       - demo mode (default, offline): extractive answer assembled from the
         retrieved chunks, so the whole demo runs with zero external calls.
"""
import re

import httpx

from .config import Settings
from .evolus_client import EvolusClient, EvolusNotConfiguredError
from .retrieval import DocumentStore, SearchHit

STEP_LINE = re.compile(r"^\s*(?:[-*]\s+Step\s+\d+:|\d+[.)]\s+|[-*]\s+)(.+)$", re.IGNORECASE)
NAMED_STEP = re.compile(r"^\s*[-*]\s+Step\s+\d+:", re.IGNORECASE)


def _clean(line_text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", line_text).strip()


def _chunk_items(text: str) -> list[tuple[bool, str]]:
    """List items in a chunk as (is_named_step, full_text).

    The seed documents hard-wrap lines, so an item's continuation lines are
    joined back into the item until the next item or a blank line.
    """
    items: list[tuple[bool, str]] = []
    current: list | None = None  # [is_named, text]
    for raw in text.splitlines():
        line = raw.strip()
        m = STEP_LINE.match(line)
        if m:
            if current:
                items.append((current[0], current[1]))
            current = [bool(NAMED_STEP.match(line)), _clean(m.group(1))]
        elif not line:
            if current:
                items.append((current[0], current[1]))
                current = None
        elif current is not None and not line.startswith("#"):
            current[1] = (current[1] + " " + _clean(line)).strip()
    if current:
        items.append((current[0], current[1]))
    return [(named, txt) for named, txt in items if txt]


def _extract_checklist(hits: list[SearchHit], store: DocumentStore | None = None,
                       limit: int = 8) -> list[str]:
    """Procedure lines from the retrieved chunks.

    Explicit "Step N:" lines (a manual's ordered procedure) come first, in
    document order; other list lines (causes, checks) follow. If the retrieved
    chunks contain no named procedure, fall back to the procedure section of
    the top hit's own document — manuals pair an explanation section with a
    separate procedure section that BM25 may rank below the cut.
    """
    named: list[str] = []
    other: list[str] = []
    for hit in hits:
        for is_named, text in _chunk_items(hit.chunk.text):
            if is_named:
                if text not in named:
                    named.append(text)
            elif text not in other and text not in named:
                other.append(text)
    if not named and store is not None and hits:
        top_doc = hits[0].chunk.doc_name
        best: list[str] = []
        for chunk in store.chunks:
            if chunk.doc_name != top_doc:
                continue
            steps = [t for is_named, t in _chunk_items(chunk.text) if is_named]
            if len(steps) > len(best):
                best = steps
        named = best
    return (named + other)[:limit]


def _term_coverage(question: str, hits: list[SearchHit], store: DocumentStore) -> float:
    """IDF-weighted fraction of the question's content terms covered by the
    retrieved chunks.

    A question can share a few high-frequency words with the corpus (model
    numbers, "compressor") while asking about something the documents never
    cover (refrigerant type, charge weight). Weighting by IDF means the
    uncovered *distinctive* terms — the ones the question is actually about —
    dominate the score, while missing filler words barely count.
    """
    from .retrieval import tokenize
    q_terms = set(tokenize(question))
    if not q_terms:
        return 0.0
    chunk_terms: set[str] = set()
    for hit in hits:
        chunk_terms.update(hit.chunk.tokens)
    total = sum(store.idf(t) for t in q_terms)
    covered = sum(store.idf(t) for t in q_terms & chunk_terms)
    return covered / total if total else 0.0


def _sources(hits: list[SearchHit]) -> list[dict]:
    best: dict[tuple[str, str], dict] = {}
    for hit in hits:
        key = (hit.chunk.doc_name, hit.chunk.heading)
        if key not in best or hit.score > best[key]["score"]:
            best[key] = {"document": key[0], "section": key[1], "score": hit.score}
    return sorted(best.values(), key=lambda e: e["score"], reverse=True)


def _handoff(question: str, hits: list[SearchHit], store: DocumentStore,
             top_score: float, coverage: float | None = None) -> dict:
    closest = [f"{h.chunk.doc_name} — {h.chunk.heading}" for h in hits[:2]]
    return {
        "type": "handoff",
        "question": question,
        "confidence": top_score,
        "coverage": coverage,
        "answer": None,
        "checklist": [],
        "sources": _sources(hits),
        "escalation": {
            "reason": (
                "The uploaded manuals and maintenance records do not contain enough "
                "information to answer this reliably, so FieldBrain is escalating "
                "instead of guessing."
            ),
            "summary": (
                f'Technician question: "{question}" — searched '
                f"{len(store.documents)} document(s) / {len(store.chunks)} sections. "
                f"Best match scored {top_score} with question-term coverage "
                f"{coverage if coverage is not None else 'n/a'} — below the "
                f"confidence gate, so no grounded answer exists in the library."
            ),
            "closest_matches": closest or ["(no matching sections at all)"],
            "suggested_route": (
                "Route to a senior technician / dispatcher with this summary attached "
                "to the work order, and add the missing document (spec sheet, nameplate "
                "photo, or vendor manual) to the library so the next tech gets an answer."
            ),
        },
    }


def _demo_answer(question: str, hits: list[SearchHit], top_score: float,
                 store: DocumentStore | None = None) -> dict:
    """Extractive grounded answer: lead chunk + procedure lines as the checklist.

    The lead chunk is the one carrying the manual's procedure (most "Step N:"
    lines) when one was retrieved — that is the section a technician actually
    needs — otherwise the top-scoring chunk.
    """
    def step_count(hit: SearchHit) -> int:
        return sum(1 for line in hit.chunk.text.splitlines() if NAMED_STEP.match(line.strip()))

    # Lead with a substantive explanatory chunk: not the procedure chunk (its
    # lines become the checklist) and not a bare summary table if a real
    # explanation was retrieved.
    explanatory = [h for h in hits if step_count(h) == 0]
    substantive = [h for h in explanatory if len(h.chunk.text) >= 400]
    lead_hit = max(substantive or explanatory or hits, key=lambda h: h.score)
    lead = lead_hit.chunk
    body = _clean(lead.text)
    answer = f"From {lead.doc_name} ({lead.heading}):\n\n{body}"
    return {
        "type": "answer",
        "question": question,
        "confidence": top_score,
        "answer": answer,
        "checklist": _extract_checklist(hits, store),
        "sources": _sources(hits),
        "escalation": None,
    }


def _llm_answer(settings: Settings, question: str, hits: list[SearchHit],
                top_score: float) -> dict:
    context = "\n\n".join(
        f"[{h.chunk.doc_name} — {h.chunk.heading}]\n{h.chunk.text}" for h in hits
    )
    prompt = (
        "You are FieldBrain, an assistant for field service technicians. Answer the "
        "question using ONLY the manual excerpts below. Be concrete and ordered. "
        "After the answer, list the recommended action checklist as bullet lines "
        "starting with '- '. If the excerpts do not answer the question, say so "
        "plainly instead of guessing.\n\n"
        f"Manual excerpts:\n{context}\n\nQuestion: {question}"
    )
    resp = httpx.post(
        f"{settings.llm_base_url}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"} if settings.llm_api_key else {},
        json={"model": settings.llm_model,
              "messages": [{"role": "user", "content": prompt}],
              "temperature": 0.2},
        timeout=60.0,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    checklist = [m.group(1).strip() for line in text.splitlines()
                 if (m := STEP_LINE.match(line.strip()))]
    return {
        "type": "answer",
        "question": question,
        "confidence": top_score,
        "answer": text,
        "checklist": checklist,
        "sources": _sources(hits),
        "escalation": None,
    }


COVERAGE_GATE = 0.6  # IDF-weighted coverage the retrieved chunks must reach


def answer_question(settings: Settings, store: DocumentStore, question: str) -> dict:
    hits = store.search(question, k=settings.top_k)
    top_score = hits[0].score if hits else 0.0
    coverage = round(_term_coverage(question, hits, store), 3) if hits else 0.0

    # Confidence gate first — applies in every mode. BM25 score alone is not
    # enough: a question about an uncovered topic can still rack up points on
    # shared words (model numbers), so term coverage gates it too.
    if not hits or top_score < settings.handoff_threshold or coverage < COVERAGE_GATE:
        return _handoff(question, hits, store, top_score, coverage)

    if settings.mode == "evolus":
        try:
            client = EvolusClient(settings.evolus_base_url, settings.evolus_api_key,
                                  settings.evolus_kb_id, settings.evolus_workflow_id)
            context = [{"text": h.chunk.text, "source": h.chunk.doc_name,
                        "score": h.score} for h in hits]
            outputs = client.run_workflow(question, context)
            if outputs.get("handoff"):
                return _handoff(question, hits, store, top_score)
            return {
                "type": "answer",
                "question": question,
                "confidence": top_score,
                "answer": outputs.get("answer", ""),
                "checklist": outputs.get("checklist", []),
                "sources": _sources(hits),
                "escalation": None,
            }
        except (EvolusNotConfiguredError, httpx.HTTPError):
            pass  # fall through to local answering

    if settings.mode == "llm":
        try:
            return _llm_answer(settings, question, hits, top_score)
        except httpx.HTTPError:
            pass  # fall through to demo mode rather than failing the tech

    return _demo_answer(question, hits, top_score, store)
