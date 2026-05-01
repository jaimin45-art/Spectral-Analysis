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

## 💬 Expected Interview / Viva Questions & Answers

### Q1: What is FFT and why is it useful in signal analysis?
**A:** FFT (Fast Fourier Transform) is an efficient algorithm to compute the Discrete Fourier Transform. It converts a time-domain signal into its constituent frequency components. In device characterisation, this helps identify which frequencies carry real device information versus which are noise — noise typically shows up as a broad elevated floor across all frequencies, while signal components appear as sharp peaks.

### Q2: Why use a Butterworth filter specifically?
**A:** Butterworth filters are called "maximally flat" filters — they have no ripple in the passband, meaning frequencies below the cutoff are passed with minimal distortion. For scientific measurement data where signal amplitude accuracy matters, ripple-free response is important. Other filters like Chebyshev have steeper roll-off but introduce passband ripple, which can distort the signal we want to preserve.

### Q3: What does SNR improvement of ~93% mean physically?
**A:** SNR (Signal-to-Noise Ratio) in dB = 10·log10(signal power / noise power). An improvement from 7.42 dB to 14.37 dB means the ratio of signal power to noise power roughly doubled. The 93% improvement figure is the relative percentage change in SNR value. In practice, this means the filtered signal is significantly easier to analyse — peaks are sharper, baselines are flatter, and extracted device parameters (like Voc or dominant frequency) will be more accurate.

### Q4: What is Fill Factor and why does it matter?
**A:** Fill Factor (FF) = Pmax / (Voc × Jsc). Geometrically, it's the ratio of the actual maximum power rectangle to the ideal rectangle defined by Voc and Jsc. It reflects internal resistances and recombination losses in a device. A perfect device would have FF = 1. Real thin-film devices typically range from 0.60–0.80. Higher FF means more of the device's theoretical maximum power is actually extracted.

### Q5: What is the significance of the Nyquist frequency?
**A:** Nyquist theorem states that to accurately represent a frequency f in digital data, the sampling rate must be at least 2f. With fs = 1000 Hz, the Nyquist limit is 500 Hz — no frequency above 500 Hz can be reliably detected. If a real signal has components above this limit, aliasing occurs: high-frequency content folds back into lower frequencies and appears as phantom peaks. In our case, setting fs = 1000 Hz is safe because our highest signal component is 120 Hz.

### Q6: Why does the I-V curve drop to zero current at Voc?
**A:** At open-circuit (no current flowing), the photogenerated current exactly equals the dark recombination current. The built-in electric field that separates electron-hole pairs is fully counterbalanced by the forward bias voltage Voc. Beyond Voc, recombination dominates and current reverses direction, which is why the curve goes negative — a physical device can't sustain this and the power output drops to zero.

### Q7: How would this analysis change with real experimental data?
**A:** Real I-V data would include series resistance (Rs) effects that cause the curve to slope inward at high voltages, and shunt resistance (Rsh) effects that cause leakage at low voltages. The single-diode model used here is simplified. For real data, we'd fit the full diode equation: J = Jsc - J0·(exp((V+J·Rs)/(n·Vt)) - 1) - (V+J·Rs)/Rsh using scipy.optimize.curve_fit to extract Rs, Rsh, J0, and ideality factor n.

### Q8: What does THD (Total Harmonic Distortion) tell us?
**A:** THD measures how much power is in harmonic frequencies (2f, 3f, 4f...) relative to the fundamental frequency. In a pure sine wave, THD = 0%. In our noisy signal, THD is higher because noise energy bleeds into harmonic frequency bins. After filtering, THD drops because high-frequency harmonics are suppressed. In device characterisation, high THD in a lock-in measurement can indicate nonlinear device behaviour or measurement system distortion.

### Q9: Can this code be adapted for real lab measurement data?
**A:** Yes — Section 7 of the notebook shows how to load any CSV file with two columns (time, signal) or (voltage, current). The `apply_fft()`, `lowpass_filter()`, and `detect_peaks()` functions work on any 1D NumPy array. For real I-V data, you would replace `generate_iv_data()` with `load_custom_csv()` and run the same curve-fitting pipeline. The only modification needed is adjusting `FS` to match your actual data acquisition sampling rate.

### Q10: What is the physical relevance of photocurrent signal analysis?
**A:** In a photodetector or solar cell under illumination, the photocurrent contains information about carrier generation, transport, and recombination dynamics. Frequency analysis of photocurrent — especially techniques like Intensity-Modulated Photocurrent Spectroscopy (IMPS) — reveals time constants related to charge transport and recombination. The FFT approach here is a simplified version of that: it identifies which frequencies dominate the response, which informs device physics interpretation.

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
