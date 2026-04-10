# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 18:42:28 2026

@author: ioriov
"""

import numpy as np
import pandas as pd
import scipy.signal as signal
import scipy.interpolate as interp
from scipy.io import savemat

def compute_equalization_filter_from_slm(
    excel_file: str,
    sheet_name: str,
    start_time_str: str,
    end_time_str: str,
    frequencies: np.ndarray,
    reference_frequency: float,
    filter_length: int,
    max_boost_db: float,
    output_mat_file: str,
    cols_to_drop: list
):
    """
    Compute FIR equalization filter coefficients (B, A) based on SLM 1/3-octave
    band data rather than a reference audio recording.

    Parameters
    ----------
    excel_file : str
        Path to the Excel file containing SLM band-level data.
    sheet_name : str
        Worksheet name inside the Excel file.
    start_time_str : str
        Start of averaging window (e.g. '2026-03-05 11:46:05').
    end_time_str : str
        End of averaging window (e.g. '2026-03-05 11:46:15').
    frequencies : np.ndarray
        Array of 1/3-octave band center frequencies (Hz).
    reference_frequency : float
        Frequency used for normalization (e.g., 1000 Hz).
    filter_length : int
        Order+1 of the FIR filter (must be odd).
    max_boost_db : float
        Maximum allowed magnitude boost (dB limit).
    output_mat_file : str
        Output .mat filename to save {"B", "A"}.
    cols_to_drop : list
        Column indices to drop from Excel input.

    Returns
    -------
    B : numpy.ndarray
        FIR numerator coefficients.
    A : numpy.ndarray
        FIR denominator (always [1.0]).
    """

    # ==========================================================
    # STEP 1 — READ AND PROCESS SLM EXCEL DATA
    # ==========================================================
    dat = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')

    # Drop unused columns
    dat2 = dat.drop(dat.columns[cols_to_drop], axis=1)

    # Parse timestamps
    dat2['Tempo'] = pd.to_datetime(dat2['Tempo'], utc=True)

    # Filter desired time window
    start_time = pd.to_datetime(start_time_str, utc=True)
    end_time   = pd.to_datetime(end_time_str, utc=True)

    test = dat2[(dat2['Tempo'] >= start_time) & (dat2['Tempo'] <= end_time)]

    # Average 1/3-octave band levels
    slm_means = test.iloc[:, 1:1+len(frequencies)].mean().to_numpy()

    # ==========================================================
    # STEP 2 — NORMALIZE SLM VALUES
    # ==========================================================
    ref_idx = np.where(frequencies == reference_frequency)[0][0]
    levels_db = slm_means - slm_means[ref_idx]

    # ==========================================================
    # STEP 3 — INVERSE RESPONSE (what your FIR must correct)
    # ==========================================================
    correction_db = -levels_db
    correction_db = np.clip(correction_db, -max_boost_db, max_boost_db)
    correction_gain = 10 ** (correction_db / 20)

    # ==========================================================
    # STEP 4 — LOG-FREQUENCY INTERPOLATION
    # ==========================================================
    log_freq = np.log10(frequencies)

    interp_func = interp.interp1d(
        log_freq,
        correction_gain,
        kind='linear',
        fill_value="extrapolate"
    )

    # Create a dense frequency grid (20 Hz → 20 kHz)
    dense_freq = np.linspace(20, 20000, 2000)
    dense_log = np.log10(dense_freq)
    dense_gain = interp_func(dense_log)

    dense_gain = np.clip(
        dense_gain,
        10 ** (-max_boost_db / 20),
        10 ** ( max_boost_db / 20)
    )

    # Normalize to Nyquist = 1 for firwin2
    dense_freq_norm = dense_freq / dense_freq.max()
    dense_freq_norm[0] = 0.0
    dense_freq_norm[-1] = 1.0

    # ==========================================================
    # STEP 5 — DESIGN FIR FILTER (firwin2)
    # ==========================================================
    if filter_length % 2 == 0:
        filter_length += 1  # ensure odd length

    B = signal.firwin2(
        filter_length,
        dense_freq_norm,
        dense_gain
    )

    A = np.array([1.0])

    # ==========================================================
    # STEP 6 — SAVE OUTPUT (.mat file)
    # ==========================================================
    savemat(output_mat_file, {"B": B, "A": A})

    return B, A

# ==================================================
# APPLY THE FUNCTION
# =================================================

frequencies = np.array([
    6.3,8,10,12.5,16,20,
    25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200,
    250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
    2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
    12500, 16000, 20000
])

cols_to_drop = [0,1,2,4,5,6,43,44,45]  # same as your script

B, A = compute_equalization_filter_from_slm(
    excel_file="C:/Users/.../LxT_sound_equalization_curve.xlsx",
    sheet_name="Profilo storico",
    start_time_str="2026-03-05 11:46:05",
    end_time_str="2026-03-05 11:46:15",
    frequencies=frequencies,
    reference_frequency=1000,
    filter_length=4097,
    max_boost_db=30,
    output_mat_file="Filter_deviceZZZ_from_SLM.mat",
    cols_to_drop=cols_to_drop
)

print("Equalization filter computed!")
print("B (first 10 coefficients):", B[:10])
print("A:", A)
