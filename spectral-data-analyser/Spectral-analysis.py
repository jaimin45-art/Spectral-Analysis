"""
=============================================================================
  Spectral Data Analyser — Solar Cell & Optoelectronic Signal Processing
  Author : Modi Jaimin Dixitkumar
  Version: 1.0.0
=============================================================================

DESCRIPTION
-----------
This tool simulates, analyses, and visualises spectral/time-series data
representative of thin-film optoelectronic device measurements.

It covers:
  1. Signal generation  — synthetic photocurrent signal with noise
  2. FFT analysis       — frequency domain decomposition & noise identification
  3. Noise filtering    — low-pass filter to recover clean signal
  4. Peak detection     — automatic identification of dominant frequencies
  5. I-V curve loading  — batch analysis of device I-V data from CSV
  6. Statistical report — SNR, THD, dominant frequency, peak metrics

Run this file directly:
    python spectral_analysis.py

Or import individual modules in your own scripts:
    from spectral_analysis import generate_signal, apply_fft, lowpass_filter
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')   # headless backend — works without a display
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import signal as scipy_signal
from scipy.optimize import curve_fit

# ── Global plot style ─────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "text.color":       "#c9d1d9",
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "lines.linewidth":  1.6,
    "font.family":      "monospace",
    "axes.titlesize":   11,
    "axes.labelsize":   9,
})

COLORS = {
    "signal":    "#58a6ff",   # blue
    "noisy":     "#ff7b72",   # red
    "filtered":  "#3fb950",   # green
    "fft":       "#d2a8ff",   # purple
    "peak":      "#f0883e",   # orange
    "iv":        "#79c0ff",   # light blue
    "power":     "#56d364",   # bright green
}

OUTPUT_DIR = "output_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
#  SECTION 1 — SIGNAL GENERATION
# =============================================================================

def generate_signal(
    duration: float = 1.0,
    fs: float = 1000.0,
    freqs: list = None,
    amplitudes: list = None,
    noise_level: float = 0.3,
    seed: int = 42
) -> tuple:
    """
    Generate a synthetic photocurrent-like time-domain signal.

    Parameters
    ----------
    duration    : signal duration in seconds
    fs          : sampling frequency in Hz
    freqs       : list of component frequencies (Hz)
    amplitudes  : list of amplitudes for each frequency component
    noise_level : standard deviation of Gaussian noise added
    seed        : random seed for reproducibility

    Returns
    -------
    t       : time array (s)
    clean   : noise-free signal (a.u.)
    noisy   : signal + Gaussian noise (a.u.)
    """
    if freqs is None:
        freqs = [10, 25, 60, 120]       # Hz — representative harmonics
    if amplitudes is None:
        amplitudes = [1.0, 0.5, 0.25, 0.1]

    rng   = np.random.default_rng(seed)
    t     = np.linspace(0, duration, int(fs * duration), endpoint=False)
    clean = sum(a * np.sin(2 * np.pi * f * t) for f, a in zip(freqs, amplitudes))
    noise = rng.normal(0, noise_level, size=t.shape)
    noisy = clean + noise

    return t, clean, noisy


# =============================================================================
#  SECTION 2 — FFT ANALYSIS
# =============================================================================

def apply_fft(signal_data: np.ndarray, fs: float) -> tuple:
    """
    Compute the single-sided FFT magnitude spectrum.

    Parameters
    ----------
    signal_data : 1-D time-domain array
    fs          : sampling frequency (Hz)

    Returns
    -------
    freqs  : frequency array (Hz), positive side only
    mag    : magnitude spectrum (normalised)
    phase  : phase spectrum (radians)
    """
    N     = len(signal_data)
    fft_c = np.fft.rfft(signal_data)
    freqs = np.fft.rfftfreq(N, d=1.0 / fs)
    mag   = np.abs(fft_c) * 2 / N          # two-sided → one-sided correction
    phase = np.angle(fft_c)
    return freqs, mag, phase


def detect_peaks(freqs: np.ndarray, mag: np.ndarray, threshold: float = 0.05) -> tuple:
    """
    Detect dominant frequency peaks above a magnitude threshold.

    Returns
    -------
    peak_freqs : array of peak frequencies (Hz)
    peak_mags  : corresponding magnitudes
    """
    peak_idx, props = scipy_signal.find_peaks(
        mag, height=threshold * mag.max(), distance=5
    )
    return freqs[peak_idx], mag[peak_idx]


# =============================================================================
#  SECTION 3 — NOISE FILTERING
# =============================================================================

def lowpass_filter(
    noisy_signal: np.ndarray,
    fs: float,
    cutoff: float = 80.0,
    order: int = 5
) -> np.ndarray:
    """
    Apply a Butterworth low-pass filter to remove high-frequency noise.

    Parameters
    ----------
    noisy_signal : input time-domain signal
    fs           : sampling frequency (Hz)
    cutoff       : -3 dB cutoff frequency (Hz)
    order        : filter order (higher = steeper roll-off)

    Returns
    -------
    filtered : cleaned signal array
    """
    nyq  = fs / 2.0
    norm = cutoff / nyq
    b, a = scipy_signal.butter(order, norm, btype='low', analog=False)
    return scipy_signal.filtfilt(b, a, noisy_signal)


# =============================================================================
#  SECTION 4 — STATISTICAL METRICS
# =============================================================================

def compute_snr(clean: np.ndarray, noisy: np.ndarray) -> float:
    """Signal-to-Noise Ratio in dB."""
    noise   = noisy - clean
    sig_pow = np.mean(clean ** 2)
    noi_pow = np.mean(noise ** 2)
    return 10 * np.log10(sig_pow / noi_pow) if noi_pow > 0 else float('inf')


def compute_thd(freqs: np.ndarray, mag: np.ndarray, fundamental: float) -> float:
    """
    Total Harmonic Distortion (%).
    Ratio of RMS of harmonics to fundamental amplitude.
    """
    tol   = 2.0   # Hz tolerance window
    f_idx = np.argmin(np.abs(freqs - fundamental))
    f_amp = mag[f_idx]

    harmonic_power = 0.0
    for h in range(2, 8):
        hf    = fundamental * h
        hidx  = np.argmin(np.abs(freqs - hf))
        if freqs[hidx] < freqs[-1]:
            harmonic_power += mag[hidx] ** 2

    thd = (np.sqrt(harmonic_power) / f_amp) * 100 if f_amp > 0 else 0.0
    return thd


def snr_improvement(original_noisy, clean, filtered) -> float:
    """Percentage SNR improvement after filtering."""
    snr_before = compute_snr(clean, original_noisy)
    snr_after  = compute_snr(clean, filtered)
    return ((snr_after - snr_before) / abs(snr_before)) * 100


# =============================================================================
#  SECTION 5 — I-V CURVE ANALYSIS
# =============================================================================

def generate_iv_data(
    n_devices: int = 5,
    voc_range: tuple = (0.6, 0.85),
    jsc_range: tuple = (15, 30),
    ff_range:  tuple = (0.60, 0.78),
    seed: int = 7
) -> pd.DataFrame:
    """
    Simulate I-V characteristic parameters for multiple thin-film devices.

    Returns a DataFrame with columns:
        Device, Voc(V), Jsc(mA/cm2), FF, PCE(%)
    """
    rng  = np.random.default_rng(seed)
    vocs = rng.uniform(*voc_range, n_devices)
    jscs = rng.uniform(*jsc_range, n_devices)
    ffs  = rng.uniform(*ff_range,  n_devices)
    pces = vocs * jscs * ffs / 100.0   # Pin assumed 100 mW/cm²

    df = pd.DataFrame({
        "Device":      [f"Dev-{i+1:02d}" for i in range(n_devices)],
        "Voc(V)":      np.round(vocs, 4),
        "Jsc(mA/cm2)": np.round(jscs, 4),
        "FF":          np.round(ffs,  4),
        "PCE(%)":      np.round(pces, 4),
    })
    return df


def iv_curve_points(voc: float, jsc: float, ff: float, n_points: int = 200) -> tuple:
    """
    Generate V and J arrays for a single-diode I-V curve.
    Uses simplified single-diode model (no series/shunt resistance).
    """
    V  = np.linspace(0, voc * 1.05, n_points)
    # Approximate: J = Jsc * (1 - exp((V - Voc) / (Vt * ideality)))
    Vt = 0.02585   # thermal voltage at 300 K
    m  = 1.3       # ideality factor
    J0 = jsc * np.exp(-voc / (m * Vt))   # saturation current approx
    J  = jsc - J0 * (np.exp(V / (m * Vt)) - 1)
    J  = np.clip(J, 0, None)
    return V, J


# =============================================================================
#  SECTION 6 — VISUALISATION
# =============================================================================

def plot_signal_analysis(t, clean, noisy, filtered, fs):
    """Figure 1: Time-domain comparison of clean / noisy / filtered signals."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    fig.suptitle("Figure 1 — Time-Domain Signal Analysis", color="#c9d1d9", fontsize=13, y=1.01)

    data  = [clean, noisy, filtered]
    cols  = [COLORS["signal"], COLORS["noisy"], COLORS["filtered"]]
    lbls  = ["Clean Signal (ground truth)", "Noisy Signal (raw measurement)", "Filtered Signal (Butterworth LP)"]

    for ax, sig, col, lbl in zip(axes, data, cols, lbls):
        ax.plot(t, sig, color=col, alpha=0.85, linewidth=0.9)
        ax.set_ylabel("Amplitude (a.u.)", fontsize=8)
        ax.set_title(lbl, color=col, fontsize=9, loc="left")
        ax.grid(True)

    axes[-1].set_xlabel("Time (s)")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig1_time_domain.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [saved] {path}")
    return path


