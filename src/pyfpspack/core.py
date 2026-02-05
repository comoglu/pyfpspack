"""
FPSPACK - Python implementation of the Fortran FPSPACK library.

A package of routines to manage earthquake focal mechanism data.
Original Fortran code by Gasperini P. and Vannucci G.

All routines use the Aki-Richards Cartesian coordinate system:
  x = North, y = East, z = Down

Reference:
  Gasperini P. and Vannucci G., FPSPACK: a package of simple Fortran
  subroutines to manage earthquake focal mechanism data.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import warnings


# ---------------------------------------------------------------------------
# Constants (equivalent to fpsset / fpscom common block)
# ---------------------------------------------------------------------------
DTOR = np.radians(1.0)  # 0.017453292519943296

# Input range limits
STRIKE_MIN = -360.0
STRIKE_MAX = 360.0
DIP_MIN = 0.0
DIP_MAX = 90.0
RAKE_MIN = -360.0
RAKE_MAX = 360.0
TREND_MIN = -360.0
TREND_MAX = 360.0
PLUNGE_MIN = 0.0
PLUNGE_MAX = 90.0

# Tolerances
ORTTOL = 2.0       # orthogonality tolerance (degrees)
OVRTOL = 0.001     # dip overtaking tolerance
TENTOL = 0.0001    # moment tensor symmetry tolerance


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------
class FPSError(Exception):
    """Base exception for FPSPACK errors."""
    pass


class StrikeOutOfRange(FPSError):
    pass


class DipOutOfRange(FPSError):
    pass


class RakeOutOfRange(FPSError):
    pass


class TrendOutOfRange(FPSError):
    pass


class PlungeOutOfRange(FPSError):
    pass


class NotPerpendicular(FPSError):
    pass


class TensorNotSymmetric(FPSError):
    pass


# ---------------------------------------------------------------------------
# Data classes for structured returns
# ---------------------------------------------------------------------------
@dataclass
class NodalPlane:
    """Strike, dip, rake (and optionally dip direction) of a nodal plane."""
    strike: float
    dip: float
    rake: float
    dipdir: float = 0.0


@dataclass
class PTBAxes:
    """P, T, and B axis vectors in Cartesian coordinates."""
    p: np.ndarray   # (px, py, pz)
    t: np.ndarray   # (tx, ty, tz)
    b: np.ndarray   # (bx, by, bz)


@dataclass
class PTBAngles:
    """P, T, and B axis trend and plunge angles."""
    trend_p: float
    plunge_p: float
    trend_t: float
    plunge_t: float
    trend_b: float
    plunge_b: float


@dataclass
class MomentTensorDecomposition:
    """Full decomposition of a moment tensor."""
    am0: float       # scalar seismic moment of principal double couple
    am1: float       # scalar seismic moment of secondary double couple
    e: float         # isotropic component (trace / 3)
    am0b: float      # scalar seismic moment of best double couple
    eta: float       # percentage of CLVD remainder
    p: np.ndarray    # P axis Cartesian components
    t: np.ndarray    # T axis Cartesian components
    b: np.ndarray    # B axis Cartesian components


@dataclass
class FullDecomposition:
    """Complete decomposition: planes, axes, and tensor properties."""
    am0: float
    am1: float
    e: float
    am0b: float
    eta: float
    plane_a: NodalPlane
    plane_b: NodalPlane
    axes: PTBAngles


# ---------------------------------------------------------------------------
# Utility routines
# ---------------------------------------------------------------------------
def _normalize(v: np.ndarray) -> Tuple[float, np.ndarray]:
    """Compute Euclidean norm and unit vector.

    Parameters
    ----------
    v : array_like, shape (3,)

    Returns
    -------
    norm : float
    unit : ndarray, shape (3,)
    """
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n == 0.0:
        return 0.0, v.copy()
    return n, v / n


def _cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cross product of two 3-vectors (equivalent to Fortran vecpro)."""
    return np.cross(a, b)


def _invert(v: np.ndarray) -> np.ndarray:
    """Negate a vector."""
    return -v


