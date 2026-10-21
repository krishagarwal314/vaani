# Stage 7 — Commitment

Goal: apply now (secure SMS link) or book a callback.

- On enter: ask whether they want to apply now via a secure link or prefer a callback.
- Apply → intent `apply_now`, suggest `closing`.
- Later / callback → intent `request_callback`, suggest `callback`.
- New objection → suggest `objection`.
