"""Evolus REST client — stub with the documented integration shape.

FieldBrain drives Evolus building blocks over REST (per the ACT III Evolus
track brief): a Knowledge Library holding the manuals + maintenance records,
and a Workflow that runs question -> retrieve -> answer -> checklist ->
hand-off. This client wraps those two blocks:

    POST {EVOLUS_BASE_URL}/v1/knowledge-libraries/{kb_id}/query
         {"query": "...", "top_k": 4}
         -> {"results": [{"text": ..., "source": ..., "score": ...}, ...]}

    POST {EVOLUS_BASE_URL}/v1/workflows/{workflow_id}/run
         {"inputs": {"question": ..., "context": [...]}}
         -> {"outputs": {"answer": ..., "checklist": [...], "handoff": bool}}

Exact paths/payloads get pinned once the free event workspace exists (event
code arrives at kickoff); the call sites in qa.py only depend on the two
method signatures below, so wiring the real workspace is a change to this
file only. The third building block from the brief — the Document Extractor
— has its ingest hook here too (`extract_document`), used later for scanned
service reports.

No real keys are bundled; base URL + API key come from the environment.
No live calls are made unless USE_EVOLUS=true and both are set.
"""
import httpx


class EvolusNotConfiguredError(RuntimeError):
    pass


class EvolusClient:
    def __init__(self, base_url: str, api_key: str, kb_id: str = "", workflow_id: str = ""):
        if not base_url or not api_key:
            raise EvolusNotConfiguredError(
                "EVOLUS_BASE_URL and EVOLUS_API_KEY must be set to use Evolus."
            )
        self.base_url = base_url.rstrip("/")
        self.kb_id = kb_id
        self.workflow_id = workflow_id
        self._client = httpx.Client(
            timeout=30.0,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )

    def query_knowledge_library(self, question: str, top_k: int = 4) -> list[dict]:
        """Retrieve grounded chunks from the Evolus Knowledge Library block."""
        resp = self._client.post(
            f"{self.base_url}/v1/knowledge-libraries/{self.kb_id}/query",
            json={"query": question, "top_k": top_k},
        )
        resp.raise_for_status()
        return resp.json().get("results", [])

    def run_workflow(self, question: str, context_chunks: list[dict]) -> dict:
        """Run the Evolus Workflow block (answer + checklist + hand-off branch)."""
        resp = self._client.post(
            f"{self.base_url}/v1/workflows/{self.workflow_id}/run",
            json={"inputs": {"question": question, "context": context_chunks}},
        )
        resp.raise_for_status()
        return resp.json().get("outputs", {})

    def extract_document(self, filename: str, content: bytes) -> dict:
        """Document Extractor block hook: scanned service report -> structured JSON.

        Not wired into the upload path yet; lands when the workspace exists.
        """
        resp = self._client.post(
            f"{self.base_url}/v1/document-extractors/default/extract",
            files={"file": (filename, content)},
        )
        resp.raise_for_status()
        return resp.json()
