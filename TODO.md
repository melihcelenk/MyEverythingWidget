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

- [ ] Persist order changes to storage (currently in-memory only)
