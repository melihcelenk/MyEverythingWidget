# G3: a 2x2 image dropped over an app; the app takes the image's old top-left cell, others stay.
Rows: 5
Columns: 5

Initial:
I1 I1 .  .  A2
I1 I1 .  .  .
.  .  .  .  .
.  .  .  A1 .
.  .  .  .  .

Action:
Drag(I1, R3C3)

Expected:
A1 .  .  .  A2
.  .  .  .  .
.  .  I1 I1 .
.  .  I1 I1 .
.  .  .  .  .
