# pyfpspack

**Python port of FPSPACK: Focal mechanism tools for seismology**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete Python implementation of the FPSPACK Fortran library by Gasperini & Vannucci (2003) for managing earthquake focal mechanism data.

## Features

- **Complete FPSPACK implementation**: All 29 original Fortran subroutines ported to Python
- **Modern Python API**: Dataclasses for structured returns, exceptions for error handling
- **Coordinate conversions**: Strike/Dip/Rake, Normal/Slip vectors, P/T/B axes, Moment tensors
- **Convention support**: Aki-Richards and Harvard CMT coordinate systems
- **Interactive GUI**: PyQt5-based application with real-time beachball visualization
- **Comprehensive test suite**: 53 tests covering all functions

## Installation

### From PyPI (when available)

```bash
pip install pyfpspack
```

### From source

```bash
git clone https://github.com/comoglu/pyfpspack.git
cd pyfpspack
pip install -e .
```

### With GUI support

```bash
pip install pyfpspack[gui]
```

### With all optional dependencies

```bash
pip install pyfpspack[all]
```

## Quick Start

```python
import pyfpspack as fp

# Define a normal fault: strike=0°, dip=45°, rake=-90°
strike, dip, rake = 0, 45, -90

# Get P, T, B axes
axes = fp.pl2pt(strike, dip, rake)
print(f"P axis: trend={axes.trend_p:.1f}°, plunge={axes.plunge_p:.1f}°")
print(f"T axis: trend={axes.trend_t:.1f}°, plunge={axes.plunge_t:.1f}°")
print(f"B axis: trend={axes.trend_b:.1f}°, plunge={axes.plunge_b:.1f}°")

# Get conjugate nodal plane
plane_b = fp.pl2pl(strike, dip, rake)
print(f"Conjugate plane: strike={plane_b.strike:.1f}°, dip={plane_b.dip:.1f}°, rake={plane_b.rake:.1f}°")

# Compute moment tensor (Aki-Richards convention)
mt = fp.pl2ar(strike, dip, rake)
print(f"Moment tensor:\n{mt}")

# Convert to Harvard CMT convention
mt_harvard = fp.ar2ha(mt)
print(f"Harvard CMT:\n{mt_harvard}")

# Full decomposition from moment tensor
decomp = fp.ar2plp(mt)
print(f"Scalar moment M0: {decomp.am0:.4f}")
print(f"CLVD component eta: {decomp.eta:.4f}")
```

## Web Demo

Try pyfpspack in your browser! Open `demo/index.html` for an interactive focal mechanism visualization:

- Strike/Dip/Rake sliders with preset fault types
- Real-time beachball rendering with equal-area projection
- P/T/B axes display
- Auxiliary plane calculation
- Moment tensor output

No installation required - just open the HTML file in any modern browser.

## GUI Application

Launch the interactive focal mechanism toolbox:

```bash
pyfpspack-gui
```

Or from Python:

```python
from pyfpspack.gui import main
main()
```

The GUI provides 4 tabs:
1. **Focal Mechanism**: Input strike/dip/rake, see all derived quantities
2. **Moment Tensor**: Input 6-component tensor, decompose to planes and axes
3. **P/T Axes**: Input P and T axes, compute nodal planes
4. **Angle Calculator**: Compare two focal mechanisms

## Coordinate System

pyfpspack uses the **Aki-Richards Cartesian coordinate system**:
- **x** = North
- **y** = East
- **z** = Down

### Parameter Ranges

| Parameter | Range | Description |
|-----------|-------|-------------|
| Strike | 0° – 360° | Clockwise from North |
| Dip | 0° – 90° | From horizontal, to the right of strike |
| Rake | -180° – +180° | On fault plane; 0°=left-lateral, ±180°=right-lateral, +90°=thrust, -90°=normal |
| Trend | 0° – 360° | Clockwise from North |
| Plunge | 0° – 90° | Downward from horizontal |

## API Reference

### Basic Conversions

| Function | Description |
|----------|-------------|
| `pl2nd(strike, dip, rake)` | Plane parameters → normal and slip vectors |
| `nd2pl(n, d)` | Normal and slip vectors → plane parameters |
| `ax2ca(trend, plunge)` | Trend/plunge → Cartesian unit vector |
| `ca2ax(v)` | Cartesian unit vector → trend/plunge |

### P/T/B Axes

| Function | Description |
|----------|-------------|
| `pl2pt(strike, dip, rake)` | Plane → P, T, B axes (angles) |
| `pt2pl(trend_p, plunge_p, trend_t, plunge_t)` | P and T axes → both nodal planes |
| `nd2pt(n, d)` | Normal/slip → P, T, B axes (vectors) |
| `pt2nd(p, t)` | P and T axes → normal/slip vectors |

### Moment Tensors

| Function | Description |
|----------|-------------|
| `pl2ar(strike, dip, rake)` | Plane → moment tensor (Aki-Richards) |
| `pl2ha(strike, dip, rake)` | Plane → moment tensor (Harvard) |
| `ar2plp(am)` | Moment tensor (AR) → full decomposition |
| `ha2plp(am)` | Moment tensor (Harvard) → full decomposition |
| `ar2ha(am)` | Convert AR ↔ Harvard (involution) |

### Utilities

| Function | Description |
|----------|-------------|
| `angles(s1, d1, r1, s2, d2, r2)` | Angle between two mechanisms (planes and slip) |
| `anglea(t1, p1, t2, p2)` | Angle between two axes |
| `hatens(rr, ss, ee, rs, re, se)` | Build Harvard tensor from 6 components |
| `tensha(am)` | Extract 6 components from Harvard tensor |

## Original Fortran Code

The `original/` directory contains:
- `FPSPACK.FOR` - Original Fortran source code
- `FPSPACK_routines.pdf` - Paper describing the library

## Citation

If you use pyfpspack in your research, please cite:

```bibtex
@article{gasperini2003fpspack,
  title={FPSPACK: a package of FORTRAN subroutines to manage earthquake focal mechanism data},
  author={Gasperini, P. and Vannucci, G.},
  journal={Computers \& Geosciences},
  volume={29},
  number={7},
  pages={893--901},
  year={2003},
  publisher={Elsevier},
  doi={10.1016/S0098-3004(03)00096-7}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- **P. Gasperini and G. Vannucci** for the original FPSPACK Fortran library
- The seismology community for continued interest in focal mechanism analysis tools
