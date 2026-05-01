"""
Generates spectral_analysis_notebook.ipynb programmatically.
Run: python3 generate_notebook.py
"""
import json

cells = []

def code(source, tags=None):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"tags": tags or []},
        "outputs": [],
        "source": source if isinstance(source, list) else [source]
    }

def md(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source if isinstance(source, list) else [source]
    }

# ─── Cell 0 — Title ──────────────────────────────────────────────────────────
cells.append(md("""# 🔬 Spectral Data Analyser — Solar Cell & Optoelectronic Signal Processing

**Author:** Modi Jaimin Dixitkumar  
**GitHub:** [github.com/jaimin45-art](https://github.com/jaimin45-art)  
**Version:** 1.0.0

---

## 📌 What This Notebook Does

This notebook simulates and analyses **spectral / time-series data** representative of measurements taken during thin-film optoelectronic device characterisation (e.g., photocurrent signals, I-V sweeps).

### Topics Covered
| # | Module | Technique |
|---|--------|-----------|
| 1 | Signal Generation | Synthetic photocurrent with Gaussian noise |
| 2 | FFT Analysis | Frequency-domain decomposition, peak detection |
| 3 | Noise Filtering | Butterworth low-pass filter |
| 4 | I-V Curve Analysis | Single-diode model, batch device metrics |
| 5 | Statistical Report | SNR, THD, PCE comparison |

---
> **Run all cells:** `Kernel → Restart & Run All`
"""))

# ─── Cell 1 — Imports ────────────────────────────────────────────────────────
cells.append(md("## 📦 Section 1 — Imports & Setup"))
cells.append(code("""\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import signal as scipy_signal
from scipy.optimize import curve_fit
import os, warnings
warnings.filterwarnings('ignore')

%matplotlib inline
plt.rcParams.update({
    'figure.facecolor': '#0d1117',
    'axes.facecolor':   '#161b22',
    'axes.edgecolor':   '#30363d',
    'axes.labelcolor':  '#c9d1d9',
    'xtick.color':      '#8b949e',
    'ytick.color':      '#8b949e',
    'text.color':       '#c9d1d9',
    'grid.color':       '#21262d',
    'grid.linestyle':   '--',
    'grid.alpha':       0.5,
    'lines.linewidth':  1.6,
    'font.family':      'monospace',
})

COLORS = {
    'signal':   '#58a6ff',
    'noisy':    '#ff7b72',
    'filtered': '#3fb950',
    'fft':      '#d2a8ff',
    'peak':     '#f0883e',
    'iv':       '#79c0ff',
}

os.makedirs('output_plots', exist_ok=True)
print("✅ All imports successful.")
print(f"   NumPy  : {np.__version__}")
print(f"   Pandas : {pd.__version__}")
"""))

# ─── Cell 2 — Signal Generation ──────────────────────────────────────────────
cells.append(md("""\
## 📡 Section 2 — Signal Generation

We simulate a **photocurrent signal** composed of multiple frequency components — representing real measurement harmonics in a device under illumination — and add Gaussian noise to mimic measurement noise.

**Parameters you can modify:**
- `DURATION` — how long the signal is (seconds)
- `FS` — sampling rate (Hz); must be > 2× highest frequency (Nyquist)
- `NOISE_LEVEL` — standard deviation of Gaussian noise (try 0.1 to 0.8)
"""))
cells.append(code("""\
# ── Configurable parameters ──────────────────────────────────────
DURATION    = 1.0      # seconds
FS          = 1000.0   # sampling frequency (Hz)
NOISE_LEVEL = 0.35     # Gaussian noise std dev
SEED        = 42       # reproducibility

# Frequency components (Hz) and their amplitudes (a.u.)
FREQ_COMPONENTS = [10, 25, 60, 120]
AMPLITUDES      = [1.0, 0.5, 0.25, 0.1]

# ── Generate ─────────────────────────────────────────────────────
rng   = np.random.default_rng(SEED)
t     = np.linspace(0, DURATION, int(FS * DURATION), endpoint=False)
clean = sum(a * np.sin(2 * np.pi * f * t)
            for f, a in zip(FREQ_COMPONENTS, AMPLITUDES))
noise = rng.normal(0, NOISE_LEVEL, size=t.shape)
noisy = clean + noise

print(f"Signal generated  : {len(t)} samples  |  {t[-1]:.2f} s  |  fs={FS} Hz")
print(f"Frequency comps   : {FREQ_COMPONENTS} Hz")
print(f"Noise level (σ)   : {NOISE_LEVEL}")
print(f"Peak amplitude    : {clean.max():.3f} a.u.")
"""))

