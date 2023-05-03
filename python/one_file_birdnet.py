from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import pydub

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "D:/uwin_sounds/split_audio/PHAZ/Jesse_-_02_PHAZ_V10/20210427_085500_98.95.wav",
    #lat=41.8414,
    #lon=-88.1846,
    #date=datetime(year=2021, month=4, day=22), # use date or week_48
    min_conf=0.25,
)
tmp_audio = pydub.AudioSegment.from_file("D:/uwin_sounds/split_audio/PHAZ/Jesse_-_02_PHAZ_V10/20210427_085500_98.95.wav")
sample_rate = tmp_audio.frame_rate
recording.analyze()
#recording.extract_detections_as_spectrogram(directory='output')
print(recording.detections)
print(sample_rate)