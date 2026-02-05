"""Tab 3: P/T Axes — input P and T trend/plunge, compute planes and tensor."""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                              QLabel, QSplitter)
from PyQt5.QtCore import Qt, QTimer

from ... import core as pyfpspack
from ..widgets.labeled_slider import LabeledSlider
from ..widgets.results_panel import ResultsPanel
from ..beachball import BeachballCanvas


class PTAxesTab(QWidget):

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

        # --- Left: input ---
        input_box = QGroupBox("P / T Axes Input")
        input_layout = QVBoxLayout()

        p_group = QGroupBox("P Axis (Compression)")
        p_layout = QVBoxLayout()
        self.p_trend = LabeledSlider("Trend:", 0, 360, 0, decimals=1)
        self.p_plunge = LabeledSlider("Plunge:", 0, 90, 45, decimals=1)
        p_layout.addWidget(self.p_trend)
        p_layout.addWidget(self.p_plunge)
        p_group.setLayout(p_layout)
        input_layout.addWidget(p_group)

        t_group = QGroupBox("T Axis (Tension)")
        t_layout = QVBoxLayout()
        self.t_trend = LabeledSlider("Trend:", 0, 360, 180, decimals=1)
        self.t_plunge = LabeledSlider("Plunge:", 0, 90, 45, decimals=1)
        t_layout.addWidget(self.t_trend)
        t_layout.addWidget(self.t_plunge)
        t_group.setLayout(t_layout)
        input_layout.addWidget(t_group)

        # Perpendicularity indicator
        self._perp_label = QLabel("")
        self._perp_label.setWordWrap(True)
        self._perp_label.setStyleSheet("padding: 8px; font-size: 12px;")
        input_layout.addWidget(self._perp_label)

        input_layout.addStretch()

        info = QLabel(
            "<b>Note:</b> P and T axes must be<br>"
            "perpendicular (within 2\u00b0 tolerance).<br>"
            "The B axis is computed as P \u00d7 T."
        )
        info.setWordWrap(True)
        info.setStyleSheet("padding: 8px; font-size: 11px;")
        input_layout.addWidget(info)

        input_box.setLayout(input_layout)
        input_box.setFixedWidth(340)

        # --- Right ---
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
        for slider in (self.p_trend, self.p_plunge,
                       self.t_trend, self.t_plunge):
            slider.valueChanged.connect(self._schedule)

    def _schedule(self):
        self._timer.start()

    def _do_update(self):
        tp = self.p_trend.value()
        pp = self.p_plunge.value()
        tt = self.t_trend.value()
        pt = self.t_plunge.value()

        try:
            pv = pyfpspack.ax2ca(tp, pp)
            tv = pyfpspack.ax2ca(tt, pt)

            # Check perpendicularity before calling pt2pl
            ang = pyfpspack._angle_between(pv, tv)
            if abs(ang - 90.0) > pyfpspack.ORTTOL:
                self._perp_label.setText(
                    f"<span style='color:#f38ba8;'>"
                    f"P \u00b7 T angle = {ang:.1f}\u00b0 (need 90\u00b0 \u00b1 2\u00b0)<br>"
                    f"Axes are NOT perpendicular.</span>"
                )
                self.results.clear_all()
                self.beachball.clear()
                if self._main:
                    self._main.statusBar().showMessage(
                        f"P and T not perpendicular: angle = {ang:.1f}\u00b0")
                return
            else:
                self._perp_label.setText(
                    f"<span style='color:#a6e3a1;'>"
                    f"P \u00b7 T angle = {ang:.1f}\u00b0 \u2714</span>"
                )

            plane_a, plane_b = pyfpspack.pt2pl(tp, pp, tt, pt)

            # Build axes info
            bv = np.cross(pv, tv)
            if bv[2] < 0:
                bv = -bv
            _, bv = pyfpspack._normalize(bv)
            tb, pb = pyfpspack.ca2ax(bv)

            axes = pyfpspack.PTBAngles(
                trend_p=tp, plunge_p=pp,
                trend_t=tt, plunge_t=pt,
                trend_b=tb, plunge_b=pb,
            )

            mt_ar = pyfpspack.pt2ar(tp, pp, tt, pt)
            mt_ha = pyfpspack.ar2ha(mt_ar)
            dec = pyfpspack.ar2plp(mt_ar)

            self.results.display_full(plane_a, plane_b, axes, mt_ar, mt_ha, dec)
            self.beachball.draw_beachball(plane_a.strike, plane_a.dip,
                                          plane_a.rake, axes)
            if self._main:
                self._main.statusBar().showMessage("Ready")
        except Exception as e:
            self.results.clear_all()
            self.beachball.clear()
            if self._main:
                self._main.statusBar().showMessage(f"Error: {e}")

    def set_theme(self, dark):
        self.beachball.set_theme(dark)
        self._do_update()
