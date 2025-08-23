from pydub import AudioSegment, silence
import os
import sys
# Load the MP3 file
def silence_segment(mp3file):
    audio = AudioSegment.from_mp3(f"source/{mp3file}.mp3")
    trimmed_audio = audio[2000:]
    # Create output folder
    output_dir = f"audio_chunks/{mp3file}"
    os.makedirs(output_dir, exist_ok=True)

    # Split on silence
    chunks = silence.split_on_silence(
        trimmed_audio ,
        min_silence_len=2000,  # silence must be at least long
        silence_thresh=audio.dBFS - 16,  # dB threshold
        keep_silence=1000  # optional: keep a bit of silence at the edges
    )

    # Export chunks
    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(output_dir, f"{mp3file}_chunk_{i+1}.mp3")
        chunk.export(chunk_filename, format="mp3")
        print(f"Saved: {chunk_filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <mp3file>")
        sys.exit(1)

    mp3file = sys.argv[1]
    silence_segment(mp3file)

if __name__ == "__main__":
    main() 