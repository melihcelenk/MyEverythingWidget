# G1, G2, G5 together: three drags in a row; the last one displaces A1 to the note's old cell.
# Untouched items (A2, A4) never move.
Rows: 5
Columns: 5

Initial:
A1 A2 A3 .  .
.  .  .  .  .
N1 N1 .  .  .
.  .  .  .  .
.  .  .  .  A4

Action:
Drag(A1, R2C2)
Drag(A3, R1C1)
Drag(N1, R2C1)

Expected:
A3 A2 .  .  .
N1 N1 .  .  .
A1 .  .  .  .
.  .  .  .  .
.  .  .  .  A4
