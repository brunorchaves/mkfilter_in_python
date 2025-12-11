#!/usr/bin/env python3
"""
mkfilter.py - Python implementation of mkfilter
Designs digital Butterworth, Bessel, and Chebyshev filters
Based on the original mkfilter by A.J. Fisher, University of York
Ported to Python 2024
"""

import numpy as np
import argparse
import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Constants
PI = np.pi
TWOPI = 2.0 * PI
EPS = 1e-10
MAXORDER = 10

@dataclass
class PoleZeroRep:
    """Representation of poles and zeros in S or Z plane"""
    poles: np.ndarray
    zeros: np.ndarray

    def __init__(self):
        self.poles = np.array([], dtype=complex)
        self.zeros = np.array([], dtype=complex)


# Bessel poles table (only one member of each complex conjugate pair)
BESSEL_POLES = np.array([
    [-1.00000000000e+00+0.00000000000e+00j], [-1.10160133059e+00+6.36009824757e-01j],
    [-1.32267579991e+00+0.00000000000e+00j], [-1.04740916101e+00+9.99264436281e-01j],
    [-1.37006783055e+00+4.10249717494e-01j], [-9.95208764350e-01+1.25710573945e+00j],
    [-1.50231627145e+00+0.00000000000e+00j], [-1.38087732586e+00+7.17909587627e-01j],
    [-9.57676548563e-01+1.47112432073e+00j], [-1.57149040362e+00+3.20896374221e-01j],
    [-1.38185809760e+00+9.71471890712e-01j], [-9.30656522947e-01+1.66186326894e+00j],
    [-1.68436817927e+00+0.00000000000e+00j], [-1.61203876622e+00+5.89244506931e-01j],
    [-1.37890321680e+00+1.19156677780e+00j], [-9.09867780623e-01+1.83645135304e+00j],
    [-1.75740840040e+00+2.72867575103e-01j], [-1.63693941813e+00+8.22795625139e-01j],
    [-1.37384121764e+00+1.38835657588e+00j], [-8.92869718847e-01+1.99832584364e+00j],
    [-1.85660050123e+00+0.00000000000e+00j], [-1.80717053496e+00+5.12383730575e-01j],
    [-1.65239648458e+00+1.03138956698e+00j], [-1.36758830979e+00+1.56773371224e+00j],
    [-8.78399276161e-01+2.14980052431e+00j], [-1.92761969145e+00+2.41623471082e-01j],
    [-1.84219624443e+00+7.27257597722e-01j], [-1.66181024140e+00+1.22110021857e+00j],
    [-1.36069227838e+00+1.73350574267e+00j], [-8.65756901707e-01+2.29260483098e+00j],
])


