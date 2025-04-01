import json
import base64
from typing import List
from PIL import Image

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from moviepy import ImageClip, CompositeVideoClip


llm = ChatOpenAI(
    model='gpt-4o',
    temperature=0.2,
    model_kwargs={"response_format": {"type": "json_object"}}
)


class CharacterPositionInformation(BaseModel):
    """Position of the character - The xy coordinates should be purely based on screen coordinate system. Consider Background image as the screen"""
    x_coordinate: int = Field(description="x coordinate of the character")
    y_coordinate: int = Field(description="y coordinate of the character")


class CharacterDimensionInformation(BaseModel):
    """Dimension of the character"""
    width: int = Field(description="Width of the character")
    height: int = Field(description="Height of the character")

class CharacterInformation(BaseModel):
    """Character size and position information"""
    desc: str = Field(description="Small description of the character")
    position: CharacterPositionInformation = Field(description="Suitable position for the character with respect to the background image")
    dimension: CharacterDimensionInformation = Field(description="Suitable dimension of the character with respect to the background image")

class CharactersData(BaseModel):
    characters: List[CharacterInformation] = Field(description="Placement information of characters in sequence.")

def fetch_chain(inputs):
    parser = JsonOutputParser(pydantic_object=CharactersData)

    prompt = '''
    You are professional layout artist. Your task is to analyze the first uploaded background image and other uploaded character images
    and determine that how the characters should be positioned on the background image according to the instructions provided in the VISUALS.
    Also give a resized new dimensions which would fit the character relative to the background itself, feel free to enlarge or shrink the character.

    VISUALS:
    The spiderman is sitting above the black chair.

    NOTE: The character's position and dimension should be relatively based on the background image's dimension. Just ignore the transparent background.
    '''
    prompt = [
        SystemMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "text", "text": parser.get_format_instructions()},
            ]
        ),
        HumanMessage(
            content=[
                {"type": "image_url", "image_url": {"url": f"{img}"}} for img in inputs["images"]
            ]
        )
    ]
    msg = llm.invoke(
        prompt
    )
    return msg.content

data = {"images": []}
image_uris = ["./bg_0.png", "./character_1.png"]
for ind, img_uri in enumerate(image_uris):
    with open(img_uri, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
    data['images'].append(f"data:image/png;base64,{base64_string}")

    with open(img_uri, "rb") as image_file:
        img = Image.open(image_file)
        print(f"REAL DIMENSIONS: {img_uri}-->>{img.size}")

msg = fetch_chain(inputs=data)
ans_payload = json.loads(msg)
print(ans_payload)

video_clips=[ImageClip(img=image_uris[0], duration=10)]
for ind, character in enumerate(ans_payload["characters"]):
    print(f"{image_uris[ind+1]} --> {(character['dimension']['width'], character['dimension']['height'])} --> {(character['position']['x_coordinate'], character['position']['y_coordinate'])}")
    video_clips.append(
        ImageClip(img=image_uris[ind+1], duration=10).resized((
            character["dimension"]['width'], character["dimension"]['height'])).with_position(
            (character["position"]["x_coordinate"], character["position"]["y_coordinate"])))

final_clip = CompositeVideoClip(video_clips)
final_clip.write_videofile("output.mp4", fps=24)