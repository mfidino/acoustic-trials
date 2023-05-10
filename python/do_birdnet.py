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
import csv
import sys

parser = argparse.ArgumentParser(description="Process all .wav files in a folder and its sub-folders.")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")
parser.add_argument("--output_folder", type = str, default = "snips", help="the folder to save the acoustic files, spectrograms, and optional csv.")
parser.add_argument("--csv_name", type = str, default = None, help="name of csv to write detections to, no need to add .csv to the end.")
parser.add_argument("--from_mixit", type=str, default = "True", help='Whether you processed files with mixit. Defaults to True.')

args = parser.parse_args()
args.from_mixit = eval(args.from_mixit)


input_folder = args.input_folder
### TO CHANGE: Input month, day, and year as argument based on visit.visitDateTime

if not os.path.exists(args.output_folder):
    os.makedirs(args.output_folder)

if args.csv_name is not None:
    csv_path = f"{args.output_folder}/{args.csv_name}.csv"
    with open(csv_path, mode='w', newline='') as csv_file:
        fieldnames = ['path', 'common_name', 'scientific_name', 'start_time', 'end_time', 'confidence']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

# a dictionary to store the lat / long of each city.
ll_dict = {
    'ATGA': {'lat': 33.7490, 'lon': -84.3880},
    'CHIL': {'lat': 41.8781, 'lon': -87.6298},
    'IOIO': {'lat': 41.6611, 'lon': -91.5302},
    'JAMS': {'lat': 32.2988, 'lon': -90.1848},
    'NACA': {'lat': 38.9072, 'lon': -77.0369},
    'OCCA': {'lat': 33.7701, 'lon': -118.1937},
    'PHAZ': {'lat': 33.4484, 'lon': -112.0740},
    'SCUT': {'lat': 40.7608, 'lon': -111.8910},
    'SEWA': {'lat': 47.6062, 'lon': -122.3321},
    'SLMO': {'lat': 38.6270, 'lon': -90.1994},
    'TOON': {'lat': 43.6532, 'lon': -79.3832},
    'WIDE': {'lat': 39.7391, 'lon': -75.5398}
}

# define output directory
#output_dir = "output"

# loop through each subdirectory and its files
for entry in os.listdir(input_folder):
    entry_path = os.path.join(input_folder, entry)
    print('entry')
    print(entry)
    if entry == 'output':
        continue
    if entry in ['ATGA', 'CHIL', 'IOIO', 'JAMS', 'NACA','OCCA', 'PHAZ','SCUT','SEWA','SLMO','TOON']:
        continue
    if os.path.isdir(entry_path):
        for root, dirs, files in os.walk(entry_path):
            detections_list = []
            main_recording = None
            main_recording_path = None
            for file in files:
                if file.endswith('.wav'):
                    # define paths
                    input_file = os.path.join(root, file)
                    # get date/time
                    tmp_name = os.path.basename(input_file)
                    date_str = tmp_name.split(".")[0]

                    
                    # create Recording object
                    ### TO CHANGE: Get lat/lon from CameraLocations.utmEast and CameraLocations.utmNorth
                    #  will also need to convert utm to lat/long so we'll also need 
                    #  CameraLocations.utmZone
                    recording = Recording(
                        analyzer,
                        input_file,
                        lat=ll_dict[entry]['lat'],
                        lon=ll_dict[entry]['lon'],
                        date=datetime(
                            year=int(date_str[:4]),
                             month=int(date_str[4:6]),
                              day=int(date_str[6:8])
                            ),
                        min_conf=0.25,
                    )
                    recording.analyze()

        
                    # save detections as spectrogram image
                    #recording.extract_detections_as_spectrogram(directory=output_file_dir)
        
                    detections_list.append(recording.detections)
                    if args.from_mixit:
                        if not re.match(r'^.*_source\d+\.wav$', input_file):
                            main_recording = recording
                            main_recording_path = input_file
                            print(main_recording_path)
                    else:
                        highest_confidence = 0
                        best_common_name = ''
                        best_scientific_name = ''
                        best_start = 0
                        best_end = 0
                        for detection in recording.detections:
                            # Loop through each detection in the current element
                            
                            if detection['confidence'] > highest_confidence:
                                highest_confidence = detection["confidence"]
                                best_common_name = detection["common_name"]
                                best_scientific_name = detection["scientific_name"]
                                best_start = detection["start_time"]
                                best_end = detection["end_time"]
                        if highest_confidence == 0:
                            continue

                        if best_start > 0:
                            start_sec = int(best_start + 0)
                        else:
                            start_sec = int(0)
                        if best_end < recording.duration:
                            end_sec = int(best_end + 0)
                        else:
                            end_sec = int(recording.duration)
                        tmp_audio = pydub.AudioSegment.from_file(input_file)

                        extract_array = recording.ndarray[
                            start_sec * tmp_audio.frame_rate : end_sec * tmp_audio.frame_rate
                        ]
                        channels = 1
                        data = np.int16(extract_array * 2**15)  # Normalized to -1, 1
                        audio = pydub.AudioSegment(
                            data.tobytes(),
                            frame_rate=tmp_audio.frame_rate,
                            sample_width=2,
                            channels=channels,
                        )
                        # root has the whole filepath
                        tmp_dir = f"{args.output_folder}/{(root.split('/')[-1])}"
                        if not os.path.exists(tmp_dir):
                            os.makedirs(tmp_dir)
                        audio_path = f"{tmp_dir}/{recording.filestem}_{start_sec}s-{end_sec}s.wav"
                        audio.export(audio_path, format="wav")
                        jpg_path = f"{tmp_dir}/{recording.filestem}_{start_sec}s-{end_sec}s.jpg"
                        plt.specgram(extract_array, Fs=tmp_audio.frame_rate,cmap="nipy_spectral") 
                        plt.ylim(top=14000)
                        plt.ylabel("frequency kHz")
                        plt.title(f"{recording.filename} ({start_sec}s - {end_sec}s). {(best_common_name)}({(round(highest_confidence,2))})", fontsize=10)
                        plt.savefig(jpg_path, dpi=144)
                        plt.close()
                        if args.csv_name is not None:
                            with open(csv_path, mode='a', newline='') as csv_file:
                                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                                writer.writerow(
                                    {'path': input_file,
                                     'common_name': best_common_name,
                                      'scientific_name': best_scientific_name,
                                       'start_time': start_sec,
                                        'end_time': end_sec,
                                     'confidence': highest_confidence})  

                        
        
            # Define a dictionary to store the grouped detections
            grouped_detections = {}
            grouped_detections_list = []
            
            if args.from_mixit:
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
                            tmp_dir = f"{args.output_folder}/{(root.split('/')[-1])}"
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
                                # write csv if present
                            if args.csv_name is not None:
                                with open(csv_path, mode='a', newline='') as csv_file:
                                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                                    writer.writerow(
                                        {'path': main_recording_path,
                                         'common_name': detection['common_name'],
                                          'scientific_name': detection['scientific_name'],
                                           'start_time': start_sec,
                                            'end_time': end_sec,
                                         'confidence': detection['confidence']})                                          
if args.csv_name is not None:
    csv_file.close()