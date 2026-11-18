# G10: shrinking a 2x2 image to 1x1 frees the other three cells.
Rows: 2
Columns: 3

Initial:
I1 I1 .
I1 I1 .

Action:
Resize(I1, 1x1)

Expected:
I1 .  .
.  .  .
