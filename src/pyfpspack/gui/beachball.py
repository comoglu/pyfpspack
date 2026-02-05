"""Beachball visualization using lower-hemisphere equal-area projection."""

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.patches import Circle

from .. import core as pyfpspack
from .themes import ThemeColors


def _stereo_project(trend_deg, plunge_deg):
    """Equal-area (Lambert) lower-hemisphere projection.

    Returns (x, y) where North is +y, East is +x.
    """
    r = np.sqrt(2.0) * np.cos(np.radians(45.0 + plunge_deg / 2.0))
    x = r * np.sin(np.radians(trend_deg))
    y = r * np.cos(np.radians(trend_deg))
    return x, y


class BeachballCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas for lower-hemisphere equal-area beachball plots."""

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.setParent(parent)
        self.colors = ThemeColors(dark=True)
        self.figure.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        self._setup_axes()
        self.clear()

    def set_theme(self, dark=True):
        self.colors.set_dark(dark)
        self.figure.set_facecolor(self.colors.bg)

    def _setup_axes(self):
        self.ax.set_xlim(-1.25, 1.25)
        self.ax.set_ylim(-1.25, 1.25)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.figure.set_facecolor(self.colors.bg)
        self.ax.set_facecolor(self.colors.bg)

    def clear(self):
        self.ax.cla()
        self._setup_axes()
        circle = Circle((0, 0), 1.0, fill=False,
                         edgecolor=self.colors.circle, linewidth=2, zorder=10)
        self.ax.add_patch(circle)
        self._draw_compass()
        self.draw()

    def draw_beachball(self, strike, dip, rake, axes_angles=None):
        """Full beachball redraw from strike/dip/rake."""
        self.ax.cla()
        self._setup_axes()

        try:
            n, d = pyfpspack.pl2nd(strike, dip, rake)
        except pyfpspack.FPSError:
            self.clear()
            return

        # 1. Fill compressional/dilatational quadrants
        self._fill_quadrants(n, d)

        # 2. Outer circle
        circle = Circle((0, 0), 1.0, fill=False,
                         edgecolor=self.colors.circle, linewidth=2, zorder=10)
        self.ax.add_patch(circle)

        # 3. Great circles for both nodal planes
        try:
            plane_b = pyfpspack.pl2pl(strike, dip, rake)
            self._draw_great_circle(strike, dip, ls='-', zorder=11)
            self._draw_great_circle(plane_b.strike, plane_b.dip, ls='--', zorder=11)
        except pyfpspack.FPSError:
            pass

        # 4. P, T, B markers
        if axes_angles is not None:
            self._plot_axis(axes_angles.trend_p, axes_angles.plunge_p,
                            'o', self.colors.p_color, 'P', 12)
            self._plot_axis(axes_angles.trend_t, axes_angles.plunge_t,
                            '^', self.colors.t_color, 'T', 12)
            self._plot_axis(axes_angles.trend_b, axes_angles.plunge_b,
                            's', self.colors.b_color, 'B', 12)
            self.ax.legend(loc='lower right', fontsize=7, framealpha=0.7,
                           facecolor=self.colors.bg, edgecolor=self.colors.grid,
                           labelcolor=self.colors.fg)

        # 5. Compass labels
        self._draw_compass()
        self.draw()

    def draw_from_planes(self, plane_a, plane_b, axes_angles=None):
        """Draw beachball given two nodal planes (used by tensor/PT tabs)."""
        self.draw_beachball(plane_a.strike, plane_a.dip, plane_a.rake,
                            axes_angles)

    def _fill_quadrants(self, n, d):
        res = 250
        x = np.linspace(-1, 1, res)
        y = np.linspace(-1, 1, res)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X ** 2 + Y ** 2)

        polarity = np.full_like(R, np.nan)
        mask = R <= 1.0
        r_v = R[mask]
        x_v = X[mask]
        y_v = Y[mask]

        # Inverse equal-area projection
        plunge_rad = np.pi / 2.0 - 2.0 * np.arcsin(
            np.clip(r_v / np.sqrt(2), 0, 1))
        trend_rad = np.arctan2(x_v, y_v)

        cos_pl = np.cos(plunge_rad)
        dx = cos_pl * np.cos(trend_rad)
        dy = cos_pl * np.sin(trend_rad)
        dz = np.sin(plunge_rad)

        dot_n = dx * n[0] + dy * n[1] + dz * n[2]
        dot_d = dx * d[0] + dy * d[1] + dz * d[2]
        polarity[mask] = dot_n * dot_d

        cs = self.ax.contourf(X, Y, polarity, levels=[-1e10, 0, 1e10],
                              colors=[self.colors.dilatational,
                                      self.colors.compressional])

        clip_circle = Circle((0, 0), 1.0, transform=self.ax.transData)
        # matplotlib 3.8+ removed .collections; contour set is its own artist
        if hasattr(cs, 'collections'):
            for coll in cs.collections:
                coll.set_clip_path(clip_circle)
        else:
            cs.set_clip_path(clip_circle)

    def _draw_great_circle(self, strike, dip, ls='-', zorder=5):
        strike_rad = np.radians(strike)
        dip_rad = np.radians(dip)

        u = np.array([np.cos(strike_rad), np.sin(strike_rad), 0.0])
        v = np.array([-np.sin(strike_rad) * np.cos(dip_rad),
                       np.cos(strike_rad) * np.cos(dip_rad),
                       np.sin(dip_rad)])

        angles = np.linspace(0, 2 * np.pi, 361)
        pts = np.zeros((len(angles), 2))

        for i, a in enumerate(angles):
            pt = np.cos(a) * u + np.sin(a) * v
            if pt[2] < 0:
                pt = -pt
            trend, plunge = pyfpspack.ca2ax(pt)
            pts[i] = _stereo_project(trend, plunge)

        # Split at discontinuities
        diffs = np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1))
        jumps = np.where(diffs > 0.3)[0] + 1
        segments = np.split(np.arange(len(pts)), jumps)

        for seg in segments:
            if len(seg) > 1:
                self.ax.plot(pts[seg, 0], pts[seg, 1],
                             color=self.colors.great_circle,
                             linewidth=1.8, linestyle=ls, zorder=zorder)

    def _plot_axis(self, trend, plunge, marker, color, label, zorder):
        x, y = _stereo_project(trend, plunge)
        self.ax.plot(x, y, marker=marker, color=color, markersize=11,
                     markeredgecolor='white', markeredgewidth=1.2,
                     label=label, zorder=zorder, linestyle='None')

    def _draw_compass(self):
        off = 1.12
        for label, (x, y) in [('N', (0, off)), ('E', (off, 0)),
                                ('S', (0, -off)), ('W', (-off, 0))]:
            self.ax.text(x, y, label, ha='center', va='center',
                         fontsize=11, fontweight='bold',
                         color=self.colors.compass)


class DualBeachballCanvas(FigureCanvasQTAgg):
    """Two beachballs side by side for comparison."""

    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        self.ax1 = self.figure.add_subplot(121)
        self.ax2 = self.figure.add_subplot(122)
        self.setParent(parent)
        self.colors = ThemeColors(dark=True)
        self.figure.subplots_adjust(left=0.02, right=0.98, top=0.92,
                                     bottom=0.02, wspace=0.15)
        self.clear()

    def set_theme(self, dark=True):
        self.colors.set_dark(dark)
        self.figure.set_facecolor(self.colors.bg)

    def _setup_ax(self, ax, title=""):
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.25)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_facecolor(self.colors.bg)
        if title:
            ax.set_title(title, color=self.colors.fg, fontsize=11,
                         fontweight='bold', pad=4)

    def clear(self):
        self.figure.set_facecolor(self.colors.bg)
        for ax in (self.ax1, self.ax2):
            ax.cla()
            self._setup_ax(ax)
            ax.add_patch(Circle((0, 0), 1.0, fill=False,
                                edgecolor=self.colors.circle, linewidth=2))
            self._draw_compass(ax)
        self.draw()

    def draw_both(self, s1, d1, r1, axes1, s2, d2, r2, axes2):
        """Draw two beachballs side by side."""
        self.figure.set_facecolor(self.colors.bg)
        for ax, s, d, r, axes_ang, title in [
            (self.ax1, s1, d1, r1, axes1, "Mechanism A"),
            (self.ax2, s2, d2, r2, axes2, "Mechanism B"),
        ]:
            ax.cla()
            self._setup_ax(ax, title)
            try:
                n, dv = pyfpspack.pl2nd(s, d, r)
                self._fill_quadrants(ax, n, dv)
                circle = Circle((0, 0), 1.0, fill=False,
                                edgecolor=self.colors.circle, linewidth=2,
                                zorder=10)
                ax.add_patch(circle)
                plane_b = pyfpspack.pl2pl(s, d, r)
                self._draw_gc(ax, s, d, '-')
                self._draw_gc(ax, plane_b.strike, plane_b.dip, '--')
                if axes_ang:
                    self._plot_axis(ax, axes_ang.trend_p, axes_ang.plunge_p,
                                    'o', self.colors.p_color, 'P')
                    self._plot_axis(ax, axes_ang.trend_t, axes_ang.plunge_t,
                                    '^', self.colors.t_color, 'T')
                    self._plot_axis(ax, axes_ang.trend_b, axes_ang.plunge_b,
                                    's', self.colors.b_color, 'B')
            except pyfpspack.FPSError:
                ax.add_patch(Circle((0, 0), 1.0, fill=False,
                                    edgecolor=self.colors.circle, linewidth=2))
            self._draw_compass(ax)
        self.draw()

    def _fill_quadrants(self, ax, n, d):
        res = 200
        x = np.linspace(-1, 1, res)
        y = np.linspace(-1, 1, res)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X ** 2 + Y ** 2)
        polarity = np.full_like(R, np.nan)
        mask = R <= 1.0
        r_v, x_v, y_v = R[mask], X[mask], Y[mask]
        plunge_rad = np.pi / 2.0 - 2.0 * np.arcsin(
            np.clip(r_v / np.sqrt(2), 0, 1))
        trend_rad = np.arctan2(x_v, y_v)
        cos_pl = np.cos(plunge_rad)
        dx = cos_pl * np.cos(trend_rad)
        dy = cos_pl * np.sin(trend_rad)
        dz = np.sin(plunge_rad)
        polarity[mask] = (dx * n[0] + dy * n[1] + dz * n[2]) * \
                          (dx * d[0] + dy * d[1] + dz * d[2])
        cs = ax.contourf(X, Y, polarity, levels=[-1e10, 0, 1e10],
                         colors=[self.colors.dilatational,
                                 self.colors.compressional])
        clip = Circle((0, 0), 1.0, transform=ax.transData)
        if hasattr(cs, 'collections'):
            for c in cs.collections:
                c.set_clip_path(clip)
        else:
            cs.set_clip_path(clip)

    def _draw_gc(self, ax, strike, dip, ls):
        sr = np.radians(strike)
        dr = np.radians(dip)
        u = np.array([np.cos(sr), np.sin(sr), 0.0])
        v = np.array([-np.sin(sr) * np.cos(dr),
                       np.cos(sr) * np.cos(dr), np.sin(dr)])
        angs = np.linspace(0, 2 * np.pi, 361)
        pts = np.zeros((len(angs), 2))
        for i, a in enumerate(angs):
            pt = np.cos(a) * u + np.sin(a) * v
            if pt[2] < 0:
                pt = -pt
            t, p = pyfpspack.ca2ax(pt)
            pts[i] = _stereo_project(t, p)
        diffs = np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1))
        jumps = np.where(diffs > 0.3)[0] + 1
        for seg in np.split(np.arange(len(pts)), jumps):
            if len(seg) > 1:
                ax.plot(pts[seg, 0], pts[seg, 1],
                        color=self.colors.great_circle,
                        linewidth=1.5, linestyle=ls, zorder=11)

    def _plot_axis(self, ax, trend, plunge, marker, color, label):
        x, y = _stereo_project(trend, plunge)
        ax.plot(x, y, marker=marker, color=color, markersize=9,
                markeredgecolor='white', markeredgewidth=1.0,
                label=label, zorder=12, linestyle='None')

    def _draw_compass(self, ax):
        off = 1.12
        for lbl, (x, y) in [('N', (0, off)), ('E', (off, 0)),
                              ('S', (0, -off)), ('W', (-off, 0))]:
            ax.text(x, y, lbl, ha='center', va='center',
                    fontsize=9, fontweight='bold', color=self.colors.compass)
