"""Reusable button with QMenu that doesn't show arrow indicator."""

from PySide6.QtCore import QPoint, Signal
from PySide6.QtWidgets import QMenu, QPushButton


class MenuButton(QPushButton):
    """A button that shows a QMenu when clicked, without the arrow indicator.

    This is a reusable component that mimics the behavior of setMenu()
    but hides the arrow indicator by using clicked.connect instead.

    Signals:
        menu_triggered: Emitted when the menu is about to be shown
    """

    menu_triggered = Signal()

    def __init__(self, text: str = "", button_height: int = 32, parent=None):
        super().__init__(text, parent)

        self.setFixedHeight(button_height)
        self._menu: QMenu | None = None

        # Connect click event to show menu
        self.clicked.connect(self._show_menu)

    def set_menu(self, menu: QMenu):
        """Set the QMenu to show when button is clicked.

        Args:
            menu: The QMenu instance to display
        """
        self._menu = menu

    def _show_menu(self):
        """Show the menu with proper positioning and width."""
        if self._menu is None:
            return

        self.menu_triggered.emit()

        # Set menu width to match button width
        self._menu.setFixedWidth(self.width())

        # Position menu below the button with 2px offset
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self._menu.exec(pos + QPoint(0, 2))
