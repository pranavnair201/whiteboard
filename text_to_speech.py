import requests
import os
from io import BytesIO
import time
from dotenv import load_dotenv
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()


def convert_mp3_to_wav(input_buffer):
    """
    Converts an MP3 buffer to WAV format and returns the WAV buffer.
    """
    print("Converting MP3 to WAV...")
    input_buffer.seek(0)  # Ensure the pointer is at the start of the MP3 buffer
    audio = AudioSegment.from_file(input_buffer, format="mp3")  # Read MP3 from buffer
    audio = audio.set_frame_rate(8000).set_channels(1)
    wav_buffer = BytesIO()
    audio.export(wav_buffer, format="wav", codec="pcm_mulaw")  # Export as WAV into the buffer
    wav_buffer.seek(0)  # Reset the pointer for WAV buffer
    return wav_buffer


def fetch_audio_to_buffer(audio_url):
    """
    Fetches an audio file from a URL and returns it as a buffer.
    """
    print(f"Fetching audio from URL: {audio_url}")
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()
    buffer = BytesIO()
    for chunk in response.iter_content(chunk_size=8192):
        buffer.write(chunk)
    buffer.seek(0)  # Reset the buffer pointer
    return buffer



def create_tts_clip(text, wellsaid_api_key):
    """
    Creates a TTS clip using the WellSaid Labs API and returns the clip ID.
    """
    try:
        url = "https://api.wellsaidlabs.com/v1/tts/clips"
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "X-API-KEY": wellsaid_api_key
        }
        payload = {
            "text": text,
            "speaker_id": 3  # Replace with the desired voice ID
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        clip_id = response.json().get("clip_id")
        if not clip_id:
            print("Error: Clip ID not found in WellSaid Labs response.")
            return None
        return clip_id
    except Exception as e:
        print(f"Error creating TTS clip: {e}")
        return None


def get_clip_info(clip_id, wellsaid_api_key):
    """
    Retrieves information about a specific TTS clip using its ID.
    """
    try:
        url = f"https://api.wellsaidlabs.com/v1/tts/clips/{clip_id}"
        headers = {
            "accept": "*/*",
            "X-API-KEY": wellsaid_api_key
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        clip_info = response.json()
        if clip_info.get("status") != "COMPLETE":
            print("Clip is not yet complete.")
            return None
        return clip_info.get("url")
    except Exception as e:
        print(f"Error retrieving clip information: {e}")
        return None


def download_audio_file(audio_url, output_file_mp3):
    """
    Downloads the audio file from the given URL and converts it to WAV format.
    """
    try:
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        with open(output_file_mp3, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    except Exception as e:
        print(f"Error downloading audio file: {e}")


def text_to_speech(text):
    try:
        wellsaid_api_key = os.getenv("WELLSAID_API_KEY")

        # Step 2: Create TTS clip using WellSaid Labs
        clip_id = create_tts_clip(text, wellsaid_api_key)
        if not clip_id:
            raise RuntimeError("Failed to create TTS clip.")

        print(f"Clip ID: {clip_id}")

        # Step 3: Poll for clip completion and get the audio URL
        audio_url = None
        while not audio_url:
            time.sleep(2)  # Wait for 2 seconds before retrying
            audio_url = get_clip_info(clip_id, wellsaid_api_key)

        print(f"Audio URL: {audio_url}")

        # Step 4: Download the audio file
        timestamp = int(time.time() * 1000)  # Milliseconds since epoch
        output_file_mp3 = f"speeches/output_audio_{timestamp}.mp3"

        download_audio_file(audio_url, output_file_mp3)
        mp3_buffer = fetch_audio_to_buffer(audio_url)

        return mp3_buffer

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__=="__main__":
    text_to_speech(text="Hello World")