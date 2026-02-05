"""Main window for pyfpspack GUI application."""

import sys
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QApplication,
                              QFileDialog, QMessageBox)
from PyQt5.QtGui import QKeySequence

from .themes import DARK_THEME, LIGHT_THEME
from .tabs.focal_mechanism_tab import FocalMechanismTab
from .tabs.moment_tensor_tab import MomentTensorTab
from .tabs.pt_axes_tab import PTAxesTab
from .tabs.angle_calculator_tab import AngleCalculatorTab


class FPSPackMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfpspack — Focal Mechanism Toolbox")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        self._dark = True

        self._build_tabs()
        self._build_menus()
        self._build_statusbar()
        self._apply_theme()

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tab_focal = FocalMechanismTab(main_window=self)
        self.tab_tensor = MomentTensorTab(main_window=self)
        self.tab_pt = PTAxesTab(main_window=self)
        self.tab_angle = AngleCalculatorTab(main_window=self)

        self.tabs.addTab(self.tab_focal, "Focal Mechanism")
        self.tabs.addTab(self.tab_tensor, "Moment Tensor")
        self.tabs.addTab(self.tab_pt, "P/T Axes")
        self.tabs.addTab(self.tab_angle, "Angle Calculator")

        self.setCentralWidget(self.tabs)

    def _build_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        export_png = QAction("Export Beachball as PNG...", self)
        export_png.setShortcut(QKeySequence("Ctrl+E"))
        export_png.triggered.connect(self._export_png)
        file_menu.addAction(export_png)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence("Ctrl+Q"))
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # View menu
        view_menu = menubar.addMenu("&View")

        self._theme_action = QAction("Switch to Light Theme", self)
        self._theme_action.setShortcut(QKeySequence("Ctrl+T"))
        self._theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(self._theme_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_act = QAction("About pyfpspack", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

        conventions_act = QAction("Conventions Reference", self)
        conventions_act.triggered.connect(self._show_conventions)
        help_menu.addAction(conventions_act)

    def _build_statusbar(self):
        self.statusBar().showMessage("Ready")

    def _apply_theme(self):
        self.setStyleSheet(DARK_THEME if self._dark else LIGHT_THEME)
        for tab in (self.tab_focal, self.tab_tensor, self.tab_pt, self.tab_angle):
            tab.set_theme(self._dark)
        label = "Switch to Light Theme" if self._dark else "Switch to Dark Theme"
        self._theme_action.setText(label)

    def _toggle_theme(self):
        self._dark = not self._dark
        self._apply_theme()

    def _export_png(self):
        current = self.tabs.currentWidget()
        canvas = None
        if hasattr(current, 'beachball'):
            canvas = current.beachball
        elif hasattr(current, 'dual_bb'):
            canvas = current.dual_bb

        if canvas is None:
            self.statusBar().showMessage("No beachball to export on this tab.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Beachball", "beachball.png",
            "PNG Images (*.png);;All Files (*)")
        if path:
            canvas.figure.savefig(path, dpi=150, bbox_inches='tight',
                                  facecolor=canvas.figure.get_facecolor())
            self.statusBar().showMessage(f"Exported to {path}")

    def _show_about(self):
        QMessageBox.about(self, "About pyfpspack",
            "<h3>pyfpspack - Focal Mechanism Toolbox</h3>"
            "<p>Python port of the FPSPACK Fortran library by "
            "P. Gasperini &amp; G. Vannucci (2003).</p>"
            "<p>Manages earthquake focal mechanism representations:<br>"
            "nodal planes, P/T/B axes, moment tensors,<br>"
            "and mechanism comparisons.</p>"
            "<p><b>Coordinate System:</b> Aki-Richards<br>"
            "x = North, y = East, z = Down</p>"
            "<p><a href='https://github.com/comoglu/pyfpspack'>GitHub Repository</a></p>")

    def _show_conventions(self):
        QMessageBox.information(self, "Conventions Reference",
            "<h3>Aki-Richards Convention</h3>"
            "<p><b>Axes:</b> x = North, y = East, z = Down</p>"
            "<p><b>Strike:</b> 0\u00b0\u2013360\u00b0 clockwise from North</p>"
            "<p><b>Dip:</b> 0\u00b0\u201390\u00b0 from horizontal, to the right of strike</p>"
            "<p><b>Rake:</b> \u2212180\u00b0 to +180\u00b0 on the fault plane</p>"
            "<hr>"
            "<h4>Fault Types</h4>"
            "<ul>"
            "<li><b>Normal:</b> rake = \u221290\u00b0 (hangingwall drops)</li>"
            "<li><b>Thrust:</b> rake = +90\u00b0 (hangingwall rises)</li>"
            "<li><b>Left-lateral SS:</b> rake = 0\u00b0</li>"
            "<li><b>Right-lateral SS:</b> rake = \u00b1180\u00b0</li>"
            "</ul>"
            "<hr>"
            "<h4>Harvard CMT</h4>"
            "<p>r = Up, \u03b8 = South, \u03c6 = East<br>"
            "Transform via ar2ha (its own inverse).</p>")


def main():
    """Launch the pyfpspack GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("pyfpspack")
    window = FPSPackMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
