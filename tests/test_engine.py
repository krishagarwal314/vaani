from agent.schema import Intent, LLMTurnOutput
from agent.stages import Stage
from agent.transcript import Outcome, Transcript
from tests.conftest import TO_OFFER, run


def test_happy_path_apply(make_session):
    s = make_session()
    reply = run(s, *TO_OFFER)
    assert s.stage == Stage.OFFER and "sixteen thousand four hundred eighty-eight rupees" in reply.text
    reply = run_more(s, "yes", "apply now")
    assert reply.ended and s.transcript.outcome == Outcome.APPLIED
    visited = [e.detail["to"] for e in s.transcript.events if e.type == "transition"]
    assert visited == ["consent", "need_discovery", "eligibility", "offer", "commitment", "closing"]
    emi = [t for t in s.transcript.tool_calls if t.name == "calculate_emi"]
    assert emi and emi[0].result["emi"] == 16488


def test_callback_path_books_and_closes(make_session):
    s = make_session()
    run(s, *TO_OFFER, "yes", "call me later")
    assert s.stage == Stage.CALLBACK
    reply = s.handle_user("tomorrow at 5 pm")
    assert reply.ended and s.transcript.outcome == Outcome.CALLBACK_BOOKED
    assert "tomorrow at 5 PM" in reply.text
    assert s.slots.callback_time.startswith("2026-10-22T17:00")


def test_callback_outside_window_reprompts(make_session):
    s = make_session()
    run(s, "busy right now")
    assert s.stage == Stage.CALLBACK
    reply = s.handle_user("tomorrow 11 pm")
    assert s.stage == Stage.CALLBACK and "9 AM and 9 PM" in reply.text
    assert s.handle_user("tomorrow 6 pm").ended


def test_wrong_person(make_session):
    s = make_session()
    reply = run(s, "no, wrong number")
    assert reply.ended and s.transcript.outcome == Outcome.WRONG_PERSON
    assert "Rahul" not in reply.text


def test_llm_cannot_jump_stages(make_session):
    class Jumpy:
        name = "jumpy"

        def generate(self, req):
            return LLMTurnOutput(reply_text="Let's talk offers!", detected_intent=Intent.OTHER,
                                 next_stage_suggestion=Stage.OFFER)

    s = make_session()
    s.llm = Jumpy()
    s.start()
    s.handle_user("hello")
    assert s.stage == Stage.GREETING
    assert any(e.type == "transition_rejected" for e in s.transcript.events)


def test_llm_failure_does_not_crash(make_session):
    class Broken:
        name = "broken"

        def generate(self, req):
            raise TimeoutError("upstream")

    s = make_session()
    s.llm = Broken()
    s.start()
    reply = s.handle_user("hello")
    assert not reply.ended and "didn't catch" in reply.text


def test_tool_not_allowed_in_stage_is_refused(make_session):
    s = make_session()
    s.start()
    from agent.schema import ToolCall
    record = s._run_tool(ToolCall(name="book_callback", arguments={"time": "2026-10-22T17:00:00+05:30"}))
    assert record.error and record.result is None


def test_dnc_customer_is_never_called(make_session):
    s = make_session("+919800000004")
    reply = s.start()
    assert reply.ended and reply.text == "" and s.transcript.outcome == Outcome.DO_NOT_CALL


def test_transcript_roundtrip(make_session, tmp_path):
    s = make_session()
    run(s, *TO_OFFER, "yes", "apply")
    loaded = Transcript.load(s.transcript.save(tmp_path))
    assert loaded == s.transcript
    assert loaded.customer_phone == "+91******0001"
    assert loaded.prompt_version.startswith("p-")
    assert all(t.start_ms <= t.end_ms for t in loaded.turns)


def run_more(session, *lines):
    reply = None
    for line in lines:
        reply = session.handle_user(line)
    return reply
