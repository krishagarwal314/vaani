# Stage 4 — Eligibility check

Goal: collect, one question at a time: `employment_type` (salaried | self_employed),
`monthly_income` (take-home, rupees), `existing_emi` (total monthly EMIs, 0 if none).

- Ask only for the first slot that is still missing in the call state.
- When all three are present, suggest `offer` with an empty `reply_text`.
- Do not comment on whether they will qualify.
