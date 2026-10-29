# G1, G5: other items keep their cells and the vacated cell stays empty.
Rows: 3
Columns: 3

Initial:
A1 A2 A3
.  .  .
.  .  .

Action:
Drag(A1, R3C1)

Expected:
.  A2 A3
.  .  .
A1 .  .
