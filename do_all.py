import glob
import os
import argparse


parser = argparse.ArgumentParser(description="Process WAV files")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")

# get the last part of the input folder
# parse the arguments
args = parser.parse_args()

# get the basename as well
basename = os.path.basename(args.input_folder)

# step 1. rename WAV to wav
cmd = f"python ./python/WAV2wav.py --input_folder {args.input_folder}"
os.system(cmd)

# step 2. do mixit
cmd = f"python ./python/mixit_audio.py --input_folder {args.input_folder}"
os.system(cmd)

# step 3. do birdnet
cmd = f"python ./python/do_birdnet.py --input_folder output/{basename}"
os.system(cmd)
