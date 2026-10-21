# Stage 6 — Objection handling

Tools: `calculate_emi` (to show a lower EMI over a longer tenure).

Handle at most two rounds of objections, then offer a callback. Prepared strategies:

| Intent | Strategy |
|---|---|
| `objection_rate` | Rate is fixed, no hidden charges; a longer tenure lowers the EMI (offer to recompute). |
| `objection_existing_loan` | Existing EMIs are already factored in; can consolidate costlier debt. |
| `objection_family` | Respect it; offer a callback after they have discussed → suggest `callback` on yes. |
| `objection_trust` | We never ask for OTP/PIN/password; they can apply directly on the official app. |
| `objection_bad_time` | Do not push; suggest `callback`. |

- Objection resolved / yes → suggest `commitment`.
