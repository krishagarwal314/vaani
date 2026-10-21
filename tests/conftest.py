from datetime import datetime
from itertools import count

import pytest

from agent.engine import CallSession
from agent.llm.mock import MockLLM
from agent.timeparse import IST
from tools import crm, scheduler

NOW = datetime(2026, 10, 21, 10, 0, tzinfo=IST)


@pytest.fixture(autouse=True)
def _reset_mock_stores():
    snapshot = {k: dict(v) for k, v in crm.CUSTOMERS.items()}
    scheduler.CALLBACKS.clear()
    yield
    crm.CUSTOMERS.clear()
    crm.CUSTOMERS.update(snapshot)


@pytest.fixture
def make_session():
    def _make(phone: str = "+919800000001") -> CallSession:
        ticks = count(0, 100)
        return CallSession(phone, MockLLM(), call_id="test", clock=lambda: next(ticks), now_fn=lambda: NOW)
    return _make


def run(session: CallSession, *lines: str):
    reply = session.start()
    for line in lines:
        reply = session.handle_user(line)
    return reply


# Shortest path to the offer stage for +919800000001 (English)
TO_OFFER = ("yes", "yes", "5 lakh for a wedding", "yes", "salaried", "80000", "yes", "no")
