import os
import argparse

# Define a function that recursively scans the input folder and returns a list of all subdirectories
def scan_for_subdirs(input_folder):
    subdirs = []
    for root, dirs, files in os.walk(input_folder):
        for dir in dirs:
            subdir = os.path.join(root, dir)
            subdirs.append(subdir)
    return subdirs

# Define a function that replaces spaces with underscores in directory names
def replace_spaces_with_underscores(directory):
    if " " in directory:
        new_directory = directory.replace(" ", "_")
        os.rename(directory, new_directory)
        return new_directory
    else:
        return directory

# Define a function that generates the cmd string for running mixit_audio.py
def generate_cmd(input_folder, output_folder):
    return f"python ./python/mixit_audio.py --input_folder {input_folder} --output_folder {output_folder}"

def add_output(input_path):
    # Split the path using either forward slash or backslash
    path_parts = input_path.split("/") if "/" in input_path else input_path.split("\\")
    
    # Add "output" between the first two parts of the path
    output_path_parts = path_parts[:1] + ["output"] + path_parts[1:]
    
    # Join the path parts back together using the appropriate separator
    output_path = os.path.join(*output_path_parts)
    
    return output_path

# Set up the argument parser
parser = argparse.ArgumentParser(description="Process WAV files")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")
parser.add_argument("--output_folder", type=str, default = None, help="the folder to save the files")

# Parse the arguments
args = parser.parse_args()

if args.output_folder is None:
    output_folder = add_output(args.input_folder)
else:
    output_folder = f"{args.output_folder}/output"
    
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Scan the input folder for all subdirectories
subdirs = scan_for_subdirs(args.input_folder)

# Replace spaces with underscores in directory names
for subdir in subdirs:
    replace_spaces_with_underscores(subdir)

# Loop through all subdirectories and run mixit_audio.py on each one
for subdir in subdirs:
    input_folder = subdir
    print(input_folder)
    cmd = generate_cmd(input_folder, output_folder)
    print(cmd)
    os.system(cmd)