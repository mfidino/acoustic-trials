# acoustic-trials

NOTE: I put together a virtual environment with anaconda using python 3.9


Goals of this repo. We are going to take in a set of wave files, parse each one out into multiple audio tracks, and then run all of the tracks through birdnet.


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


### Setup

Right now, we are going to assume we have a sub-folder titled `small_audio`, which will contain the wave files. For this example I trimmed down the 10-15 minute files to just the first 30 seconds as a proof of concept.

### Step 1. Some initial cleaning of audio files

The first ML processing step requires audio files to end in `.wav`. However, it seems like audioMoth recorders output files as `.WAV`. I made a little script to rename files if needed titled `WAV2wav.py`. This Python script renames all files with a ".WAV" extension to ".wav" in a specified folder. It uses the argparse module to parse command-line arguments and the os module to traverse the directory and rename the files.

```
python ./python/WAV2wav.py --input_folder small_audio

```


### Step 2. splitting recordings with `mixit`

`mixit` has "models for Unsupervised Sound Separation of Bird Calls Using Mixture Invariant Training." We use this to take in a single recording and split it into multiple tracks, which will hopefully remove urban noise. See instructions here for downloading mixit as well as tensorflow.

https://github.com/google-research/sound-separation/tree/master/models/bird_mixit

To run this, I also collected one script from that repo: `process_wav.py`. It seems as if this script is what is used to send a file through the `mixit` models.

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

However, each visit to a site will have multiple files (i.e., multiple days of recording). So we are going to want to be able to apply this to all `wav` files in a given folder.  So I but together `./python/mixit_audio.py` to do just that. This code processes wav files by taking an input folder containing .wav files and uses the pre-trained mixit model to generate source-separated audio files for each input file. It creates an output folder to store the processed files, and also copies over the original file into this folder as well (more on this later). 

The folder hierarchy for the output is:`output/{site visit}/name of wav file` Where `site visit` is the name of the original folder (which contains the site name and date of visit). Each of these folders will have 5 files:

1. The original sound file.
2. Four source-seperated audio files ending in `_source0.wav` through `_source3.wav`.

These files SHOULD be treated as temporary, in that after they are successfully processed in the next step they can get removed. They are currently not treated as temporary.

An example of calling this script is:

```
python ./python/mixit_audio.py --input_folder small_audio/CHIL-CTG-04232021
```

### Step 3. Run through birdnet

Now that we have each file for a given visit seperated out into different tracks, we can run all of them through birdnet. The detections for birdnet are in json format and look something like this.


```
[[
{'common_name': 'American Robin', 'scientific_name': 'Turdus migratorius', 'start_time': 0.0, 'end_time': 3.0, 'confidence': 0.43399834632873535},
{'common_name': 'American Robin', 'scientific_name': 'Turdus migratorius', 'start_time': 9.0, 'end_time': 12.0, 'confidence': 0.87421541544584154}
]]
```
where each element in this list has some json about the species detected, how confident the model is, and the start and end time of the detection (relative to the start of the file itself). In the example above there are two detections within a single audio file. Because we have 5 files associated to each orginal file, we run birdnet 5 times and then summarise the detections across those 5 files. To do so I grouped them based on their start & end time and then take the species with the highest confidence at that time across files. The script `do_birdnet.py` will do all of this when given an `--input_folder`. While not currently saved, there is a `grouped_detections_list` which contains the detection info (should get saved / put into a table on SQL). Additionally, the script saves the 3 second files for each detections and makes a spectrogram (both of which could be used for verfication / reporting in the app).

This script can be run with

```
python ./python/do_birdnet.py --input_folder output/CHIL-CTG-04232021
```

### step 4. Stiching it all together

Really the only thing that needs to get pointed at is a folder to start from, everything else functions off of that. The script in the main repo called `do_all.py` does steps 1 through 3.

```
python do_all.py --input_folder small_audio/CHIL-CTG-04232021
```

### Next steps.

There are quite a few variables throughout this that are hard-coded, or pulled off of the `--input_folder` argument. When interfacing with the UWIN web app a number of these bits of information can actually be pulled from specific tables in the database, namely to date & time of a visit to a given location as well as that locations coordinates. I've also used a file naming structure for the folders that is similar to the way the web app names buckets on google cloud. Finally, after the ML outputs are collected we really don't need to store all of the seperated 'tracks.' What we really just need are:
1. The original soundfile stored in the coldest of cold storages.
2. The small bits of soundfiles that are the species detections stored in something that can possibly be verified by a user. 
3. The spectrograms that are associated to those soundfiles as well so there is a visual as well as an auditory representation.

