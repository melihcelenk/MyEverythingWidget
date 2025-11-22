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

## Pending

- [ ] Persist order changes to storage (currently in-memory only)
