import base64

file_path = "test.wav"

# Read the WAV file in binary mode
with open(file_path, "rb") as wav_file:
    encoded_string = base64.b64encode(wav_file.read()).decode('utf-8')

# Save the base64 encoded string to a text file
with open(file_path + ".txt", "w") as f:
    f.write(encoded_string)