def plot_fft_spectrum(freqs, mag_noisy, mag_filtered, peak_freqs, peak_mags):
    """Figure 2: FFT magnitude spectrum before and after filtering."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle("Figure 2 — FFT Frequency Spectrum", color="#c9d1d9", fontsize=13)

    ax1.plot(freqs, mag_noisy, color=COLORS["noisy"], alpha=0.8, linewidth=0.8, label="Noisy")
    ax1.scatter(peak_freqs, peak_mags, color=COLORS["peak"], zorder=5, s=40, label="Peaks")
    for pf, pm in zip(peak_freqs, peak_mags):
        ax1.annotate(f"{pf:.1f} Hz", xy=(pf, pm), xytext=(pf + 5, pm + 0.02),
                     fontsize=7, color=COLORS["peak"])
    ax1.set_ylabel("Magnitude (a.u.)")
    ax1.set_title("Before Filtering", color=COLORS["noisy"], fontsize=9, loc="left")
    ax1.legend(fontsize=8)
    ax1.grid(True)

    ax2.plot(freqs, mag_filtered, color=COLORS["filtered"], alpha=0.8, linewidth=0.8)
    ax2.set_ylabel("Magnitude (a.u.)")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_title("After Low-Pass Filtering (cutoff = 80 Hz)", color=COLORS["filtered"], fontsize=9, loc="left")
    ax2.grid(True)
    ax2.set_xlim(0, 200)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig2_fft_spectrum.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [saved] {path}")
    return path


def plot_iv_curves(df: pd.DataFrame):
    """Figure 3: I-V and Power-Voltage curves for all simulated devices."""
    n   = len(df)
    fig = plt.figure(figsize=(14, 6))
    gs  = gridspec.GridSpec(1, 2, figure=fig, wspace=0.35)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    cmap   = plt.cm.plasma
    colors = [cmap(i / n) for i in range(n)]

    for i, row in df.iterrows():
        V, J = iv_curve_points(row["Voc(V)"], row["Jsc(mA/cm2)"], row["FF"])
        P    = V * J
        lbl  = f"{row['Device']} | PCE={row['PCE(%)']:.2f}%"
        ax1.plot(V, J, color=colors[i], label=lbl)
        ax2.plot(V, P, color=colors[i])

    ax1.set_xlabel("Voltage (V)")
    ax1.set_ylabel("Current Density (mA/cm²)")
    ax1.set_title("I-V Characteristics", color="#c9d1d9")
    ax1.legend(fontsize=7, loc="lower left")
    ax1.grid(True)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)

    ax2.set_xlabel("Voltage (V)")
    ax2.set_ylabel("Power Density (mW/cm²)")
    ax2.set_title("Power-Voltage Curves", color="#c9d1d9")
    ax2.grid(True)
    ax2.set_xlim(left=0)
    ax2.set_ylim(bottom=0)

    fig.suptitle("Figure 3 — Thin-Film Device I-V & P-V Analysis", color="#c9d1d9", fontsize=13)
    path = os.path.join(OUTPUT_DIR, "fig3_iv_curves.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [saved] {path}")
    return path


def plot_device_metrics(df: pd.DataFrame):
    """Figure 4: Bar charts comparing Voc, Jsc, FF, and PCE across devices."""
    metrics = ["Voc(V)", "Jsc(mA/cm2)", "FF", "PCE(%)"]
    units   = ["V", "mA/cm²", "—", "%"]
    cols    = [COLORS["signal"], COLORS["noisy"], COLORS["filtered"], COLORS["peak"]]

    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    axes = axes.flatten()
    fig.suptitle("Figure 4 — Device Performance Metrics Comparison", color="#c9d1d9", fontsize=13)

    for ax, metric, unit, col in zip(axes, metrics, units, cols):
        bars = ax.bar(df["Device"], df[metric], color=col, alpha=0.8, edgecolor="#30363d")
        ax.set_title(metric, color=col, fontsize=10)
        ax.set_ylabel(f"Value ({unit})")
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df["Device"], rotation=30, ha="right", fontsize=8)
        ax.grid(True, axis="y")
        for bar, val in zip(bars, df[metric]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=7, color="#c9d1d9")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig4_device_metrics.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [saved] {path}")
    return path


# =============================================================================
#  SECTION 7 — CSV I/O
# =============================================================================

def save_iv_csv(df: pd.DataFrame, path: str = "output_plots/device_iv_data.csv"):
    df.to_csv(path, index=False)
    print(f"  [saved] {path}")


def load_custom_csv(filepath: str) -> pd.DataFrame:
    """
    Load a user-provided CSV file for custom analysis.
    Expected columns: time, signal  (or  voltage, current)
    Returns a DataFrame — use df.head() to inspect.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded '{filepath}' — shape: {df.shape}")
    print(df.describe())
    return df


