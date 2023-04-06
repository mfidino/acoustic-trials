# acoustic-trials

NOTE: I put together a virtual environment with anaconda using python 3.9

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
```


### Setup

Right now, we are going to assume we have a sub-folder titled `audio`, which will contain the wave files. In this case, we will assume that all the files are from a single location.

### Step 1. Some initial cleaning of audio files

The first ML processing step requires audio files to end in `.wav`. However, it seems like audioMoth recorders output files as `.WAV`. I made a little script to rename files if needed titled `WAV2wav.py`

```
python ./python/WAV2wav.py audio

```


### Step 2. splitting recordings with `mixit`

`mixit` has "models for Unsupervised Sound Separation of Bird Calls Using Mixture Invariant Training." We use this to take in a single recording and split it into multiple tracks, which will hopefully remove urban noise. See instructions here for downloading mixit as well as tensorflow.

https://github.com/google-research/sound-separation/tree/master/models/bird_mixit

To run this, I also collected one script from that repo: `process_wav.py`. It seems as if this script is what is used to send a file through the `mixit` models.

To run a single audio file, the python call would be:

```
python3 ../tools/process_wav.py \
--model_dir bird_mixit_model_checkpoints/output_sources4 \
--checkpoint bird_mixit_model_checkpoints/output_sources4/model.ckpt-3223090 \
--num_sources 4 \
--input <input name>.wav \
--output <output_name>.wav
```

I put