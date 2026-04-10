# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 18:01:49 2026

@author: ioriov
"""

import librosa
import soundfile as sf
import os

def extract_snippets(
    audio_path: str,
    time_windows: list,
    output_folder: str = "snippets"
):
    """
    Extracts audio snippets based on time windows.

    Parameters:
    - audio_path: Path to input audio file
    - time_windows: List of tuples [(start_sec, end_sec, name), ...]
    - output_folder: Folder to save snippets
    """

    # Load audio
    audio, sr = librosa.load(audio_path, sr=48000)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for start, end, label in time_windows:
        start_ms = int(start * sr)
        end_ms = int(end * sr)

        # Extract slice
        snippet = audio[start_ms:end_ms]

        # Output path
        output_path = os.path.join(output_folder, calib_n + "_" + sensor_n + "_" + f"{label}.wav")

        # Save snippet
        sf.write(output_path, snippet, sr)
        print(f"Saved: {output_path}")


# ------------------------------
# Example usage
# ------------------------------
if __name__ == "__main__":
    sr = 48000
    
    calib_n = "Calib0039"
    sensor_n = "SM012"
    
    audio_path = "G:\\Drive condivisi\\Sound_recorder_calibration_DB\\data\\Audio\\" + calib_n + "\\" + calib_n + "_" + sensor_n + "_full_test.wav"
    output_folder = "G:\\Drive condivisi\\Sound_recorder_calibration_DB\\data\\Audio\\" + calib_n 

    # Define your windows: (start_time_sec, end_time_sec, label)
    time_windows = [
        (12, 30, "1kHz_a"),
        (44, 62, "1kHz_b"),
        (76, 95, "1kHz_c"),
        (108, 127, "whiteNoise_a"),
        (140, 159, "whiteNoise_b"),
        (172, 191, "whiteNoise_c")
    ]

    extract_snippets(audio_path, time_windows, output_folder)
