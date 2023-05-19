from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import pydub
import numpy as np 
import matplotlib.pyplot as plt
# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

input_file = "D:/uwin_sounds/split_audio/output/JAMS/Adam_Rohnke_-_JAMS_PAP_2648/20210416_060100_225.15/20210416_060100_225.15.wav"
recording = Recording(
    analyzer,
    input_file,
    #lat=41.8414,
    #lon=-88.1846,
    #date=datetime(year=2021, month=4, day=22), # use date or week_48
    min_conf=0.25,
)


recording.analyze()
#recording.extract_detections_as_spectrogram(directory='output')
print(recording.detections)

for detection in recording.detections:
    start_sec = 0#int(detection["start_time"]) + 0
    end_sec = 3#int(detection["end_time"]) + 0
    tmp_audio = pydub.AudioSegment.from_file(input_file)
    sample_rate = tmp_audio.frame_rate
    print(sample_rate)
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
    plt.specgram(extract_array, Fs=tmp_audio.frame_rate,cmap="nipy_spectral") 
    plt.ylim(top=8000)
    plt.ylabel("frequency kHz")
    plt.title(f"{recording.filename} ({start_sec}s - {end_sec}s))", fontsize=10)
    plt.savefig("mixit_example2.jpg", dpi=144)
    plt.close()