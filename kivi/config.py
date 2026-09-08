"""Configuration, validated at startup.

The brief's reviewer is an agent that will not repair a misconfigured app, so config
failures must be loud and specific rather than surfacing later as a confusing 500.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent

# Sarvam published prices, INR per 1M tokens (docs.sarvam.ai/api-reference-docs/pricing,
# retrieved 2026-09-02). Used to report measured cost in rupees rather than an estimate.
SARVAM_PRICING_INR_PER_MTOK: dict[str, tuple[float, float]] = {
    "sarvam-105b": (29.28, 73.2),
    "sarvam-105b-conversations": (29.28, 73.2),
}


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from exc


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Thresholds:
    """Every number the system uses to make a decision, in one inspectable place.

    These are tuned on the dev split only (docs/03-evaluation-spec.md). The holdout
    split is never used to choose them.
    """

    # --- learning: evidence weights (docs/02-design.md, evidence ladder) ---
    w_manual_entry: float = 1.00      # E3 authoritative
    w_user_spelling: float = 0.95     # E1 authoritative
    w_user_edit: float = 0.90         # E2 authoritative
    w_repetition_step: float = 0.18   # E4 corroborating, per SEPARATE interaction
    w_repetition_cap: float = 0.85    # repetition alone can never reach certainty
    w_naming_frame: float = 0.40      # E6 suggestive -> candidate only
    w_app_context: float = 0.05       # E5 weak
    w_app_context_cap: float = 0.10   # and capped, so it can never promote on its own

    confirm_at: float = 0.70          # candidate -> confirmed
    candidate_floor: float = 0.30     # below this, nothing is stored

    # --- retrieval ---
    max_span_tokens: int = 4
    fuzzy_min_lexical: float = 0.72   # Jaro-Winkler floor for tier 3
    phonetic_min_lexical: float = 0.45  # a phonetic hit still needs SOME spelling proximity
    ambiguity_margin: float = 0.08    # top-2 within this -> abstain as ambiguous (N12)

    # --- context gate: the bar a candidate must clear, by situation ---
    ctx_required_default: float = 0.20        # heard form is not an ordinary English word
    ctx_required_ordinary: float = 0.55       # heard form IS an ordinary word (N1-N3)
    ctx_required_ordinary_common: float = 0.75  # ...and it is a very common one
    ctx_required_orthographic: float = 0.0    # meaning-preserving spelling swap (A11): always safe
    ctx_required_fuzzy: float = 0.45          # a COLD inexact match, where identity itself is a guess
    ctx_common_rank: int = 5000               # "very common" = frequency rank at or below this

    # Tokens more frequent than this are excluded from a memory's learned co-occurrence
    # profile. A word as common as "the" appearing near a memory carries no information,
    # and counting it let one function word clear the context bar on its own.
    ctx_profile_stopword_rank: int = 300

    # uncertain band around the bar, where the optional LLM adjudicator is consulted
    ctx_uncertain_band: float = 0.15


@dataclass(frozen=True)
class Config:
    db_path: Path
    llm_api_key: str | None
    llm_model: str
    llm_base_url: str
    llm_timeout_s: float
    apply_mode: str
    use_llm_adjudicator: bool
    thresholds: Thresholds = field(default_factory=Thresholds)

    @property
    def llm_available(self) -> bool:
        return bool(self.llm_api_key)

    def price_per_mtok(self) -> tuple[float, float]:
        return SARVAM_PRICING_INR_PER_MTOK.get(self.llm_model, (0.0, 0.0))

    def describe(self) -> dict[str, object]:
        """Safe-to-log summary. Never includes the key itself."""
        return {
            "db_path": str(self.db_path),
            "apply_mode": self.apply_mode,
            "llm_configured": self.llm_available,
            "llm_model": self.llm_model if self.llm_available else None,
            "use_llm_adjudicator": self.use_llm_adjudicator,
        }


def load_config(*, env_file: str | os.PathLike[str] | None = None) -> Config:
    load_dotenv(env_file or (REPO_ROOT / ".env"), override=False)

    apply_mode = (os.environ.get("KIVI_APPLY_MODE") or "deterministic").strip().lower()
    if apply_mode not in {"deterministic", "prompt"}:
        raise ConfigError(
            f"KIVI_APPLY_MODE must be 'deterministic' or 'prompt', got {apply_mode!r}"
        )

    api_key = (os.environ.get("SARVAM_API_KEY") or "").strip() or None
    use_adjudicator = _env_bool("KIVI_USE_LLM_ADJUDICATOR", False)

    # Fail loudly on the one combination that cannot work, and say exactly how to fix it.
    if apply_mode == "prompt" and not api_key:
        raise ConfigError(
            "KIVI_APPLY_MODE=prompt needs a model key, but SARVAM_API_KEY is empty.\n"
            "Either set SARVAM_API_KEY in .env (see .env.example), or use "
            "KIVI_APPLY_MODE=deterministic, which needs no credentials."
        )
    if use_adjudicator and not api_key:
        raise ConfigError(
            "KIVI_USE_LLM_ADJUDICATOR=1 needs a model key, but SARVAM_API_KEY is empty.\n"
            "Set SARVAM_API_KEY in .env (see .env.example), or set "
            "KIVI_USE_LLM_ADJUDICATOR=0 to run the fully deterministic system."
        )

    db_raw = (os.environ.get("KIVI_DB_PATH") or "./kivi.db").strip()
    db_path = Path(db_raw)
    if not db_path.is_absolute():
        db_path = (REPO_ROOT / db_path).resolve()

    return Config(
        db_path=db_path,
        llm_api_key=api_key,
        llm_model=(os.environ.get("KIVI_LLM_MODEL") or "sarvam-105b").strip(),
        llm_base_url=(os.environ.get("KIVI_LLM_BASE_URL") or "https://api.sarvam.ai/v1").strip(),
        llm_timeout_s=_env_float("KIVI_LLM_TIMEOUT_S", 20.0),
        apply_mode=apply_mode,
        use_llm_adjudicator=use_adjudicator,
    )
