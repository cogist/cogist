#!/usr/bin/env python3
"""Test script for QSlider + QSpinBox combination."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SliderSpinBoxDemo(QWidget):
    """Demonstrate QSlider + QSpinBox combination."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSlider + QSpinBox Demo")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # === Brightness Control ===
        brightness_group = QVBoxLayout()
        brightness_label = QLabel("Brightness:")
        brightness_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        brightness_group.addWidget(brightness_label)

        brightness_layout = QHBoxLayout()
        brightness_layout.setSpacing(8)

        # Slider
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(50, 150)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self._on_brightness_slider_changed)
        brightness_layout.addWidget(self.brightness_slider)

        # SpinBox
        self.brightness_spin = QSpinBox()
        self.brightness_spin.setRange(50, 150)
        self.brightness_spin.setValue(100)
        self.brightness_spin.setFixedWidth(70)
        self.brightness_spin.valueChanged.connect(self._on_brightness_spin_changed)
        brightness_layout.addWidget(self.brightness_spin)

        brightness_group.addLayout(brightness_layout)
        layout.addLayout(brightness_group)

        # Display current value
        self.brightness_display = QLabel("Current: 1.00")
        self.brightness_display.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.brightness_display)

        # === Opacity Control ===
        opacity_group = QVBoxLayout()
        opacity_label = QLabel("Opacity:")
        opacity_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        opacity_group.addWidget(opacity_label)

        opacity_layout = QHBoxLayout()
        opacity_layout.setSpacing(8)

        # Slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)
        opacity_layout.addWidget(self.opacity_slider)

        # SpinBox
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 255)
        self.opacity_spin.setValue(255)
        self.opacity_spin.setFixedWidth(70)
        self.opacity_spin.valueChanged.connect(self._on_opacity_spin_changed)
        opacity_layout.addWidget(self.opacity_spin)

        opacity_group.addLayout(opacity_layout)
        layout.addLayout(opacity_group)

        # Display current value
        self.opacity_display = QLabel("Current: 255 (100%)")
        self.opacity_display.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.opacity_display)

        layout.addStretch()
        self.setLayout(layout)

    def _on_brightness_slider_changed(self, value: int):
        """Sync spinbox when slider changes."""
        self.brightness_spin.blockSignals(True)
        self.brightness_spin.setValue(value)
        self.brightness_spin.blockSignals(False)
        self.brightness_display.setText(f"Current: {value / 100.0:.2f}")

    def _on_brightness_spin_changed(self, value: int):
        """Sync slider when spinbox changes."""
        self.brightness_slider.blockSignals(True)
        self.brightness_slider.setValue(value)
        self.brightness_slider.blockSignals(False)
        self.brightness_display.setText(f"Current: {value / 100.0:.2f}")

    def _on_opacity_slider_changed(self, value: int):
        """Sync spinbox when slider changes."""
        self.opacity_spin.blockSignals(True)
        self.opacity_spin.setValue(value)
        self.opacity_spin.blockSignals(False)
        self.opacity_display.setText(f"Current: {value} ({value / 255 * 100:.0f}%)")

    def _on_opacity_spin_changed(self, value: int):
        """Sync slider when spinbox changes."""
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(value)
        self.opacity_slider.blockSignals(False)
        self.opacity_display.setText(f"Current: {value} ({value / 255 * 100:.0f}%)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SliderSpinBoxDemo()
    window.show()
    sys.exit(app.exec())
