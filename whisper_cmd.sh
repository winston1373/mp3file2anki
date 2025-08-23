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
    source_mp3=$(printf "%03d" "$num")  # format as 3-digit padded

    filepath="source/${source_mp3}.mp3"

    if [[ -f "$filepath" ]]; then
        echo "Processing $filepath"
        
        python3 silence_segment.py "${source_mp3}"
        
        # Transcribe
        for mp3file in audio_chunks/${source_mp3}/*.mp3; do
            filename=$(basename "$mp3file" .mp3)
            whisper "$mp3file" \
                --model medium\
                --language Japanese \
                --output_dir "whisper_output/chunk/${source_mp3}"
        done

        python3 generate_modified_audio.py "$source_mp3"

        python3 insert_anki.py "$source_mp3"


    else
        echo "File $filepath not found, stopping."
        break
    fi
done

