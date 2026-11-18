# TODO - MyEverythingWidget

## Completed

- [x] Add order field to AppShortcut and Note models
- [x] Create DraggableMixin for drag-drop support
- [x] Add drag-drop to AppCard, NoteCard, ImageCard
- [x] Update TabManager to handle reordering
- [x] Fix memory leak on tab switching
- [x] Remove "All" category
- [x] Update tests for removed All category
- [x] Fix category add dialog appearing during tests (monkeypatch)
- [x] Add visual drag feedback (semi-transparent silhouette with blue border)
- [x] Add drop indicator (dashed blue border on drag over)
- [x] Implement drag-drop for NoteCard
- [x] Implement drag-drop for ImageCard
- [x] Write drag-drop tests (14 tests)
- [x] Fix window dragging issue (event.accept() in mouse events)
- [x] Fix grid layout overflow (2-col + 3-col images in same row)
- [x] Fix note reordering (use target item ID instead of grid index)
- [x] Fix scroll position reset after drag-drop
- [x] Write reordering tests (4 tests)
- [x] Optimize drag-drop performance (widget reuse instead of recreation)
- [x] Fix forward drag-drop bug (items moving to wrong position)
- [x] Add TabManager integration tests (5 tests for all drag scenarios)

## Pending

### Grid-Based Positioning System (Android-like)

#### Analysis & Requirements

**Current Problem:**

1. Items auto-flow left-to-right, can't leave gaps (e.g., can't move item from col 1 to col 2 leaving col 1 empty)
2. Drag-drop is item-based (drop ON an item) instead of grid-based (drop TO a grid cell)
3. No explicit grid position tracking - items placed by `order` field sequentially

**Target Behavior (Android Launcher):**

- Items have explicit grid positions: `(row, col, col_span, row_span)`
- Dragging to empty cell: item moves, others stay in place
- Dragging to occupied cell:
    - If source cell available → swap
    - If source cell not available → find first available empty cell
- Grid can have gaps (empty cells)

#### Data Model Changes Required

- [ ] **Add grid position fields to AppShortcut**:
    - `grid_row: int | None` - Row position in grid (0-indexed)
    - `grid_col: int | None` - Column position in grid (0-2 for 3-col grid)
    - `col_span: int = 1` - Columns occupied (for future: wide widgets)
    - `row_span: int = 1` - Rows occupied (for future: tall widgets)

- [ ] **Add grid position fields to Note**:
    - `grid_row: int | None` - Row position in grid
    - `grid_col: int | None` - Column position in grid
    - Notes already support multi-column spans (2 or 3)
    - Image notes already support multi-row/col spans

- [ ] **Update serialization**:
    - Add grid fields to `Note.to_dict()` and `Note.from_dict()`
    - AppShortcut is dataclass - auto-serializes

#### Grid Drop System

- [ ] **Create GridDropZone widget**:
    - QWidget that overlays entire grid area
    - Accepts drops on ANY grid cell (occupied or empty)
    - Converts drop position → grid cell (row, col)
    - Emits `itemDroppedOnGrid(item_id, item_type, target_row, target_col)` signal
    - Visual feedback: highlight target cell on dragOver

- [ ] **Implement grid cell calculator**:
    - Method: `_pos_to_grid_cell(QPoint) → (row, col)`
    - Calculate based on cell size + spacing + margins
    - Cell size: 90x100 (from layout code)
    - Spacing: 4px
    - Margins: 8px

#### Placement Logic

- [ ] **Grid state tracker**:
    - Track occupied cells: `Set[(row, col)]`
    - Account for multi-cell items (span)
    - Method: `_get_occupied_cells(category) → Set[(row, col)]`

- [ ] **Auto-placement algorithm** (for items without grid_row/grid_col):
    - Sort items by `order`
    - For each item without explicit position:
        - Find first available cell (left-to-right, top-to-bottom)
        - Skip occupied cells
        - Handle multi-cell items (check if span fits)
    - Method: `_auto_place_item(item, occupied_cells) → (row, col)`

- [ ] **Drop handler logic**:
  ```python
  def _on_grid_drop(item_id, item_type, target_row, target_col, category):
      # 1. Get dragged item and its current position
      item = find_item(item_id)
      source_row, source_col = item.grid_row, item.grid_col

      # 2. Get all occupied cells in grid
      occupied = _get_occupied_cells(category)

      # 3. Check if target cells are free
      target_cells = get_cells_for_position(target_row, target_col, item.col_span, item.row_span)
      target_free = all(cell not in occupied or cell in item's current cells for cell in target_cells)

      # 4a. If target is free → just move item
      if target_free:
          item.grid_row = target_row
          item.grid_col = target_col
          # DON'T touch other items!

      # 4b. If target occupied → handle collision
      else:
          occupying_item = find_item_at(target_row, target_col)

          # Check if source is free (for swap)
          source_cells = get_cells_for_position(source_row, source_col, occupying_item.col_span, occupying_item.row_span)
          source_free = all(cell not in occupied or cell in occupying_item's current cells for cell in source_cells)

          if source_free:
              # Swap: dragged → target, occupying → source
              item.grid_row = target_row
              item.grid_col = target_col
              occupying_item.grid_row = source_row
              occupying_item.grid_col = source_col
          else:
              # Find first empty position for displaced item
              empty_pos = find_first_empty_position(occupying_item, occupied)
              item.grid_row = target_row
              item.grid_col = target_col
              occupying_item.grid_row = empty_pos[0]
              occupying_item.grid_col = empty_pos[1]

      # 5. Refresh grid layout
      refresh_category_grid(category)
  ```

#### Rendering Logic

- [ ] **Update `_populate_category_grid`**:
    - Don't auto-flow items
    - For each item:
        - If has `grid_row, grid_col` → place at explicit position
        - Else → use auto-placement to assign position
    - Use `layout.addWidget(widget, row, col, row_span, col_span)`

- [ ] **Handle empty cells**:
    - Don't fill gaps automatically
    - GridDropZone allows dropping in empty cells

#### Migration Strategy

- [ ] **Handle existing data**:
    - Existing items have `order` but no `grid_row/grid_col`
    - On first load: auto-assign grid positions based on order
    - Save positions to preserve layout

#### Testing Requirements

- [ ] **Unit tests for grid logic**:
    - Grid cell calculation (pos → grid)
    - Occupied cell tracking
    - Auto-placement algorithm
    - Collision detection

- [ ] **Integration tests for drag-drop**:
    - Drop to empty cell → item moves, others unchanged
    - Drop to occupied cell (swap available) → items swap
    - Drop to occupied cell (swap unavailable) → displaced item finds empty cell
    - Multi-span items (images, wide notes)

#### Implementation Order

1. Data model changes (grid fields) - **CRITICAL FIRST**
2. Grid cell calculator + occupied tracker
3. Auto-placement algorithm (for backward compat)
4. GridDropZone widget
5. Drop handler logic
6. Update rendering logic
7. Tests
8. Migration/backward compatibility

---

### Other Pending

- [ ] Persist order changes to storage (currently in-memory only)
