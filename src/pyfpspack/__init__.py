"""
pyfpspack - Python port of FPSPACK focal mechanism library.

A complete Python implementation of the FPSPACK Fortran library by
Gasperini & Vannucci (2003) for managing earthquake focal mechanism data.

Coordinate System (Aki-Richards):
    x = North, y = East, z = Down

Main Functions:
    Coordinate Conversions:
        pl2nd - Strike/dip/rake to normal and slip vectors
        nd2pl - Normal and slip vectors to strike/dip/rake
        ax2ca - Trend/plunge to Cartesian unit vector
        ca2ax - Cartesian unit vector to trend/plunge

    P/T/B Axes:
        pt2nd - P and T axes to normal and slip vectors
        nd2pt - Normal and slip vectors to P, T, B axes
        pl2pt - Strike/dip/rake to P, T, B axes
        pt2pl - P and T axes to both nodal planes

    Moment Tensors:
        nd2ar - Normal/slip to moment tensor (Aki-Richards)
        ar2pt - Moment tensor decomposition to P, T, B axes
        ar2ha - Convert between Aki-Richards and Harvard conventions
        pl2ar - Strike/dip/rake to moment tensor (Aki-Richards)
        pl2ha - Strike/dip/rake to moment tensor (Harvard)
        ar2plp - Full moment tensor decomposition (Aki-Richards)
        ha2plp - Full moment tensor decomposition (Harvard)

    Utilities:
        angles - Angle between two focal mechanisms (planes and slip)
        anglea - Angle between two axes
        hatens - Build Harvard tensor from 6 components
        tensha - Extract 6 components from Harvard tensor

    Convenience:
        sdr_to_moment_tensor - Strike/dip/rake to moment tensor
        moment_tensor_to_sdr - Moment tensor to strike/dip/rake

References:
    Gasperini P. and Vannucci G. (2003). FPSPACK: a package of FORTRAN
    subroutines to manage earthquake focal mechanism data. Computers &
    Geosciences, 29, 893-901. doi:10.1016/S0098-3004(03)00096-7

Example:
    >>> import pyfpspack as fp
    >>>
    >>> # Normal fault: strike=0, dip=45, rake=-90
    >>> axes = fp.pl2pt(0, 45, -90)
    >>> print(f"P axis: trend={axes.trend_p:.1f}, plunge={axes.plunge_p:.1f}")
    >>> print(f"T axis: trend={axes.trend_t:.1f}, plunge={axes.plunge_t:.1f}")
    >>>
    >>> # Get moment tensor
    >>> mt = fp.pl2ar(0, 45, -90)
    >>> print(mt)
"""

__version__ = "1.0.0"
__author__ = "Ali Comoglu"
__email__ = "comoglu@github.com"

from .core import (
    # Constants
    DTOR,
    ORTTOL,
    OVRTOL,
    TENTOL,
    # Exceptions
    FPSError,
    StrikeOutOfRange,
    DipOutOfRange,
    RakeOutOfRange,
    TrendOutOfRange,
    PlungeOutOfRange,
    NotPerpendicular,
    TensorNotSymmetric,
    # Data classes
    NodalPlane,
    PTBAxes,
    PTBAngles,
    MomentTensorDecomposition,
    FullDecomposition,
    # Basic routines
    pl2nd,
    nd2pl,
    ax2ca,
    ca2ax,
    pt2nd,
    nd2pt,
    ar2pt,
    nd2ar,
    ar2ha,
    # Composite routines
    nd2ha,
    pl2pl,
    pl2pt,
    pt2pl,
    ar2plp,
    ha2plp,
    pl2ar,
    pl2ha,
    pt2ar,
    pt2ha,
    # Utility routines
    angles,
    anglea,
    hatens,
    tensha,
    # Convenience functions
    sdr_to_moment_tensor,
    moment_tensor_to_sdr,
)

__all__ = [
    # Version
    "__version__",
    # Constants
    "DTOR",
    "ORTTOL",
    "OVRTOL",
    "TENTOL",
    # Exceptions
    "FPSError",
    "StrikeOutOfRange",
    "DipOutOfRange",
    "RakeOutOfRange",
    "TrendOutOfRange",
    "PlungeOutOfRange",
    "NotPerpendicular",
    "TensorNotSymmetric",
    # Data classes
    "NodalPlane",
    "PTBAxes",
    "PTBAngles",
    "MomentTensorDecomposition",
    "FullDecomposition",
    # Basic routines
    "pl2nd",
    "nd2pl",
    "ax2ca",
    "ca2ax",
    "pt2nd",
    "nd2pt",
    "ar2pt",
    "nd2ar",
    "ar2ha",
    # Composite routines
    "nd2ha",
    "pl2pl",
    "pl2pt",
    "pt2pl",
    "ar2plp",
    "ha2plp",
    "pl2ar",
    "pl2ha",
    "pt2ar",
    "pt2ha",
    # Utility routines
    "angles",
    "anglea",
    "hatens",
    "tensha",
    # Convenience functions
    "sdr_to_moment_tensor",
    "moment_tensor_to_sdr",
]
