# mkfilter Digital Filter Generation Program

**Now available in Python! 🐍**

## Quick Start - Python Version

```bash
# Install
pip install numpy

# Design a Butterworth lowpass filter using Hz (EASY! ✨)
python mkfilter.py -Bu -Lp -o 4 -f 1000 -s 10000

# Or use normalized frequency (traditional)
python mkfilter.py -Bu -Lp -o 4 -a 0.1

# Generate C code ready to copy-paste
python mkfilter.py -Bu -Lp -o 4 -f 1000 -s 10000 -c
```

**New in v1.1:** Now you can specify frequencies directly in Hz with `-f` and `-s`! No more manual alpha calculations! 🎉

**See [QUICK_START.md](QUICK_START.md) for immediate usage or [README_PYTHON.md](README_PYTHON.md) for full documentation.**

---

## Original C++ Version

(mkfilter vsn. 4.5 and friends)

*Cleaned up to compile cleanly on modern (2016) OSx.
Source was tested on OSx 10.11 (you will need to install xcode) but should also compile on other Unix variants.
Uses Clang (rather than gcc).*

**For detailed usage see doc.pdf (converted from doc.ps).**

### Introduction

mkfilter is a program which designs an infinite impulse response digital filter from
parameters specified on the command line. Lowpass, highpass, bandpass and
bandstop filters, with Butterworth, Bessel or Chebyshev characteristics, are designed
using the bilinear transform or matched z-transform method. For most applications
the bilinear transform method is recommended. The program can also design
resonators with bandpass, bandstop or allpass characteristics. A companion program,
mkshape, designs raised-cosine finite-impulse-response filters and Hilbert transformers.
Other programs generate "C" code (in a variety of formats) from the compiled
filter specification, and generate various graphs in "gif" format.

The source code of the programs (in C++) is at
http://www-users.cs.york.ac.uk/~fisher/software/mkfilter
and there is a World Wide Web form-based front end at
http://www-users.cs.york.ac.uk/~fisher/mkfilter

The WWW front end is recommended. For most applications, it is the most convenient
way to use the mkfilter package.

---

## Python Implementation - New!

This repository now includes a complete Python implementation that:
- ✅ **NEW v1.1:** Specify frequencies in Hz directly! `-f 1000 -s 10000` 🎉
- ✅ Maintains 100% syntax compatibility with original
- ✅ Generates identical C code output
- ✅ Can be used as a Python library
- ✅ No compilation needed
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ Includes examples and tests (all passing)

### Files

**Python Implementation (NEW):**
- `mkfilter.py` - Main Python implementation
- `README_PYTHON.md` - Complete Python documentation
- `QUICK_START.md` - Quick reference guide (updated with Hz examples!)
- `CHANGELOG.md` - Version history and new features
- `PROJETO_COMPLETO.md` - Complete project summary
- `example_usage.py` - Examples with visualizations
- `test_simple.py` - Automated tests

**Original C++ Implementation:**
- `original_cpp/` - Original C++ source code and documentation
  - `src/mkfilter.cpp` - Original filter design program
  - `src/gencode.cpp` - Original C code generator
  - `doc.pdf` - Original documentation
  - `Makefile` - Build file
  - See [original_cpp/README.md](original_cpp/README.md) for details

### Why Use the Python Version?

1. **No compilation needed** - works immediately
2. **Specify frequencies in Hz** - no need to calculate alpha manually! ✨ NEW!
3. **Easy to integrate** - use as a library in your Python projects
4. **Generate C code** - for embedded systems and performance-critical applications
5. **Cross-platform** - runs anywhere Python runs
6. **Modern workflow** - easier to modify and extend

### Quick Example - Command Line (NEW!)

**Using frequencies in Hz (easiest way!):**
```bash
# Lowpass: 1 kHz cutoff, 10 kHz sample rate
python mkfilter.py -Bu -Lp -o 4 -f 1000 -s 10000 -c

# Bandpass: 1-3 kHz, 10 kHz sample rate
python mkfilter.py -Bu -Bp -o 4 -f 1000 3000 -s 10000 -c

# Notch filter: remove 60 Hz noise
python mkfilter.py -Bu -Bs -o 2 -f 58 62 -s 1000 -c
```

### Quick Example - Python Library

```python
from mkfilter import MkFilter, generate_c_code

# Design filter
mkf = MkFilter()
xcoeffs, ycoeffs = mkf.design(
    filter_type='Bu',  # Butterworth
    band_type='Lp',    # Lowpass
    order=4,
    alpha1=0.1         # Or calculate from Hz: 1000/10000
)

# Generate C code
c_code = generate_c_code(mkf)
print(c_code)
```

Output:
```c
#define NZEROS 4
#define NPOLES 4
#define GAIN   2.072820954e+02

static float filterStep(float input) {
  // Ready to use!
}
```

### Documentation

- **[QUICK_START.md](QUICK_START.md)** - Start here!
- **[README_PYTHON.md](README_PYTHON.md)** - Full documentation
- **[PROJETO_COMPLETO.md](PROJETO_COMPLETO.md)** - Complete project summary

### Testing

All tests pass:
```bash
$ python test_simple.py
[OK] TODOS OS TESTES PASSARAM!
```

---


## Credits

**Original mkfilter:** A.J. Fisher, University of York
**Python implementation:** 2024 port maintaining full compatibility
