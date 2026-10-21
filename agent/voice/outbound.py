"""Outbound PSTN dialing via LiveKit SIP + Twilio trunk (Phase 2, not implemented yet).

Plan: create a room, dispatch the agent, then create a SIP participant on LIVEKIT_SIP_TRUNK_ID
dialing the customer's number. Refuse to dial numbers flagged DNC in the CRM or outside 09:00-21:00 IST.
"""


def dial(phone: str) -> None:
    raise NotImplementedError("Phase 2: outbound SIP calling")
