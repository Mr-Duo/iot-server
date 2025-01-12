import base64

file_path = "test.wav.txt"

# Read the base64 encoded content
with open(file_path, "r") as f:
    wav = base64.b64decode(f.read().encode("utf-8"))
    # wav = f.read().encode("utf-8")

# Write the decoded WAV file
with open(file_path + ".wav", "wb") as wav_file:
    wav_file.write(wav)  # Directly write the decoded bytes
