#!/bin/bash
# Usage: ./run_pipeline.sh 003

if [ -z "$1" ]; then
    echo "Usage: $0 <mp3file>"
    exit 1
fi

mp3file="$1"

# 1. Transcribe
whisper "source/${mp3file}.mp3" --model small --language Japanese --output_dir whisper_output

# 2. Merge subtitles
python3 merge_srt.py "$mp3file"

# 3. Cut audio
python3 cut_mp3.py "$mp3file"

# 4. Insert into Anki
python3 insert_anki.py "$mp3file"