import os
import sys
import librosa
import soundfile as sf
import pyrubberband as pyrb
import random

def slow_keep_pitch(audio_array, speed_factor):
    """
    Slow down or speed up audio without changing pitch.
    Returns the processed audio array.
    """
    return librosa.effects.time_stretch(audio_array, rate=speed_factor)

def change_pitch(audio_array, sample_rate, n_steps):
    """
    Change pitch of audio without changing speed.
    Returns the processed audio array.
    """
    return pyrb.pitch_shift(audio_array, sample_rate, n_steps)


def generate_modified_audio(mp3_path, output_dir,
                           slow_factor=0.5, pitch_shift_steps=0):
    """
    Parameters:
        slow_factor (float): Speed factor for slow version (<1 slows down).
        pitch_shift_steps (list[float]): Semitone shifts for pitch versions (e.g., [2, -2]).
    """    

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    for mp3 in os.listdir(mp3_path):
        if not mp3.endswith(".mp3"):
            continue
        full_path = os.path.join(mp3_path, mp3)
        chunk = os.path.splitext(mp3)[0]
        # Load into librosa for processing
        y, sr = librosa.load(full_path, sr=None)

        shifted_audio = change_pitch(y, sr, pitch_shift_steps)
        sf.write(os.path.join(output_dir, f"{chunk}_pitch.mp3"),
                    shifted_audio, sr)
        
        slow_audio = slow_keep_pitch(shifted_audio, slow_factor)
        sf.write(os.path.join(output_dir, f"{chunk}_slow.mp3"), slow_audio, sr)

        print(f"Saved: {mp3}, slow version, and pitch shifts for segment ")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <mp3file>")
        sys.exit(1)

    mp3file = sys.argv[1]
    generate_modified_audio(
        f"audio_chunks/{mp3file}/",
        f"output_segments/{mp3file}", 
        pitch_shift_steps= random.uniform(-2, 2)
    )

if __name__ == "__main__":
    main()

