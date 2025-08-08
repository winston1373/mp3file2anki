import re
import os
import sys
from pydub import AudioSegment
from datetime import datetime
import subprocess
def parse_srt_timestamp(ts):
    """Convert SRT timestamp to milliseconds."""
    dt = datetime.strptime(ts, "%H:%M:%S,%f")
    return (dt.hour * 3600 + dt.minute * 60 + dt.second) * 1000 + int(dt.microsecond / 1000)
def change_speed(sound, speed=1.0):
    # Change playback speed
    sound_with_altered_frame_rate = sound._spawn(
        sound.raw_data,
        overrides={"frame_rate": int(sound.frame_rate * speed)}
    )
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
def slow_keep_pitch(input_path, output_path, factor=0.5):
    """
    Slow audio without changing pitch using ffmpeg's atempo filter.
    ffmpeg atempo supports only 0.5–2.0 in one step, so 0.5x works fine directly.
    """
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", f"atempo={factor}",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def extract_audio_segments(srt_path, mp3_path, output_dir):
    # Load audio file
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

        # Clean subtitle text (remove newlines, leading/trailing spaces)
        subtitle_text = text.strip().replace('\n', ' ')

        # Extract and save audio segment
        segment = audio[start_ms:end_ms]
        audio_path = os.path.join(output_dir, f"part_{int(idx):03d}.mp3")
        segment.export(audio_path, format="mp3")
        
        # Save slow-speed audio (0.5× speed, pitch preserved)
        slow_audio_path = os.path.join(output_dir, f"part_{int(idx):03d}_slow.mp3")
        slow_keep_pitch(audio_path, slow_audio_path, 0.65)
        # Save subtitle to text file
        subtitle_path = os.path.join(output_dir, f"part_{int(idx):03d}.txt")
        with open(subtitle_path, 'w', encoding='utf-8') as sub_file:
            sub_file.write(subtitle_text)

        print(f"Saved: {audio_path} and {slow_audio_path} ({start_str} --> {end_str})")
        print(f"Subtitle: {subtitle_text}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <mp3file>")
        sys.exit(1)

    mp3file = sys.argv[1]
    extract_audio_segments(
        f"whisper_output/{mp3file}_merged.srt",
        f"source/{mp3file}.mp3",
        f"output_segments/{mp3file}"
    )

if __name__ == "__main__":
    main()

