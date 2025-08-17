import re
import os
import sys
from pydub import AudioSegment
from datetime import datetime
import librosa
import soundfile as sf
import pyrubberband as pyrb
import random

def parse_srt_timestamp(ts):
    """Convert SRT timestamp to milliseconds."""
    dt = datetime.strptime(ts, "%H:%M:%S,%f")
    return (dt.hour * 3600 + dt.minute * 60 + dt.second) * 1000 + int(dt.microsecond / 1000)

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


def extract_audio_segments(srt_path, mp3_path, output_dir,
                           slow_factor=0.5, pitch_shift_steps=0):
    """
    Extract audio segments from MP3 + SRT.
    Saves normal, slow (pitch preserved), and optional pitch-shifted versions.
    
    Parameters:
        slow_factor (float): Speed factor for slow version (<1 slows down).
        pitch_shift_steps (list[float]): Semitone shifts for pitch versions (e.g., [2, -2]).
    """
    # Load audio file for slicing
    audio = AudioSegment.from_mp3(mp3_path)

    # Read SRT file
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_data = f.read()

    # Parse SRT blocks
    pattern = re.compile(
        r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)",
        re.DOTALL
    )
    matches = pattern.findall(srt_data)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    for idx, start_str, end_str, text in matches:
        start_ms = parse_srt_timestamp(start_str)
        end_ms = parse_srt_timestamp(end_str)

        subtitle_text = text.strip().replace('\n', ' ')

        # Extract original segment and save
        segment = audio[start_ms:end_ms]
        audio_path = os.path.join(output_dir, f"part_{int(idx):03d}.mp3")
        segment.export(audio_path, format="mp3")

        # Load into librosa for processing
        y, sr = librosa.load(audio_path, sr=None)

        shifted_audio = change_pitch(y, sr, pitch_shift_steps)
        sf.write(os.path.join(output_dir, f"part_{int(idx):03d}_pitch.mp3"),
                    shifted_audio, sr)
        
        slow_audio = slow_keep_pitch(shifted_audio, slow_factor)
        sf.write(os.path.join(output_dir, f"part_{int(idx):03d}_slow.mp3"), slow_audio, sr)


        # Save subtitle text
        with open(os.path.join(output_dir, f"part_{int(idx):03d}.txt"),
                  'w', encoding='utf-8') as sub_file:
            sub_file.write(subtitle_text)

        print(f"Saved: {audio_path}, slow version, and pitch shifts for segment {idx}")
        print(f"Subtitle: {subtitle_text}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <mp3file>")
        sys.exit(1)

    mp3file = sys.argv[1]
    extract_audio_segments(
        f"whisper_output/{mp3file}_merged.srt",
        f"source/{mp3file}.mp3",
        f"output_segments/{mp3file}", 
        pitch_shift_steps= random.uniform(-2, 2)
    )

if __name__ == "__main__":
    main()

