"""Reusable results display panel."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox,
                              QFormLayout, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
import numpy as np


class ResultsPanel(QScrollArea):
    """Scrollable panel that displays computed focal mechanism results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setSpacing(4)

        # Nodal Plane A
        self._np_a_group = QGroupBox("Nodal Plane A")
        self._np_a_layout = QFormLayout()
        self._np_a_layout.setSpacing(2)
        self._np_a_fields = {}
        for name in ["Strike", "Dip", "Rake", "Dip Dir"]:
            lbl = QLabel("--")
            lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self._np_a_layout.addRow(f"{name}:", lbl)
            self._np_a_fields[name] = lbl
        self._np_a_group.setLayout(self._np_a_layout)
        self._layout.addWidget(self._np_a_group)

        # Nodal Plane B
        self._np_b_group = QGroupBox("Nodal Plane B")
        self._np_b_layout = QFormLayout()
        self._np_b_layout.setSpacing(2)
        self._np_b_fields = {}
        for name in ["Strike", "Dip", "Rake", "Dip Dir"]:
            lbl = QLabel("--")
            lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self._np_b_layout.addRow(f"{name}:", lbl)
            self._np_b_fields[name] = lbl
        self._np_b_group.setLayout(self._np_b_layout)
        self._layout.addWidget(self._np_b_group)

        # P/T/B Axes
        self._axes_group = QGroupBox("P / T / B Axes")
        self._axes_layout = QFormLayout()
        self._axes_layout.setSpacing(2)
        self._axes_fields = {}
        for axis in ["P", "T", "B"]:
            for ang in ["Trend", "Plunge"]:
                key = f"{axis} {ang}"
                lbl = QLabel("--")
                lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
                self._axes_layout.addRow(f"{key}:", lbl)
                self._axes_fields[key] = lbl
        self._axes_group.setLayout(self._axes_layout)
        self._layout.addWidget(self._axes_group)

        # Moment Tensor AR
        self._mt_ar_group = QGroupBox("Moment Tensor (Aki-Richards)")
        self._mt_ar_layout = QVBoxLayout()
        self._mt_ar_label = QLabel("--")
        self._mt_ar_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._mt_ar_label.setStyleSheet("font-family: monospace; font-size: 12px;")
        self._mt_ar_layout.addWidget(self._mt_ar_label)
        self._mt_ar_group.setLayout(self._mt_ar_layout)
        self._layout.addWidget(self._mt_ar_group)

        # Moment Tensor Harvard
        self._mt_ha_group = QGroupBox("Moment Tensor (Harvard CMT)")
        self._mt_ha_layout = QVBoxLayout()
        self._mt_ha_label = QLabel("--")
        self._mt_ha_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._mt_ha_label.setStyleSheet("font-family: monospace; font-size: 12px;")
        self._mt_ha_layout.addWidget(self._mt_ha_label)
        self._mt_ha_group.setLayout(self._mt_ha_layout)
        self._layout.addWidget(self._mt_ha_group)

        # Decomposition
        self._dec_group = QGroupBox("Decomposition")
        self._dec_layout = QFormLayout()
        self._dec_layout.setSpacing(2)
        self._dec_fields = {}
        for name in ["M0 (principal)", "M1 (secondary)", "M0b (best DC)",
                      "Isotropic (e)", "CLVD (eta)"]:
            lbl = QLabel("--")
            lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self._dec_layout.addRow(f"{name}:", lbl)
            self._dec_fields[name] = lbl
        self._dec_group.setLayout(self._dec_layout)
        self._layout.addWidget(self._dec_group)

        self._layout.addStretch()
        self.setWidget(container)

    def update_plane(self, plane, fields):
        fields["Strike"].setText(f"{plane.strike:.2f}\u00b0")
        fields["Dip"].setText(f"{plane.dip:.2f}\u00b0")
        fields["Rake"].setText(f"{plane.rake:.2f}\u00b0")
        fields["Dip Dir"].setText(f"{plane.dipdir:.2f}\u00b0")

    def update_axes(self, axes):
        self._axes_fields["P Trend"].setText(f"{axes.trend_p:.2f}\u00b0")
        self._axes_fields["P Plunge"].setText(f"{axes.plunge_p:.2f}\u00b0")
        self._axes_fields["T Trend"].setText(f"{axes.trend_t:.2f}\u00b0")
        self._axes_fields["T Plunge"].setText(f"{axes.plunge_t:.2f}\u00b0")
        self._axes_fields["B Trend"].setText(f"{axes.trend_b:.2f}\u00b0")
        self._axes_fields["B Plunge"].setText(f"{axes.plunge_b:.2f}\u00b0")

    def _format_tensor(self, am):
        rows = []
        for i in range(3):
            row = "  ".join(f"{am[i,j]:10.4f}" for j in range(3))
            rows.append(f"[ {row} ]")
        return "\n".join(rows)

    def update_tensor_ar(self, am):
        self._mt_ar_label.setText(self._format_tensor(am))

    def update_tensor_ha(self, am):
        self._mt_ha_label.setText(self._format_tensor(am))

    def update_decomposition(self, am0, am1, am0b, e, eta):
        self._dec_fields["M0 (principal)"].setText(f"{am0:.6g}")
        self._dec_fields["M1 (secondary)"].setText(f"{am1:.6g}")
        self._dec_fields["M0b (best DC)"].setText(f"{am0b:.6g}")
        self._dec_fields["Isotropic (e)"].setText(f"{e:.6g}")
        self._dec_fields["CLVD (eta)"].setText(f"{eta:.4f}")

    def display_full(self, plane_a, plane_b, axes, mt_ar, mt_ha, dec):
        """Update all fields from a complete computation."""
        self.update_plane(plane_a, self._np_a_fields)
        self.update_plane(plane_b, self._np_b_fields)
        self.update_axes(axes)
        self.update_tensor_ar(mt_ar)
        self.update_tensor_ha(mt_ha)
        self.update_decomposition(dec.am0, dec.am1, dec.am0b, dec.e, dec.eta)

    def clear_all(self):
        for fields in [self._np_a_fields, self._np_b_fields, self._axes_fields,
                        self._dec_fields]:
            for lbl in fields.values():
                lbl.setText("--")
        self._mt_ar_label.setText("--")
        self._mt_ha_label.setText("--")
