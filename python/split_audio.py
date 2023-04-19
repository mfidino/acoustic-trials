import argparse
import os
import numpy as np
import soundfile as sf

path = 'E:\\BirdClef_2023\\birdclef-2023\\train_audio\\'


# create an argument parser
parser = argparse.ArgumentParser(description="Rename files with a .WAV extension to .wav")
parser.add_argument("--input_folder", type=str, help="the folder containing the files to rename")
parser.add_argument("--output_folder", type=str, help="the folder where you want to store the files")
# parse the arguments
args = parser.parse_args()

path = args.input_folder

outpath = args.output_folder
def input_files(path):
    allowed_filetypes=['wav', 'flac', 'mp3', 'ogg', 'm4a']
    files = []
    for root, dirs, flist in os.walk(path):
        for dir in dirs:
            print(dir)
        for f in flist:
            if len(f.rsplit('.', 1)) > 1 and f.rsplit('.', 1)[1].lower() in allowed_filetypes:
                files.append(os.path.join(root, f))

    print(f'{len(files)} files foundin {path}')
    return files

def chunk_wav(wav, cut_center, var_win_measure):
    check_points = np.arange(-2, 2, step = 0.1)
    centered_checks = [check + cut_center for check in check_points]
    
    chunks = []
    for check in centered_checks:
        chunks.append(wav[round(check*sr):round((check+var_win_measure)*sr)])
    return chunks, centered_checks



for root, dirs, flist in os.walk(path):
     for dir in dirs:
         read_dir_path = os.path.join(root,dir)
         write_dir_path = os.path.join(outpath,dir)
         if not os.path.exists(write_dir_path):
             os.makedirs(write_dir_path)
         files = input_files(read_dir_path)
         for f in files:
             print(f)
             fname = files[0].split('\\')[-1].split('.')[0] 
             wav, sr = sf.read(f)
             clip_length_s = len(wav)/sr
             variance_window = 0.5 
             cut_window_length = 5
             num_cuts = clip_length_s / cut_window_length
             if (num_cuts - round(num_cuts) ) < 0.5: 
                 num_cuts = round(num_cuts) - 1
             else:
                 num_cuts = round(num_cuts)
             #establishing cut points in seconds
             cut_points = [0]
             for i in range(num_cuts):
                 cut_center = (i+1) * cut_window_length
                 chunked_wav, centered_checks = chunk_wav(wav, cut_center, variance_window)
                 chunked_var = [np.max(chunk) for chunk in chunked_wav]
                 idx = np.argmin(chunked_var)
                 cut_points.append(centered_checks[idx]+ (variance_window/2) )
             cut_points.append(clip_length_s)
             #writing clipped wavs
             for i in range(len(cut_points)-1):
                 start = round(cut_points[i]*sr)
                 stop = round(cut_points[i+1]*sr)
                 tmp_wav = wav[start:stop]
                 tmp_name = f'{fname}_{cut_points[i]}.wav'
                 write_path = os.path.join(write_dir_path, tmp_name)
                 sf.write(write_path, tmp_wav, sr)
            