def _angle_between(a: np.ndarray, b: np.ndarray) -> float:
    """Angle in degrees between two vectors.

    Parameters
    ----------
    a, b : array_like, shape (3,)

    Returns
    -------
    angle : float
        Angle in degrees [0, 180].
    """
    _, ua = _normalize(a)
    _, ub = _normalize(b)
    dot = np.clip(np.dot(ua, ub), -1.0, 1.0)
    return np.degrees(np.arccos(dot))


def _check_perpendicular(a: np.ndarray, b: np.ndarray, routine: str = ""):
    """Raise if two vectors are not approximately perpendicular."""
    ang = _angle_between(a, b)
    if abs(ang - 90.0) > ORTTOL:
        raise NotPerpendicular(
            f"{routine}: input vectors not perpendicular, angle={ang:.7f}"
        )


def _check_symmetric(am: np.ndarray, routine: str = ""):
    """Raise if a 3x3 tensor is not symmetric within tolerance."""
    pairs = [(0, 1), (0, 2), (1, 2)]
    for i, j in pairs:
        if abs(am[i, j] - am[j, i]) > TENTOL:
            raise TensorNotSymmetric(
                f"{routine}: input tensor not symmetrical, "
                f"m({i+1},{j+1})={am[i,j]}, m({j+1},{i+1})={am[j,i]}"
            )


def _validate_strike(strike: float):
    if strike < STRIKE_MIN or strike > STRIKE_MAX:
        raise StrikeOutOfRange(f"Strike angle {strike} out of range [{STRIKE_MIN}, {STRIKE_MAX}]")


def _validate_dip(dip: float) -> float:
    """Validate dip, applying overtaking tolerance if needed. Returns corrected dip."""
    if dip < DIP_MIN or dip > DIP_MAX:
        if dip < DIP_MAX and dip > -OVRTOL:
            return DIP_MIN
        elif dip > DIP_MIN and (dip - DIP_MAX) < OVRTOL:
            return DIP_MAX
        else:
            raise DipOutOfRange(f"Dip angle {dip} out of range [{DIP_MIN}, {DIP_MAX}]")
    return dip


def _validate_rake(rake: float):
    if rake < RAKE_MIN or rake > RAKE_MAX:
        raise RakeOutOfRange(f"Rake angle {rake} out of range [{RAKE_MIN}, {RAKE_MAX}]")


def _validate_trend(trend: float):
    if trend < TREND_MIN or trend > TREND_MAX:
        raise TrendOutOfRange(f"Trend angle {trend} out of range [{TREND_MIN}, {TREND_MAX}]")


def _validate_plunge(plunge: float) -> float:
    """Validate plunge, applying overtaking tolerance. Returns corrected plunge."""
    if plunge < PLUNGE_MIN or plunge > PLUNGE_MAX:
        if plunge < PLUNGE_MAX and plunge > -OVRTOL:
            return PLUNGE_MIN
        elif plunge > PLUNGE_MIN and (plunge - PLUNGE_MAX) < OVRTOL:
            return PLUNGE_MAX
        else:
            raise PlungeOutOfRange(f"Plunge angle {plunge} out of range [{PLUNGE_MIN}, {PLUNGE_MAX}]")
    return plunge


