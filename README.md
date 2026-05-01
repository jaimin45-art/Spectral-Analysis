# 🔬 Spectral Data Analyser
### Solar Cell & Optoelectronic Signal Processing in Python

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.23%2B-orange?logo=numpy)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-1.9%2B-lightblue)](https://scipy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> A research-oriented Python toolkit for simulating, analysing, and visualising time-series and spectral data relevant to thin-film semiconductor optoelectronic device characterisation.

---

## 📌 What This Project Does

This project models and analyses **photocurrent signals** and **I-V characteristics** — the two most fundamental measurement types in solar cell and photodetector research.

It demonstrates:
- How **raw measurement data** contains noise that masks real device behaviour
- How **FFT (Fast Fourier Transform)** decomposes a signal into its frequency components
- How **digital filtering** recovers a clean signal and improves SNR by ~90%
- How **I-V curves** are generated and used to extract device performance metrics (Voc, Jsc, FF, PCE)

This project is directly relevant to experimental workflows in:
- Thin-film solar cells (perovskite, CdTe, CIGS, OPV)
- Photodetectors and optical sensors
- LED and laser characterisation
- Materials characterisation lab data processing

---

## 🗂️ Project Structure

```
spectral-data-analyser/
│
├── spectral_analysis.py          # Main script — run this for full pipeline
├── generate_notebook.py          # Generates the Jupyter notebook file
├── spectral_analysis_notebook.ipynb  # Interactive Jupyter notebook
│
├── output_plots/                 # Auto-generated figures and CSV
│   ├── fig1_time_domain.png
│   ├── fig2_fft_spectrum.png
│   ├── fig3_filter_result.png
│   ├── fig4_iv_curves.png
│   ├── fig5_device_metrics.png
│   └── device_iv_data.csv
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## ⚙️ Installation & Setup

### Step 1 — Clone the Repository
```bash
git clone https://github.com/jaimin45-art/spectral-data-analyser.git
cd spectral-data-analyser
```

### Step 2 — Create a Virtual Environment (Recommended)
```bash
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

**requirements.txt contents:**
```
numpy>=1.23.0
pandas>=1.5.0
matplotlib>=3.6.0
scipy>=1.9.0
jupyter>=1.0.0
```

---

## 🚀 How to Run

### Option A — Run the Python Script (No Jupyter needed)
```bash
python spectral_analysis.py
```

This runs the complete 6-step pipeline and:
- Generates 4 figures saved to `output_plots/`
- Saves I-V device data to `output_plots/device_iv_data.csv`
- Prints a full statistical report in the terminal

**Expected terminal output:**
```
  Spectral Data Analyser — v1.0.0
  Author: Modi Jaimin Dixitkumar

[1/6] Generating synthetic photocurrent signal...
[2/6] Applying Butterworth low-pass filter (cutoff=80 Hz)...
[3/6] Computing FFT spectra...
[4/6] Generating I-V device data...
  [saved] output_plots/device_iv_data.csv
[5/6] Generating plots (saved to output_plots/)...
  [saved] output_plots/fig1_time_domain.png
  [saved] output_plots/fig2_fft_spectrum.png
  [saved] output_plots/fig3_iv_curves.png
  [saved] output_plots/fig4_device_metrics.png
[6/6] Computing statistical report...

==============================================================
  SPECTRAL ANALYSIS REPORT
==============================================================
  Signal duration       : 1.00 s
  Sampling frequency    : 1000 Hz
  Total samples         : 1000
  SNR (before filter)   : 7.42 dB
  SNR (after filter)    : 14.37 dB
  SNR improvement       : 93.8%
  THD                   : 26.17%
  Dominant frequency    : 10.0 Hz
  Peaks detected        : 9
==============================================================
```

---

### Option B — Interactive Jupyter Notebook

**Step 1:** Generate the notebook file
```bash
python generate_notebook.py
```

**Step 2:** Open it in Jupyter
```bash
jupyter notebook spectral_analysis_notebook.ipynb
```

**Step 3:** In Jupyter, click **`Kernel → Restart & Run All`**

Each cell is self-contained with markdown explanations. You can:
- Modify parameters directly in each cell
- Re-run individual sections
- Add your own CSV data in Section 7

---

### Option C — Use as a Module in Your Own Code
```python
from spectral_analysis import (
    generate_signal,
    apply_fft,
    lowpass_filter,
    detect_peaks,
    compute_snr,
    generate_iv_data,
    iv_curve_points
)

# Generate a custom signal
t, clean, noisy = generate_signal(
    duration=2.0,
    fs=2000.0,
    freqs=[5, 50, 100],
    amplitudes=[1.0, 0.4, 0.2],
    noise_level=0.5
)

# Apply FFT
freqs, magnitude, phase = apply_fft(noisy, fs=2000.0)

# Filter
filtered = lowpass_filter(noisy, fs=2000.0, cutoff=120.0, order=4)

# Check SNR
print(f"SNR before: {compute_snr(clean, noisy):.2f} dB")
print(f"SNR after : {compute_snr(clean, filtered):.2f} dB")
```

---

## 📊 Output Figures Explained

### Figure 1 — Time-Domain Signal Analysis
Three subplots comparing:
1. Clean signal (ground truth)
2. Noisy signal (simulates raw measurement from a device)
3. Filtered signal (after Butterworth low-pass filter)

**What to look for:** The filtered signal should closely match the clean signal despite never having access to it — only the noisy version.

---

### Figure 2 — FFT Frequency Spectrum
Shows the signal broken into frequency components.

- **Noisy spectrum** — has a high noise floor across all frequencies
- **Peaks** — detected automatically at 10, 25, 60 Hz (the actual signal components)
- **After filtering** — noise floor drops sharply above the cutoff

**What to look for:** Sharp peaks at signal frequencies; flat noise floor elsewhere; high-frequency content disappears after filtering.

---

### Figure 3 — Filter Frequency Response + Time Comparison
- Left plot: Butterworth filter gain in dB across frequency — shows where it "cuts off"
- Right plot: Noisy, filtered, and clean signals overlaid

**What to look for:** Filter gain is 0 dB (no change) below cutoff; drops sharply above it. Filtered signal matches clean signal closely.

---

### Figure 4 — I-V and P-V Curves
Five simulated thin-film devices plotted with:
- **I-V curve** — current density vs voltage; area under curve relates to power output
- **P-V curve** — power density vs voltage; peak = maximum power point (MPP)

**What to look for:** Devices with higher Voc (rightward curve) and higher Jsc (taller curve) have higher PCE. The P-V peak indicates the MPP.

---

### Figure 5 — Device Metrics Bar Charts
Bar charts comparing Voc, Jsc, FF, and PCE across all 5 devices. Allows quick visual ranking of device performance.

---

## 🧪 Core Concepts Reference

| Concept | Symbol | Formula | Meaning |
|---------|--------|---------|---------|
| Sampling Rate | fs | samples/second | How often measurements are taken |
| Nyquist Limit | fN | fs/2 | Max detectable frequency |
| SNR | — | 10·log10(Ps/Pn) | Signal quality in dB |
| THD | — | √(Σh²)/f1 × 100% | Harmonic distortion percentage |
| FFT | — | DFT algorithm | Converts time → frequency domain |
| Open-circuit voltage | Voc | V at J=0 | Max voltage of solar cell |
| Short-circuit current | Jsc | J at V=0 | Max current of solar cell |
| Fill Factor | FF | Pmax/(Voc·Jsc) | Curve squareness (0 to 1) |
| Efficiency | PCE | Voc·Jsc·FF/Pin | % of sunlight converted |

---

## 🔧 Configurable Parameters

All key parameters are defined at the top of each section for easy modification:

| Parameter | Default | Effect of changing |
|-----------|---------|--------------------|
| `DURATION` | 1.0 s | Longer signal = better frequency resolution |
| `FS` | 1000 Hz | Must be > 2× highest frequency |
| `NOISE_LEVEL` | 0.35 | Higher = noisier signal, lower SNR |
| `FREQ_COMPONENTS` | [10, 25, 60, 120] Hz | Signal frequency components |
| `CUTOFF_HZ` | 80 Hz | Low-pass filter cutoff |
| `FILTER_ORDER` | 5 | Higher = sharper filter roll-off |
| `n_devices` | 5 | Number of simulated solar cells |

---


---

## 🛠️ Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.8+ | Core language |
| NumPy | 1.23+ | Numerical arrays, FFT computation |
| Pandas | 1.5+ | Structured data handling, CSV I/O |
| Matplotlib | 3.6+ | All visualisation |
| SciPy | 1.9+ | Signal filtering, peak detection, curve fitting |
| Jupyter | 1.0+ | Interactive notebook interface |

---

## 📁 Sample CSV Output

`output_plots/device_iv_data.csv`:

```
Device,Voc(V),Jsc(mA/cm2),FF,PCE(%)
Dev-01,0.7563,28.1033,0.6545,13.91
Dev-02,0.8243,15.0790,0.6501,8.08
Dev-03,0.7939,27.3184,0.6459,14.01
Dev-04,0.6563,26.9560,0.6801,12.03
Dev-05,0.6750,22.0190,0.6908,10.27
```

---

## 👤 Author

**Modi Jaimin Dixitkumar**  
B.E. Computer Engineering — LDRP Institute of Technology & Research  
📧 GitHub: [github.com/jaimin45-art](https://github.com/jaimin45-art)  
🔗 LinkedIn: [linkedin.com/in/jaimin-modi-590566285](https://linkedin.com/in/jaimin-modi-590566285)

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- Signal processing theory from Oppenheim & Schafer, *Discrete-Time Signal Processing*
- Solar cell device physics from Nelson, *The Physics of Solar Cells*
- SciPy documentation for filter design references
