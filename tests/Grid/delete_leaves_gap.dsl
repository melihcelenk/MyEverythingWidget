# G5: deleting an item leaves its cell empty; nothing slides up or left.
Rows: 2
Columns: 3

Initial:
A1 A2 A3
A4 .  .

Action:
Delete(A2)

Expected:
A1 .  A3
A4 .  .