# =============================================================================
#  SECTION 8 — MAIN RUNNER
# =============================================================================

def print_report(t, clean, noisy, filtered, freqs_n, mag_n, peak_freqs, peak_mags, df):
    """Print a formatted statistical summary to the terminal."""
    snr_b  = compute_snr(clean, noisy)
    snr_a  = compute_snr(clean, filtered)
    snr_imp = snr_improvement(noisy, clean, filtered)
    thd    = compute_thd(freqs_n, mag_n, fundamental=peak_freqs[0] if len(peak_freqs) > 0 else 10)

    print("\n" + "="*62)
    print("  SPECTRAL ANALYSIS REPORT")
    print("="*62)
    print(f"  Signal duration       : {t[-1]:.2f} s")
    print(f"  Sampling frequency    : 1000 Hz")
    print(f"  Total samples         : {len(t)}")
    print(f"  SNR (before filter)   : {snr_b:.2f} dB")
    print(f"  SNR (after filter)    : {snr_a:.2f} dB")
    print(f"  SNR improvement       : {snr_imp:.1f}%")
    print(f"  THD                   : {thd:.2f}%")
    print(f"  Dominant frequency    : {peak_freqs[0]:.1f} Hz" if len(peak_freqs) else "  No peaks found")
    print(f"  Peaks detected        : {len(peak_freqs)}")
    print()
    print("  I-V DEVICE SUMMARY")
    print("-"*62)
    print(df.to_string(index=False))
    best = df.loc[df["PCE(%)"].idxmax()]
    print(f"\n  Best device: {best['Device']}  |  PCE = {best['PCE(%)']:.2f}%")
    print("="*62 + "\n")


