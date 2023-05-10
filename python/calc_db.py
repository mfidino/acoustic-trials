import os
import argparse
import wave
import math
import numpy as np

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

parser = argparse.ArgumentParser(description="Process all .wav files in a folder and its sub-folders.")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")
parser.add_argument("--csv_name", type = str, default = 'mean_SPL', help="name of csv to write mean SPL to.")

args = parser.parse_args()

if not os.path.exists(args.output_folder):
    os.makedirs(args.output_folder)

csv_path = f"{args.output_folder}/{args.csv_name}.csv"
with open(csv_path, mode='w', newline='') as csv_file:
    fieldnames = ['path', 'mean_SPL']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

 for entry in os.listdir(input_folder):
    entry_path = os.path.join(input_folder, entry)
    if os.path.isdir(entry_path):
    	for root, dirs, files in os.walk(entry_path):
            for file in files:
                if file.endswith('.wav'):
                	with open(csv_path, mode='a', newline='') as csv_file:
                		writer = csv.DictWriter(csv_file, filenames=fieldnames)
                		writer.writerow(
                			{
                			'path': os.path.join(root, file),
                			'mean_SPL': calculate_mean_SPL(file)
                			})

csv_file.close()

