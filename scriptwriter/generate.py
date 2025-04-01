import json
import os
from enum import Enum
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains import LLMChain
from langchain.agents.openai_assistant import OpenAIAssistantRunnable

from json_parser import CustomJsonOutputParser
from audio_el import text_to_speech_file
from scriptwriter.audio_el import generate_silent_mp3, concatenate_mp3, voice_generation, delete_voice


llm_json = ChatOpenAI(
    model='gpt-4o',
    temperature=0.2,
    verbose=True,
    model_kwargs={"response_format": {"type": "json_object"}}
)
llm = ChatOpenAI(
    model='gpt-4o',
    temperature=0,
    verbose=True,
    max_tokens=1000
)

class SpeakerType(str, Enum):
    MALE = "character"
    NARRATOR = "narrator"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

#
# class SceneCharacter(BaseModel):
#     """Character needed to appear visually on the scene"""
#     name: str = Field(description="Name of Character")

class CharacterInformation(BaseModel):
    """Character description"""
    name: str = Field(description="Name of Character")
    gender: Gender = Field(description="Gender of Character")
    age: int = Field(description="Age of Character")
    voice_description: str = Field(description="Description of the character's voice suitable for tha scene")
    visual_description: str = Field(description="Full-body 2D cartoon illustration of the character suitable for the script")

class Dialogue(BaseModel):
    speaker_type: SpeakerType = Field(description="Type of the speaker")
    name: Optional[str] = Field(description="Name of the Character if speaker is a character")
    dialogue: str = Field(description="Dialogue of the speaker. Action tags are not needed, only the dialogue")
    sec_pause_before: int = Field(description="Milli seconds pause needed before delivering the dialogue")
    # style: float = Field(description="The style exaggeration of the voice required for the dialogue.", gt=0, lt=1)
    # speed: float = Field(description="The speed required for the dialogue delivery.", gt=0.7, lt=1.2)

class SceneInformation(BaseModel):
    """Scene description"""
    title: str = Field(description="Title of the scene")
    # visible_characters: List[SceneCharacter] = Field(description="List of characters need to visually appear on the scene")
    background: str = Field(description="2D cartoon illustration of the background suitable for the scene. There should be no depiction of characters.")
    dialogues: List[Dialogue] = Field(description="List of Dialogue in sequence for the scene", min_length=4)
    display_text: Optional[str] = Field(description="Text required to displayed on the scene")

class ScriptInformation(BaseModel):
    """Script description"""
    scenes: List[SceneInformation] = Field(description="List of scenes",min_length=3)
    characters: List[CharacterInformation] = Field(description="List of mature and old characters required for the script. No minors", max_length=3)


def fetch_assistant_response(user_query, thread_id=None):
    assistant = OpenAIAssistantRunnable(assistant_id="asst_Wcysum0zlbdyb0WXCZbrty8r")
    input = {"content":user_query}

    if thread_id is not None:
        input['thread_id'] = thread_id

    msg = assistant.invoke(input=input)
    return msg[-1].content[-1].text.value, msg[-1].thread_id


def fetch_chain(inputs):
    prompt = f'''
    You are a professional scriptwriter and director for scripting 2D cartoon illustrated training videos related to healthcare field.
    Generate a training script according to the human given topic.
    
    '''
    parser = CustomJsonOutputParser(pydantic_object=ScriptInformation)

    prompt = [
        SystemMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "text", "text": parser.get_schema_json()},
            ]
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": inputs['query']}
            ]
        )
    ]
    msg = llm_json.invoke(
        prompt
    )
    return msg.content


def fetch_img_chain(inputs):
    sys_prompt = '''
    You are a professional in generating cartoon background images. Generate a most suitable background image according to the scene.
    
    '''
    prompt = [
        SystemMessage(
            content=[
                {"type": "text", "text": sys_prompt}
            ]
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": f"{inputs['query']}"}
            ]
        )
    ]
    chat_prompt = ChatPromptTemplate(messages=prompt)
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    msg = chain.invoke(
        input={}
    )
    return msg.get('text')


if __name__ == "__main__":
    query = "Corona virus. How to prevent it. Make the script more sarcastic and funny"
    thread_id = None #"thread_1"
    # response = fetch_chain(inputs={"query": query})
    response, thread_id = fetch_assistant_response(user_query=query, thread_id=thread_id)
    print(f"THREAD_ID--->>{thread_id}")
    print(response)
    ans_payload = json.loads(response)

    os.makedirs(f"bg", exist_ok=True)
    os.makedirs(f"characters", exist_ok=True)

    voice_map = {}
    for ind, character in enumerate(ans_payload['characters']):
        # img_url = fetch_img_url(img_desc=character['visual_description'], img_type='character')
        # character["img_url"] = download_img(img_url=img_url, filename=f"./characters/character_{ind}.png", img_type="character")
        voice_map[character["name"]] = voice_generation(gender=character['gender'], age=character['age'], voice_description=character["voice_description"])
    print(voice_map)
    for s_ind, scene in enumerate(ans_payload['scenes']):
        # img_url = fetch_img_url(img_desc=scene['background'], img_type='background')
        # scene["bg_url"] = download_img(img_url=img_url, filename=f"./bg/bg_{s_ind}.png")
        audio_files = []
        for d_ind, dialogue in enumerate(scene['dialogues']):
            dialogue["audio"] = text_to_speech_file(
                text=dialogue['dialogue'],
                file_name=f"dialogue_{s_ind}_{d_ind}",
                voice_id=voice_map.get(dialogue.get("name", "Narrator"), None)
            )
            if dialogue['sec_pause_before']>0:
                pause_audio = generate_silent_mp3(dialogue['sec_pause_before'], f"pause_{s_ind}_{d_ind}")
                audio_files.append(pause_audio)
            audio_files.append(dialogue["audio"])
        scene['audio'] = concatenate_mp3(files=audio_files, output_file=f"./dialogues/scene_{s_ind}.mp3")

    for voice_id in voice_map.values():
        delete_voice(voice_id=voice_id)

    with open("./script.json", "w") as file:
        json.dump(ans_payload, file, indent=4)