"""API surface tests, including the reviewer's whole journey through HTTP.

These run against the real app with a real database file (set in conftest), so a passing
suite means the endpoints the demo interface calls actually work.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from kivi.api import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/reset", json={"reseed": True})
        yield c


def test_health_reports_configuration_and_migrations(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert "001_init" in body["migrations_applied"]
    assert body["config"]["apply_mode"] == "deterministic"
    assert body["lexicon"]["ordinary_words"] > 10_000


def test_health_says_plainly_when_no_model_is_configured(client):
    body = client.get("/api/health?check_model=true").json()
    assert body["model_check"]["ok"] is False
    assert "SARVAM_API_KEY" in body["model_check"]["detail"]


def test_the_three_stages_come_back_together(client):
    body = client.post(
        "/api/memory-aware-format",
        json={"asr_text": "ask aditya to review the sarvam kiwi service"},
    ).json()
    assert body["stages"]["formatted"] == "Ask Aditya to review the Sarvam Kiwi service."
    assert body["stages"]["memory_aware"] == "Ask Aaditya to review the Sarvam Kivi service."
    assert body["intervened"] is True
    assert len(body["applied"]) == 2


def test_every_applied_correction_carries_its_reasoning(client):
    body = client.post(
        "/api/memory-aware-format", json={"formatted_text": "Ship the Kiwi update on Friday."}
    ).json()
    row = body["applied"][0]
    for key in (
        "memory_id", "match_tier", "lexical_score", "phonetic_score",
        "context_score", "required_context", "reason_code", "reason_text", "signals",
    ):
        assert key in row, f"missing {key} in the explanation payload"


def test_non_intervention_is_explained_rather_than_silent(client):
    body = client.post(
        "/api/memory-aware-format", json={"formatted_text": "I ate a kiwi on the flight."}
    ).json()
    assert body["intervened"] is False
    assert body["abstained"], "an abstention must be reported, not merely implied"
    assert body["abstained"][0]["reason_text"]


def test_a_decision_can_be_replayed_from_its_id(client):
    made = client.post(
        "/api/memory-aware-format", json={"formatted_text": "Ship the Kiwi update on Friday."}
    ).json()
    trace = client.get(f"/api/decisions/{made['decision_id']}").json()
    assert trace["memory_aware_text"] == made["stages"]["memory_aware"]
    assert trace["grouped"]["applied"]


def test_observations_return_every_learning_decision_including_refusals(client):
    body = client.post(
        "/api/observations",
        json={"formatted_text": "We might call the new service Kivali if legal agrees."},
    ).json()
    assert body["interaction_id"]
    outcomes = {d["outcome"] for d in body["decisions"]}
    assert "rejected" in outcomes


def test_memories_can_be_listed_filtered_and_inspected(client):
    listing = client.get("/api/memories").json()
    assert listing["count"] > 0

    confirmed = client.get("/api/memories?status=confirmed").json()
    assert all(m["status"] == "confirmed" for m in confirmed["memories"])

    target = next(m for m in confirmed["memories"] if m["canonical_form"] == "Kivi")
    detail = client.get(f"/api/memories/{target['id']}").json()
    assert detail["evidence"] and detail["events"] and detail["variants"]
    assert "context_terms" in detail


def test_a_memory_can_be_added_by_hand_and_is_authoritative(client):
    created = client.post(
        "/api/memories",
        json={
            "canonical_form": "Zorvex",
            "word_type": "product",
            "observed_forms": ["Zorvecks"],
            "gloss": "the inference gateway",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "confirmed"
    assert "Zorvecks" in [v["variant_form"] for v in body["variants"]]


def test_adding_a_duplicate_is_rejected_not_silently_merged(client):
    client.post("/api/memories", json={"canonical_form": "Dupe", "word_type": "term"})
    again = client.post("/api/memories", json={"canonical_form": "Dupe", "word_type": "term"})
    assert again.status_code == 409


def test_changing_a_canonical_form_supersedes_and_keeps_the_old_one(client):
    created = client.post(
        "/api/memories", json={"canonical_form": "Sumeetx", "word_type": "person"}
    ).json()
    updated = client.patch(
        f"/api/memories/{created['id']}", json={"canonical_form": "Sumitx"}
    ).json()

    assert updated["id"] != created["id"]
    old = client.get(f"/api/memories/{created['id']}").json()
    assert old["status"] == "superseded"
    assert old["superseded_by"] == updated["id"]
    assert old["canonical_form"] == "Sumeetx"


def test_deleting_then_restoring_a_memory_works_over_http(client):
    created = client.post(
        "/api/memories", json={"canonical_form": "Tempx", "word_type": "term"}
    ).json()
    assert client.delete(f"/api/memories/{created['id']}").json()["status"] == "deleted"
    assert client.post(f"/api/memories/{created['id']}/restore").json()["status"] != "deleted"


def test_deletion_takes_effect_on_the_next_request(client):
    listing = client.get("/api/memories?status=confirmed").json()
    kivi = next(m for m in listing["memories"] if m["canonical_form"] == "Kivi")

    before = client.post(
        "/api/memory-aware-format", json={"formatted_text": "Ship the Kiwi update on Friday."}
    ).json()
    assert before["intervened"] is True

    client.delete(f"/api/memories/{kivi['id']}")
    after = client.post(
        "/api/memory-aware-format", json={"formatted_text": "Ship the Kiwi update on Friday."}
    ).json()
    assert after["intervened"] is False

    client.post(f"/api/memories/{kivi['id']}/restore")
    client.patch(f"/api/memories/{kivi['id']}", json={"status": "confirmed"})


def test_learning_decisions_are_queryable_by_outcome(client):
    body = client.get("/api/learning-decisions?outcome=rejected").json()
    assert body["learning_decisions"]
    assert all(d["outcome"] == "rejected" for d in body["learning_decisions"])


def test_stats_report_storage_growth_and_model_cost(client):
    body = client.get("/api/stats").json()
    assert body["storage"]["file_bytes"] > 0
    assert body["storage"]["row_counts"]["word_memories"] > 0
    assert body["decisions"]["llm_cost_inr"] == 0.0    # nothing was configured


def test_reset_is_deterministic_and_reports_what_it_did(client):
    wiped = client.post("/api/reset", json={"reseed": False}).json()
    assert wiped["memory_count"] == 0
    assert client.get("/api/memories").json()["count"] == 0

    reseeded = client.post("/api/reset", json={"reseed": True}).json()
    assert reseeded["memory_count"] > 0
    assert reseeded["reseeded"]["observations"] > 0

    first = client.get("/api/memories").json()
    client.post("/api/reset", json={"reseed": True})
    second = client.get("/api/memories").json()
    assert [(m["canonical_form"], m["status"]) for m in first["memories"]] == [
        (m["canonical_form"], m["status"]) for m in second["memories"]
    ]


def test_prompt_mode_is_refused_clearly_without_a_key(client):
    res = client.post(
        "/api/memory-aware-format",
        json={"formatted_text": "Ship the Kiwi update.", "apply_mode": "prompt"},
    )
    assert res.status_code == 400
    assert "SARVAM_API_KEY" in res.json()["detail"]


def test_bad_requests_are_rejected_with_a_useful_message(client):
    assert client.post("/api/observations", json={}).status_code == 422
    assert client.post("/api/memory-aware-format", json={}).status_code == 422
    assert client.get("/api/memories/999999").status_code == 404
    assert client.get("/api/decisions/999999").status_code == 404


def test_the_demo_interface_and_api_docs_are_served(client):
    assert client.get("/").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/openapi.json").status_code == 200
