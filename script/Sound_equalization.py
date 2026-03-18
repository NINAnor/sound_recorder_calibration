# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 09:07:49 2026

@author: ioriov
"""

import numpy as np
import pandas as pd
import scipy.signal as signal
import scipy.interpolate as interp
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

# =====================================
# USER INPUT
# =====================================

# Excel SLM data
file_path = "C:\\Users\\ioriov\\Desktop\\LxT_0003857-20260212 180718-LxT_Data.036.xlsx"
sheet_name = "Profilo storico"

# Time window for averaging from the test
start_time_str = "2026-03-05 11:46:05"
end_time_str   = "2026-03-05 11:46:15"

# 1/3 octave center frequencies (Hz)
frequencies = np.array([
    6.3,8,10,12.5,16,20,
    25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200,
    250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
    2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
    12500, 16000, 20000
])

reference_frequency = 1000        # Hz normalization anchor
filter_length = 4097              # must be odd (Type I FIR)
max_boost_db = 30                 # boost limitation

input_wav = "C:\\Users\\ioriov\\Desktop\\New files\\Calibrazione_Whitenoise.wav"
output_wav = "C:\\Users\\ioriov\\Desktop\\New files\\equalized_white_noise.wav"

# Columns to drop (R: 1,2,3,5,6,7,44,45,46 => Python zero-based)
cols_to_drop = [0,1,2,4,5,6,43,44,45]

# ==========================================================
# STEP 1 — READ AND PROCESS SLM EXCEL DATA
# ==========================================================

dat = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

# Drop unwanted columns
dat2 = dat.drop(dat.columns[cols_to_drop], axis=1)

# Parse timestamps
dat2['Tempo'] = pd.to_datetime(dat2['Tempo'], format="%Y-%m-%d %H:%M:%S", utc=True)

# Filter time window
start_time = pd.to_datetime(start_time_str, utc=True)
end_time   = pd.to_datetime(end_time_str, utc=True)
test = dat2[(dat2['Tempo'] >= start_time) & (dat2['Tempo'] <= end_time)]

# Compute mean SLM values for columns 2–37 (1/3 octave bands)
slm_means = test.iloc[:, 1:37].mean().to_numpy()

# ==========================================================
# STEP 2 — NORMALIZE SLM VALUES
# ==========================================================

# Normalize relative to 1 kHz
ref_idx = np.where(frequencies == reference_frequency)[0][0]
levels_db = slm_means - slm_means[ref_idx]

# ==========================================================
# STEP 3 — BUILD INVERSE RESPONSE
# ==========================================================

correction_db = -levels_db
correction_db = np.clip(correction_db, -max_boost_db, max_boost_db)
correction_gain = 10 ** (correction_db / 20)

# ==========================================================
# STEP 4 — LOG-FREQUENCY INTERPOLATION
# ==========================================================

# Log-frequency interpolation (important!)
log_freq = np.log10(frequencies)

# Normalized frequency (0 to 1 for firwin2)
# freq_norm = frequencies / (fs / 2)

# Interpolate gain curve over FFT bins
interp_func = interp.interp1d(
    log_freq,
    correction_gain,
    kind='linear',
    fill_value="extrapolate"
)

# Load audio
fs, audio = wav.read(input_wav)
nyquist = fs / 2

# Dense frequency grid
dense_freq = np.linspace(20, fs/2, 2000)
dense_log = np.log10(dense_freq)
dense_gain = interp_func(dense_log)

dense_gain = np.clip(dense_gain, 10**(-max_boost_db/20), 10**(max_boost_db/20))

dense_freq_norm = dense_freq / nyquist

# Ensure boundaries
dense_freq_norm[0] = 0.0
dense_freq_norm[-1] = 1.0

# ==========================================================
# STEP 5 — DESIGN FIR FILTER
# ==========================================================

# Ensure odd length
if filter_length % 2 == 0:
    filter_length += 1
    
fir_coeff = signal.firwin2(
    filter_length,
    dense_freq_norm,
    dense_gain
)

# ==========================================================
# STEP 6 — APPLY FILTER
# ==========================================================

if audio.ndim > 1:
    audio = audio.mean(axis=1)
    
audio_corrected = signal.fftconvolve(audio, fir_coeff, mode='same')

# Normalize
audio_corrected /= np.max(np.abs(audio_corrected))
audio_corrected *= 0.9

# =====================================
# STEP 7 - SAVE OUTPUT
# =====================================

wav.write(output_wav, fs, audio_corrected.astype(np.float32))

# ==========================================================
# STEP 8 — PLOT ORIGINAL, COMPENSATION, AND COMBINED
# ==========================================================

# Frequency response of FIR filter
w, h = signal.freqz(fir_coeff, worN=8192)
freq_fir = w * fs / (2*np.pi)
gain_db = 20 * np.log10(np.abs(h))

# Interpolate original measured response onto FIR frequency axis
interp_speaker = interp.interp1d(
    frequencies,
    levels_db,
    kind='linear',
    fill_value="extrapolate"
)

speaker_interp_db = interp_speaker(freq_fir)

# Predicted combined response
combined_db = speaker_interp_db + gain_db

# Plot
plt.figure(figsize=(11,8))

# ±6 dB tolerance band
plt.fill_between(freq_fir, -6, 6, alpha=0.2, label="±6 dB tolerance")

# Plot curves
plt.semilogx(freq_fir, speaker_interp_db, label="Original Speaker Response")
plt.semilogx(freq_fir, gain_db, label="Compensation FIR")
plt.semilogx(freq_fir, combined_db, label="Predicted Combined")

plt.axhline(0, linestyle='--')
plt.xlim(20, fs/2)

plt.title("Speaker Equalization")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (dB)")
plt.legend()
plt.grid()
plt.show()

print("Calibration complete. Compensation FIR applied and plotted.")