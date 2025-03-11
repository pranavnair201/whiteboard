import os
import json
import base64
from typing import List

from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(
    model='gpt-4o',
    temperature=0.2,
    model_kwargs={"response_format": {"type": "json_object"}}
)


class SceneImageInformation(BaseModel):
    """Scene information"""
    visual_description: str = Field(description="visual description of the image")
    characters: List[str] = Field(description="Precisely described keywords of characters inside the image")
    props: List[str] = Field(description="Precisely described keywords of props inside the image")
    motions: List[str] = Field(description="detailed keyword of animated motion inside the image")


class CharacterInformation(BaseModel):
    """Character information"""
    visual_description: str = Field(description="Precise description of the character")

class PropInformation(BaseModel):
    """Prop information"""
    visual_description: str = Field(description="Precise description of the prop")


def embed_scenes():
    path = './images_v2/scenes/'

    image_uris = sorted(
        [
            os.path.join(path, image_name)
            for image_name in os.listdir(path)
            if image_name.endswith(".png")
        ]
    )

    IMG_DESC = []

    parser = JsonOutputParser(pydantic_object=SceneImageInformation)

    def fetch_chain(inputs):
        prompt = '''
        Provide the full detailed description of the image in hospital scenario. Also provide list of characters, props and animation motion visible in the image. 
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
                        {"type": "image_url", "image_url": {"url": f"{inputs['image']}"}}
                    ]
                )
            ]
        msg = llm.invoke(
            prompt
        )
        return msg.content

    for ind, img_uri in enumerate(image_uris):
        with open(img_uri, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode("utf-8")
        msg = fetch_chain(inputs={"image": f"data:image/png;base64,{base64_string}"})
        ans_payload = json.loads(msg)
        ans_payload.update({"id": ind, "uri": img_uri})
        ans_payload['characters'] = ",".join(ans_payload['characters'])
        ans_payload['props'] = ",".join(ans_payload['props'])
        ans_payload['motions'] = ",".join(ans_payload['motions'])
        print("Scene->", ans_payload)
        IMG_DESC.append(ans_payload)

    img_vectorstore = Chroma(
        collection_name="whiteboard_scenes_v1",
        persist_directory='./chroma',
        embedding_function=OpenAIEmbeddings()
    )

    img_vectorstore.add_texts(texts=[obj['visual_description'] for obj in IMG_DESC], metadatas=IMG_DESC)
    print("Scene embeddings saved successfully")

def embed_props_and_characters():
    character_path = './images_v2/characters/'
    props_path = './images_v2/props/'

    character_image_uris = sorted(
        [
            os.path.join(character_path, image_name)
            for image_name in os.listdir(character_path)
            if image_name.endswith(".png")
        ]
    )
    props_image_uris = sorted(
        [
            os.path.join(props_path, image_name)
            for image_name in os.listdir(props_path)
            if image_name.endswith(".png")
        ]
    )

    IMG_DESC = []

    def fetch_chain(inputs, type):
        if type == "character":
            parser = JsonOutputParser(pydantic_object=CharacterInformation)
            prompt = '''
            Provide the precise description of the character in hospital scenario. 
            '''
        else:
            parser = JsonOutputParser(pydantic_object=PropInformation)
            prompt = '''
            Provide the precise description of the prop in hospital scenario. 
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
                        {"type": "image_url", "image_url": {"url": f"{inputs['image']}"}}
                    ]
                )
            ]
        msg = llm.invoke(
            prompt
        )
        return msg.content

    for ind, img_uri in enumerate(character_image_uris):
        with open(img_uri, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode("utf-8")
        msg = fetch_chain(inputs={"image": f"data:image/png;base64,{base64_string}"}, type='characters')
        ans_payload = json.loads(msg)
        ans_payload.update({"id": ind, "uri": img_uri})
        print("Character->", ans_payload)
        IMG_DESC.append(ans_payload)

    character_vectorstore = Chroma(
        collection_name="whiteboard_characters_v1",
        persist_directory='./chroma',
        embedding_function=OpenAIEmbeddings()
    )

    character_vectorstore.add_texts(texts=[obj['visual_description'] for obj in IMG_DESC], metadatas=IMG_DESC)
    print("Character embeddings saved successfully")

    IMG_DESC = []
    for ind, img_uri in enumerate(props_image_uris):
        with open(img_uri, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode("utf-8")
        msg = fetch_chain(inputs={"image": f"data:image/png;base64,{base64_string}"}, type='props')
        ans_payload = json.loads(msg)
        ans_payload.update({"id": ind, "uri": img_uri})
        print("Props->", ans_payload)
        IMG_DESC.append(ans_payload)

    prop_vectorstore = Chroma(
        collection_name="whiteboard_props_v1",
        persist_directory='./chroma',
        embedding_function=OpenAIEmbeddings()
    )

    prop_vectorstore.add_texts(texts=[obj['visual_description'] for obj in IMG_DESC], metadatas=IMG_DESC)
    print("Props embeddings saved successfully")

embed_scenes()
embed_props_and_characters()