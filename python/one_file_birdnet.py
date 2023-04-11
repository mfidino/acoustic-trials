from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "./output/CHIL-CTG-04232021/20210422_053000/20210422_053000.wav",
    lat=41.8414,
    lon=-88.1846,
    date=datetime(year=2021, month=4, day=22), # use date or week_48
    min_conf=0.25,
)
recording.analyze()
#recording.extract_detections_as_spectrogram(directory='output')
print(recording.detections)
print(recording)