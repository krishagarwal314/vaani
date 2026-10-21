"""One test (or more) per recovery path from the spec."""
from agent.engine import DEAD_AIR_MS
from agent.stages import Stage
from agent.transcript import Outcome
from tests.conftest import TO_OFFER, run
from tools import crm


def test_barge_in_truncates_and_discards_unspoken(make_session):
    s = make_session()
    run(s, "yes")  # agent now speaking the long consent disclosure
    full = s.transcript.turns[-1].text
    s.handle_barge_in(heard_chars=25)
    turn = s.transcript.turns[-1]
    assert turn.interrupted and len(turn.text) <= 25 and full.startswith(turn.text)
    assert turn.unspoken_text and full.endswith(turn.unspoken_text)
    assert s.history[-1] == {"role": "assistant", "content": turn.text}
    s.handle_user("yes, go on")
    assert s.stage == Stage.NEED_DISCOVERY


def test_barge_in_cuts_on_word_boundary(make_session):
    s = make_session()
    s.start()
    s.handle_barge_in(heard_chars=8)  # "Hello, am I speaking..." -> "Hello,"
    assert s.transcript.turns[-1].text == "Hello,"


def test_dead_air_reprompts_then_exits(make_session):
    s = make_session()
    s.start()
    assert s.handle_silence(DEAD_AIR_MS - 1) is None
    first = s.handle_silence(DEAD_AIR_MS + 500)
    assert "still there" in first.text and "Rahul Sharma" in first.text and not first.ended
    second = s.handle_silence(DEAD_AIR_MS + 500)
    assert second.ended and s.transcript.outcome == Outcome.NO_RESPONSE


def test_dead_air_counter_resets_after_speech(make_session):
    s = make_session()
    s.start()
    s.handle_silence(5000)
    s.handle_user("yes")
    assert not s.handle_silence(5000).ended


def test_off_topic_acknowledged_and_steered_back(make_session):
    s = make_session()
    run(s, "yes", "yes")
    reply = s.handle_user("did you watch the cricket match yesterday?")
    assert s.stage == Stage.NEED_DISCOVERY
    assert "fair enough" in reply.text and "How much loan" in reply.text


def test_amounts_read_back_before_accepted(make_session):
    s = make_session()
    reply = run(s, "yes", "yes", "I need 5 lakh")
    assert reply.text == "Just to confirm, five lakh rupees?"
    assert s.slots.loan_amount is None and s.stage == Stage.NEED_DISCOVERY
    s.handle_user("yes")
    assert s.slots.loan_amount == 500000 and s.stage == Stage.ELIGIBILITY


def test_misheard_amount_corrected(make_session):
    s = make_session()
    run(s, "yes", "yes", "I need 5 lakh")
    reply = s.handle_user("no, 4 lakh")
    assert reply.text == "Just to confirm, four lakh rupees?"
    s.handle_user("yes")
    assert s.slots.loan_amount == 400000


def test_rejected_amount_asks_again(make_session):
    s = make_session()
    run(s, "yes", "yes", "I need 5 lakh")
    reply = s.handle_user("no")
    assert "amount again" in reply.text and s.slots.loan_amount is None and not s.pending


def test_language_switch_is_mirrored(make_session):
    s = make_session()
    reply = run(s, "yes")
    assert s.lang == "en" and "This call is recorded" in reply.text
    reply = s.handle_user("haan ji, bolo")
    assert s.lang == "hinglish" and "Aapko kitne loan" in reply.text
    reply = s.handle_user("मुझे पांच लाख चाहिए")
    assert s.lang == "hi" and "सही है" in reply.text
    assert any(e.type == "language_switch" for e in s.transcript.events)


def test_are_you_a_bot_answered_honestly_and_continues(make_session):
    s = make_session()
    run(s, "yes")
    reply = s.handle_user("wait, are you a bot?")
    assert "AI assistant" in reply.text and "Do you have two minutes?" in reply.text
    assert s.stage == Stage.CONSENT and not reply.ended
    s.handle_user("ok yes")
    assert s.stage == Stage.NEED_DISCOVERY


def test_do_not_call_ends_and_flags_crm(make_session):
    s = make_session()
    reply = run(s, "yes", "please don't call me again")
    assert reply.ended and s.transcript.outcome == Outcome.DO_NOT_CALL
    assert crm.CUSTOMERS["+919800000001"]["dnc"] is True


def test_not_interested_ends_politely(make_session):
    s = make_session()
    reply = run(s, "yes", "mujhe loan nahi chahiye")
    assert reply.ended and s.transcript.outcome == Outcome.NOT_INTERESTED
    assert "shukriya" in reply.text


def test_recovery_mid_offer_keeps_slots(make_session):
    s = make_session()
    run(s, *TO_OFFER)
    s.handle_user("are you a robot?")
    assert s.stage == Stage.OFFER and s.slots.monthly_income == 80000


def test_short_english_reply_does_not_flip_hinglish_call(make_session):
    s = make_session("+919800000002")
    run(s, "haan ji", "ok sure")
    assert s.lang == "hinglish"
