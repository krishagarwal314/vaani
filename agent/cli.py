"""Chat with Vaani in text mode.

    python -m agent.cli --phone +919800000001            # offline mock LLM
    python -m agent.cli --phone +919800000002 --llm openai

Commands: /silence <sec>  simulate dead air     /bargein <chars>  interrupt the last agent line
          /state           show stage & slots    /quit             hang up
"""
from __future__ import annotations

import argparse
import os

from agent.engine import CallSession
from agent.llm import get_llm


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--phone", default="+919800000001")
    parser.add_argument("--llm", default=os.getenv("VAANI_LLM", "mock"), choices=["mock", "openai"])
    parser.add_argument("--out", default="transcripts")
    args = parser.parse_args()

    session = CallSession(args.phone, get_llm(args.llm))
    reply = session.start()
    if reply.ended:
        print(f"[call not placed: {session.transcript.events[-1].detail.get('reason')}]")
    else:
        print(f"[{reply.stage.value}] Vaani: {reply.text}")

    while not session.ended:
        try:
            line = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            session.hang_up()
            break
        if not line:
            continue
        if line == "/quit":
            session.hang_up()
            break
        if line == "/state":
            print(f"  stage={session.stage.value} lang={session.lang} pending={session.pending}")
            print(f"  slots={session.slots.model_dump(exclude_none=True)}")
            continue
        if line.startswith("/silence"):
            reply = session.handle_silence(int(float(line.split()[1]) * 1000))
            if reply is None:
                continue
        elif line.startswith("/bargein"):
            session.handle_barge_in(int(line.split()[1]))
            print(f"  [agent cut to: {session.transcript.turns[-1].text!r}]")
            continue
        else:
            reply = session.handle_user(line)
        print(f"[{reply.stage.value}] Vaani: {reply.text}")

    path = session.transcript.save(args.out)
    print(f"\n[outcome: {session.transcript.outcome.value}] transcript saved to {path}")


if __name__ == "__main__":
    main()
