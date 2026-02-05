"""Dark and light theme stylesheets for FPSPACK GUI."""

DARK_THEME = """
QMainWindow { background-color: #1e1e2e; }
QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', 'Ubuntu', sans-serif; font-size: 13px; }
QTabWidget::pane { border: 1px solid #45475a; background-color: #1e1e2e; }
QTabBar::tab { background: #313244; color: #cdd6f4; padding: 8px 20px; border: 1px solid #45475a;
               border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
QTabBar::tab:selected { background: #45475a; border-bottom: 2px solid #89b4fa; }
QTabBar::tab:hover { background: #45475a; }
QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 12px; padding: 12px 8px 8px 8px;
            font-weight: bold; color: #89b4fa; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QSlider::groove:horizontal { height: 6px; background: #45475a; border-radius: 3px; }
QSlider::handle:horizontal { width: 18px; height: 18px; background: #89b4fa; border-radius: 9px;
                              margin: -6px 0; }
QSlider::handle:horizontal:hover { background: #b4befe; }
QDoubleSpinBox, QSpinBox { background: #313244; border: 1px solid #45475a; border-radius: 4px;
                            padding: 4px 8px; color: #cdd6f4; min-width: 80px; }
QDoubleSpinBox:focus, QSpinBox:focus { border: 1px solid #89b4fa; }
QComboBox { background: #313244; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px;
            color: #cdd6f4; min-width: 120px; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background: #313244; color: #cdd6f4; selection-background-color: #45475a; }
QPushButton { background: #313244; border: 1px solid #45475a; border-radius: 4px; padding: 6px 16px;
              color: #cdd6f4; }
QPushButton:hover { background: #45475a; border-color: #89b4fa; }
QPushButton:pressed { background: #585b70; }
QLabel { color: #cdd6f4; background: transparent; }
QStatusBar { background: #181825; color: #a6adc8; border-top: 1px solid #45475a; padding: 4px; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #1e1e2e; width: 10px; }
QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenuBar { background: #181825; color: #cdd6f4; border-bottom: 1px solid #45475a; }
QMenuBar::item:selected { background: #45475a; }
QMenu { background: #313244; color: #cdd6f4; border: 1px solid #45475a; }
QMenu::item:selected { background: #45475a; }
QSplitter::handle { background: #45475a; }
"""

LIGHT_THEME = """
QMainWindow { background-color: #eff1f5; }
QWidget { background-color: #eff1f5; color: #4c4f69; font-family: 'Segoe UI', 'Ubuntu', sans-serif; font-size: 13px; }
QTabWidget::pane { border: 1px solid #ccd0da; background-color: #eff1f5; }
QTabBar::tab { background: #e6e9ef; color: #4c4f69; padding: 8px 20px; border: 1px solid #ccd0da;
               border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
QTabBar::tab:selected { background: #dce0e8; border-bottom: 2px solid #1e66f5; }
QTabBar::tab:hover { background: #dce0e8; }
QGroupBox { border: 1px solid #ccd0da; border-radius: 6px; margin-top: 12px; padding: 12px 8px 8px 8px;
            font-weight: bold; color: #1e66f5; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QSlider::groove:horizontal { height: 6px; background: #ccd0da; border-radius: 3px; }
QSlider::handle:horizontal { width: 18px; height: 18px; background: #1e66f5; border-radius: 9px;
                              margin: -6px 0; }
QSlider::handle:horizontal:hover { background: #7287fd; }
QDoubleSpinBox, QSpinBox { background: #ffffff; border: 1px solid #ccd0da; border-radius: 4px;
                            padding: 4px 8px; color: #4c4f69; min-width: 80px; }
QDoubleSpinBox:focus, QSpinBox:focus { border: 1px solid #1e66f5; }
QComboBox { background: #ffffff; border: 1px solid #ccd0da; border-radius: 4px; padding: 4px 8px;
            color: #4c4f69; min-width: 120px; }
QComboBox QAbstractItemView { background: #ffffff; color: #4c4f69; selection-background-color: #dce0e8; }
QPushButton { background: #e6e9ef; border: 1px solid #ccd0da; border-radius: 4px; padding: 6px 16px;
              color: #4c4f69; }
QPushButton:hover { background: #dce0e8; border-color: #1e66f5; }
QPushButton:pressed { background: #bcc0cc; }
QLabel { color: #4c4f69; background: transparent; }
QStatusBar { background: #dce0e8; color: #6c6f85; border-top: 1px solid #ccd0da; padding: 4px; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #eff1f5; width: 10px; }
QScrollBar::handle:vertical { background: #ccd0da; border-radius: 5px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenuBar { background: #dce0e8; color: #4c4f69; border-bottom: 1px solid #ccd0da; }
QMenuBar::item:selected { background: #ccd0da; }
QMenu { background: #e6e9ef; color: #4c4f69; border: 1px solid #ccd0da; }
QMenu::item:selected { background: #dce0e8; }
QSplitter::handle { background: #ccd0da; }
"""


class ThemeColors:
    """Colors that matplotlib uses, matching the active theme."""

    def __init__(self, dark=True):
        self.set_dark(dark)

    def set_dark(self, dark=True):
        self.dark = dark
        if dark:
            self.bg = '#1e1e2e'
            self.fg = '#cdd6f4'
            self.compressional = '#585b70'
            self.dilatational = '#1e1e2e'
            self.circle = '#cdd6f4'
            self.great_circle = '#f5c2e7'
            self.great_circle2 = '#f5c2e7'
            self.p_color = '#f38ba8'
            self.t_color = '#89b4fa'
            self.b_color = '#a6e3a1'
            self.compass = '#bac2de'
            self.grid = '#45475a'
        else:
            self.bg = '#eff1f5'
            self.fg = '#4c4f69'
            self.compressional = '#4c4f69'
            self.dilatational = '#eff1f5'
            self.circle = '#4c4f69'
            self.great_circle = '#d20f39'
            self.great_circle2 = '#d20f39'
            self.p_color = '#d20f39'
            self.t_color = '#1e66f5'
            self.b_color = '#40a02b'
            self.compass = '#5c5f77'
            self.grid = '#ccd0da'
