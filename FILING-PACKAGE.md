# FieldBrain — AMD ACT III (lablab.ai) FILING PACKAGE

Paste-ready. All copy taken verbatim from `SUBMISSION-OFFLINE.md` (the
offline-honest filing copy of record). Do NOT substitute the run sheet's
long description — it claims a live vLLM endpoint and Evolus blocks that
do not exist at filing time.

---

**Title:**
FieldBrain — Technician Manual Q&A with Honest Hand-Off

**Selected challenge:**
Track 1 — Intelligent Industry

**Short description:**
Field technicians ask plain-language questions and get answers grounded in their own equipment manuals and maintenance history — with named sources, the manual's own action checklist, and an honest escalation hand-off instead of a guess when the docs can't answer.

**Long description:**
Field technicians lose time digging through equipment manuals and old work orders, and junior techs miss the recommended next action. The documents exist — nobody can query them from a rooftop. FieldBrain indexes uploaded manuals and maintenance logs and answers a question like "compressor short-cycling, fault code E47 — what do I check first?" with (1) an answer grounded in the retrieved sections, citing document + section, (2) a recommended action checklist extracted from the manual's own procedure, in order, and (3) when retrieval confidence is low, a structured hand-off summary (question, what was searched, closest matches, suggested route) for a senior tech or dispatcher. The demo build runs in offline demo mode: retrieval and answer assembly are local (BM25 over the indexed corpus), so it works with no external model call. The production architecture targets an open model served by vLLM on AMD Developer Cloud (ROCm) behind the same API; the grounding, checklist, and hand-off behaviour are identical in both modes, because they live in the retrieval layer, not the model. Built by a practitioner with 10 years managing residential and commercial service accounts — the workflow is the one he lived.

**Tech tags:**
FastAPI, BM25, RAG, Docker, Python, vLLM (target), ROCm (target), AMD Developer Cloud (target)

**Public GitHub repo:**
https://github.com/QuincyGB/fieldbrain

**Working prototype / app URL:**
No hosted URL — the demo build runs locally in offline demo mode
(`docker compose up`, or uvicorn per the repo README quick start; the
bundled seed corpus indexes automatically at startup). Use the GitHub
repo URL for this field if a URL is required.

**Demo video:**
demo-fieldbrain.mp4 (in this folder and in the GitHub repo) — narrated
capture of the bundled two-question demo (`scripts/run_demo.py`):
Q1 E47 short-cycling → sourced answer + manual checklist; Q2 refrigerant
type/charge weight → confidence gate → hand-off summary. The video
describes the build honestly as offline demo mode.

**Pitch presentation:**
pitch-fieldbrain.pdf (in this folder and in the GitHub repo) — 6 slides
built on the 5-beat outline in SUBMISSION-OFFLINE.md.

**Cover image:**
Required by the lablab package list (per the 2026-10-11 kickoff prep in
`~/workspace/hackathons/weekend-20261017-18-run-sheet.md`). None existed
in the project, so a simple title cover was generated:
cover-fieldbrain.png (1920×1080, in this folder and in the GitHub repo).

---

## Pre-flight results (Sat Oct 17, 2026, checked ~19:27–19:35 EDT)

- **AMD Developer Cloud activation email: NOT received.** Gmail search
  (`in:anywhere`, after Oct 14) over AMD / "Developer Cloud" / LabLab
  mail found exactly five messages: the Oct 15 "Your Free AMD Cloud
  Credits Are Waiting" email (pre-claim), an Oct 15 LabLab Discord-connect
  notice, an Oct 15 AMD profile-completeness marketing email, an Oct 15
  LabLab newsletter, and the Oct 16 LabLab ACT III registration
  confirmation. **No activation message has arrived since the credits
  claim was submitted on Oct 16** — so the offline-honest copy above
  governs, exactly as SUBMISSION-OFFLINE.md prescribes.
- **Evolus event code: NOT found.** A Gmail search for "evolus"
  (in:anywhere, full-text) returned zero messages. No event code exists
  in email, and no Evolus workspace exists — the Evolus partner-track
  claim stays out of the filing (already removed from the copy above).
- **GitHub repo: PUBLIC.** `gh repo view QuincyGB/fieldbrain` →
  visibility PUBLIC, https://github.com/QuincyGB/fieldbrain — judges can
  open it anonymously.
- **Demo verified fresh tonight:** `scripts/run_demo.py` re-run against
  the local server (health: mode=demo, 3 documents, 23 chunks); output
  saved as DEMO-RUN-FINAL.txt and byte-identical to today's earlier
  verified run (DEMO-RUN-2026-10-17.txt).
