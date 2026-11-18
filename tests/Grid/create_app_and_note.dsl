# Source: legacy/tests/humanized/drag/create_app_and_note.dsl, expectation corrected (MEW-4 Karar K4).
# N1 is created first (R1C1-C2), A1 next (R1C3). Dropping N1 at R1C2 collides with A1,
# which moves to the vacated top-left cell of N1.
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
A1 N1 N1 .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
