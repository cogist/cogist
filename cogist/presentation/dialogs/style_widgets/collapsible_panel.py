"""Collapsible panel widget without checkbox."""

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QMouseEvent
from qtpy.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class _TitleBar(QWidget):
    """Custom title bar that handles mouse clicks."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    # ruff: noqa: N802
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press to toggle collapse."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


# ruff: noqa: N802
class CollapsiblePanel(QFrame):
    """A collapsible panel that toggles by clicking the title bar.

    Similar to QGroupBox but without checkbox. Click the title to expand/collapse.
    """

    toggled = Signal(bool)  # Emitted when panel is expanded/collapsed

    def __init__(self, title: str = "", collapsed: bool = False, parent=None):
        super().__init__(parent)

        self._title = title
        self._collapsed = collapsed

        # Setup frame style
        self.setFrameShape(QFrame.StyledPanel)
        self._update_style()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar with click handler
        self._title_bar = _TitleBar()
        self._title_bar.setFixedHeight(32)
        self._title_bar.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QWidget:hover {
                background-color: #F5F5F5;
            }
        """)
        self._title_bar.clicked.connect(self.toggle)

        title_layout = QGridLayout(self._title_bar)
        title_layout.setContentsMargins(12, 0, 12, 0)
        title_layout.setSpacing(4)

        # Arrow indicator
        self._arrow_label = QLabel("▼")
        self._arrow_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 10px;
                background: transparent;
            }
        """)
        self._arrow_label.setFixedWidth(16)
        title_layout.addWidget(self._arrow_label, 0, 0, Qt.AlignVCenter)

        # Title label
        self._title_label = QLabel(title)
        self._title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: bold;
                font-size: 13px;
                background: transparent;
            }
        """)
        title_layout.addWidget(self._title_label, 0, 1, Qt.AlignVCenter)

        title_layout.setColumnStretch(2, 1)  # Spacer

        main_layout.addWidget(self._title_bar)

        # Content widget - subclasses should set their layout directly on this
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        main_layout.addWidget(self._content_widget)

        # Set initial state
        if collapsed:
            self._content_widget.setVisible(False)
            self._arrow_label.setText("▶")
            self._collapsed = True
        else:
            self._content_widget.setVisible(True)
            self._arrow_label.setText("▼")
            self._collapsed = False

    def setTitle(self, title: str):
        """Set the panel title."""
        self._title = title
        self._title_label.setText(title)

    def title(self) -> str:
        """Get the panel title."""
        return self._title

    def setLayout(self, layout):
        """Set the content layout directly on _content_widget."""
        self._content_widget.setLayout(layout)
        self._content_layout = layout

    def layout(self):
        """Get the content layout."""
        return self._content_layout

    def toggle(self):
        """Toggle the collapsed state."""
        self._collapsed = not self._collapsed
        self._update_visual_state()
        self.toggled.emit(not self._collapsed)

    def setCollapsed(self, collapsed: bool):
        """Set the collapsed state."""
        if self._collapsed != collapsed:
            self._collapsed = collapsed
            self._update_visual_state()
            self.toggled.emit(not self._collapsed)

    def isCollapsed(self) -> bool:
        """Check if panel is collapsed."""
        return self._collapsed

    def _update_visual_state(self):
        """Update visual indicators based on collapsed state."""
        if self._collapsed:
            self._arrow_label.setText("▶")
            self._content_widget.setVisible(False)
        else:
            self._arrow_label.setText("▼")
            self._content_widget.setVisible(True)

        self._update_style()

    def _update_style(self):
        """Update panel style based on collapsed state."""
        if self._collapsed:
            self.setStyleSheet("""
                CollapsiblePanel {
                    background-color: #FFFFFF;
                    border: 1px solid #C8C8C8;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                CollapsiblePanel {
                    background-color: #FFFFFF;
                    border: 1px solid #C8C8C8;
                    border-radius: 8px;
                }
            """)
