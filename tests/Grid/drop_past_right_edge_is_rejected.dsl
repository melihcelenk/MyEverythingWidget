# G6: a 2x1 note dropped on the last column would leave the grid; it stays where it was.
Rows: 3
Columns: 5

Initial:
N1 N1 .  .  .
.  .  .  .  .
.  .  .  .  .

Action:
Drag(N1, R2C5)

Expected:
N1 N1 .  .  .
.  .  .  .  .
.  .  .  .  .

Outcome: OutOfBounds
