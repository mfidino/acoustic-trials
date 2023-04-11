import glob
import os
from concurrent.futures import ThreadPoolExecutor

input_folder = "small_audio"
output_folder = "output"

model_dir = "bird_mixit_model_checkpoints/output_sources4"
checkpoint = "bird_mixit_model_checkpoints/output_sources4/model.ckpt-3223090"
num_sources = 4

# get a list of all the .wav files in the input folder
input_files = glob.glob(os.path.join(input_folder, "*.wav"))

def process_file(input_file):
    # get the name of the output file
    output_file = os.path.join(output_folder, os.path.basename(input_file))
    
    # call the process_wav script with the current input and output file names
    cmd = f"python ./python/process_wav.py \
    --model_dir {model_dir} \
    --checkpoint {checkpoint} \
    --num_sources {num_sources} \
    --input {input_file} \
    --output {output_file}"
    
    os.system(cmd)

# create a thread pool with 4 worker threads
with ThreadPoolExecutor(max_workers=4) as executor:
    # submit each file to the thread pool for processing
    for input_file in input_files:
        executor.submit(process_file, input_file)