import matplotlib.pyplot as plt, moviepy.editor as mp, numpy as np, scipy, soundfile as sf, sys
from scipy.io.wavfile import write
from typing import Tuple

FPS = 44100

def load_audio(infile: str, seconds_range: Tuple[float,float]) -> np.ndarray:
    clip = mp.VideoFileClip(infile)
    audio = clip.audio.to_soundarray()
    if seconds_range is not None:
        start = seconds_range[0]
        if len(seconds_range) > 1:
            end = seconds_range[1]
        else:
            end = audio.shape[0]
        breakpoint()
        audio = audio[start*FPS:end*FPS,:]
    return audio

def highpass_filter(audio: np.ndarray, freq: float) -> np.ndarray:
    if len(audio.shape) == 2:
        mono = np.mean(audio, axis=1)
    else:
        mono = audio
    sos = scipy.signal.butter(4, freq, btype="highpass", fs=FPS, output="sos")
    filtered = scipy.signal.sosfilt(sos, mono)
    return filtered

def main(infile, freq = 4, seconds_range: Tuple[float,float] = None) -> None:
    outname = f"Data/{'_'.join(infile.split('/'))}_filtered"
    audio = load_audio(infile, seconds_range)
    filtered = highpass_filter(audio, freq)
    write(f"{outname}.wav", FPS, filtered)
    xscale = np.linspace(seconds_range[0], seconds_range[1], len(filtered)) if seconds_range is not None else np.linspace(0, len(filtered)/FPS, len(filtered))
    plt.plot(xscale, filtered)
    plt.xlabel("t (s)")
    plt.savefig(f"{outname}_plot.png")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], int(sys.argv[2]))
    elif len(sys.argv) == 4:
        main(sys.argv[1], int(sys.argv[2]), (int(sys.argv[3]),))
    elif len(sys.argv) == 5:
        main(sys.argv[1], int(sys.argv[2]), (int(sys.argv[3]), int(sys.argv[4])))
    else:
        print("ERROR: too many arguments")