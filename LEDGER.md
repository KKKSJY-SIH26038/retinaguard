# RetinaGuard root ledger

Append-only. One line per entry, format:

    YYYY-MM-DD HH:MM IST — <single sentence, past tense, ends with a period.>

This root ledger is EMPTY during the 9 Sep build night. At the end of the night
the per-directory ledgers (`module1_quality/LEDGER.md`, `capacity_model/LEDGER.md`)
are merged here sorted by timestamp, and that merge is itself the final entry.
