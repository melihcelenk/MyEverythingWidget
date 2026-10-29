# G4: the 2x1 note cannot sit at the app's old cell (it would leave the grid),
# so it goes to the first free cells in reading order.
Rows: 3
Columns: 5

Initial:
.  .  .  .  A1
N1 N1 .  .  .
.  .  .  .  .

Action:
Drag(A1, R2C1)

Expected:
N1 N1 .  .  .
A1 .  .  .  .
.  .  .  .  .
