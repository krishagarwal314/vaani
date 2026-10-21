from agent.schema import Slots
from agent.stages import STAGE_TOOLS, TRANSITIONS, Stage, check_transition


def test_exactly_nine_stages():
    assert len(Stage) == 9


def test_every_stage_can_reach_closing():
    for stage in Stage:
        seen, frontier = {stage}, [stage]
        while frontier:
            for nxt in TRANSITIONS[frontier.pop()]:
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        assert Stage.CLOSING in seen


def test_disallowed_transition_rejected():
    assert check_transition(Stage.GREETING, Stage.OFFER, Slots()) is not None
    assert check_transition(Stage.CLOSING, Stage.GREETING, Slots()) is not None


def test_guards_require_slots():
    assert "consent" in check_transition(Stage.CONSENT, Stage.NEED_DISCOVERY, Slots())
    assert check_transition(Stage.CONSENT, Stage.NEED_DISCOVERY, Slots(consent_given=True)) is None
    reason = check_transition(Stage.ELIGIBILITY, Stage.OFFER, Slots(loan_amount=500000, employment_type="salaried"))
    assert "monthly_income" in reason and "existing_emi" in reason
    full = Slots(loan_amount=500000, employment_type="salaried", monthly_income=80000, existing_emi=0)
    assert check_transition(Stage.ELIGIBILITY, Stage.OFFER, full) is None


def test_tools_scoped_per_stage():
    assert STAGE_TOOLS[Stage.CALLBACK] == {"book_callback"}
    assert "book_callback" not in STAGE_TOOLS[Stage.OFFER]
