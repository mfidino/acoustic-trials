from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import os
import argparse
import re
import json
import numpy as np 
import pydub
import matplotlib.pyplot as plt

SAMPLE_RATE = 48000

parser = argparse.ArgumentParser(description="Process all .wav files in a folder and its sub-folders.")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")
args = parser.parse_args()

input_folder = args.input_folder

# get the date/time info from the folder
parts = input_folder.split("-")
date_str = parts[-1]  # get the last element
### TO CHANGE: Input month, day, and year as argument based on visit.visitDateTime
file_month = int(date_str[:2])
file_day = int(date_str[2:4])
file_year = int(date_str[4:])

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

# define output directory
#output_dir = "output"

# loop through each subdirectory and its files
for root, dirs, files in os.walk(input_folder):
    detections_list = []
    main_recording = None
    for file in files:
        if file.endswith('.wav'):
            # define paths
            input_file = os.path.join(root, file)
            # create Recording object
            ### TO CHANGE: Get lat/lon from CameraLocations.utmEast and CameraLocations.utmNorth
            #  will also need to convert utm to lat/long so we'll also need 
            #  CameraLocations.utmZone
            recording = Recording(
                analyzer,
                input_file,
                lat=41.8414,
                lon=-88.1846,
                date=datetime(year=file_year, month=file_month, day=file_day),
                min_conf=0.25,
            )
            recording.analyze()

            # save detections as spectrogram image
            #recording.extract_detections_as_spectrogram(directory=output_file_dir)

            detections_list.append(recording.detections)
            if not re.match(r'^.*_source\d+\.wav$', input_file):
                main_recording = recording
                

    # Define a dictionary to store the grouped detections
    grouped_detections = {}
    grouped_detections_list = []
    

    # Loop through each element in the list
    for element in detections_list:
        # Loop through each detection in the current element
        for detection in element:
            # Extract the start and end times from the current detection
            start_time = detection['start_time']
            end_time = detection['end_time']
    
            # If this start/end time pair isn't in the dictionary yet, add it
            if (start_time, end_time) not in grouped_detections:
                grouped_detections[(start_time, end_time)] = {}
    
            # If this common name isn't in the dictionary yet, add it with its confidence value and scientific name
            common_name = detection['common_name']
            scientific_name = detection['scientific_name']
            confidence = detection['confidence']
            if common_name not in grouped_detections[(start_time, end_time)]:
                grouped_detections[(start_time, end_time)][common_name] = {'confidence': confidence, 'scientific_name': scientific_name}
    
            # If this common name is already in the dictionary, update its confidence value if the new value is higher
            else:
                if confidence > grouped_detections[(start_time, end_time)][common_name]['confidence']:
                    grouped_detections[(start_time, end_time)][common_name]['confidence'] = confidence
                    grouped_detections[(start_time, end_time)][common_name]['scientific_name'] = scientific_name
    
    for start_end, detections in grouped_detections.items():
        highest_confidence = 0
        best_common_name = ''
        best_scientific_name = ''
        for common_name, data in detections.items():
            if data['confidence'] > highest_confidence:
                highest_confidence = data['confidence']
                best_common_name = common_name
                best_scientific_name = data['scientific_name']
        grouped_detections_list.append({
            'common_name': best_common_name,
            'scientific_name': best_scientific_name,
            'start_time': int(start_end[0]),
            'end_time': int(start_end[1]),
            'confidence': float(highest_confidence)
        })
    print(grouped_detections_list)
    if main_recording is not None:
        for detection in grouped_detections_list:
                    # Skip if detection is under min_conf parameter.
                    # Useful for reducing the number of extracted detections.
                    if float(detection["confidence"]) < 0.0:
                        continue
        
                    start_sec = int(
                        detection["start_time"] - 0
                        if detection["start_time"] > 0
                        else 0
                    )
                    end_sec = int(
                        detection["end_time"] + 0
                        if detection["end_time"] + 0 < main_recording.duration
                        else main_recording.duration
                    )
        
                    extract_array = main_recording.ndarray[
                        start_sec * SAMPLE_RATE : end_sec * SAMPLE_RATE
                    ]
        
                    channels = 1
                    data = np.int16(extract_array * 2**15)  # Normalized to -1, 1
                    audio = pydub.AudioSegment(
                        data.tobytes(),
                        frame_rate=SAMPLE_RATE,
                        sample_width=2,
                        channels=channels,
                    )
                    # root has the whole filepath
                    tmp_dir = f"snips/{(root.split('/')[-1])}"
                    if not os.path.exists(tmp_dir):
                        os.makedirs(tmp_dir)
                    audio_path = f"{tmp_dir}/{main_recording.filestem}_{start_sec}s-{end_sec}s.wav"
                    audio.export(audio_path, format="wav")
                    jpg_path = f"{tmp_dir}/{main_recording.filestem}_{start_sec}s-{end_sec}s.jpg"
                    plt.specgram(extract_array, Fs=SAMPLE_RATE,cmap="nipy_spectral") 
                    plt.ylim(top=14000)
                    plt.ylabel("frequency kHz")
                    plt.title(f"{main_recording.filename} ({start_sec}s - {end_sec}s). {(detection['common_name'])}({(round(detection['confidence'],2))})", fontsize=10)
                    plt.savefig(jpg_path, dpi=144)
                    plt.close()
