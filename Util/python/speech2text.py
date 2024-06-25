from glob import glob

from openai import OpenAI

client = OpenAI(api_key="")

transcriptions = []
for path in sorted(glob("*.m4a")):
    with open(path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        print(transcription.text)
        transcriptions.append(transcription.text)

full_transcription = "\n".join(transcriptions)
print(full_transcription)

with open("tmp.txt", "w") as file:
    file.writelines(full_transcription)
