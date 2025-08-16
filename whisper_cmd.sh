#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <start_number: e.g. 002> [iterations]"
    exit 1
fi

start="$1"
iterations="${2:-1}"   # default to 1 if not given

# Ensure start is treated as integer
start_num=$((10#$start))  # 10# avoids octal interpretation

for ((i=0; i<iterations; i++)); do
    num=$((start_num + i))
    mp3file=$(printf "%03d" "$num")  # format as 3-digit padded

    filepath="source/${mp3file}.mp3"

    if [[ -f "$filepath" ]]; then
        echo "Processing $filepath"
        # put your real command here
        # whisper "$filepath" --model small --language Japanese
        # 1. Transcribe
        whisper "source/${mp3file}.mp3" --model small --language Japanese --output_dir whisper_output

        # 2. Merge subtitles
        python3 merge_srt.py "$mp3file"

        # 3. Cut audio
        python3 cut_mp3.py "$mp3file"

        # 4. Insert into Anki
        python3 insert_anki.py "$mp3file"


    else
        echo "File $filepath not found, stopping."
        break
    fi
done

