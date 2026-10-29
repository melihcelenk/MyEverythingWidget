# G9: a new 2x1 note skips a single free cell and takes the first two adjacent free cells.
Rows: 2
Columns: 5

Initial:
A1 .  A2 .  .
.  .  .  .  .

Action:
Create(NOTE, "Groceries", N1)

Expected:
A1 .  A2 N1 N1
.  .  .  .  .
