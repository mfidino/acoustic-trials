import os
import argparse
import wave
import math
import numpy as np
import csv
from pydub import AudioSegment

def calculate_mean_SPL(sound_file_path, reference=20e-6):
    # Open the sound file
    with wave.open(sound_file_path, 'rb') as wav_file:
        # Read audio data
        audio_data = wav_file.readframes(wav_file.getnframes())
        # Convert audio data to numeric array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        # Calculate the root mean square (RMS)
        rms = np.sqrt(np.mean(np.square(audio_array)))
        # Calculate SPL
        mean_SPL = 20 * math.log10(rms / reference)
    
    return mean_SPL

def calculate_noise_levels(audio_path, start_freq, end_freq):
    try:
        audio = AudioSegment.from_file(audio_path)
        samples = np.array(audio.get_array_of_samples())

        # Apply Fourier Transform
        fft_data = np.fft.fft(samples)

        # Calculate magnitudes of each frequency bin
        magnitudes = np.abs(fft_data)

        sample_rate = audio.frame_rate
        start_bin = int(start_freq * len(magnitudes) / sample_rate)
        end_bin = int(end_freq * len(magnitudes) / sample_rate)

        noise_levels = []
        for i in range(start_bin, end_bin + 1):
            freq = i * sample_rate / len(magnitudes)
            level = 20 * np.log10(magnitudes[i])
            noise_levels.append((freq, level))

        return noise_levels
    except Exception as e:
        print(f"Error occurred while processing {audio_path}: {e}")
        return None

start_freq = 1000
end_freq = 4000

def calculate_average_noise_level(noise_levels, start_freq, end_freq):
    total_level = 0.0
    count = 0

    for freq, level in noise_levels:
        if start_freq <= freq <= end_freq:
            total_level += level
            count += 1

    if count > 0:
        average_level = total_level / count
        return average_level
    else:
        return None

parser = argparse.ArgumentParser(description="Process all .wav files in a folder and its sub-folders.")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")
parser.add_argument("--csv_name", type = str, default = 'mean_SPL', help="name of csv to write mean SPL to.")

args = parser.parse_args()
input_folder = args.input_folder

csv_path = f"{args.csv_name}.csv"
fieldnames = ['path', 'mean_dB']
with open(csv_path, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

for entry in os.listdir(input_folder):
   entry_path = os.path.join(input_folder, entry)
   if entry == 'output':
       continue
   if os.path.isdir(entry_path):
   	for root, dirs, files in os.walk(entry_path):
           for file in files:
               if file.endswith('.wav'):
                noise_levels = calculate_noise_levels(os.path.join(root, file), 1000, 4000)
                if noise_levels is not None:
                    average_level = calculate_average_noise_level(noise_levels, 1000, 4000)
                else:
                    average_level = None
               	with open(csv_path, mode='a', newline='') as csv_file:
               		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
               		writer.writerow(
               			{
               			'path': os.path.join(root, file),
               			'mean_dB': average_level
               			})

csv_file.close()

