"""Tab 4: Angle Calculator — compare two focal mechanisms."""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                              QLabel, QFormLayout, QSplitter)
from PyQt5.QtCore import Qt, QTimer

from ... import core as pyfpspack
from ..widgets.labeled_slider import LabeledSlider
from ..beachball import DualBeachballCanvas


class _MechanismInput(QGroupBox):
    """Input widget for a single focal mechanism (strike/dip/rake)."""

    def __init__(self, title, s=0, d=45, r=90, parent=None):
        super().__init__(title, parent)
        layout = QVBoxLayout()
        self.strike = LabeledSlider("Strike:", 0, 360, s, decimals=1)
        self.dip = LabeledSlider("Dip:", 0, 90, d, decimals=1)
        self.rake = LabeledSlider("Rake:", -180, 180, r, decimals=1)
        layout.addWidget(self.strike)
        layout.addWidget(self.dip)
        layout.addWidget(self.rake)
        self.setLayout(layout)

    def values(self):
        return self.strike.value(), self.dip.value(), self.rake.value()


class AngleCalculatorTab(QWidget):

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self._main = main_window
        self._build_ui()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._do_update)
        self._connect_signals()
        self._do_update()

    def _build_ui(self):
        outer = QHBoxLayout(self)

        # --- Left: two mechanism inputs ---
        input_box = QWidget()
        input_layout = QVBoxLayout(input_box)

        self.mech_a = _MechanismInput("Mechanism A", s=0, d=45, r=90)
        self.mech_b = _MechanismInput("Mechanism B", s=90, d=60, r=-90)
        input_layout.addWidget(self.mech_a)
        input_layout.addWidget(self.mech_b)
        input_layout.addStretch()

        input_box.setFixedWidth(340)

        # --- Right: results + dual beachball ---
        right_splitter = QSplitter(Qt.Vertical)

        # Angle results
        results_box = QGroupBox("Angle Comparison")
        results_layout = QFormLayout()
        results_layout.setSpacing(8)

        self._fields = {}
        labels = [
            ("Angle between planes:", "planes"),
            ("Angle between slip directions:", "slip"),
            ("P axis angle:", "p"),
            ("T axis angle:", "t"),
            ("B axis angle:", "b"),
        ]
        for text, key in labels:
            lbl = QLabel("--")
            lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
            lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            results_layout.addRow(text, lbl)
            self._fields[key] = lbl

        results_box.setLayout(results_layout)
        right_splitter.addWidget(results_box)

        self.dual_bb = DualBeachballCanvas(width=8, height=4, dpi=100)
        right_splitter.addWidget(self.dual_bb)
        right_splitter.setStretchFactor(0, 2)
        right_splitter.setStretchFactor(1, 5)

        outer.addWidget(input_box)
        outer.addWidget(right_splitter, stretch=1)

    def _connect_signals(self):
        for mech in (self.mech_a, self.mech_b):
            for slider in (mech.strike, mech.dip, mech.rake):
                slider.valueChanged.connect(self._schedule)

    def _schedule(self):
        self._timer.start()

    def _do_update(self):
        s1, d1, r1 = self.mech_a.values()
        s2, d2, r2 = self.mech_b.values()
        axes1 = axes2 = None
        try:
            # Compute angles
            ang_p, ang_d = pyfpspack.angles(s1, d1, r1, s2, d2, r2)
            self._fields["planes"].setText(f"{ang_p:.2f}\u00b0")
            self._fields["slip"].setText(f"{ang_d:.2f}\u00b0")

            axes1 = pyfpspack.pl2pt(s1, d1, r1)
            axes2 = pyfpspack.pl2pt(s2, d2, r2)

            ang_pp = pyfpspack.anglea(axes1.trend_p, axes1.plunge_p,
                                     axes2.trend_p, axes2.plunge_p)
            ang_tt = pyfpspack.anglea(axes1.trend_t, axes1.plunge_t,
                                     axes2.trend_t, axes2.plunge_t)
            ang_bb = pyfpspack.anglea(axes1.trend_b, axes1.plunge_b,
                                     axes2.trend_b, axes2.plunge_b)

            self._fields["p"].setText(f"{ang_pp:.2f}\u00b0")
            self._fields["t"].setText(f"{ang_tt:.2f}\u00b0")
            self._fields["b"].setText(f"{ang_bb:.2f}\u00b0")

            self.dual_bb.draw_both(s1, d1, r1, axes1, s2, d2, r2, axes2)

            if self._main:
                self._main.statusBar().showMessage("Ready")
        except pyfpspack.FPSError as e:
            for lbl in self._fields.values():
                lbl.setText("--")
            self.dual_bb.clear()
            if self._main:
                self._main.statusBar().showMessage(f"Error: {e}")

    def set_theme(self, dark):
        self.dual_bb.set_theme(dark)
        self._do_update()
