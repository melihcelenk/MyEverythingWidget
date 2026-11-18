# G10: spans are limited to 1-3 in each direction.
Rows: 2
Columns: 5

Initial:
N1 N1 .  .  .
.  .  .  .  .

Action:
Resize(N1, 4x1)

Expected:
N1 N1 .  .  .
.  .  .  .  .

Outcome: InvalidSpan