# ─── Cell 3 — Time Domain Plot ───────────────────────────────────────────────
cells.append(md("### 📊 Time-Domain View: Clean vs Noisy Signal"))
cells.append(code("""\
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 6), sharex=True)
fig.suptitle("Time-Domain Signal — Clean vs Noisy", color='#c9d1d9', fontsize=12)

ax1.plot(t, clean, color=COLORS['signal'], linewidth=1.0, label='Clean (ground truth)')
ax1.set_ylabel('Amplitude (a.u.)')
ax1.set_title('Clean Photocurrent Signal', color=COLORS['signal'], fontsize=9, loc='left')
ax1.legend(fontsize=8); ax1.grid(True)

ax2.plot(t, noisy, color=COLORS['noisy'], linewidth=0.6, alpha=0.8, label='Noisy (raw measurement)')
ax2.set_ylabel('Amplitude (a.u.)'); ax2.set_xlabel('Time (s)')
ax2.set_title('Noisy Signal (Gaussian noise added)', color=COLORS['noisy'], fontsize=9, loc='left')
ax2.legend(fontsize=8); ax2.grid(True)

plt.tight_layout()
plt.savefig('output_plots/fig1_time_domain_clean_noisy.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved → output_plots/fig1_time_domain_clean_noisy.png")
"""))

# ─── Cell 4 — FFT ────────────────────────────────────────────────────────────
cells.append(md("""\
## 🌊 Section 3 — FFT Analysis

**Fast Fourier Transform (FFT)** converts a time-domain signal into its frequency components.  
Each peak in the spectrum corresponds to a frequency component present in the signal.

**Key concept:** Noise appears as a broad, elevated "floor" across all frequencies.  
Signal components appear as sharp, tall peaks.
"""))
cells.append(code("""\
def apply_fft(sig, fs):
    N      = len(sig)
    fft_c  = np.fft.rfft(sig)
    freqs  = np.fft.rfftfreq(N, d=1.0/fs)
    mag    = np.abs(fft_c) * 2 / N
    phase  = np.angle(fft_c)
    return freqs, mag, phase

freqs_n, mag_n, phase_n = apply_fft(noisy, FS)
freqs_c, mag_c, phase_c = apply_fft(clean, FS)

print(f"FFT computed  :  {len(freqs_n)} frequency bins")
print(f"Frequency resolution : {freqs_n[1] - freqs_n[0]:.3f} Hz")
print(f"Max detectable freq  : {freqs_n[-1]:.1f} Hz  (Nyquist limit)")
"""))

# ─── Cell 5 — Peak Detection ─────────────────────────────────────────────────
cells.append(md("### 🔍 Peak Detection — Identifying Dominant Frequencies"))
cells.append(code("""\
from scipy.signal import find_peaks

peak_idx, _ = find_peaks(mag_n, height=0.05 * mag_n.max(), distance=5)
peak_freqs  = freqs_n[peak_idx]
peak_mags   = mag_n[peak_idx]

print(f"Peaks detected: {len(peak_freqs)}")
print(f"{'Frequency (Hz)':<20} {'Magnitude':>12}")
print("-" * 34)
for pf, pm in zip(peak_freqs, peak_mags):
    marker = " ← dominant" if pm == peak_mags.max() else ""
    print(f"  {pf:>8.1f} Hz         {pm:>8.4f}{marker}")
"""))

