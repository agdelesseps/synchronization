# Align pairs of video files based on their audio.
# Steps:
# 1. Extract audio.  Cut it into 30-minute chunks if necessary.  Save audio files.
# 2. Determine necessary shift to align each 30 minute (or less) pair of audio files.  Save shift directions to text file.
# 3. (Future development) Directly trim and shift MP4 files.

# Takes command line argument, e.g. python3 audio_align.py <left file> <right file>
# Relies heavily on https://github.com/benfmiller/audalign/wiki/Alignment-Functions-Details

import audalign as ad, os, soundfile as sf, sys
from moviepy import editor as mp
from typing import List, Tuple

FPS = 48000
CHUNK_SECONDS = 30*60
TEST_SECONDS = 60

# # for testing chunk breakup on shorter recordings:
# CHUNK_SECONDS = 20
# TEST_SECONDS = 10

def extract_audio(left_infile: str, right_infile: str, out_superfolder: str) -> int:
    """
    Extract audio from MP4 files, separate into 30-minute chunks if necessary, and save as pairs of .wav files in folders.

    Arguments:
    - in_folder: folder containing 'left.MP4' and 'right.MP4'
    - out_superfolder: where to put folders of .wav files (don't include final '/' in string)
                       within out_folder, there will be numbered folders
                       each numbered folder corresponds to a chunk of time
                       within each numbered folder, there will be two files: left.wav and right.wav
    Returns:
    - number of subfolders
    """

    left_clip = mp.VideoFileClip(left_infile)
    right_clip = mp.VideoFileClip(right_infile)

    left_audio = left_clip.audio.to_soundarray(fps=FPS)
    right_audio = right_clip.audio.to_soundarray(fps=FPS)

    left_n_full_chunks = left_audio.shape[0] // (CHUNK_SECONDS * FPS)
    right_n_full_chunks = right_audio.shape[0] // (CHUNK_SECONDS * FPS)
    n_subfolders = max(left_n_full_chunks, right_n_full_chunks) + 1

    if not os.path.exists(out_superfolder):
        os.mkdir(out_superfolder)

    for i in range(n_subfolders):
        if not os.path.exists(f"{out_superfolder}/{i+1}"):
            os.mkdir(f"{out_superfolder}/{i+1}")

    if left_n_full_chunks > 0:
        for i in range(left_n_full_chunks):
            chunk_audio = left_audio[i*CHUNK_SECONDS*FPS:(i*CHUNK_SECONDS+TEST_SECONDS)*FPS,:]
            sf.write(f"{out_superfolder}/{i+1}/left.wav", chunk_audio, FPS)
        last = min(left_audio.shape[0], (left_n_full_chunks*CHUNK_SECONDS+TEST_SECONDS)*FPS)
        chunk_audio = left_audio[left_n_full_chunks*CHUNK_SECONDS*FPS:last,:]
        sf.write(f"{out_superfolder}/{left_n_full_chunks+1}/left.wav", chunk_audio, FPS)
    else:
        last = min(left_audio.shape[0], TEST_SECONDS*FPS)
        sf.write(f"{out_superfolder}/1/left.wav", left_audio[:last,:], FPS)
    
    if right_audio.shape[0] > CHUNK_SECONDS * FPS:
        for i in range(right_n_full_chunks):
            chunk_audio = right_audio[i*CHUNK_SECONDS*FPS:(i*CHUNK_SECONDS+TEST_SECONDS)*FPS,:]
            sf.write(f"{out_superfolder}/{i+1}/right.wav", chunk_audio, FPS)
        last = min(right_audio.shape[0], (right_n_full_chunks*CHUNK_SECONDS+TEST_SECONDS)*FPS)
        chunk_audio = right_audio[right_n_full_chunks*CHUNK_SECONDS*FPS:last,:]
        sf.write(f"{out_superfolder}/{right_n_full_chunks+1}/right.wav", chunk_audio, FPS)
    else:
        last = min(right_audio.shape[0], TEST_SECONDS*FPS)
        sf.write(f"{out_superfolder}/1/right.wav", right_audio[:last,:], FPS)
    
    return n_subfolders

def align_chunk(in_subfolder: str) -> Tuple[float, float]:
    """
    Determine time shifts to align two audio files.

    Arguments:
    - in_subfolder: subfolder containing two audio files (should be just a number)
    Returns:
    - tuple containing time (in seconds) that should be added to each file (one should be zero)
    """

    correlation_rec = ad.CorrelationRecognizer()
    cor_spec_rec = ad.CorrelationSpectrogramRecognizer()

    results = ad.align(in_subfolder, recognizer=correlation_rec)
    fine_results = ad.fine_align(results, recognizer=cor_spec_rec)

    # assuming files in folder were called 'left.wav' and 'right.wav'
    return (fine_results["left.wav"], fine_results["right.wav"])

def align_many_chunks(in_superfolder: str, n_subfolders: int) -> List[Tuple[float, float]]:
    """
    Determine time shifts to align possibly many pairs of audio files.

    Arguments:
    - in_superfolder: where to access subfolders (each with a pair of files)
    - n_subfolders: number of subfolders (each with a pair of files)
    Returns:
    - list of tuples containing time (in seconds) that should be added to each file
    """

    results = []
    for i in range(n_subfolders):
        results += [align_chunk(f"{in_superfolder}/{i+1}")]
    
    return results

def main(left_infile: str, right_infile: str) -> None:
    """
    
    """

    print(f"\nExtracting audio from {left_infile} and {right_infile}.")

    new_folder = f"Data/{('-').join(left_infile.split('/')[-4:-1])}_{('-').join(right_infile.split('/')[-4:-1])}"
    superfolder = f"{new_folder}/audio"
    n_subfolders = extract_audio(left_infile, right_infile, superfolder)

    print(f"\nAudio files in {superfolder}/audio.\n\nFinding time shifts to align {n_subfolders} pair(s) of chunks.\n")
    
    results = align_many_chunks(superfolder, n_subfolders)

    with open(f"{new_folder}/time_shifts.txt", "w") as f:
        f.write("Seconds to be added to (left, right) in each pair of chunks (shifts independent of each other):\n")
        f.writelines(f"{results}")
    
    print(f"\nAbsolute time shifts in {new_folder}/time_shifts.txt.")

# this if statement prevents multiprocessing errors
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

#Amphawa/08272022/C0002 done
#Amphawa/08272022/C0003 done