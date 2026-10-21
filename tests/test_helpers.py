from datetime import datetime

import pytest

from agent.lang import detect_lang, is_affirm, is_deny
from agent.numbers import number_words, parse_amount
from agent.timeparse import IST, parse_callback_time
from agent.voice.chunker import SentenceChunker
from agent.voice.fillers import FillerPolicy
from agent.voice.turn_detection import VADSilenceDetector
from tests.conftest import NOW
from tools.emi import calculate_emi
from tools.scheduler import book_callback


@pytest.mark.parametrize("text, amount", [
    ("5 lakh", 500000), ("paanch lakh chahiye", 500000), ("₹50,000", 50000), ("1.5 crore", 15000000),
    ("2.5L", 250000), ("80k per month", 80000), ("dedh lakh", 150000), ("पांच लाख", 500000),
    ("36 months", None), ("11.5 %", None), ("hello", None), ("80000 monthly", 80000),
])
def test_parse_amount(text, amount):
    assert parse_amount(text) == amount


def test_number_words_indian_system():
    assert number_words(500000) == "five lakh"
    assert number_words(1250000) == "twelve lakh fifty thousand"
    assert number_words(16488) == "sixteen thousand four hundred eighty-eight"
    assert number_words(25000000) == "two crore fifty lakh"


@pytest.mark.parametrize("text, lang", [
    ("Yes, I'm interested", "en"), ("haan ji bolo", "hinglish"), ("mujhe paanch lakh chahiye", "hinglish"),
    ("हाँ जी", "hi"), ("ok", None), ("5 lakh", None),
])
def test_detect_lang(text, lang):
    assert detect_lang(text) == lang


def test_affirm_deny():
    assert is_affirm("haan ji") and is_affirm("yes") and is_affirm("हाँ")
    assert is_deny("nahi") and is_deny("no, 4 lakh") and not is_affirm("no")


@pytest.mark.parametrize("text, expected", [
    ("tomorrow at 5 pm", datetime(2026, 10, 22, 17, 0, tzinfo=IST)),
    ("kal shaam 6 baje", datetime(2026, 10, 22, 18, 0, tzinfo=IST)),
    ("call at 4", datetime(2026, 10, 21, 16, 0, tzinfo=IST)),
    ("9 am", datetime(2026, 10, 22, 9, 0, tzinfo=IST)),  # already past today -> tomorrow
    ("whenever", None),
])
def test_parse_callback_time(text, expected):
    assert parse_callback_time(text, NOW) == expected


def test_emi_formula():
    assert calculate_emi(500000, 11.5, 36)["emi"] == 16488
    assert calculate_emi(120000, 0, 12)["emi"] == 10000
    with pytest.raises(ValueError):
        calculate_emi(0, 10, 12)


def test_book_callback_window():
    now = NOW.isoformat()
    assert book_callback("2026-10-22T17:00:00+05:30", now=now)["booked"]
    assert book_callback("2026-10-22T22:00:00+05:30", now=now)["error"] == "outside_call_window"
    assert book_callback("2026-10-20T17:00:00+05:30", now=now)["error"] == "time_in_past"


def test_sentence_chunker_streams():
    c = SentenceChunker()
    out = []
    for tok in "Your EMI is Rs. 16,488 at 11.5 percent. Shall we go ahead? Great".split(" "):
        out += c.feed(tok + " ")
    assert out == ["Your EMI is Rs. 16,488 at 11.5 percent.", "Shall we go ahead?"]
    assert c.flush() == ["Great"]


def test_filler_policy():
    f = FillerPolicy(threshold_ms=700)
    assert f.pick(300, "en") is None
    a, b = f.pick(800, "hinglish"), f.pick(800, "hinglish")
    assert a and b and a != b


def test_vad_detector():
    d = VADSilenceDetector(silence_ms=500)
    assert not d.is_end_of_turn("so I was thinking umm", 300)
    assert d.is_end_of_turn("so I was thinking umm", 600)
