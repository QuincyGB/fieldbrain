"""Local document store: chunking + BM25 retrieval (no embeddings, no network).

Documents arrive as .txt / .md / .pdf uploads (or the bundled seed set), are
split into section-aware chunks, and indexed with a small from-scratch BM25
implementation. This keeps the scaffold fully runnable offline; the Evolus
Knowledge Library (or a real vector index) can replace this module later
behind the same `search()` shape.
"""
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field

TOKEN_RE = re.compile(r"[a-z0-9]+")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
MAX_CHUNK_CHARS = 700

# Common words carry no retrieval signal; fault codes ("e47") and model
# numbers ("9000") are not stopwords and stay.
STOPWORDS = frozenset("""
a an and are as at be been by can could did do does for from had has have how
i if in into is it its me my of on or our should so than that the their them
then there these they this to under up was we what when where which who why
will with would you your
get gets got give gives keep keeps kept know make makes say says see show
shows showed take takes tell
""".split())


def _stem(token: str) -> str:
    # Crude singularisation so "checks" in a heading matches "check" in a
    # question (and "pressures" -> "pressure"). Good enough for this corpus;
    # a real stemmer can replace it later.
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    return [_stem(t) for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


@dataclass
class Chunk:
    doc_name: str
    heading: str
    text: str
    tokens: list[str] = field(default_factory=list)


@dataclass
class SearchHit:
    chunk: Chunk
    score: float


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown/plain text into (heading, body) sections."""
    sections: list[tuple[str, str]] = []
    heading = "Introduction"
    buf: list[str] = []
    for line in text.splitlines():
        m = HEADING_RE.match(line.strip())
        if m:
            if buf:
                sections.append((heading, "\n".join(buf).strip()))
            heading = m.group(2).strip()
            buf = []
        else:
            buf.append(line)
    if buf:
        sections.append((heading, "\n".join(buf).strip()))
    return [(h, b) for h, b in sections if b]


def chunk_text(doc_name: str, text: str) -> list[Chunk]:
    """Split into chunks; the section heading is part of each chunk's tokens.

    Headings carry the discriminative terms ("Fault E47", "Recommended
    checks"), so a procedure chunk whose body never repeats the fault code
    still retrieves against it.
    """
    chunks: list[Chunk] = []

    def make(heading: str, body_text: str) -> Chunk:
        return Chunk(doc_name, heading, body_text, tokenize(heading + "\n" + body_text))

    for heading, body in _split_sections(text):
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        current = ""
        for para in paragraphs:
            if len(current) + len(para) + 1 <= MAX_CHUNK_CHARS:
                current = (current + "\n" + para).strip()
            else:
                if current:
                    chunks.append(make(heading, current))
                # Very long single paragraphs are hard-split.
                while len(para) > MAX_CHUNK_CHARS:
                    chunks.append(make(heading, para[:MAX_CHUNK_CHARS]))
                    para = para[MAX_CHUNK_CHARS:]
                current = para
        if current:
            chunks.append(make(heading, current))
    return chunks


def extract_text(path: str, raw: bytes) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(raw))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    return raw.decode("utf-8", errors="replace")


class DocumentStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.documents: dict[str, int] = {}  # doc_name -> chunk count
        self._df: Counter = Counter()
        self._avgdl: float = 0.0

    # -- ingestion ---------------------------------------------------------
    def add_document(self, doc_name: str, text: str) -> int:
        new_chunks = chunk_text(doc_name, text)
        self.chunks.extend(new_chunks)
        self.documents[doc_name] = self.documents.get(doc_name, 0) + len(new_chunks)
        self._rebuild_index()
        return len(new_chunks)

    def load_directory(self, directory: str) -> None:
        if not os.path.isdir(directory):
            return
        for name in sorted(os.listdir(directory)):
            if os.path.splitext(name)[1].lower() not in (".txt", ".md", ".pdf"):
                continue
            path = os.path.join(directory, name)
            with open(path, "rb") as fh:
                self.add_document(name, extract_text(path, fh.read()))

    def _rebuild_index(self) -> None:
        self._df = Counter()
        total_len = 0
        for chunk in self.chunks:
            total_len += len(chunk.tokens)
            for term in set(chunk.tokens):
                self._df[term] += 1
        self._avgdl = (total_len / len(self.chunks)) if self.chunks else 0.0

    def idf(self, term: str) -> float:
        n_docs = len(self.chunks) or 1
        df = self._df.get(term, 0)
        return math.log(1 + (n_docs - df + 0.5) / (df + 0.5))

    # -- retrieval (BM25, k1=1.5, b=0.75) ----------------------------------
    def search(self, query: str, k: int = 4) -> list[SearchHit]:
        q_tokens = tokenize(query)
        if not q_tokens or not self.chunks:
            return []
        n_docs = len(self.chunks)
        hits: list[SearchHit] = []
        for chunk in self.chunks:
            tf = Counter(chunk.tokens)
            dl = len(chunk.tokens) or 1
            score = 0.0
            for term in set(q_tokens):
                if term not in tf:
                    continue
                df = self._df.get(term, 0)
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                freq = tf[term]
                denom = freq + 1.5 * (1 - 0.75 + 0.75 * dl / (self._avgdl or 1))
                score += idf * (freq * 2.5) / denom
            if score > 0:
                hits.append(SearchHit(chunk, round(score, 3)))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]
