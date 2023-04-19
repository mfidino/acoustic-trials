import os
import argparse



parser = argparse.ArgumentParser(description="Process WAV files")
parser.add_argument("--input_folder", type=str, help="the folder containing the input files")
# parse the arguments
args = parser.parse_args()

subdirs = [f.path for f in os.scandir(args.input_folder) if f.is_dir()]

cities = [os.path.basename(os.path.normpath(subdir)) for subdir in subdirs]
# Print the list of subdirectories
#print(subdirs)

for sd in subdirs:
	city = os.path.basename(sd)
	# get files in this
	sites = os.listdir(sd)
	for site in sites:
		inp = f"{args.input_folder}\\{city}\\{site}"
		onp = f"{args.input_folder}\\output\\{city}\\{site}"
		print(inp)
		cmd=f"python ./python/mixit_audio.py \
--input_folder {inp}\\ \
--output_folder {onp}\\"
		#print(cmd)
		os.system(cmd)
		