"""Tab 1: Focal Mechanism — Strike/Dip/Rake input with full output."""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                              QComboBox, QLabel, QSplitter)
from PyQt5.QtCore import Qt, QTimer

from ... import core as pyfpspack
from ..widgets.labeled_slider import LabeledSlider
from ..widgets.results_panel import ResultsPanel
from ..beachball import BeachballCanvas


PRESETS = {
    "Custom": None,
    "Normal Fault (N-S)": (0, 45, -90),
    "Thrust Fault (N-S)": (0, 45, 90),
    "Left-Lateral SS": (0, 90, 0),
    "Right-Lateral SS": (0, 90, 180),
    "Oblique Normal": (45, 60, -120),
    "Oblique Thrust": (135, 30, 60),
}


class FocalMechanismTab(QWidget):

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

        # --- Left: input panel ---
        input_box = QGroupBox("Input Parameters")
        input_layout = QVBoxLayout()

        self.strike_slider = LabeledSlider("Strike:", 0, 360, 0, decimals=1)
        self.dip_slider = LabeledSlider("Dip:", 0, 90, 45, decimals=1)
        self.rake_slider = LabeledSlider("Rake:", -180, 180, 90, decimals=1)

        input_layout.addWidget(self.strike_slider)
        input_layout.addWidget(self.dip_slider)
        input_layout.addWidget(self.rake_slider)

        # Presets
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        for name in PRESETS:
            self.preset_combo.addItem(name)
        preset_row.addWidget(self.preset_combo, stretch=1)
        input_layout.addLayout(preset_row)

        input_layout.addStretch()

        # Info box
        info = QLabel(
            "<b>Aki-Richards Convention</b><br>"
            "x = North, y = East, z = Down<br><br>"
            "<b>Beachball Legend</b><br>"
            "Dark = Compressional<br>"
            "Light = Dilatational<br>"
            "Solid line = Plane A<br>"
            "Dashed line = Plane B"
        )
        info.setWordWrap(True)
        info.setStyleSheet("padding: 8px; font-size: 11px;")
        input_layout.addWidget(info)

        input_box.setLayout(input_layout)
        input_box.setFixedWidth(340)

        # --- Right: results + beachball ---
        right_splitter = QSplitter(Qt.Vertical)

        self.results = ResultsPanel()
        self.beachball = BeachballCanvas(width=4, height=4, dpi=100)

        right_splitter.addWidget(self.results)
        right_splitter.addWidget(self.beachball)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 4)

        outer.addWidget(input_box)
        outer.addWidget(right_splitter, stretch=1)

    def _connect_signals(self):
        self.strike_slider.valueChanged.connect(self._schedule)
        self.dip_slider.valueChanged.connect(self._schedule)
        self.rake_slider.valueChanged.connect(self._schedule)
        self.preset_combo.currentIndexChanged.connect(self._on_preset)

    def _schedule(self):
        self._timer.start()

    def _on_preset(self, idx):
        name = self.preset_combo.currentText()
        vals = PRESETS.get(name)
        if vals is None:
            return
        s, d, r = vals
        self.strike_slider.setValue(s)
        self.dip_slider.setValue(d)
        self.rake_slider.setValue(r)
        self._do_update()

    def _do_update(self):
        strike = self.strike_slider.value()
        dip = self.dip_slider.value()
        rake = self.rake_slider.value()
        try:
            n, d = pyfpspack.pl2nd(strike, dip, rake)
            plane_a = pyfpspack.nd2pl(n, d)
            plane_b = pyfpspack.pl2pl(strike, dip, rake)
            axes = pyfpspack.pl2pt(strike, dip, rake)
            mt_ar = pyfpspack.pl2ar(strike, dip, rake)
            mt_ha = pyfpspack.pl2ha(strike, dip, rake)
            dec = pyfpspack.ar2plp(mt_ar)

            self.results.display_full(plane_a, plane_b, axes, mt_ar, mt_ha, dec)
            self.beachball.draw_beachball(strike, dip, rake, axes)
            if self._main:
                self._main.statusBar().showMessage("Ready")
        except pyfpspack.FPSError as e:
            self.results.clear_all()
            self.beachball.clear()
            if self._main:
                self._main.statusBar().showMessage(f"Error: {e}")

    def set_theme(self, dark):
        self.beachball.set_theme(dark)
        self._do_update()
