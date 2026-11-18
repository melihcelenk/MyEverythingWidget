# G2, G3: a 2x1 note that is hit by a 1x1 app moves to the app's cell when it fits there.
Rows: 3
Columns: 5

Initial:
A1 .  .  .  .
N1 N1 .  .  .
.  .  .  .  .

Action:
Drag(A1, R2C1)

Expected:
N1 N1 .  .  .
A1 .  .  .  .
.  .  .  .  .