class MkFilter:
    """Digital filter design class"""

    def __init__(self):
        self.splane = PoleZeroRep()
        self.zplane = PoleZeroRep()
        self.order = 0
        self.raw_alpha1 = 0.0
        self.raw_alpha2 = 0.0
        self.warped_alpha1 = 0.0
        self.warped_alpha2 = 0.0
        self.chebrip = 0.0
        self.filter_type = None  # 'Bu', 'Be', 'Ch'
        self.band_type = None    # 'Lp', 'Hp', 'Bp', 'Bs'
        self.use_blt = True      # True for bilinear transform, False for matched-z
        self.prewarp = True
        self.xcoeffs = None
        self.ycoeffs = None
        self.dc_gain = 0.0
        self.fc_gain = 0.0
        self.hf_gain = 0.0

    def design(self, filter_type: str, band_type: str, order: int,
               alpha1: float, alpha2: Optional[float] = None,
               chebrip: float = -1.0, use_blt: bool = True,
               prewarp: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Design a digital filter

        Args:
            filter_type: 'Bu' (Butterworth), 'Be' (Bessel), 'Ch' (Chebyshev)
            band_type: 'Lp' (lowpass), 'Hp' (highpass), 'Bp' (bandpass), 'Bs' (bandstop)
            order: Filter order (1-10)
            alpha1: Frequency parameter (f_corner / f_sample)
            alpha2: Second frequency for bandpass/bandstop (optional)
            chebrip: Chebyshev ripple in dB (must be negative)
            use_blt: Use bilinear transform (True) or matched-z (False)
            prewarp: Pre-warp frequencies for bilinear transform

        Returns:
            Tuple of (xcoeffs, ycoeffs) for the recurrence relation
        """
        self.filter_type = filter_type
        self.band_type = band_type
        self.order = order
        self.raw_alpha1 = alpha1
        self.raw_alpha2 = alpha2 if alpha2 is not None else alpha1
        self.chebrip = chebrip
        self.use_blt = use_blt
        self.prewarp = prewarp

        # Compute S-plane poles and zeros
        self._compute_s_plane()

        # Pre-warp frequencies
        self._prewarp_frequencies()

        # Normalize (convert prototype to desired filter type)
        self._normalize()

        # Transform to Z-plane
        if use_blt:
            self._compute_z_blt()
        else:
            self._compute_z_mzt()

        # Expand polynomials to get coefficients
        self._expand_poly()

        return self.xcoeffs, self.ycoeffs

    def _compute_s_plane(self):
        """Compute S-plane poles for prototype LP filter"""
        poles = []

        if self.filter_type == 'Be':
            # Bessel filter
            p = (self.order * self.order) // 4
            if self.order & 1:  # odd order
                poles.append(BESSEL_POLES[p][0])
                p += 1
            for i in range(self.order // 2):
                pole = BESSEL_POLES[p][0]
                poles.append(pole)
                poles.append(np.conj(pole))
                p += 1

        if self.filter_type in ['Bu', 'Ch']:
            # Butterworth filter (also used as base for Chebyshev)
            for i in range(2 * self.order):
                if self.order & 1:
                    theta = (i * PI) / self.order
                else:
                    theta = ((i + 0.5) * PI) / self.order
                pole = np.exp(1j * theta)
                if pole.real < 0.0:  # Only keep left half-plane poles
                    poles.append(pole)

        self.splane.poles = np.array(poles)

        if self.filter_type == 'Ch':
            # Modify for Chebyshev
            if self.chebrip >= 0.0:
                raise ValueError(f"Chebyshev ripple is {self.chebrip} dB; must be < 0.0")

            rip = 10.0 ** (-self.chebrip / 10.0)
            eps = np.sqrt(rip - 1.0)
            y = np.arcsinh(1.0 / eps) / self.order

            if y <= 0.0:
                raise ValueError(f"Chebyshev y={y}; must be > 0.0")

            # Scale poles
            self.splane.poles = self.splane.poles.real * np.sinh(y) + \
                               1j * self.splane.poles.imag * np.cosh(y)

    def _prewarp_frequencies(self):
        """Pre-warp frequencies for bilinear transform"""
        if not self.prewarp or not self.use_blt:
            self.warped_alpha1 = self.raw_alpha1
            self.warped_alpha2 = self.raw_alpha2
        else:
            self.warped_alpha1 = np.tan(PI * self.raw_alpha1) / PI
            self.warped_alpha2 = np.tan(PI * self.raw_alpha2) / PI

    def _normalize(self):
        """Transform prototype to desired filter type (LP/HP/BP/BS)"""
        w1 = TWOPI * self.warped_alpha1
        w2 = TWOPI * self.warped_alpha2

        if self.band_type == 'Lp':
            # Lowpass: scale poles by w1
            self.splane.poles = self.splane.poles * w1
            self.splane.zeros = np.array([], dtype=complex)

        elif self.band_type == 'Hp':
            # Highpass: invert poles and add zeros at origin
            self.splane.poles = w1 / self.splane.poles
            self.splane.zeros = np.zeros(len(self.splane.poles), dtype=complex)

        elif self.band_type == 'Bp':
            # Bandpass: LP to BP transformation
            w0 = np.sqrt(w1 * w2)
            bw = w2 - w1
            new_poles = []
            for pole in self.splane.poles:
                hba = 0.5 * pole * bw
                temp = np.sqrt(1.0 - (w0 / hba)**2)
                new_poles.append(hba * (1.0 + temp))
                new_poles.append(hba * (1.0 - temp))
            self.splane.poles = np.array(new_poles)
            self.splane.zeros = np.zeros(len(self.splane.poles) // 2, dtype=complex)

        elif self.band_type == 'Bs':
            # Bandstop: LP to BS transformation
            w0 = np.sqrt(w1 * w2)
            bw = w2 - w1
            new_poles = []
            new_zeros = []
            for pole in self.splane.poles:
                hba = 0.5 * bw / pole
                temp = np.sqrt(1.0 - (w0 / hba)**2)
                new_poles.append(hba * (1.0 + temp))
                new_poles.append(hba * (1.0 - temp))
                new_zeros.append(1j * w0)
                new_zeros.append(-1j * w0)
            self.splane.poles = np.array(new_poles)
            self.splane.zeros = np.array(new_zeros)

    def _compute_z_blt(self):
        """Transform from S-plane to Z-plane using bilinear transform"""
        # BLT: z = (2 + s) / (2 - s)
        self.zplane.poles = (2.0 + self.splane.poles) / (2.0 - self.splane.poles)
        if len(self.splane.zeros) > 0:
            self.zplane.zeros = (2.0 + self.splane.zeros) / (2.0 - self.splane.zeros)
        else:
            self.zplane.zeros = np.array([], dtype=complex)

        # Add zeros at -1 to make filter causal
        while len(self.zplane.zeros) < len(self.zplane.poles):
            self.zplane.zeros = np.append(self.zplane.zeros, -1.0)

    def _compute_z_mzt(self):
        """Transform from S-plane to Z-plane using matched z-transform"""
        # MZT: z = exp(s)
        self.zplane.poles = np.exp(self.splane.poles)
        if len(self.splane.zeros) > 0:
            self.zplane.zeros = np.exp(self.splane.zeros)
        else:
            self.zplane.zeros = np.array([], dtype=complex)

    def _expand_poly(self):
        """Expand polynomials to get recurrence relation coefficients"""
        # Expand (z - z1)(z - z2)... to get polynomial coefficients
        topcoeffs = self._expand(self.zplane.zeros)
        botcoeffs = self._expand(self.zplane.poles)

        # Compute gains at DC, center frequency, and high frequency
        self.dc_gain = self._evaluate(topcoeffs, botcoeffs, 1.0)
        theta = TWOPI * 0.5 * (self.raw_alpha1 + self.raw_alpha2)
        self.fc_gain = self._evaluate(topcoeffs, botcoeffs, np.exp(1j * theta))
        self.hf_gain = self._evaluate(topcoeffs, botcoeffs, -1.0)

        # Extract real coefficients for recurrence relation
        # x[n] = sum(xcoeffs[i] * input[n-i])
        # y[n] = sum(xcoeffs[i] * x[n-i]) - sum(ycoeffs[i] * y[n-i])
        nzeros = len(self.zplane.zeros)
        npoles = len(self.zplane.poles)

        self.xcoeffs = np.real(topcoeffs) / np.real(botcoeffs[-1])
        self.ycoeffs = -np.real(botcoeffs) / np.real(botcoeffs[-1])

    def _expand(self, roots: np.ndarray) -> np.ndarray:
        """Expand roots to polynomial coefficients"""
        if len(roots) == 0:
            return np.array([1.0], dtype=complex)

        # Start with coefficient for z^0
        coeffs = np.array([1.0], dtype=complex)

        # Multiply by (z - root) for each root
        for root in roots:
            new_coeffs = np.zeros(len(coeffs) + 1, dtype=complex)
            new_coeffs[0] = -root * coeffs[0]
            for i in range(1, len(coeffs)):
                new_coeffs[i] = coeffs[i-1] - root * coeffs[i]
            new_coeffs[-1] = coeffs[-1]
            coeffs = new_coeffs

        return coeffs

    def _evaluate(self, topcoeffs: np.ndarray, botcoeffs: np.ndarray,
                  z: complex) -> complex:
        """Evaluate transfer function at given z"""
        top = sum(c * z**i for i, c in enumerate(topcoeffs))
        bot = sum(c * z**i for i, c in enumerate(botcoeffs))
        return top / bot

    def get_gain(self) -> float:
        """Get the passband gain"""
        if self.band_type == 'Lp':
            return abs(self.dc_gain)
        elif self.band_type == 'Hp':
            return abs(self.hf_gain)
        elif self.band_type in ['Bp', 'Ap']:
            return abs(self.fc_gain)
        elif self.band_type == 'Bs':
            return abs(np.sqrt(self.dc_gain * self.hf_gain))
        return 1.0

    def print_summary(self):
        """Print filter summary (like mkfilter -l output)"""
        print(f"raw alpha1    = {self.raw_alpha1:14.10f}")
        print(f"raw alpha2    = {self.raw_alpha2:14.10f}")
        print(f"warped alpha1 = {self.warped_alpha1:14.10f}")
        print(f"warped alpha2 = {self.warped_alpha2:14.10f}")

        print(f"\ngain at dc:     mag = {abs(self.dc_gain):15.9e}", end="")
        if abs(self.dc_gain) > EPS:
            print(f"   phase = {np.angle(self.dc_gain)/PI:14.10f} pi")
        else:
            print()

        print(f"gain at centre: mag = {abs(self.fc_gain):15.9e}", end="")
        if abs(self.fc_gain) > EPS:
            print(f"   phase = {np.angle(self.fc_gain)/PI:14.10f} pi")
        else:
            print()

        print(f"gain at hf:     mag = {abs(self.hf_gain):15.9e}", end="")
        if abs(self.hf_gain) > EPS:
            print(f"   phase = {np.angle(self.hf_gain)/PI:14.10f} pi")
        else:
            print()

        print("\nS-plane zeros:")
        for z in self.splane.zeros:
            print(f"\t{z.real:14.10f} + j {z.imag:14.10f}")

        print("\nS-plane poles:")
        for p in self.splane.poles:
            print(f"\t{p.real:14.10f} + j {p.imag:14.10f}")

        print("\nZ-plane zeros:")
        for z in self.zplane.zeros:
            print(f"\t{z.real:14.10f} + j {z.imag:14.10f}")

        print("\nZ-plane poles:")
        for p in self.zplane.poles:
            print(f"\t{p.real:14.10f} + j {p.imag:14.10f}")

        print("\nRecurrence relation:")
        print("y[n] = ", end="")
        for i, c in enumerate(self.xcoeffs):
            if i > 0:
                print("     + ", end="")
            print(f"({c:14.10f} * x[n-{len(self.xcoeffs)-1-i:2d}])")
        print()
        for i, c in enumerate(self.ycoeffs[:-1]):  # Don't print last (always -1)
            print(f"     + ({c:14.10f} * y[n-{len(self.ycoeffs)-1-i:2d}])")
        print()


def generate_c_code(mkf: MkFilter, optimize: bool = True) -> str:
    """
    Generate C code to implement the filter

    Args:
        mkf: MkFilter object with designed filter
        optimize: Generate optimized code (True) or simple loop (False)

    Returns:
        C code as string
    """
    nzeros = len(mkf.xcoeffs) - 1
    npoles = len(mkf.ycoeffs) - 1
    gain = mkf.get_gain()

    code = []
    code.append("/* Digital filter designed by mkfilter.py */")
    code.append(f"/* {mkf.filter_type} {mkf.band_type} filter, order {mkf.order} */")
    code.append(f"/* alpha1={mkf.raw_alpha1}, alpha2={mkf.raw_alpha2} */\n")

    code.append(f"#define NZEROS {nzeros}")
    code.append(f"#define NPOLES {npoles}")
    code.append(f"#define GAIN   {gain:15.9e}\n")

    code.append("static float xv[NZEROS+1], yv[NPOLES+1];\n")

    if optimize:
        code.append("static float filterStep(float input)")
        code.append("{")

        # Shift x values
        for i in range(nzeros):
            code.append(f"  xv[{i}] = xv[{i+1}];")
        code.append(f"  xv[{nzeros}] = input / GAIN;")
        code.append("")

        # Shift y values
        for i in range(npoles):
            code.append(f"  yv[{i}] = yv[{i+1}];")

        # Compute output
        # X coefficients
        terms = []
        for i, c in enumerate(mkf.xcoeffs):
            if abs(c) > EPS:
                terms.append(f"({c:14.10f} * xv[{i}])")

        # Y coefficients (skip last which is always -1)
        for i, c in enumerate(mkf.ycoeffs[:-1]):
            if abs(c) > EPS:
                terms.append(f"({c:14.10f} * yv[{i}])")

        code.append(f"  yv[{npoles}] = " + terms[0])
        for term in terms[1:]:
            code.append("           + " + term)
        code[-1] = code[-1] + ";"

        code.append(f"  return yv[{npoles}];")
        code.append("}\n")
    else:
        # Generate simple loop version with coefficient arrays
        xcoeff_lines = []
        current_line = "  "
        for i, c in enumerate(mkf.xcoeffs):
            if i > 0 and i % 4 == 0:
                xcoeff_lines.append(current_line)
                current_line = "   "
            current_line += f" {c:+0.10f},"
        xcoeff_lines.append(current_line)

        code.append("static float xcoeffs[] = {")
        code.extend(xcoeff_lines)
        code.append("};\n")

        ycoeff_lines = []
        current_line = "  "
        for i, c in enumerate(mkf.ycoeffs[:-1]):
            if i > 0 and i % 4 == 0:
                ycoeff_lines.append(current_line)
                current_line = "   "
            current_line += f" {c:+0.10f},"
        ycoeff_lines.append(current_line)

        code.append("static float ycoeffs[] = {")
        code.extend(ycoeff_lines)
        code.append("};\n")

        code.append("static float filterStep(float input)")
        code.append("{")
        code.append("  int i;")
        code.append("  for (i = 0; i < NZEROS; i++) xv[i] = xv[i+1];")
        code.append("  xv[NZEROS] = input / GAIN;")
        code.append("  for (i = 0; i < NPOLES; i++) yv[i] = yv[i+1];")
        code.append("  yv[NPOLES] = 0.0;")
        code.append("  for (i = 0; i <= NZEROS; i++) yv[NPOLES] += xcoeffs[i] * xv[i];")
        code.append("  for (i = 0; i < NPOLES; i++) yv[NPOLES] += ycoeffs[i] * yv[i];")
        code.append("  return yv[NPOLES];")
        code.append("}\n")

    return '\n'.join(code)


def main():
    parser = argparse.ArgumentParser(
        description='mkfilter.py - Design digital filters (Butterworth, Bessel, Chebyshev)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 4th order Butterworth lowpass, corner at 0.1 * sample_rate
  python mkfilter.py -Bu -Lp -o 4 -a 0.1

  # 6th order Butterworth bandpass, 0.2 to 0.3 * sample_rate
  python mkfilter.py -Bu -Bp -o 6 -a 0.2 0.3

  # 3rd order Chebyshev highpass with -1dB ripple, corner at 0.25
  python mkfilter.py -Ch -1.0 -Hp -o 3 -a 0.25

  # Generate C code
  python mkfilter.py -Bu -Lp -o 4 -a 0.1 -c
        """
    )

    # Filter type
    ftype = parser.add_mutually_exclusive_group(required=True)
    ftype.add_argument('-Bu', action='store_const', const='Bu', dest='filter_type',
                      help='Butterworth filter')
    ftype.add_argument('-Be', action='store_const', const='Be', dest='filter_type',
                      help='Bessel filter')
    ftype.add_argument('-Ch', metavar='RIPPLE', type=float, dest='chebrip',
                      help='Chebyshev filter (RIPPLE in dB, must be negative)')

    # Band type
    btype = parser.add_mutually_exclusive_group(required=True)
    btype.add_argument('-Lp', action='store_const', const='Lp', dest='band_type',
                      help='Lowpass filter')
    btype.add_argument('-Hp', action='store_const', const='Hp', dest='band_type',
                      help='Highpass filter')
    btype.add_argument('-Bp', action='store_const', const='Bp', dest='band_type',
                      help='Bandpass filter')
    btype.add_argument('-Bs', action='store_const', const='Bs', dest='band_type',
                      help='Bandstop filter')

    # Parameters
    parser.add_argument('-o', type=int, required=True, dest='order',
                       help=f'Filter order (1-{MAXORDER})')
    parser.add_argument('-a', type=float, nargs='+', required=True, dest='alpha',
                       help='Frequency parameter(s): f_corner/f_sample (1 for LP/HP, 2 for BP/BS)')

    # Transform options
    parser.add_argument('-z', action='store_false', dest='use_blt',
                       help='Use matched z-transform instead of bilinear')
    parser.add_argument('-w', action='store_false', dest='prewarp',
                       help="Don't pre-warp frequencies")

    # Output options
    parser.add_argument('-l', action='store_true', dest='list_only',
                       help='List filter parameters only (compact format)')
    parser.add_argument('-c', '--code', action='store_true',
                       help='Generate C code')
    parser.add_argument('--code-simple', action='store_true',
                       help='Generate simple C code with loops')

    args = parser.parse_args()

    # Validate arguments
    if args.order < 1 or args.order > MAXORDER:
        print(f"Error: order must be between 1 and {MAXORDER}", file=sys.stderr)
        return 1

    if args.band_type in ['Bp', 'Bs'] and len(args.alpha) != 2:
        print(f"Error: {args.band_type} requires two alpha values", file=sys.stderr)
        return 1

    if args.band_type in ['Lp', 'Hp'] and len(args.alpha) != 1:
        print(f"Error: {args.band_type} requires one alpha value", file=sys.stderr)
        return 1

    # Determine filter type
    if args.chebrip is not None:
        filter_type = 'Ch'
        chebrip = args.chebrip
    else:
        filter_type = args.filter_type
        chebrip = -1.0

    # Create filter
    mkf = MkFilter()

    try:
        alpha1 = args.alpha[0]
        alpha2 = args.alpha[1] if len(args.alpha) > 1 else None

        mkf.design(
            filter_type=filter_type,
            band_type=args.band_type,
            order=args.order,
            alpha1=alpha1,
            alpha2=alpha2,
            chebrip=chebrip,
            use_blt=args.use_blt,
            prewarp=args.prewarp
        )

        if args.list_only:
            # Compact output format (like mkfilter -l)
            gain = mkf.get_gain()
            print(f"G  = {gain:.10e}")
            print(f"NZ = {len(mkf.xcoeffs)-1}")
            for c in mkf.xcoeffs:
                print(f"{c:18.10e}")
            print(f"NP = {len(mkf.ycoeffs)-1}")
            for c in mkf.ycoeffs:
                print(f"{c:18.10e}")
        elif args.code or args.code_simple:
            # Generate C code
            code = generate_c_code(mkf, optimize=not args.code_simple)
            print(code)
        else:
            # Full summary
            mkf.print_summary()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
