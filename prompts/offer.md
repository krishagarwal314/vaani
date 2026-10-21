# Stage 5 — Offer & EMI quote

Tools: `calculate_emi`.

- On enter: if there is no `calculate_emi` result yet, call it with principal = the lower of `loan_amount`
  and the CRM `pre_approved_amount`, rate = CRM `offer_rate`, tenure = CRM `default_tenure`.
- With the result: state amount, rate, tenure and EMI in words, then ask if they want to go ahead.
- Yes → suggest `commitment`. Objection → suggest `objection`. Different tenure → recompute.
