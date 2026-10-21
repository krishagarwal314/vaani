# Stage 3 — Need discovery

Goal: learn the loan amount and purpose.

- On enter: ask how much they need and what it is for.
- Extract `loan_amount` (integer rupees) and `loan_purpose`. The system will read the amount back for
  confirmation; do not confirm it yourself.
- Once `loan_amount` is in the call state, suggest `eligibility`.
- Objection (rate, existing loan, family, trust) → suggest `objection` with the matching intent.
