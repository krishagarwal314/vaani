import pytest

from agent.stages import Stage
from agent.transcript import Outcome
from tests.conftest import TO_OFFER, run


@pytest.mark.parametrize("utterance, expected", [
    ("the interest rate is too high", "rate is fixed"),
    ("I already have a loan", "already counted"),
    ("I need to ask my family first", "discussed it with your family"),
    ("I don't trust phone calls, could be a scam", "never ask for your OTP"),
])
def test_objection_strategies(make_session, utterance, expected):
    s = make_session()
    run(s, *TO_OFFER)
    reply = s.handle_user(utterance)
    assert s.stage == Stage.OBJECTION and expected in reply.text


def test_bad_time_goes_to_callback(make_session):
    s = make_session()
    run(s, *TO_OFFER)
    reply = s.handle_user("I'm driving, not now")
    assert s.stage == Stage.CALLBACK and "What time" in reply.text


def test_family_objection_then_yes_books_callback(make_session):
    s = make_session()
    run(s, *TO_OFFER, "let me discuss with my wife")
    s.handle_user("yes please")
    assert s.stage == Stage.CALLBACK
    assert s.handle_user("kal shaam 6 baje").ended
    assert s.transcript.outcome == Outcome.CALLBACK_BOOKED


def test_objection_resolved_leads_to_commitment(make_session):
    s = make_session()
    run(s, *TO_OFFER, "rate is too high")
    s.handle_user("okay fine")
    assert s.stage == Stage.COMMITMENT
