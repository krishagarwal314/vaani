"""Outbound PSTN dialing via LiveKit SIP + Twilio trunk.

Design: create a room, dispatch the agent, then create a SIP participant on LIVEKIT_SIP_TRUNK_ID
dialing the customer's number. Refuse to dial numbers flagged DNC in the CRM or outside 09:00-21:00 IST.
"""


def dial(phone: str) -> None:
    raise NotImplementedError("outbound SIP calling")
