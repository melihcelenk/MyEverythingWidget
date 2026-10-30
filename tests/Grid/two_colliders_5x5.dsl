# K5: a 2x1 note dropped on two apps; A1 takes the note's old top-left cell, A2 the next free cell.
Rows: 5
Columns: 5

Initial:
N1 N1 .  .  .
A1 A2 .  .  .
.  .  .  .  A3
.  .  .  .  .
.  .  .  .  .

Action:
Drag(N1, R2C1)

Expected:
A1 A2 .  .  .
N1 N1 .  .  .
.  .  .  .  A3
.  .  .  .  .
.  .  .  .  .
