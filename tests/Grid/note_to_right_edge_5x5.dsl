# MEW-3 "Bug 1": a 2x1 note dragged to the right edge must land on the last two columns, not one to the left.
Rows: 5
Columns: 5

Initial:
.  .  .  .  .
N1 N1 .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action:
Drag(N1, R2C4)

Expected:
.  .  .  .  .
.  .  .  N1 N1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