def run_full_analysis():
    print("\n  Spectral Data Analyser — v1.0.0")
    print("  Author: Modi Jaimin Dixitkumar\n")

    # ── 1. Generate signal ───────────────────────────────────────────
    print("[1/6] Generating synthetic photocurrent signal...")
    FS                   = 1000.0
    t, clean, noisy      = generate_signal(duration=1.0, fs=FS, noise_level=0.35)

    # ── 2. Filter ────────────────────────────────────────────────────
    print("[2/6] Applying Butterworth low-pass filter (cutoff=80 Hz)...")
    filtered             = lowpass_filter(noisy, FS, cutoff=80.0, order=5)

    # ── 3. FFT ───────────────────────────────────────────────────────
    print("[3/6] Computing FFT spectra...")
    freqs_n, mag_n, _    = apply_fft(noisy,    FS)
    freqs_f, mag_f, _    = apply_fft(filtered, FS)
    peak_freqs, peak_mags = detect_peaks(freqs_n, mag_n)

    # ── 4. I-V data ──────────────────────────────────────────────────
    print("[4/6] Generating I-V device data...")
    df = generate_iv_data(n_devices=5)
    save_iv_csv(df)

    # ── 5. Plots ─────────────────────────────────────────────────────
    print("[5/6] Generating plots (saved to output_plots/)...")
    plot_signal_analysis(t, clean, noisy, filtered, FS)
    plot_fft_spectrum(freqs_n, mag_n, mag_f, peak_freqs, peak_mags)
    plot_iv_curves(df)
    plot_device_metrics(df)

    # ── 6. Report ────────────────────────────────────────────────────
    print("[6/6] Computing statistical report...")
    print_report(t, clean, noisy, filtered, freqs_n, mag_n, peak_freqs, peak_mags, df)

    print("  All done! Open 'output_plots/' to view the figures.\n")


if __name__ == "__main__":
    run_full_analysis()