from scipy.io import wavfile

sample_rate, data = wavfile.read('/home/julia.wiel/Code/sound_recorder_calibration/data/gdrive_calib/data/Audio/SMA/SMA07591/Data/SMA07591_20260207_160351.wav')
print("Sample rate:", sample_rate)
print("Data shape:", data.shape)