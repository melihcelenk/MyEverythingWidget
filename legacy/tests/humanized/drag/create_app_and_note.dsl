Rows: 5
Columns: 5

Initial:
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action:
Create(NOTE, "Test Note", N1)
Create(APP, "Test App", A1)
Drag(N1, R1C2)

Expected:
A1 .  .  .  .
.  .  N1 N1 .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

