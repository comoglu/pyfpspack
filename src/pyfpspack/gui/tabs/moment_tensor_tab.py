"""Tab 2: Moment Tensor — input tensor, decompose to planes and axes."""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                              QComboBox, QLabel, QSplitter, QDoubleSpinBox,
                              QGridLayout, QPushButton, QFormLayout)
from PyQt5.QtCore import Qt

from ... import core as pyfpspack
from ..widgets.results_panel import ResultsPanel
from ..beachball import BeachballCanvas


class MomentTensorTab(QWidget):

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self._main = main_window
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        outer = QHBoxLayout(self)

        # --- Left: input ---
        input_box = QGroupBox("Moment Tensor Input")
        input_layout = QVBoxLayout()

        # Convention
        conv_row = QHBoxLayout()
        conv_row.addWidget(QLabel("Convention:"))
        self.conv_combo = QComboBox()
        self.conv_combo.addItems(["Aki-Richards", "Harvard CMT"])
        conv_row.addWidget(self.conv_combo, stretch=1)
        input_layout.addLayout(conv_row)

        # 6-component input
        self._six_group = QGroupBox("6 Independent Components")
        six_layout = QFormLayout()
        six_layout.setSpacing(6)

        self._ar_labels = ["Mxx (1,1)", "Myy (2,2)", "Mzz (3,3)",
                           "Mxy (1,2)", "Mxz (1,3)", "Myz (2,3)"]
        self._ha_labels = ["Mss (1,1)", "Mee (2,2)", "Mrr (3,3)",
                           "Mse (1,2)", "Mrs (1,3)", "Mre (2,3)"]

        self.six_spins = []
        defaults = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for i, (ar_l, val) in enumerate(zip(self._ar_labels, defaults)):
            spin = QDoubleSpinBox()
            spin.setRange(-1e30, 1e30)
            spin.setDecimals(6)
            spin.setValue(val)
            spin.setSingleStep(0.1)
            self.six_spins.append(spin)
            six_layout.addRow(ar_l, spin)

        self._six_group.setLayout(six_layout)
        input_layout.addWidget(self._six_group)

        # 3x3 matrix input
        self._mat_group = QGroupBox("3x3 Matrix (symmetric)")
        mat_layout = QGridLayout()
        self.mat_spins = [[None]*3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                spin = QDoubleSpinBox()
                spin.setRange(-1e30, 1e30)
                spin.setDecimals(6)
                spin.setValue(0.0)
                spin.setSingleStep(0.1)
                if j < i:
                    spin.setEnabled(False)
                    spin.setStyleSheet("color: gray;")
                self.mat_spins[i][j] = spin
                mat_layout.addWidget(spin, i, j)
        self._mat_group.setLayout(mat_layout)
        input_layout.addWidget(self._mat_group)

        # Preset tensors
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Custom",
                                     "Pure Thrust (s=0,d=45,r=90)",
                                     "Pure Normal (s=0,d=45,r=-90)",
                                     "Strike-Slip (s=0,d=90,r=0)"])
        preset_row.addWidget(self.preset_combo, stretch=1)
        input_layout.addLayout(preset_row)

        # Decompose button
        self.decompose_btn = QPushButton("Decompose")
        self.decompose_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        input_layout.addWidget(self.decompose_btn)

        input_layout.addStretch()
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
        self.decompose_btn.clicked.connect(self._do_decompose)
        self.conv_combo.currentIndexChanged.connect(self._update_labels)
        self.preset_combo.currentIndexChanged.connect(self._on_preset)
        # Mirror upper-triangle to lower-triangle
        for i in range(3):
            for j in range(i+1, 3):
                self.mat_spins[i][j].valueChanged.connect(
                    lambda val, r=j, c=i: self.mat_spins[r][c].setValue(val))

    def _update_labels(self):
        labels = self._ar_labels if self.conv_combo.currentIndex() == 0 \
            else self._ha_labels
        layout = self._six_group.layout()
        for i, lbl in enumerate(labels):
            item = layout.itemAt(i, QFormLayout.LabelRole)
            if item and item.widget():
                item.widget().setText(lbl)

    def _on_preset(self, idx):
        presets = {
            1: (0, 45, 90),
            2: (0, 45, -90),
            3: (0, 90, 0),
        }
        if idx not in presets:
            return
        s, d, r = presets[idx]
        am = pyfpspack.pl2ar(s, d, r)
        if self.conv_combo.currentIndex() == 1:
            am = pyfpspack.ar2ha(am)
        # Fill 6-component
        self.six_spins[0].setValue(am[0, 0])
        self.six_spins[1].setValue(am[1, 1])
        self.six_spins[2].setValue(am[2, 2])
        self.six_spins[3].setValue(am[0, 1])
        self.six_spins[4].setValue(am[0, 2])
        self.six_spins[5].setValue(am[1, 2])
        # Fill matrix
        for i in range(3):
            for j in range(3):
                self.mat_spins[i][j].setValue(am[i, j])
        self._do_decompose()

    def _read_tensor(self):
        am = np.zeros((3, 3))
        am[0, 0] = self.six_spins[0].value()
        am[1, 1] = self.six_spins[1].value()
        am[2, 2] = self.six_spins[2].value()
        am[0, 1] = am[1, 0] = self.six_spins[3].value()
        am[0, 2] = am[2, 0] = self.six_spins[4].value()
        am[1, 2] = am[2, 1] = self.six_spins[5].value()
        return am

    def _do_decompose(self):
        try:
            am = self._read_tensor()
            is_harvard = self.conv_combo.currentIndex() == 1

            if is_harvard:
                dec = pyfpspack.ha2plp(am)
                mt_ha = am
                mt_ar = pyfpspack.ar2ha(am)  # involution
            else:
                dec = pyfpspack.ar2plp(am)
                mt_ar = am
                mt_ha = pyfpspack.ar2ha(am)

            self.results.display_full(dec.plane_a, dec.plane_b, dec.axes,
                                       mt_ar, mt_ha, dec)
            self.beachball.draw_beachball(dec.plane_a.strike, dec.plane_a.dip,
                                          dec.plane_a.rake, dec.axes)
            if self._main:
                self._main.statusBar().showMessage("Ready")
        except Exception as e:
            self.results.clear_all()
            self.beachball.clear()
            if self._main:
                self._main.statusBar().showMessage(f"Error: {e}")

    def set_theme(self, dark):
        self.beachball.set_theme(dark)
