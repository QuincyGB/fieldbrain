"""FieldBrain — thin web app.

A technician asks a plain-language question and gets an answer grounded in the
uploaded equipment manuals + maintenance history, with sources and a
recommended action checklist — or an escalation hand-off when the documents
can't answer it.

Run:  uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import settings
from .qa import answer_question
from .retrieval import DocumentStore, extract_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_DIR = os.path.join(BASE_DIR, settings.data_dir, "seed")
UPLOAD_DIR = os.path.join(BASE_DIR, settings.data_dir, "uploads")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
ALLOWED_EXTENSIONS = (".txt", ".md", ".pdf")

store = DocumentStore()
store.load_directory(SEED_DIR)     # bundled demo corpus
store.load_directory(UPLOAD_DIR)   # anything uploaded in earlier sessions

app = FastAPI(title="FieldBrain", version="0.1.0")


class AskRequest(BaseModel):
    question: str


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": settings.mode,
        "documents": len(store.documents),
        "chunks": len(store.chunks),
        "handoff_threshold": settings.handoff_threshold,
    }


@app.get("/api/documents")
def list_documents():
    return {"documents": [{"name": name, "chunks": count}
                          for name, count in sorted(store.documents.items())]}


@app.post("/admin/upload")
async def upload(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. "
                                 f"Accepted: {', '.join(ALLOWED_EXTENSIONS)}")
    raw = await file.read()
    try:
        text = extract_text(file.filename, raw)
    except Exception as exc:  # corrupt PDF etc.
        raise HTTPException(400, f"Could not extract text from {file.filename}: {exc}")
    if not text.strip():
        raise HTTPException(400, f"No extractable text in {file.filename}.")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, os.path.basename(file.filename)), "wb") as fh:
        fh.write(raw)
    chunks = store.add_document(os.path.basename(file.filename), text)
    return {"document": os.path.basename(file.filename), "chunks_added": chunks,
            "total_documents": len(store.documents), "total_chunks": len(store.chunks)}


@app.post("/api/ask")
def ask(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(400, "Question must not be empty.")
    result = answer_question(settings, store, question)
    result["mode"] = settings.mode
    return result
