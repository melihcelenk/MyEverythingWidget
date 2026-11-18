# G10: growing to 3 columns from the fourth column would leave a 5-column grid.
Rows: 2
Columns: 5

Initial:
.  .  .  N1 N1
.  .  .  .  .

Action:
Resize(N1, 3x1)

Expected:
.  .  .  N1 N1
.  .  .  .  .

Outcome: OutOfBounds
