"""FieldBrain configuration — everything comes from environment variables.

See .env.example for the full list. No secrets live in the codebase.
"""
import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    # --- LLM (OpenAI-compatible chat completions endpoint) ---
    # Later this points at our own vLLM server on AMD Developer Cloud (ROCm),
    # or at the Evolus OpenAI-compatible chat API. Empty => demo mode.
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "").rstrip("/")
    llm_api_key: str = os.environ.get("LLM_API_KEY", "")
    llm_model: str = os.environ.get("LLM_MODEL", "")

    # --- Evolus building blocks (REST) ---
    use_evolus: bool = _bool("USE_EVOLUS", False)
    evolus_base_url: str = os.environ.get("EVOLUS_BASE_URL", "").rstrip("/")
    evolus_api_key: str = os.environ.get("EVOLUS_API_KEY", "")
    evolus_kb_id: str = os.environ.get("EVOLUS_KB_ID", "")
    evolus_workflow_id: str = os.environ.get("EVOLUS_WORKFLOW_ID", "")

    # --- Retrieval / hand-off ---
    # Confidence gate (see qa.answer_question): the top chunk must clear this
    # BM25 score AND at least half the question's content terms must appear in
    # the retrieved chunks. Failing either means "the docs can't answer it"
    # and the hand-off branch fires. The score floor is tuned against the
    # bundled seed corpus; the coverage gate is what catches on-topic-worded
    # questions about facts the documents never state (e.g. refrigerant type).
    handoff_threshold: float = float(os.environ.get("HANDOFF_THRESHOLD", "2.5"))
    top_k: int = int(os.environ.get("TOP_K", "6"))

    # --- Storage ---
    data_dir: str = os.environ.get("DATA_DIR", "data")

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_base_url and self.llm_model)

    @property
    def evolus_configured(self) -> bool:
        return bool(self.evolus_base_url and self.evolus_api_key)

    @property
    def mode(self) -> str:
        if self.use_evolus and self.evolus_configured:
            return "evolus"
        if self.llm_configured:
            return "llm"
        return "demo"


settings = Settings()
