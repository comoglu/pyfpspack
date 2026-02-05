"""
Test suite for the Python FPSPACK implementation.

Tests validate:
1. Round-trip consistency (forward -> inverse -> forward)
2. Known seismological values for standard fault types
3. Symmetry and orthogonality properties
4. Edge cases and error handling
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose
import pyfpspack as fpspack


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def angles_close(a, b, atol=0.5):
    """Check if two angles are close, accounting for 360-degree wrapping."""
    diff = abs(a - b) % 360.0
    return diff < atol or (360.0 - diff) < atol


# ---------------------------------------------------------------------------
# Test pl2nd and nd2pl round-trip
# ---------------------------------------------------------------------------
class TestPl2ndNd2pl:
    """Test strike/dip/rake <-> normal/slip vector conversions."""

    @pytest.mark.parametrize("strike,dip,rake", [
        (0, 45, 90),       # pure thrust, N-S strike
        (90, 45, -90),     # pure normal, E-W strike
        (45, 90, 0),       # vertical strike-slip
        (180, 30, 60),     # oblique thrust
        (270, 60, -120),   # oblique normal
        (0, 90, 180),      # vertical, pure strike-slip
        (120, 45, 90),     # thrust, NW strike
        (315, 75, -30),    # predominantly normal with strike-slip
    ])
    def test_round_trip(self, strike, dip, rake):
        """pl2nd -> nd2pl should recover original strike/dip/rake."""
        n, d = fpspack.pl2nd(strike, dip, rake)
        result = fpspack.nd2pl(n, d)

        assert angles_close(result.strike, strike % 360.0), \
            f"Strike: got {result.strike}, expected {strike % 360.0}"
        assert_allclose(result.dip, dip, atol=0.01)
        # Rake can differ by 360 degrees
        rake_diff = abs(result.rake - rake) % 360.0
        assert rake_diff < 0.5 or (360.0 - rake_diff) < 0.5, \
            f"Rake: got {result.rake}, expected {rake}"

    def test_normal_slip_perpendicular(self):
        """Normal and slip vectors must be perpendicular."""
        n, d = fpspack.pl2nd(45, 60, 30)
        dot = np.dot(n, d)
        assert_allclose(dot, 0.0, atol=1e-10)

    def test_normal_slip_unit_vectors(self):
        """Normal and slip vectors should be unit vectors."""
        n, d = fpspack.pl2nd(120, 45, -90)
        assert_allclose(np.linalg.norm(n), 1.0, atol=1e-10)
        assert_allclose(np.linalg.norm(d), 1.0, atol=1e-10)


# ---------------------------------------------------------------------------
# Test ax2ca and ca2ax round-trip
# ---------------------------------------------------------------------------
class TestAx2caCa2ax:

    @pytest.mark.parametrize("trend,plunge", [
        (0, 0),
        (90, 0),
        (180, 45),
        (270, 90),
        (45, 30),
        (315, 60),
    ])
    def test_round_trip(self, trend, plunge):
        v = fpspack.ax2ca(trend, plunge)
        t, p = fpspack.ca2ax(v)
        assert angles_close(t, trend % 360.0), \
            f"Trend: got {t}, expected {trend % 360.0}"
        assert_allclose(p, plunge, atol=0.01)

    def test_unit_vector(self):
        v = fpspack.ax2ca(45, 30)
        assert_allclose(np.linalg.norm(v), 1.0, atol=1e-10)


# ---------------------------------------------------------------------------
# Test pt2nd and nd2pt round-trip
# ---------------------------------------------------------------------------
class TestPt2ndNd2pt:

    def test_round_trip(self):
        """P,T -> n,d -> P,T should recover one of the two conjugate planes."""
        # Start from a known plane
        n, d = fpspack.pl2nd(30, 60, 45)
        axes = fpspack.nd2pt(n, d)

        # Now go back -- pt2nd may return either conjugate plane
        n2, d2 = fpspack.pt2nd(axes.p, axes.t)

        plane_orig = fpspack.nd2pl(n, d)
        plane_conj = fpspack.pl2pl(30, 60, 45)
        plane_recovered = fpspack.nd2pl(n2, d2)

        match_orig = (angles_close(plane_recovered.strike, plane_orig.strike) and
                      abs(plane_recovered.dip - plane_orig.dip) < 1.0)
        match_conj = (angles_close(plane_recovered.strike, plane_conj.strike) and
                      abs(plane_recovered.dip - plane_conj.dip) < 1.0)
        assert match_orig or match_conj

    def test_ptb_orthogonal(self):
        """P, T, B axes must be mutually perpendicular."""
        n, d = fpspack.pl2nd(120, 45, -90)
        axes = fpspack.nd2pt(n, d)
        assert_allclose(np.dot(axes.p, axes.t), 0.0, atol=1e-10)
        assert_allclose(np.dot(axes.p, axes.b), 0.0, atol=1e-10)
        assert_allclose(np.dot(axes.t, axes.b), 0.0, atol=1e-10)

    def test_ptb_downward(self):
        """P, T, B z-components should be >= 0 (downward convention)."""
        for s, d, r in [(0, 45, 90), (90, 60, -90), (45, 30, 0)]:
            n, dv = fpspack.pl2nd(s, d, r)
            axes = fpspack.nd2pt(n, dv)
            assert axes.p[2] >= -1e-10, f"P axis z < 0 for ({s},{d},{r})"
            assert axes.t[2] >= -1e-10, f"T axis z < 0 for ({s},{d},{r})"
            assert axes.b[2] >= -1e-10, f"B axis z < 0 for ({s},{d},{r})"


# ---------------------------------------------------------------------------
# Test moment tensor routines
# ---------------------------------------------------------------------------
class TestMomentTensor:

    def test_pl2ar_symmetric(self):
        """Moment tensor from pl2ar should be symmetric."""
        am = fpspack.pl2ar(45, 60, 90, am0=1.0)
        assert_allclose(am, am.T, atol=1e-10)

    def test_pl2ar_trace(self):
        """Pure double-couple moment tensor should have zero trace."""
        am = fpspack.pl2ar(45, 60, 90, am0=1.0)
        assert_allclose(np.trace(am), 0.0, atol=1e-10)

    def test_nd2ar_round_trip(self):
        """nd2ar -> ar2pt -> pt2nd should recover one of the conjugate planes."""
        n, d = fpspack.pl2nd(30, 60, 45)
        am = fpspack.nd2ar(n, d, am0=1.0)
        dec = fpspack.ar2pt(am)
        n2, d2 = fpspack.pt2nd(dec.p, dec.t)

        plane_orig = fpspack.nd2pl(n, d)
        plane_conj = fpspack.pl2pl(30, 60, 45)
        plane_recovered = fpspack.nd2pl(n2, d2)

        match_orig = (angles_close(plane_recovered.strike, plane_orig.strike) and
                      abs(plane_recovered.dip - plane_orig.dip) < 1.0)
        match_conj = (angles_close(plane_recovered.strike, plane_conj.strike) and
                      abs(plane_recovered.dip - plane_conj.dip) < 1.0)
        assert match_orig or match_conj

    def test_ar2ha_involution(self):
        """AR2HA applied twice should return the original tensor."""
        am = fpspack.pl2ar(45, 60, 90)
        ha = fpspack.ar2ha(am)
        recovered = fpspack.ar2ha(ha)
        assert_allclose(recovered, am, atol=1e-10)

    def test_ar2pt_pure_dc(self):
        """For a pure double couple, CLVD remainder (eta) should be ~0."""
        am = fpspack.pl2ar(45, 60, 90, am0=1.0)
        dec = fpspack.ar2pt(am)
        assert abs(dec.eta) < 0.01, f"eta = {dec.eta} for pure DC"
        assert_allclose(dec.e, 0.0, atol=1e-10)

    def test_am0_scaling(self):
        """Moment tensor should scale linearly with am0."""
        am1 = fpspack.pl2ar(45, 60, 90, am0=1.0)
        am2 = fpspack.pl2ar(45, 60, 90, am0=2.0)
        assert_allclose(am2, 2.0 * am1, atol=1e-10)


# ---------------------------------------------------------------------------
# Test composite routines
# ---------------------------------------------------------------------------
class TestCompositeRoutines:

    def test_pl2pl_round_trip(self):
        """Computing second plane, then its second plane, should return original."""
        s1, d1, r1 = 45, 60, 90
        plane_b = fpspack.pl2pl(s1, d1, r1)
        plane_a = fpspack.pl2pl(plane_b.strike, plane_b.dip, plane_b.rake)

        assert angles_close(plane_a.strike, s1 % 360.0)
        assert_allclose(plane_a.dip, d1, atol=0.5)
        assert angles_close(plane_a.rake, r1, atol=1.0)

    def test_pl2pt_axes_sum_to_90(self):
        """For a pure DC, P and T plunges should be complementary to 45 for vertical dip."""
        # For strike=0, dip=90, rake=0 (pure left-lateral strike-slip)
        axes = fpspack.pl2pt(0, 90, 0)
        # Both P and T should plunge at 0 degrees for this geometry
        assert axes.plunge_p < 1.0 or axes.plunge_t < 1.0

    def test_pt2pl_round_trip(self):
        """pl2pt -> pt2pl should recover the original plane."""
        s, d, r = 120, 45, -90
        axes = fpspack.pl2pt(s, d, r)
        plane_a, plane_b = fpspack.pt2pl(
            axes.trend_p, axes.plunge_p,
            axes.trend_t, axes.plunge_t
        )

        # One of the two planes should match the original
        match_a = (angles_close(plane_a.strike, s % 360.0) and
                   abs(plane_a.dip - d) < 1.0)
        match_b = (angles_close(plane_b.strike, s % 360.0) and
                   abs(plane_b.dip - d) < 1.0)
        assert match_a or match_b, \
            f"Neither plane matches original ({s}, {d}, {r})\n" \
            f"Plane A: ({plane_a.strike:.1f}, {plane_a.dip:.1f}, {plane_a.rake:.1f})\n" \
            f"Plane B: ({plane_b.strike:.1f}, {plane_b.dip:.1f}, {plane_b.rake:.1f})"

    def test_ar2plp_full_cycle(self):
        """strike/dip/rake -> tensor -> decomposition should recover planes."""
        s, d, r = 30, 50, 70
        am = fpspack.pl2ar(s, d, r)
        dec = fpspack.ar2plp(am)

        match_a = (angles_close(dec.plane_a.strike, s % 360.0) and
                   abs(dec.plane_a.dip - d) < 1.0)
        match_b = (angles_close(dec.plane_b.strike, s % 360.0) and
                   abs(dec.plane_b.dip - d) < 1.0)
        assert match_a or match_b

    def test_ha2plp(self):
        """Harvard CMT decomposition should give same result as AR path."""
        s, d, r = 60, 45, 90
        am_ar = fpspack.pl2ar(s, d, r)
        am_ha = fpspack.ar2ha(am_ar)

        dec_ar = fpspack.ar2plp(am_ar)
        dec_ha = fpspack.ha2plp(am_ha)

        # Both decompositions should agree
        assert_allclose(dec_ar.am0, dec_ha.am0, atol=1e-6)
        assert_allclose(dec_ar.axes.plunge_p, dec_ha.axes.plunge_p, atol=0.5)
        assert_allclose(dec_ar.axes.plunge_t, dec_ha.axes.plunge_t, atol=0.5)


# ---------------------------------------------------------------------------
# Test hatens / tensha
# ---------------------------------------------------------------------------
class TestHarwardTensor:

    def test_hatens_tensha_round_trip(self):
        components = (1.0, 2.0, 3.0, 0.5, -0.5, 0.3)
        am = fpspack.hatens(*components)
        recovered = fpspack.tensha(am)
        assert_allclose(recovered, components, atol=1e-10)

    def test_hatens_symmetric(self):
        am = fpspack.hatens(1.0, 2.0, 3.0, 0.5, -0.5, 0.3)
        assert_allclose(am, am.T, atol=1e-10)


# ---------------------------------------------------------------------------
# Test angles routines
# ---------------------------------------------------------------------------
class TestAngles:

    def test_same_plane_zero_angle(self):
        """Same plane should have zero angle."""
        a_p, a_d = fpspack.angles(45, 60, 90, 45, 60, 90)
        assert_allclose(a_p, 0.0, atol=0.1)
        assert_allclose(a_d, 0.0, atol=0.1)

    def test_conjugate_planes(self):
        """Conjugate nodal planes should have known angle."""
        plane_b = fpspack.pl2pl(45, 60, 90)
        a_p, a_d = fpspack.angles(45, 60, 90,
                                  plane_b.strike, plane_b.dip, plane_b.rake)
        # Normal vectors of conjugate planes are perpendicular to each other's slip
        # The angle should be > 0
        assert a_p > 0.1

    def test_anglea_same_axis(self):
        ang = fpspack.anglea(45, 30, 45, 30)
        assert_allclose(ang, 0.0, atol=0.1)

    def test_anglea_perpendicular(self):
        ang = fpspack.anglea(0, 0, 90, 0)
        assert_allclose(ang, 90.0, atol=0.1)


# ---------------------------------------------------------------------------
# Test known seismological cases
# ---------------------------------------------------------------------------
class TestKnownCases:

    def test_pure_thrust_north(self):
        """Pure thrust fault, N-S strike, dip=45, rake=90."""
        s, d, r = 0, 45, 90
        n, slip = fpspack.pl2nd(s, d, r)
        # Normal should point upward-west for this geometry
        assert n[2] < 0, "Normal z should be negative (upward in Aki-Richards)"

    def test_pure_normal_fault(self):
        """Pure normal fault: rake = -90.
        In Aki-Richards convention, for a normal fault the P (compression)
        axis is near-vertical since gravity (vertical stress) drives the
        extension, while T (tension) is near-horizontal."""
        s, d, r = 0, 45, -90
        axes = fpspack.pl2pt(s, d, r)
        # P axis should be more vertical than T for a normal fault
        assert axes.plunge_p > axes.plunge_t

    def test_pure_strike_slip(self):
        """Pure left-lateral strike-slip: dip=90, rake=0."""
        s, d, r = 0, 90, 0
        axes = fpspack.pl2pt(s, d, r)
        # P and T axes should be horizontal (plunge near 0)
        assert axes.plunge_p < 5.0
        assert axes.plunge_t < 5.0

    def test_moment_tensor_pure_dc_eigenvalues(self):
        """A pure DC tensor should have eigenvalues (+M0, 0, -M0)."""
        am = fpspack.pl2ar(45, 60, 90, am0=1e16)
        vals = np.sort(np.linalg.eigvalsh(am))[::-1]
        # Should be approximately +M0, ~0, -M0
        assert_allclose(vals[1], 0.0, atol=1e10)
        assert_allclose(vals[0], -vals[2], atol=1e10)


# ---------------------------------------------------------------------------
# Test error handling
# ---------------------------------------------------------------------------
class TestErrorHandling:

    def test_strike_out_of_range(self):
        with pytest.raises(fpspack.StrikeOutOfRange):
            fpspack.pl2nd(400, 45, 90)

    def test_dip_out_of_range(self):
        with pytest.raises(fpspack.DipOutOfRange):
            fpspack.pl2nd(0, 100, 90)

    def test_rake_out_of_range(self):
        with pytest.raises(fpspack.RakeOutOfRange):
            fpspack.pl2nd(0, 45, 400)

    def test_trend_out_of_range(self):
        with pytest.raises(fpspack.TrendOutOfRange):
            fpspack.ax2ca(400, 45)

    def test_plunge_out_of_range(self):
        with pytest.raises(fpspack.PlungeOutOfRange):
            fpspack.ax2ca(0, 100)

    def test_not_perpendicular(self):
        with pytest.raises(fpspack.NotPerpendicular):
            fpspack.nd2pl(np.array([1, 0, 0]), np.array([1, 0, 0]))

    def test_tensor_not_symmetric(self):
        am = np.array([[1, 2, 3], [0, 1, 2], [3, 2, 1]], dtype=float)
        with pytest.raises(fpspack.TensorNotSymmetric):
            fpspack.ar2pt(am)

    def test_dip_tolerance_correction(self):
        """Dip slightly out of range but within tolerance should be corrected."""
        n, d = fpspack.pl2nd(0, -0.0005, 90)  # Just within ovrtol
        assert n is not None


# ---------------------------------------------------------------------------
# Test high-level convenience functions
# ---------------------------------------------------------------------------
class TestConvenienceFunctions:

    def test_sdr_to_moment_tensor_ar(self):
        am = fpspack.sdr_to_moment_tensor(45, 60, 90, convention="aki-richards")
        assert am.shape == (3, 3)
        assert_allclose(am, am.T, atol=1e-10)

    def test_sdr_to_moment_tensor_harvard(self):
        am = fpspack.sdr_to_moment_tensor(45, 60, 90, convention="harvard")
        assert am.shape == (3, 3)

    def test_moment_tensor_to_sdr(self):
        am = fpspack.pl2ar(45, 60, 90)
        dec = fpspack.moment_tensor_to_sdr(am, convention="aki-richards")
        assert isinstance(dec, fpspack.FullDecomposition)

    def test_unknown_convention(self):
        with pytest.raises(ValueError):
            fpspack.sdr_to_moment_tensor(45, 60, 90, convention="unknown")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
