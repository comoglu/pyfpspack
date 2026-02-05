"""
pyfpspack.gui - Interactive GUI for focal mechanism analysis.

Requires optional dependencies: pip install pyfpspack[gui]
"""

try:
    from .main_window import FPSPackMainWindow, main
    __all__ = ["FPSPackMainWindow", "main"]
except ImportError as e:
    import warnings
    warnings.warn(
        f"GUI dependencies not installed. Install with: pip install pyfpspack[gui]\n"
        f"Original error: {e}"
    )
    __all__ = []
