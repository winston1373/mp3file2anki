from datetime import datetime, timedelta
import re
import sys

def parse_srt_timestamp(ts):
    return datetime.strptime(ts, "%H:%M:%S,%f")

def format_srt_timestamp(dt):
    return dt.strftime("%H:%M:%S,%f")[:-3]

def merge_short_subs(srt_content, min_duration_seconds=5):
    pattern = re.compile(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)", re.DOTALL)
    entries = pattern.findall(srt_content)

    merged = []
    i = 0
    while i < len(entries):
        idx, start, end, text = entries[i]
        start_time = parse_srt_timestamp(start)
        end_time = parse_srt_timestamp(end)
        duration = (end_time - start_time).total_seconds()

        # Merge with next if duration is too short and next exists
        while duration < min_duration_seconds and i + 1 < len(entries):
            next_idx, next_start, next_end, next_text = entries[i + 1]
            end_time = parse_srt_timestamp(next_end)
            text += '\n' + next_text
            duration = (end_time - start_time).total_seconds()
            i += 1  # skip the next because we merged it

        merged.append((len(merged) + 1, format_srt_timestamp(start_time), format_srt_timestamp(end_time), text.strip()))
        i += 1

    # Reconstruct SRT format
    new_srt = ""
    for idx, start, end, text in merged:
        new_srt += f"{idx}\n{start} --> {end}\n{text}\n\n"
    return new_srt.strip()

# Example usage
file_name = "002"


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <srtfile>")
        sys.exit(1)

    file_name = sys.argv[1]
    with open(f"whisper_output/{file_name}.srt", "r", encoding="utf-8") as f:
        srt_data = f.read()

    result = merge_short_subs(srt_data, min_duration_seconds=5)

    with open(f"whisper_output/{file_name}_merged.srt", "w", encoding="utf-8") as f:
        f.write(result)
if __name__ == "__main__":
    main()
