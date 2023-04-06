import os
import wave

# create the output directory if it doesn't exist
if not os.path.exists("small_audio"):
    os.mkdir("small_audio")

# loop over all files in the audio directory
for filename in os.listdir("audio"):
    print(filename)
    if not filename.endswith(".WAV"):
        continue

    # open the input file for reading
    input_path = os.path.join("audio", filename)
    with wave.open(input_path, "rb") as input_file:
        # get the number of frames and channels
        num_frames = input_file.getnframes()
        print(num_frames)
        num_channels = input_file.getnchannels()
        frame_rate = input_file.getframerate()
        sample_width = input_file.getsampwidth()

        # calculate the number of frames in the first 30 seconds
        thirty_sec_frames = int(frame_rate * 30)

        # read the first 30 seconds of audio data
        input_file.setpos(0)
        frames = input_file.readframes(thirty_sec_frames)

    # create the output file path
    output_path = os.path.join("small_audio", filename)

    # open the output file for writing
    with wave.open(output_path, "wb") as output_file:
        # set the output file parameters to match the input file
        output_file.setnchannels(num_channels)
        output_file.setframerate(frame_rate)
        output_file.setsampwidth(sample_width)

        # write the first 30 seconds of audio data to the output file
        output_file.writeframes(frames)
