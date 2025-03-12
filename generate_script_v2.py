import json
import io
from typing import List, Optional

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from json_parser import CustomJsonOutputParser


llm = ChatOpenAI(
    model='gpt-4o',
    temperature=0.2,
    verbose=True,
    model_kwargs={"response_format": {"type": "json_object"}}
)


class SceneInformation(BaseModel):
    """Scene description"""
    title: str = Field(description="Title of the scene")
    visual: str = Field(description="Detailed description of the scene")
    narration: str = Field(description="Narration of the scene")
    display_text: Optional[str] = Field(description="Text required to displayed on the scene")

class ScriptInformation(BaseModel):
    """Script description"""
    scenes: List[SceneInformation] = Field(description="List of scenes",min_length=3)

def fetch_chain(inputs):
    prompt = f'''
    You are a professional scriptwriter for training videos related to healthcare field.
    Generate a training script according to the user given topic
    '''
    parser = CustomJsonOutputParser(pydantic_object=ScriptInformation)

    prompt = [
        SystemMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "text", "text": parser.get_format_instructions()},
            ]
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": inputs['query']}
            ]
        )
    ]
    msg = llm.invoke(
        prompt
    )
    return msg.content



if __name__ == "__main__":
    # topic = input("Enter a topic for the script: ")
    query = "CLOSTRIDIUM DIFFICILE (C-Diff)"

    response = fetch_chain(inputs={"query": query})
    ans_payload = json.loads(response)
    scenes = ans_payload['scenes']
    for scene in scenes:
        print(scene)