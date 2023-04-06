import os
import argparse

# create an argument parser
parser = argparse.ArgumentParser(description="Rename files with a .WAV extension to .wav")
parser.add_argument("folder", type=str, help="the folder containing the files to rename")

# parse the arguments
args = parser.parse_args()

# loop through all files in the specified folder
for file_name in os.listdir(args.folder):
    # check if the file ends with ".WAV"
    if file_name.endswith(".WAV"):
        # generate the new file name
        new_file_name = os.path.join(args.folder, file_name.lower().replace(".WAV", ".wav"))
        
        # rename the file
        os.rename(os.path.join(args.folder, file_name), new_file_name)
        
        print(f"Renamed {file_name} to {new_file_name}")
