
import os
import uuid

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def concatenate_mp3(files, output_file="./dialogues/output.mp3"):
    combined = AudioSegment.empty()
    for file in files:
        audio = AudioSegment.from_mp3(file)
        combined += audio
    combined.export(output_file, format="mp3")
    return output_file

def generate_silent_mp3(duration_ms, output_file="silent.mp3"):
    filename = f"./dialogues/{output_file}"
    silent_audio = AudioSegment.silent(duration=duration_ms)
    silent_audio.export(filename, format="mp3")
    return filename

def voice_generation(gender, age, voice_description):
    response = client.text_to_voice.create_previews(
        voice_description=f"GENDER:{gender} AGE:{age} VOICE: {voice_description}",
        text="hello i am a demo voice generated for whiteboard animation. I hope you all are fine. I am just a AI generated voice from the voice description.",
        )
    voice_id = response.previews[0].generated_voice_id
    response = client.text_to_voice.create_voice_from_preview(
        voice_name=str(uuid.uuid4()),
        voice_description="Random voice generated",
        generated_voice_id=voice_id,
    )
    return response.voice_id


def delete_voice(voice_id):
    response = client.voices.delete(voice_id=voice_id)
    return True


def text_to_speech_file(text: str, file_name, voice_id):
    # VOICE_MAP = {
    #     "narrator": "pNInz6obpgDQGcFmaJgB",
    #     "male": "29vD33N1CtxCmqQRPOHJ",
    #     "female":"21m00Tcm4TlvDq8ikWAM"
    # }
    if voice_id is None:
        voice_id = "pNInz6obpgDQGcFmaJgB"
    response = client.text_to_speech.convert(
        voice_id=voice_id,
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0,
            use_speaker_boost=True,
            speed=1,
        ),
    )

    # uncomment the line below to play the audio back
    # play(response)
    os.makedirs(f"dialogues", exist_ok=True)

    # Generating a unique file name for the output MP3 file
    save_file_path = f"./dialogues/{file_name}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    audio = AudioSegment.from_file(save_file_path)
    duration_ms = len(audio)

    # Return the path of the saved audio file
    return save_file_path, duration_ms

# text_to_speech_file("How can you do this to me?", "demo","male")