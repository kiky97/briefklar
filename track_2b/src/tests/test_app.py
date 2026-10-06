from datetime import date

import pytest
from fastapi.testclient import TestClient

from app import pipeline
from app.grounding import find_amounts, find_dates, normalize_digits, parse_date
from app.llm import MockLLM, get_llm
from app.main import app
from eval.dataset import LETTERS
from eval.run_eval import score_explanation, score_extraction


def test_find_dates_handles_de_fr_it_formats():
    text = "bis 30.11.2026, am 12. November 2026, le 1er janvier 2027, entro il 15 novembre 2026, 2026-10-20"
    assert find_dates(text) == {
        date(2026, 11, 30), date(2026, 11, 12), date(2027, 1, 1), date(2026, 11, 15), date(2026, 10, 20)
    }


def test_parse_date_rejects_invalid():
    assert parse_date("31.02.2026") is None
    assert parse_date("2026-11-30") == date(2026, 11, 30)


def test_swiss_amounts_and_foreign_digits():
    assert {2486.40, 120.0} <= find_amounts("CHF 2'486.40 und Fr. 120.–")
    assert normalize_digits("٣٠.١١.٢٠٢٦") == "30.11.2026"


def test_english_formats_from_model_output():
    assert {date(2026, 10, 28)} == find_dates("by October 28, 2026")
    assert {1150.0, 73.30} <= find_amounts("CHF 1,150.00 plus CHF 73.30")
    assert 120.5 in find_amounts("Fr. 120,50")


def test_dates_to_dmy_and_language_labels():
    from app.grounding import dates_to_dmy
    from app.languages import label

    assert dates_to_dmy("Pay by November 30, 2026 or 12 November 2026.") == "Pay by 30.11.2026 or 12.11.2026."
    assert label("Tigrinya") == "Tigrinya (ትግርኛ)"
    assert label("English") == "English" and label("Klingon") == "Klingon"


def test_langcheck_tells_tigrinya_from_amharic():
    from eval.langcheck import check_language

    amharic = "ይህ ደብዳቤ ምን ነው? እስከ 31.10.2026 ድረስ ክፍያውን ያድርጉ። አስፈላጊ ቀናት"
    tigrinya = "እዚ እንታይ ደብዳቤ እዩ? ክሳብ 31.10.2026 ናይ CHF 120.00 ክትኸፍል ኣለካ።"
    assert check_language(amharic, "Tigrinya")["detected"] == "amharic"
    assert not check_language(amharic, "Tigrinya")["language_ok"]
    assert check_language(tigrinya, "Tigrinya")["language_ok"]
    assert check_language("Це податковий рахунок (Einsprache)", "Ukrainian")["language_ok"]
    assert not check_language("This is a tax bill", "Ukrainian")["language_ok"]


def test_parse_json_tolerates_fences_and_prose():
    assert pipeline.parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert pipeline.parse_json('Here you go: {"a": 1} hope it helps') == {"a": 1}
    with pytest.raises(ValueError):
        pipeline.parse_json("no json here")


class FakeLLM:
    """Returns a hallucinated date and amount to check that grounding flags them."""

    def chat(self, messages, task="", **kw):
        return """{"sender": "Steueramt", "letter_type": "tax", "urgency": "high",
                  "key_dates": [{"date": "30.11.2026", "kind": "deadline", "what": "pay"},
                                {"date": "2026-12-24", "kind": "nonsense", "what": "invented"}],
                  "amounts": [{"value": "CHF 2'486.40"}, {"value": 999}],
                  "actions": ["Pay the tax"]}"""


def test_grounding_flags_unverified_facts():
    letter = LETTERS[0]["text"]
    facts = pipeline.extract_facts(FakeLLM(), letter)
    assert [(d.date, d.verified) for d in facts.key_dates] == [("2026-11-30", True), ("2026-12-24", False)]
    assert facts.key_dates[1].kind == "other"
    assert [(a.value, a.verified) for a in facts.amounts] == [(2486.40, True), (999.0, False)]
    assert len(facts.warnings) == 2


def test_scoring_on_mock_pipeline():
    llm = MockLLM()
    letter = LETTERS[0]
    facts = pipeline.extract_facts(llm, letter["text"])
    scores = score_extraction(letter, facts)
    assert scores["date_recall"] == 1.0 and scores["invented_dates"] == 0
    text = pipeline.explain(llm, letter["text"], facts, "English")
    assert score_explanation(letter, text)["critical_facts_preserved"] == 1.0


@pytest.fixture
def client():
    app.dependency_overrides[get_llm] = MockLLM
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_api_flow(client):
    r = client.post("/api/analyze", json={"letter": LETTERS[1]["text"], "language": "Ukrainian"})
    assert r.status_code == 200
    facts = r.json()["facts"]
    assert "2026-10-31" in {d["date"] for d in facts["key_dates"]}
    assert client.post("/api/ask", json={"letter": "x", "facts": facts, "question": "?"}).status_code == 200
    assert client.post("/api/reply", json={"letter": "x", "facts": facts, "intent": "I paid"}).status_code == 200
    ics = client.post("/api/ics", json=facts)
    assert ics.status_code == 200 and "DTSTART;VALUE=DATE:20261031" in ics.text
    assert client.get("/").status_code == 200


def test_no_external_assets(client):
    # Air-gapped requirement: Swagger (CDN-loaded) is off and the page loads nothing remote.
    assert client.get("/docs").status_code == 404
    html = client.get("/").text
    assert "<script src=" not in html and "<link" not in html and "@import" not in html
