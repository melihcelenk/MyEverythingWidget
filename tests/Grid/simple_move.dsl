# G1: dropping on an empty cell moves only the dragged item.
Rows: 3
Columns: 3

Initial:
A1 .  .
.  .  .
.  .  .

Action:
Drag(A1, R2C2)

Expected:
.  .  .
.  A1 .
.  .  .
