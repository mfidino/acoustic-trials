# acoustic-trials


This repository is a where I have been trying to wrap my head around processing acoustic data collected from autonomous recording units (ARUs), along urbanization gradients in a few different cities that are a part of the Urban Wildlife Information Network. One tricky aspect of audio recordings in urban areas is that there can be substantial urban noise, which we want to try to remove to get better classifications via machine learning. 

In a nutshell, the code here :
1. Splits audio files into smaller pieces (thanks to Matt Weldy for sharing some code on how to do so)
2. Uses [`mixit`](https://github.com/google-research/sound-separation) to separate sounds out of each smaller segment (i.e., remove urban noise and isolate different bird calls)
3. Sends all those sound separated segments through [`birdnet`](https://github.com/kahst/BirdNET-Analyzer) to classify bird songs and calls.
4. Save the output from birdnet, the small sound file, and a spectrogram for additional validation (if that is something you are interested in).



### Table of contents

1. [Setup](#setup)
2. [Step 1. Some initial cleaning of audio files](#step-1-some-initial-cleaning-of-audio-files)
3. [Step 2. Splitting longer audio files into smaller pieces](#step-2-splitting-longer-audio-files-into-smaller-pieces)
4. [Step 3. Separating recordings with `mixit`](#step-3-separating-recordings-with-mixit)
5. [Step 4. Run through `birdnet`](#step-4-run-through-birdnet)
6. [Step 5. Stitching it all together](#step-5-stitching-it-all-together)
7. [Future improvements](#future-improvements)
8. [Batch processing](#batch-processing)

### Setup

---

Assuming you have anaconda installed, open up an anaconda prompt to create it with this:
```
conda create -n acoustic-trials python=3.9 anaconda

```

and if you want to switch to that environment use this:
```
conda activate acoustic-trials
```

Aside from the two ML libraries you need to install, you need to install tensorflow

```
pip install tensorflow
pip install birdnetlib
pip install librosa
pip install resampy
```


Right now, we are going to assume we have a sub-folder titled `small_audio`, which will contain the wave files. For this example I trimmed down the 10-15 minute files to just the first 30 seconds as a proof of concept.

[Back to table of contents ⤒](#table-of-contents)

### Step 1. Some initial cleaning of audio files

---

The first ML processing step requires audio files to end in `.wav`. However, it seems like audioMoth recorders output files as `.WAV`. I made a little script to rename files if needed titled `WAV2wav.py`. This Python script renames all files with a ".WAV" extension to ".wav" in a specified folder. It uses the argparse module to parse command-line arguments and the os module to traverse the directory and rename the files.

```
python ./python/WAV2wav.py --input_folder small_audio

```

[Back to table of contents ⤒](#table-of-contents)

### Step 2. Splitting longer audio files into smaller pieces

The audiomoths we deploy will record for minutes at a time (in this example they ran for 15 minutes every time they were triggered). This creates an issue with splitting the sound
file into seperate tracks because there are likely more than 4 distinct sounds that occur
over the whole length of the file. Consider a morning chorus for birds, there can be many
species songing all at once! Add in some urban noise and you can see how this can be an
issue. Given an `input_folder` (where you want the script to search for wav files) and an `output_folder` (where you want the script to save the new files), the script `./python/split_audio.py` can be used to recursively look through folders
and will split each file into many small pieces about 5 seconds in length. The variation that is caused here is the result of the script looking for a quite point to create a split. Where the split occurred (in seconds) will be added to the end of the file name. So, for example, if you have a wav file called `my_bird.wav` it will generate a number of files that could look something like `my_bird_0.wav` (i.e., starts at 0 seconds of the original file) or `my_bird_3.35.wav` (i.e., starts at 3.35 seconds of the original file).

```
python ./python/split_audio.py --input_folder small_audio --output_folder split_audio
```
These files here should be treated as temporary.

NOTE: Folder hierarchy is maintained with this function, so if `--input_folder` is one folder that has data from multiple cities, each of which has multiple sites (e.g., `my_folder/<city name>/<site name>` then that hierarchy gets transferred along to `--output_folder`).


[Back to table of contents ⤒](#table-of-contents)

### Step 3. Separating recordings with `mixit`

`mixit` has "models for Unsupervised Sound Separation of Bird Calls Using Mixture Invariant Training." We use this to take in a single recording and split it into multiple tracks, which will hopefully remove urban noise. See instructions here for downloading mixit as well as tensorflow. One thing to note here is that you will need to be able to call `gsutil` from your command line to download `mixit` if you are following their directions.

https://github.com/google-research/sound-separation/tree/master/models/bird_mixit

To run this, I also collected two script from that repo: `process_wav.py` and `inference.py`. It seems as if both of these scripts are needed to send a file through the `mixit` models.

To run a single audio file, the python call would be:

```
python ../tools/process_wav.py \
--model_dir bird_mixit_model_checkpoints/output_sources4 \
--checkpoint bird_mixit_model_checkpoints/output_sources4/model.ckpt-3223090 \
--num_sources 4 \
--input <input name>.wav \
--output <output_name>.wav
```

I downloaded the model to my current working directory so that `--model_dir` and `--checkpoint` can be found there.

However, each visit to a site will have multiple files (i.e., multiple days of recording). So we are going to want to be able to apply this to all `wav` files in a given folder.  So I put together `./python/mixit_audio.py` to do just that. This code processes the `wav` files in `--input_folder` and uses the pre-trained mixit model to generate source-separated audio files for each input file. It creates an output folder to store the processed files, and also copies over the original file into this folder as well (more on this later). 

The folder hierarchy for the output is:`output/{site visit}/name of wav file` Where `site visit` is the name of the original folder (which contains the site name and date of visit). Each of these folders will have 5 files:

1. The original sound file.
2. Four source-seperated audio files ending in `_source0.wav` through `_source3.wav`.

These files SHOULD be treated as temporary, in that after they are successfully processed in the next step they can get removed. They are currently not treated as temporary. We've pulled over the original file because that one should also be ran through birdnet (it has been shown to improve accuracy to run that one plus the source-separated files).

An example of calling this script is:

```
python ./python/mixit_audio.py --input_folder small_audio/CHIL-CTG-04232021
```

NOTE: Check out [Extra things](#extra-things) below for how to run this on multiple folders at once.


[Back to table of contents ⤒](#table-of-contents)

### Step 4. Run through `birdnet`

Now that we have each file for a given visit separated out into different tracks, we can run all of them through birdnet. The detections for birdnet are in json format and look something like this.


```
[[
{'common_name': 'American Robin', 'scientific_name': 'Turdus migratorius', 'start_time': 0.0, 'end_time': 3.0, 'confidence': 0.43399834632873535},
{'common_name': 'American Robin', 'scientific_name': 'Turdus migratorius', 'start_time': 9.0, 'end_time': 12.0, 'confidence': 0.87421541544584154}
]]
```
where each element in this list has some json about the species detected, how confident the model is, and the start and end time of the detection (relative to the start of the file itself). In the example above there are two detections within a single audio file. Because we have 5 files associated to each original file, we run birdnet 5 times and then summarize the detections across those 5 files. To do so I grouped them based on their start & end time and then take the species with the highest confidence at that time across files. The script `do_birdnet.py` will do all of this when given an `--input_folder`. While not currently saved, there is a `grouped_detections_list` which contains the detection info (should get saved / put into a table on SQL). Additionally, the script saves the 3 second files for each detections and makes a spectrogram (both of which could be used for verfication / reporting in the app).

This script can be run with

```
python ./python/do_birdnet.py --input_folder output/CHIL-CTG-04232021
```

and an example of the spectrogram that gets output is

<div align="center"><img width="600" height="auto" src="./snips/CHIL-CTG-04232021/20210423_080000/20210423_080000_21s-24s.jpg" /></div>

[Back to table of contents ⤒](#table-of-contents)

### Step 5. Stitching it all together

Really the only thing that needs to get pointed at is a folder to start from, everything else functions off of that. The script in the main repo called `do_all.py` does steps 1 through 3.

```
python do_all.py --input_folder small_audio/CHIL-CTG-04232021
```

[Back to table of contents ⤒](#table-of-contents)

### Future improvements

There are quite a few variables throughout this that are hard-coded, or pulled off of the `--input_folder` argument. When interfacing with the UWIN web app a number of these bits of information can actually be pulled from specific tables in the database, namely to date & time of a visit to a given location as well as that locations coordinates. I've also used a file naming structure for the folders that is similar to the way the web app names buckets on google cloud. Finally, after the ML outputs are collected we really don't need to store all of the separated 'tracks.' What we really just need are:

1. The original soundfile stored in the coldest of cold storages.
2. The small bits of soundfiles that are the species detections stored in something that can possibly be verified by a user. In this example these are getting stored in a snips sub-folder
3. The spectrograms that are associated to those soundfiles as well so there is a visual as well as an auditory representation. In this example these are getting stored in the snips sub--folder.

I built this script with the thought in mind that the function would get called once a user tells them to apply all the ML to a given visit. That being said, it may make sense to be able to batch process them by having a user select those across a given time range (e.g., a month). We should also
keep track of whether or not a given batch of files have completed the ML pipeline so that we can ensure they are not sent through it again (as that could add up). 

I am positive there is other stuff I am missing here, but at a minimum these scripts are at least a proof of concept that this pipeline works.

[Back to table of contents ⤒](#table-of-contents)

### Batch processing

Since I've been testing this out on my local computer I also wanted a way to batch process more than one folder (e.g., all the sub-folders within another audio folder). The script

[Back to table of contents ⤒](#table-of-contents)

