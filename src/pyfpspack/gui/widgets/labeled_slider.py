"""Reusable labeled slider + spinbox widget."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QDoubleSpinBox
from PyQt5.QtCore import Qt, pyqtSignal


class LabeledSlider(QWidget):
    """A labeled horizontal slider synchronized with a spinbox.

    Layout: [Label] [====slider====] [spinbox]
    """

    valueChanged = pyqtSignal(float)

    def __init__(self, label, min_val, max_val, default, decimals=1,
                 label_width=70, parent=None):
        super().__init__(parent)
        self._block = False
        self._decimals = decimals
        self._scale = 10 ** decimals

        self._label = QLabel(label)
        self._label.setFixedWidth(label_width)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(int(min_val * self._scale),
                              int(max_val * self._scale))
        self._slider.setValue(int(default * self._scale))

        self._spin = QDoubleSpinBox()
        self._spin.setRange(min_val, max_val)
        self._spin.setDecimals(decimals)
        self._spin.setSingleStep(1.0 / self._scale)
        self._spin.setValue(default)
        self._spin.setFixedWidth(90)

        self._slider.valueChanged.connect(self._from_slider)
        self._spin.valueChanged.connect(self._from_spin)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.addWidget(self._label)
        layout.addWidget(self._slider, stretch=1)
        layout.addWidget(self._spin)

    def _from_slider(self, int_val):
        if not self._block:
            self._block = True
            fv = int_val / self._scale
            self._spin.setValue(fv)
            self._block = False
            self.valueChanged.emit(fv)

    def _from_spin(self, float_val):
        if not self._block:
            self._block = True
            self._slider.setValue(int(float_val * self._scale))
            self._block = False
            self.valueChanged.emit(float_val)

    def value(self):
        return self._spin.value()

    def setValue(self, v):
        self._block = True
        self._spin.setValue(v)
        self._slider.setValue(int(v * self._scale))
        self._block = False
