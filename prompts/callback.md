# Stage 8 — Callback scheduling

Tools: `book_callback`.

- On enter: ask for a convenient day and time.
- Resolve the time relative to `now` in the call state (IST) and call `book_callback` with an ISO 8601
  timestamp (`+05:30`). Calls are only allowed 09:00–21:00 IST.
- Booked → confirm the time in words, suggest `closing`.
- Rejected → explain the allowed window and ask again.
