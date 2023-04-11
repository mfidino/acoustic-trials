import glob
import os
import argparse
import shutil



parser = argparse.ArgumentParser(description="Process WAV files")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")

# parse the arguments
args = parser.parse_args()

# get the basename as well
basename = os.path.basename(args.input_folder)

# just a temporary output folder
output_folder = "output"

model_dir = "bird_mixit_model_checkpoints/output_sources4"
checkpoint = "bird_mixit_model_checkpoints/output_sources4/model.ckpt-3223090"
num_sources = 4

# get a list of all the .wav files in the input folder

input_files = glob.glob(os.path.join(args.input_folder, "*.wav"))

# loop through each input file and process it
for input_file in input_files:
    print(input_file)
    # get the name of the output file
    name_without_ext = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder,basename, name_without_ext, os.path.basename(input_file))
    print(output_file)
    
    # call the process_wav script with the current input and output file names
    cmd = f"python ./python/process_wav.py \
--model_dir {model_dir} \
--checkpoint {checkpoint} \
--num_sources {num_sources} \
--input {input_file} \
--output {output_file}"
    
    os.system(cmd)
    shutil.copy(input_file, os.path.join(output_folder, basename, name_without_ext, os.path.basename(input_file)))
