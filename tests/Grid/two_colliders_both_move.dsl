# K5: a 2x1 note dropped on two apps; both apps move, in reading order:
# A1 to the note's old top-left cell, A2 to the next free cell.
Rows: 3
Columns: 5

Initial:
N1 N1 .  .  .
A1 A2 .  .  .
.  .  .  .  .

Action:
Drag(N1, R2C1)

Expected:
A1 A2 .  .  .
N1 N1 .  .  .
.  .  .  .  .
