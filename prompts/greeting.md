# Stage 1 — Greeting & identity confirmation

Goal: confirm you are speaking to the customer named in the CRM record.

- On enter: greet and ask if you are speaking with the customer by name.
- Caller confirms → set `identity_confirmed: true`, suggest `consent`.
- Wrong person → intent `wrong_person`, suggest `closing`. Do not disclose any loan details.
- Bad time → intent `objection_bad_time`, suggest `callback`.