cells.append(code("""\
fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
fig.suptitle("FFT Frequency Spectrum — Noisy vs Clean Signal", color='#c9d1d9', fontsize=12)

axes[0].plot(freqs_n, mag_n, color=COLORS['noisy'], linewidth=0.7, alpha=0.85, label='Noisy signal')
axes[0].scatter(peak_freqs, peak_mags, color=COLORS['peak'], zorder=5, s=45, label='Detected peaks')
for pf, pm in zip(peak_freqs, peak_mags):
    if pm > 0.08 * mag_n.max():
        axes[0].annotate(f"{pf:.0f} Hz", xy=(pf, pm),
                         xytext=(pf+3, pm+0.01), fontsize=7, color=COLORS['peak'])
axes[0].set_ylabel('Magnitude'); axes[0].set_title('Noisy Signal Spectrum', color=COLORS['noisy'], fontsize=9, loc='left')
axes[0].legend(fontsize=8); axes[0].grid(True); axes[0].set_xlim(0, 250)

axes[1].plot(freqs_c, mag_c, color=COLORS['signal'], linewidth=0.8, label='Clean signal (reference)')
axes[1].set_ylabel('Magnitude'); axes[1].set_xlabel('Frequency (Hz)')
axes[1].set_title('Clean Signal Spectrum (ground truth)', color=COLORS['signal'], fontsize=9, loc='left')
axes[1].legend(fontsize=8); axes[1].grid(True)

plt.tight_layout()
plt.savefig('output_plots/fig2_fft_spectrum.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# ─── Cell 6 — Filter ─────────────────────────────────────────────────────────
cells.append(md("""\
## 🧹 Section 4 — Noise Filtering

A **Butterworth low-pass filter** suppresses all frequencies above the cutoff.  
Since our signal components are at 10, 25, 60 Hz — setting cutoff = 80 Hz  
preserves all signal while attenuating high-frequency noise.

**Try changing:**
- `CUTOFF_HZ` — lower = more aggressive filtering (may distort signal)
- `FILTER_ORDER` — higher = steeper roll-off, more phase delay
"""))
cells.append(code("""\
CUTOFF_HZ    = 80.0   # Hz — adjust and observe effect
FILTER_ORDER = 5      # Butterworth filter order

def lowpass_filter(sig, fs, cutoff, order=5):
    b, a = scipy_signal.butter(order, cutoff / (fs/2), btype='low')
    return scipy_signal.filtfilt(b, a, sig)   # zero-phase filtering

filtered = lowpass_filter(noisy, FS, CUTOFF_HZ, FILTER_ORDER)

# Frequency response of the filter
w, h = scipy_signal.freqz(*scipy_signal.butter(FILTER_ORDER, CUTOFF_HZ/(FS/2), btype='low'))
freq_axis = w * FS / (2 * np.pi)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Butterworth Low-Pass Filter", color='#c9d1d9', fontsize=12)

axes[0].plot(freq_axis, 20*np.log10(np.abs(h)+1e-10), color=COLORS['fft'], linewidth=1.5)
axes[0].axvline(CUTOFF_HZ, color=COLORS['peak'], linestyle='--', label=f'Cutoff = {CUTOFF_HZ} Hz')
axes[0].set_xlabel('Frequency (Hz)'); axes[0].set_ylabel('Gain (dB)')
axes[0].set_title('Filter Frequency Response', loc='left'); axes[0].legend(fontsize=8); axes[0].grid(True)
axes[0].set_xlim(0, 300); axes[0].set_ylim(-80, 5)

axes[1].plot(t, noisy,    color=COLORS['noisy'],    alpha=0.5, linewidth=0.6, label='Noisy')
axes[1].plot(t, filtered, color=COLORS['filtered'], linewidth=1.2, label='Filtered')
axes[1].plot(t, clean,    color=COLORS['signal'],   linewidth=0.8, alpha=0.7, linestyle='--', label='Clean (truth)')
axes[1].set_xlabel('Time (s)'); axes[1].set_ylabel('Amplitude')
axes[1].set_title('Time-Domain: Noisy → Filtered', loc='left'); axes[1].legend(fontsize=8); axes[1].grid(True)

plt.tight_layout()
plt.savefig('output_plots/fig3_filter_result.png', dpi=150, bbox_inches='tight')
plt.show()
print(f"Filter order: {FILTER_ORDER}  |  Cutoff: {CUTOFF_HZ} Hz")
"""))

# ─── Cell 7 — SNR ────────────────────────────────────────────────────────────
cells.append(md("## 📈 Section 5 — Statistical Metrics (SNR, THD)"))
cells.append(code("""\
def compute_snr(clean_sig, measured_sig):
    noise   = measured_sig - clean_sig
    sig_pow = np.mean(clean_sig**2)
    noi_pow = np.mean(noise**2)
    return 10 * np.log10(sig_pow / noi_pow) if noi_pow > 0 else float('inf')

def compute_thd(freqs, mag, fundamental_hz):
    tol   = 2.0
    f_idx = np.argmin(np.abs(freqs - fundamental_hz))
    f_amp = mag[f_idx]
    harm  = sum(mag[np.argmin(np.abs(freqs - fundamental_hz*h))]**2 for h in range(2, 8))
    return (np.sqrt(harm) / f_amp * 100) if f_amp > 0 else 0.0

snr_before = compute_snr(clean, noisy)
snr_after  = compute_snr(clean, filtered)
snr_gain   = ((snr_after - snr_before) / abs(snr_before)) * 100
thd        = compute_thd(freqs_n, mag_n, fundamental_hz=10.0)

print("=" * 50)
print("  SIGNAL QUALITY REPORT")
print("=" * 50)
print(f"  SNR before filtering  : {snr_before:>8.2f} dB")
print(f"  SNR after  filtering  : {snr_after:>8.2f} dB")
print(f"  SNR improvement       : {snr_gain:>8.1f} %")
print(f"  Total Harmonic Dist.  : {thd:>8.2f} %")
print(f"  Dominant frequency    : {peak_freqs[0]:>8.1f} Hz")
print(f"  Peaks detected        : {len(peak_freqs):>8d}")
print("=" * 50)
"""))

# ─── Cell 8 — I-V ────────────────────────────────────────────────────────────
cells.append(md("""\
## ⚡ Section 6 — I-V Curve Analysis (Thin-Film Devices)

Simulates **current-voltage (I-V) characteristics** for multiple thin-film solar cell devices.

**Device parameters:**
| Symbol | Meaning |
|--------|---------|
| Voc | Open-circuit voltage — max voltage at zero current |
| Jsc | Short-circuit current density — max current at zero voltage |
| FF | Fill Factor — measure of "squareness" of I-V curve |
| PCE | Power Conversion Efficiency = Voc × Jsc × FF / Pin |
"""))
cells.append(code("""\
def generate_iv_data(n_devices=5, seed=7):
    rng  = np.random.default_rng(seed)
    vocs = rng.uniform(0.60, 0.85, n_devices)
    jscs = rng.uniform(15,   30,   n_devices)
    ffs  = rng.uniform(0.60, 0.78, n_devices)
    pces = vocs * jscs * ffs / 100.0
    return pd.DataFrame({
        'Device':      [f'Dev-{i+1:02d}' for i in range(n_devices)],
        'Voc(V)':      np.round(vocs, 4),
        'Jsc(mA/cm2)': np.round(jscs, 4),
        'FF':          np.round(ffs,  4),
        'PCE(%)':      np.round(pces, 4),
    })

def iv_curve_points(voc, jsc, n_points=200):
    V  = np.linspace(0, voc * 1.05, n_points)
    Vt, m = 0.02585, 1.3
    J0 = jsc * np.exp(-voc / (m * Vt))
    J  = jsc - J0 * (np.exp(V / (m * Vt)) - 1)
    return V, np.clip(J, 0, None)

df = generate_iv_data(n_devices=5)
df.to_csv('output_plots/device_iv_data.csv', index=False)
print(df.to_string(index=False))
best = df.loc[df['PCE(%)'].idxmax()]
print(f"\\n✅ Best device: {best['Device']}  |  PCE = {best['PCE(%)']:.2f}%")
"""))

cells.append(code("""\
cmap   = plt.cm.plasma
colors = [cmap(i / len(df)) for i in range(len(df))]

fig = plt.figure(figsize=(14, 6))
gs  = gridspec.GridSpec(1, 2, figure=fig, wspace=0.35)
ax1, ax2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

for i, row in df.iterrows():
    V, J = iv_curve_points(row['Voc(V)'], row['Jsc(mA/cm2)'])
    lbl  = f"{row['Device']} | PCE={row['PCE(%)']:.2f}%"
    ax1.plot(V, J, color=colors[i], label=lbl)
    ax2.plot(V, V*J, color=colors[i])

ax1.set(xlabel='Voltage (V)', ylabel='Current Density (mA/cm²)', title='I-V Curves')
ax1.legend(fontsize=7, loc='lower left'); ax1.grid(True); ax1.set_xlim(left=0); ax1.set_ylim(bottom=0)

ax2.set(xlabel='Voltage (V)', ylabel='Power Density (mW/cm²)', title='P-V Curves')
ax2.grid(True); ax2.set_xlim(left=0); ax2.set_ylim(bottom=0)

fig.suptitle("Thin-Film Solar Cell I-V & P-V Characteristics", color='#c9d1d9', fontsize=12)
plt.savefig('output_plots/fig4_iv_curves.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# ─── Cell 9 — Metrics Bar ────────────────────────────────────────────────────
cells.append(md("### 📊 Device Performance Metrics Comparison"))
cells.append(code("""\
metrics = ['Voc(V)', 'Jsc(mA/cm2)', 'FF', 'PCE(%)']
cols    = [COLORS['signal'], COLORS['noisy'], COLORS['filtered'], COLORS['peak']]

fig, axes = plt.subplots(2, 2, figsize=(12, 7))
fig.suptitle("Device Performance Metrics Comparison", color='#c9d1d9', fontsize=12)
axes = axes.flatten()

for ax, metric, col in zip(axes, metrics, cols):
    bars = ax.bar(df['Device'], df[metric], color=col, alpha=0.8, edgecolor='#30363d')
    ax.set_title(metric, color=col, fontsize=10); ax.grid(True, axis='y')
    ax.set_xticklabels(df['Device'], rotation=30, ha='right', fontsize=8)
    for bar, val in zip(bars, df[metric]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.002,
                f'{val:.3f}', ha='center', va='bottom', fontsize=7, color='#c9d1d9')

plt.tight_layout()
plt.savefig('output_plots/fig5_device_metrics.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# ─── Cell 10 — Custom CSV ────────────────────────────────────────────────────
cells.append(md("""\
## 📂 Section 7 — Load Your Own CSV Data

Replace the file path below with your actual data file.

Expected format:
```
time,signal
0.001,0.543
0.002,0.512
...
```
Or for I-V data:
```
voltage,current
0.0,28.3
0.1,28.1
...
```
"""))
cells.append(code("""\
# ── Load custom CSV ────────────────────────────────────────────────────────
# Uncomment and edit the path below to analyse your own data:

# df_custom = pd.read_csv('your_data.csv')
# print(df_custom.head(10))
# print(df_custom.describe())

# Example: run FFT on the first two columns (time, signal)
# t_c = df_custom.iloc[:, 0].values
# s_c = df_custom.iloc[:, 1].values
# fs_c = 1.0 / np.mean(np.diff(t_c))
# freqs_custom, mag_custom, _ = apply_fft(s_c, fs_c)
# plt.figure(figsize=(10,4))
# plt.plot(freqs_custom, mag_custom, color=COLORS['fft'])
# plt.xlabel('Frequency (Hz)'); plt.ylabel('Magnitude')
# plt.title('Custom Data FFT Spectrum'); plt.grid(True); plt.show()

print("Custom CSV section ready. Uncomment the lines above to use your data.")
"""))

# ─── Cell 11 — Final Summary ─────────────────────────────────────────────────
cells.append(md("## ✅ Section 8 — Final Summary"))
cells.append(code("""\
print("=" * 58)
print("  SPECTRAL DATA ANALYSER — FINAL SUMMARY")
print("=" * 58)
print()
print("  SIGNAL ANALYSIS")
print(f"    Sampling frequency   : {FS:.0f} Hz")
print(f"    Signal duration      : {DURATION:.2f} s")
print(f"    Frequency components : {FREQ_COMPONENTS} Hz")
print(f"    SNR before filter    : {snr_before:.2f} dB")
print(f"    SNR after  filter    : {snr_after:.2f} dB")
print(f"    Improvement          : {snr_gain:.1f}%")
print(f"    Cutoff frequency     : {CUTOFF_HZ} Hz")
print()
print("  I-V DEVICE ANALYSIS")
print(df.to_string(index=False))
print()
print("  OUTPUT FILES GENERATED")
for f in sorted(os.listdir('output_plots')):
    print(f"    output_plots/{f}")
print()
print("  Analysis complete ✓")
print("=" * 58)
"""))

# ─── Assemble notebook ───────────────────────────────────────────────────────
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "cells": cells
}

with open("spectral_analysis_notebook.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)

print("✅ Notebook generated: spectral_analysis_notebook.ipynb")
