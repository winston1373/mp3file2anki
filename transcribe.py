import whisper

model = whisper.load_model("base")
# Transcribe the MP3 file
audio_path = "source/001.mp3"  # Replace with the path to your MP3 file
result = model.transcribe(audio_path, language='ja')

# Print the transcription
print("Transcription:\n", result['text'])