# ---------------------------------------------------------------------------
# Eigenvalue decomposition (replaces Fortran avec + JACOBI/EVCSF)
# ---------------------------------------------------------------------------
def _avec(am: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute eigenvalues and eigenvectors of a symmetric 3x3 matrix.

    Returns eigenvalues and eigenvectors sorted by descending absolute value.

    Parameters
    ----------
    am : ndarray, shape (3, 3)

    Returns
    -------
    eigenvalues : ndarray, shape (3,)
    eigenvectors : ndarray, shape (3, 3)
        Column j is the eigenvector for eigenvalue j.
    """
    vals, vecs = np.linalg.eigh(am)
    # Sort by descending absolute value of eigenvalues
    idx = np.argsort(-np.abs(vals))
    vals = vals[idx]
    vecs = vecs[:, idx]
    return vals, vecs


# ---------------------------------------------------------------------------
# BASIC ROUTINES
# ---------------------------------------------------------------------------
def pl2nd(strike: float, dip: float, rake: float
          ) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Cartesian components of outward normal and slip vectors
    from strike, dip and rake.

    Parameters
    ----------
    strike : float
        Strike angle in degrees.
    dip : float
        Dip angle in degrees.
    rake : float
        Rake angle in degrees.

    Returns
    -------
    n : ndarray, shape (3,)
        Fault plane outward normal vector (Aki-Richards).
    d : ndarray, shape (3,)
        Slip vector (Aki-Richards).
    """
    _validate_strike(strike)
    dip = _validate_dip(dip)
    _validate_rake(rake)

    wstrik = np.radians(strike)
    wdip = np.radians(dip)
    wrake = np.radians(rake)

    anx = -np.sin(wdip) * np.sin(wstrik)
    any_ = np.sin(wdip) * np.cos(wstrik)
    anz = -np.cos(wdip)

    dx = np.cos(wrake) * np.cos(wstrik) + np.cos(wdip) * np.sin(wrake) * np.sin(wstrik)
    dy = np.cos(wrake) * np.sin(wstrik) - np.cos(wdip) * np.sin(wrake) * np.cos(wstrik)
    dz = -np.sin(wdip) * np.sin(wrake)

    return np.array([anx, any_, anz]), np.array([dx, dy, dz])


def nd2pl(n: np.ndarray, d: np.ndarray) -> NodalPlane:
    """Compute strike, dip, rake and dip direction from Cartesian
    components of the outward normal and slip vectors.

    Parameters
    ----------
    n : array_like, shape (3,)
        Fault plane outward normal vector.
    d : array_like, shape (3,)
        Slip vector.

    Returns
    -------
    NodalPlane
        strike, dip, rake, dipdir in degrees.
    """
    n = np.asarray(n, dtype=float)
    d = np.asarray(d, dtype=float)

    _check_perpendicular(n, d, "ND2PL")

    _, anx_arr = _normalize(n)
    _, dx_arr = _normalize(d)

    anx, any_, anz = anx_arr
    dx, dy, dz = dx_arr

    if anz > 0.0:
        anx, any_, anz = -anx, -any_, -anz
        dx, dy, dz = -dx, -dy, -dz

    if anz == -1.0:
        wdelta = 0.0
        wphi = 0.0
        walam = np.arctan2(-dy, dx)
    else:
        wdelta = np.arccos(-anz)
        wphi = np.arctan2(-anx, any_)
        walam = np.arctan2(-dz / np.sin(wdelta),
                           dx * np.cos(wphi) + dy * np.sin(wphi))

    phi = np.degrees(wphi)
    delta = np.degrees(wdelta)
    alam = np.degrees(walam)
    phi = phi % 360.0
    dipdir = (phi + 90.0) % 360.0

    return NodalPlane(strike=phi, dip=delta, rake=alam, dipdir=dipdir)


def ax2ca(trend: float, plunge: float) -> np.ndarray:
    """Compute Cartesian components from trend and plunge.

    Parameters
    ----------
    trend : float
        Clockwise angle from North in degrees.
    plunge : float
        Inclination angle in degrees.

    Returns
    -------
    ndarray, shape (3,)
        Axis direction downward versor (Aki-Richards).
    """
    _validate_trend(trend)
    plunge = _validate_plunge(plunge)

    tr = np.radians(trend)
    pl = np.radians(plunge)

    ax = np.cos(pl) * np.cos(tr)
    ay = np.cos(pl) * np.sin(tr)
    az = np.sin(pl)

    return np.array([ax, ay, az])


def ca2ax(v: np.ndarray) -> Tuple[float, float]:
    """Compute trend and plunge from Cartesian components.

    Parameters
    ----------
    v : array_like, shape (3,)
        Axis direction vector (Aki-Richards).

    Returns
    -------
    trend : float
        Clockwise angle from North in degrees [0, 360).
    plunge : float
        Inclination angle in degrees [0, 90].
    """
    v = np.asarray(v, dtype=float)
    _, uv = _normalize(v)
    ax, ay, az = uv

    if az < 0.0:
        ax, ay, az = -ax, -ay, -az

    if ay != 0.0 or ax != 0.0:
        trend = np.degrees(np.arctan2(ay, ax))
    else:
        trend = 0.0

    trend = trend % 360.0
    plunge = np.degrees(np.arcsin(az))

    return trend, plunge


def pt2nd(p: np.ndarray, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute outward normal and slip vectors from P and T axis vectors.

    Parameters
    ----------
    p : array_like, shape (3,)
        P (maximum dilatation) axis vector.
    t : array_like, shape (3,)
        T (maximum tension) axis vector.

    Returns
    -------
    n : ndarray, shape (3,)
        Fault plane outward normal versor.
    d : ndarray, shape (3,)
        Slip versor.
    """
    p = np.asarray(p, dtype=float)
    t = np.asarray(t, dtype=float)

    _check_perpendicular(p, t, "PT2ND")

    _, px = _normalize(p)
    if px[2] < 0.0:
        px = -px

    _, tx = _normalize(t)
    if tx[2] < 0.0:
        tx = -tx

    n = tx + px
    _, n = _normalize(n)

    d = tx - px
    _, d = _normalize(d)

    if n[2] > 0.0:
        n = -n
        d = -d

    return n, d


def nd2pt(n: np.ndarray, d: np.ndarray) -> PTBAxes:
    """Compute P, T, and B axis Cartesian components from outward normal
    and slip vectors.

    Parameters
    ----------
    n : array_like, shape (3,)
        Fault plane outward normal vector.
    d : array_like, shape (3,)
        Slip vector.

    Returns
    -------
    PTBAxes
        P, T, and B axis vectors (downward convention).
    """
    n = np.asarray(n, dtype=float)
    d = np.asarray(d, dtype=float)

    _, nu = _normalize(n)
    _, du = _normalize(d)

    _check_perpendicular(nu, du, "ND2PT")

    p = nu - du
    _, p = _normalize(p)
    if p[2] < 0.0:
        p = -p

    t = nu + du
    _, t = _normalize(t)
    if t[2] < 0.0:
        t = -t

    b = _cross(p, t)
    if b[2] < 0.0:
        b = -b

    return PTBAxes(p=p, t=t, b=b)


def ar2pt(am: np.ndarray) -> MomentTensorDecomposition:
    """Compute deformation axes (P, T, B) from moment tensor
    (Aki & Richards convention).

    Parameters
    ----------
    am : ndarray, shape (3, 3)
        Seismic moment tensor (Aki-Richards).

    Returns
    -------
    MomentTensorDecomposition
    """
    am = np.asarray(am, dtype=float)
    _check_symmetric(am, "AR2PT")

    vals, vecs = _avec(am)

    # Isotropic component
    e = (vals[0] + vals[1] + vals[2]) / 3.0

    # Deviatoric eigenvalues
    dvals = vals - e

    # Re-sort deviatoric by descending absolute value
    idx = np.argsort(-np.abs(dvals))
    dvals = dvals[idx]
    vecs = vecs[:, idx]

    am0 = dvals[0]
    eta = -dvals[2] / (2.0 * am0) if am0 != 0.0 else 0.0
    am1 = abs(dvals[2])
    am0b = (abs(dvals[0]) + abs(dvals[1])) / 2.0

    if am0 < 0.0:
        am0 = -am0
        t = vecs[:, 1].copy()
        p = vecs[:, 0].copy()
    else:
        t = vecs[:, 0].copy()
        p = vecs[:, 1].copy()

    b = vecs[:, 2].copy()

    return MomentTensorDecomposition(
        am0=am0, am1=am1, e=e, am0b=am0b, eta=eta,
        p=p, t=t, b=b
    )


def nd2ar(n: np.ndarray, d: np.ndarray, am0: float = 1.0) -> np.ndarray:
    """Compute moment tensor (Aki & Richards convention) from outward
    normal and slip vectors.

    Parameters
    ----------
    n : array_like, shape (3,)
        Fault plane outward normal vector.
    d : array_like, shape (3,)
        Slip vector.
    am0 : float, optional
        Scalar seismic moment. Default 1.0.

    Returns
    -------
    ndarray, shape (3, 3)
        Seismic moment tensor (Aki-Richards).
    """
    n = np.asarray(n, dtype=float)
    d = np.asarray(d, dtype=float)

    _check_perpendicular(n, d, "ND2AR")

    _, nu = _normalize(n)
    _, du = _normalize(d)

    aam0 = am0 if am0 != 0.0 else 1.0

    am = np.zeros((3, 3))
    # M_ij = am0 * (d_i * n_j + d_j * n_i)
    for i in range(3):
        for j in range(3):
            am[i, j] = aam0 * (du[i] * nu[j] + du[j] * nu[i])

    return am


def ar2ha(am: np.ndarray) -> np.ndarray:
    """Transform moment tensor from Aki-Richards to Harvard CMT convention
    (and vice versa -- the transform is its own inverse).

    Parameters
    ----------
    am : ndarray, shape (3, 3)
        Input moment tensor.

    Returns
    -------
    ndarray, shape (3, 3)
        Output moment tensor in the other convention.
    """
    am = np.asarray(am, dtype=float)
    _check_symmetric(am, "AR2HA")

    amo = np.zeros((3, 3))
    amo[0, 0] = am[0, 0]
    amo[0, 1] = -am[0, 1]
    amo[0, 2] = am[0, 2]
    amo[1, 0] = -am[1, 0]
    amo[1, 1] = am[1, 1]
    amo[1, 2] = -am[1, 2]
    amo[2, 0] = am[2, 0]
    amo[2, 1] = -am[2, 1]
    amo[2, 2] = am[2, 2]

    return amo


# ---------------------------------------------------------------------------
# COMPOSITE ROUTINES
# ---------------------------------------------------------------------------
def nd2ha(n: np.ndarray, d: np.ndarray, am0: float = 1.0) -> np.ndarray:
    """Compute moment tensor (Harvard CMT convention) from outward normal
    and slip vectors.

    Parameters
    ----------
    n, d : array_like, shape (3,)
    am0 : float

    Returns
    -------
    ndarray, shape (3, 3)
    """
    am = nd2ar(n, d, am0)
    return ar2ha(am)


def pl2pl(strike_a: float, dip_a: float, rake_a: float) -> NodalPlane:
    """Compute the second nodal plane from the first.

    Parameters
    ----------
    strike_a, dip_a, rake_a : float
        Strike, dip, rake of the first nodal plane in degrees.

    Returns
    -------
    NodalPlane
        Parameters of the second nodal plane.
    """
    n, d = pl2nd(strike_a, dip_a, rake_a)
    return nd2pl(d, n)


def pl2pt(strike: float, dip: float, rake: float) -> PTBAngles:
    """Compute trend and plunge of P, T and B axes from strike, dip, rake.

    Parameters
    ----------
    strike, dip, rake : float
        Nodal plane parameters in degrees.

    Returns
    -------
    PTBAngles
    """
    n, d = pl2nd(strike, dip, rake)
    axes = nd2pt(d, n)

    trend_p, plunge_p = ca2ax(axes.p)
    trend_t, plunge_t = ca2ax(axes.t)
    trend_b, plunge_b = ca2ax(axes.b)

    return PTBAngles(
        trend_p=trend_p, plunge_p=plunge_p,
        trend_t=trend_t, plunge_t=plunge_t,
        trend_b=trend_b, plunge_b=plunge_b,
    )


def pt2pl(trend_p: float, plunge_p: float,
          trend_t: float, plunge_t: float
          ) -> Tuple[NodalPlane, NodalPlane]:
    """Compute both nodal planes from P and T axes.

    Parameters
    ----------
    trend_p, plunge_p : float
        P axis trend and plunge in degrees.
    trend_t, plunge_t : float
        T axis trend and plunge in degrees.

    Returns
    -------
    plane_a, plane_b : NodalPlane
    """
    pv = ax2ca(trend_p, plunge_p)
    tv = ax2ca(trend_t, plunge_t)
    n, d = pt2nd(pv, tv)
    plane_a = nd2pl(n, d)
    plane_b = nd2pl(d, n)
    return plane_a, plane_b


def ar2plp(am: np.ndarray) -> FullDecomposition:
    """Compute planes and axes of principal double couple from moment
    tensor (Aki & Richards convention).

    Parameters
    ----------
    am : ndarray, shape (3, 3)

    Returns
    -------
    FullDecomposition
    """
    dec = ar2pt(am)

    trend_p, plunge_p = ca2ax(dec.p)
    trend_t, plunge_t = ca2ax(dec.t)
    trend_b, plunge_b = ca2ax(dec.b)

    n, d = pt2nd(dec.p, dec.t)
    plane_a = nd2pl(n, d)
    plane_b = nd2pl(d, n)

    return FullDecomposition(
        am0=dec.am0, am1=dec.am1, e=dec.e, am0b=dec.am0b, eta=dec.eta,
        plane_a=plane_a, plane_b=plane_b,
        axes=PTBAngles(
            trend_p=trend_p, plunge_p=plunge_p,
            trend_t=trend_t, plunge_t=plunge_t,
            trend_b=trend_b, plunge_b=plunge_b,
        ),
    )


def ha2plp(am: np.ndarray) -> FullDecomposition:
    """Compute planes and axes of principal double couple from moment
    tensor (Harvard CMT convention).

    Parameters
    ----------
    am : ndarray, shape (3, 3)

    Returns
    -------
    FullDecomposition
    """
    ama = ar2ha(am)  # Harvard->AR (transform is its own inverse)
    return ar2plp(ama)


def pl2ar(strike: float, dip: float, rake: float,
          am0: float = 1.0) -> np.ndarray:
    """Compute moment tensor (Aki & Richards) from strike, dip, rake.

    Parameters
    ----------
    strike, dip, rake : float
        Nodal plane parameters in degrees.
    am0 : float
        Scalar seismic moment.

    Returns
    -------
    ndarray, shape (3, 3)
    """
    n, d = pl2nd(strike, dip, rake)
    return nd2ar(n, d, am0)


def pl2ha(strike: float, dip: float, rake: float,
          am0: float = 1.0) -> np.ndarray:
    """Compute moment tensor (Harvard CMT) from strike, dip, rake.

    Parameters
    ----------
    strike, dip, rake : float
    am0 : float

    Returns
    -------
    ndarray, shape (3, 3)
    """
    am = pl2ar(strike, dip, rake, am0)
    return ar2ha(am)


def pt2ar(trend_p: float, plunge_p: float,
          trend_t: float, plunge_t: float,
          am0: float = 1.0) -> np.ndarray:
    """Compute moment tensor (Aki & Richards) from P and T axes.

    Parameters
    ----------
    trend_p, plunge_p, trend_t, plunge_t : float
        P and T axis angles in degrees.
    am0 : float
        Scalar seismic moment.

    Returns
    -------
    ndarray, shape (3, 3)
    """
    pv = ax2ca(trend_p, plunge_p)
    tv = ax2ca(trend_t, plunge_t)
    n, d = pt2nd(pv, tv)
    return nd2ar(n, d, am0)


def pt2ha(trend_p: float, plunge_p: float,
          trend_t: float, plunge_t: float,
          am0: float = 1.0) -> np.ndarray:
    """Compute moment tensor (Harvard CMT) from P and T axes.

    Parameters
    ----------
    trend_p, plunge_p, trend_t, plunge_t : float
    am0 : float

    Returns
    -------
    ndarray, shape (3, 3)
    """
    am = pt2ar(trend_p, plunge_p, trend_t, plunge_t, am0)
    return ar2ha(am)


def angles(strike_a: float, dip_a: float, rake_a: float,
           strike_b: float, dip_b: float, rake_b: float
           ) -> Tuple[float, float]:
    """Compute the angle between two nodal planes and between their
    slip directions.

    Parameters
    ----------
    strike_a, dip_a, rake_a : float
        First nodal plane.
    strike_b, dip_b, rake_b : float
        Second nodal plane.

    Returns
    -------
    angle_planes : float
        Angle in degrees between the planes.
    angle_slip : float
        Angle in degrees between slip directions.
    """
    na, da = pl2nd(strike_a, dip_a, rake_a)
    nb, db = pl2nd(strike_b, dip_b, rake_b)
    return _angle_between(na, nb), _angle_between(da, db)


def anglea(trend_a: float, plunge_a: float,
           trend_b: float, plunge_b: float) -> float:
    """Compute the angle between two axes given as trend/plunge.

    Parameters
    ----------
    trend_a, plunge_a : float
        First axis.
    trend_b, plunge_b : float
        Second axis.

    Returns
    -------
    float
        Angle in degrees.
    """
    a = ax2ca(trend_a, plunge_a)
    b = ax2ca(trend_b, plunge_b)
    return _angle_between(a, b)


def hatens(amrr: float, amss: float, amee: float,
           amrs: float, amre: float, amse: float) -> np.ndarray:
    """Build the Harvard CMT tensor from 6 independent components.

    Parameters
    ----------
    amrr, amss, amee, amrs, amre, amse : float
        Harvard CMT tensor components.

    Returns
    -------
    ndarray, shape (3, 3)
    """
    am = np.array([
        [amss, amse, amrs],
        [amse, amee, amre],
        [amrs, amre, amrr],
    ])
    return am


def tensha(am: np.ndarray) -> Tuple[float, float, float, float, float, float]:
    """Extract 6 independent Harvard CMT components from a tensor.

    Parameters
    ----------
    am : ndarray, shape (3, 3)

    Returns
    -------
    amrr, amss, amee, amrs, amre, amse : float
    """
    am = np.asarray(am, dtype=float)
    amrr = am[2, 2]
    amss = am[0, 0]
    amee = am[1, 1]
    amrs = am[2, 0]
    amre = am[2, 1]
    amse = am[0, 1]
    return amrr, amss, amee, amrs, amre, amse


# ---------------------------------------------------------------------------
# Convenience / high-level functions (extensions beyond original FPSPACK)
# ---------------------------------------------------------------------------
def sdr_to_moment_tensor(strike: float, dip: float, rake: float,
                         am0: float = 1.0,
                         convention: str = "aki-richards") -> np.ndarray:
    """Convert strike/dip/rake to moment tensor.

    Parameters
    ----------
    strike, dip, rake : float
        Fault plane parameters in degrees.
    am0 : float
        Scalar seismic moment.
    convention : str
        'aki-richards' or 'harvard'.

    Returns
    -------
    ndarray, shape (3, 3)
    """
    if convention.lower() in ("aki-richards", "ar"):
        return pl2ar(strike, dip, rake, am0)
    elif convention.lower() in ("harvard", "cmt", "ha"):
        return pl2ha(strike, dip, rake, am0)
    else:
        raise ValueError(f"Unknown convention: {convention}")


def moment_tensor_to_sdr(am: np.ndarray,
                         convention: str = "aki-richards") -> FullDecomposition:
    """Decompose a moment tensor into nodal planes and principal axes.

    Parameters
    ----------
    am : ndarray, shape (3, 3)
    convention : str
        'aki-richards' or 'harvard'.

    Returns
    -------
    FullDecomposition
    """
    if convention.lower() in ("aki-richards", "ar"):
        return ar2plp(am)
    elif convention.lower() in ("harvard", "cmt", "ha"):
        return ha2plp(am)
    else:
        raise ValueError(f"Unknown convention: {convention}")
