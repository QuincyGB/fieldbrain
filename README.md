# FieldBrain — Technician Manual Q&A with Honest Hand-Off

Built for the **AMD Developer Hackathon ACT III** (Track 1: Intelligent Industry,
plus the Evolus "Business Agents on AMD" partner track). MIT licensed.

## The problem

Field technicians lose time digging through equipment manuals and old work
orders, and junior techs miss the recommended next action. The documents exist —
nobody can query them from a rooftop.

## What FieldBrain does

A technician asks a plain-language question ("compressor short-cycling, fault
code E47 — what do I check first?") and gets:

1. **An answer grounded in the uploaded manuals + maintenance history**, with
   named sources (document + section) — never free-floating model text.
2. **A recommended action checklist**, extracted from the manual's own
   procedure, in order.
3. **An escalation hand-off when the docs can't answer.** If retrieval
   confidence is low, FieldBrain says so, and returns a structured summary
   (question, what was searched, closest matches, suggested route) for a senior
   tech or dispatcher — instead of guessing. Honest uncertainty is the feature.

## Quick start

### Local (Python 3.12)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # defaults = offline demo mode, no keys needed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 — the bundled seed corpus (two fictional manuals +
one maintenance log) is indexed automatically at startup.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

Then open http://localhost:8000.

### Run the demo scenario

With the server running:

```bash
python scripts/run_demo.py
```

1. **"The rooftop unit keeps short-cycling and shows fault code E47. What
   should I check first?"** → sourced answer from the RTU-9000 manual's E47
   section (corroborated by the 2026-03-14 maintenance log entry, where the
   same fault was fixed by washing the condenser coil) + the manual's ordered
   checklist of recommended checks.
2. **"What refrigerant type does the RTU-9000 use, and what is its factory
   charge weight in kilograms?"** → the seed documents deliberately never state
   the refrigerant type or charge weight, so the question fails the confidence
   gate (top-chunk BM25 score + IDF-weighted coverage of the question's terms)
   and the **hand-off branch** returns an escalation summary instead of an
   invented spec.

## API

| Endpoint | What it does |
|---|---|
| `GET /` | Chat UI |
| `GET /health` | Status, active mode, indexed document/chunk counts |
| `GET /api/documents` | List indexed documents |
| `POST /admin/upload` | Multipart upload of `.txt` / `.md` / `.pdf`; extracted, chunked, indexed, persisted under `data/uploads/` |
| `POST /api/ask` | `{"question": "..."}` → answer + checklist + sources, or a hand-off object |

## Architecture

```
app/
  main.py           FastAPI app: UI, upload, ask, health
  retrieval.py      Section-aware chunking + from-scratch BM25 index (offline)
  qa.py             Pipeline: retrieve -> confidence gate -> answer | hand-off
  evolus_client.py  Evolus REST client stub (Knowledge Library + Workflow)
  config.py         All configuration from environment variables
data/seed/          Fictional sample manuals + maintenance log (demo corpus)
scripts/run_demo.py The two-question demo scenario above
```

Retrieval is deliberately embedding-free in the scaffold (BM25 over
section-aware chunks) so the whole demo runs offline with zero keys. The
pipeline's `search()` shape is the seam where the Evolus Knowledge Library —
or a vector index — drops in.

## How the AMD + Evolus pieces plug in

**AMD (the required AMD workload).** The main agent's model is an open model
(Qwen/Llama family) served by **vLLM on AMD Developer Cloud (ROCm)**. Point the
app at it — no code change:

```bash
LLM_BASE_URL=http://<amd-developer-cloud-instance>:8001/v1
LLM_MODEL=<served-model-name>
LLM_API_KEY=<if the endpoint is key-protected>
```

`app/qa.py` then sends the retrieved chunks to that endpoint's
OpenAI-compatible `/chat/completions` and returns its grounded answer. If the
endpoint is unreachable the app falls back to offline demo mode rather than
failing the technician. Health reports `mode: "llm"` when configured.

**Evolus building blocks (≥2, per the partner track).**

1. **Knowledge Library** — the manuals + maintenance records live in an Evolus
   knowledge library; `EvolusClient.query_knowledge_library()` retrieves from
   it (`POST /v1/knowledge-libraries/{id}/query`).
2. **Workflow** — question → retrieve → answer → checklist → hand-off runs as
   an Evolus workflow; `EvolusClient.run_workflow()` drives it
   (`POST /v1/workflows/{id}/run`). The hand-off branch is part of the
   workflow's outputs.
3. **Document Extractor** (hook ready) — scanned service reports → structured
   JSON on ingest, via `EvolusClient.extract_document()`.

Enable with:

```bash
USE_EVOLUS=true
EVOLUS_BASE_URL=<workspace API base>
EVOLUS_API_KEY=<workspace key>
EVOLUS_KB_ID=<knowledge library id>
EVOLUS_WORKFLOW_ID=<workflow id>
```

Exact Evolus paths/payloads get pinned in `app/evolus_client.py` once the free
event workspace is created (event code shared at kickoff; workspace free until
Oct 31). Nothing else in the app changes — `qa.py` depends only on the two
method signatures.

## Modes

`GET /health` reports the active mode: `demo` (offline extractive, default),
`llm` (OpenAI-compatible endpoint configured), or `evolus` (Evolus enabled and
configured). The confidence gate runs in every mode.

## Status / what's left

Scaffold: ✅ app, retrieval, hand-off branch, demo corpus, Docker, Evolus stub.
Next, when access lands: claim the $100 AMD Developer Cloud credits → stand up
vLLM with an open model → set `LLM_*`; create the Evolus event workspace →
build the Knowledge Library + Workflow blocks → set `EVOLUS_*` / `USE_EVOLUS`;
then end-to-end test, demo video, and submission before the Oct 18 deadline.
