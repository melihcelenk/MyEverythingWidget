# G3: a 2x2 image dropped so that it covers an app; the app takes the image's old top-left cell.
Rows: 4
Columns: 4

Initial:
I1 I1 .  .
I1 I1 .  .
.  .  .  .
.  .  .  A1

Action:
Drag(I1, R3C3)

Expected:
A1 .  .  .
.  .  .  .
.  .  I1 I1
.  .  I1 I1
