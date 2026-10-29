# G6: a 1x2 item dropped on the last row would leave the grid.
Rows: 3
Columns: 3

Initial:
I1 .  .
I1 .  .
.  .  .

Action:
Drag(I1, R3C2)

Expected:
I1 .  .
I1 .  .
.  .  .

Outcome: OutOfBounds
