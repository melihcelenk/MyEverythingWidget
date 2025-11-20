"""
Custom draggable tab bar widget
Supports drag-to-scroll and wheel scroll navigation
"""
from PySide6.QtWidgets import QTabBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent


class DraggableTabBar(QTabBar):
    """Custom tab bar with drag-to-scroll and wheel scroll support"""

    DRAG_THRESHOLD = 10  # Pixels to move before drag starts
    SCROLL_THRESHOLD = 20  # Pixels to scroll before changing tab

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_start_pos = None
        self._is_dragging = False
        self._pressed_index = -1
        self.setMouseTracking(True)
        self.setUsesScrollButtons(True)

    # === Public Properties ===

    @property
    def last_category_index(self) -> int:
        """Index of the last category tab (before + button)"""
        return self.count() - 2

    @property
    def add_button_index(self) -> int:
        """Index of the + button tab"""
        return self.count() - 1

    def is_add_button(self, index: int) -> bool:
        """Check if given index is the add button"""
        return index == self.add_button_index

    # === Mouse Event Handlers ===

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press - start potential drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_left_button_press(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move - drag scrolling"""
        if self._is_left_button_dragging(event):
            self._handle_drag_move(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release - end drag or select tab"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_left_button_release()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel - scroll through tabs"""
        delta = event.angleDelta().y()
        if delta > 0:
            self._scroll_to_previous_tab()
        else:
            self._scroll_to_next_tab()
        event.accept()

    # === Private Mouse Handling Methods ===

    def _handle_left_button_press(self, event: QMouseEvent):
        """Process left mouse button press"""
        self._drag_start_pos = event.position().toPoint()
        self._is_dragging = False
        self._pressed_index = self.tabAt(event.position().toPoint())
        self.tabBarClicked.emit(self._pressed_index)
        event.accept()

    def _is_left_button_dragging(self, event: QMouseEvent) -> bool:
        """Check if left button is being dragged"""
        return (self._drag_start_pos is not None and
                event.buttons() == Qt.MouseButton.LeftButton)

    def _handle_drag_move(self, event: QMouseEvent):
        """Process drag movement"""
        current_pos = event.position().toPoint()
        delta = current_pos.x() - self._drag_start_pos.x()

        if abs(delta) > self.DRAG_THRESHOLD:
            self._is_dragging = True
            self._scroll_by_drag(delta)
            self._drag_start_pos = current_pos

    def _handle_left_button_release(self):
        """Process left mouse button release"""
        if self._should_select_tab():
            self.setCurrentIndex(self._pressed_index)
        self._reset_drag_state()

    def _should_select_tab(self) -> bool:
        """Check if a tab should be selected on release"""
        return (not self._is_dragging and
                self._pressed_index >= 0 and
                not self.is_add_button(self._pressed_index))

    def _reset_drag_state(self):
        """Reset drag tracking state"""
        self._drag_start_pos = None
        self._is_dragging = False
        self._pressed_index = -1

    # === Tab Scrolling Methods ===

    def _scroll_to_previous_tab(self):
        """Scroll to previous tab (left)"""
        new_index = max(0, self.currentIndex() - 1)
        self.setCurrentIndex(new_index)

    def _scroll_to_next_tab(self):
        """Scroll to next tab (right)"""
        current = self.currentIndex()

        if current < self.last_category_index:
            self.setCurrentIndex(current + 1)
        elif current == self.last_category_index:

            self._make_add_button_visible()

    def _make_add_button_visible(self):
        """Make the + button visible by temporarily selecting it"""
        self.setCurrentIndex(self.add_button_index)
        self.setCurrentIndex(self.last_category_index)

    def _scroll_by_drag(self, delta: int):
        """Scroll tabs based on drag delta"""
        if delta > self.SCROLL_THRESHOLD:
            self._scroll_to_previous_tab()
        elif delta < -self.SCROLL_THRESHOLD:
            new_index = min(self.last_category_index, self.currentIndex() + 1)
            self.setCurrentIndex(new_index)
