import json
from pathlib import Path

from fastapi.testclient import TestClient

from agent.transcript import Transcript, TurnMetrics
from crm_service.app import app
from eval.latency_report import collect
from eval.talk_over import talk_over_rates
from eval.wer import wer
from tests.conftest import run


def test_schema_file_up_to_date():
    path = Path(__file__).resolve().parent.parent / "schemas" / "transcript.schema.json"
    assert json.loads(path.read_text()) == Transcript.model_json_schema()


def test_latency_and_talk_over(make_session):
    s = make_session()
    run(s, "yes")
    agent_turn = s.transcript.turns[-1]
    agent_turn.metrics = TurnMetrics(user_eos_ms=1000, user_true_end_ms=1100, stt_final_ms=1150,
                                     llm_first_token_ms=1450, tts_first_byte_ms=1650, turn_detector="vad")
    samples = collect([s.transcript])
    assert samples["voice_to_voice"] == [650] and samples["llm_ttft"] == [300]
    assert talk_over_rates([s.transcript]) == {"vad": (0, 1)}
    agent_turn.metrics.tts_first_byte_ms = 1050
    assert talk_over_rates([s.transcript]) == {"vad": (1, 1)}


def test_wer():
    assert wer(["mujhe paanch lakh chahiye"], ["mujhe paanch lakh chahiye"]) == 0
    assert wer(["mujhe paanch lakh chahiye"], ["mujhe panch lakh chahiye"]) == 0.25
    assert wer(["loan of five lakh"], ["loan of nine lakh"], numbers_only=True) == 0.5


def test_crm_api():
    client = TestClient(app)
    assert client.get("/customers/+919800000001").json()["name"] == "Rahul Sharma"
    assert client.get("/customers/+910000000000").status_code == 404
    assert client.post("/callbacks", json={"phone": "+919800000001", "time": "2020-01-01T10:00:00+05:30"}).status_code == 422
