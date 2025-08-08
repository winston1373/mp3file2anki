import os
import requests
import base64
import sys


def create_anki_cards(deck_name, output_dir, filename):
    """Create Anki cards from audio + subtitle files in a given directory."""

    def invoke(action, params):
        """Send request to AnkiConnect API."""
        response = requests.post(
            "http://localhost:8765",
            json={"action": action, "version": 6, "params": params}
        ).json()
        if response.get("error"):
            print(f"❌ AnkiConnect Error: {response['error']}")
        return response

    def encode_audio(file_path):
        """Read and base64-encode audio file."""
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    # Ensure deck exists
    invoke("createDeck", {"deck": deck_name})

    # Path to target audio+subtitle folder
    audio_subtitle_dir = os.path.join(output_dir, filename)

    for file in sorted(os.listdir(audio_subtitle_dir)):
        if not file.endswith(".txt"):
            continue

        base_name = os.path.splitext(file)[0]
        txt_path = os.path.join(audio_subtitle_dir, file)
        mp3_path = os.path.join(audio_subtitle_dir, f"{base_name}.mp3")
        mp3_path_slow = os.path.join(audio_subtitle_dir, f"{base_name}_slow.mp3")
        
        # Check for required files
        if not os.path.isfile(mp3_path):
            print(f"❌ Missing {base_name}.mp3, skipping.")
            continue
        if not os.path.isfile(mp3_path_slow):
            print(f"❌ Missing {base_name}_slow.mp3, skipping.")
            continue

        # Read subtitle text
        with open(txt_path, 'r', encoding='utf-8') as f:
            subtitle = f.read().strip()
            
        base_name = os.path.splitext(file)[0] + filename
        # Upload normal and slow audio to Anki
        for audio_file in [(mp3_path, f"{base_name}.mp3"),
                           (mp3_path_slow, f"{base_name}_slow.mp3")]:
            invoke("storeMediaFile", {
                "filename": audio_file[1],
                "data": encode_audio(audio_file[0])
            })

        # Add note to Anki
        result = invoke("addNote", {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": f"[sound:{base_name}.mp3]",
                    "Back": f"{subtitle} ({filename}) [sound:{base_name}_slow.mp3]"
                },
                "options": {"allowDuplicate": False}
            }
        })

        if result.get("error"):
            print(f"❌ Error adding {base_name}: {result['error']}")
        else:
            print(f"✅ Added card: {base_name}")




def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <mp3file>")
        sys.exit(1)

    mp3file = sys.argv[1]
    create_anki_cards("Japanese Listening", "output_segments", mp3file)

if __name__ == "__main__":
    main()

