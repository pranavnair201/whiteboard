import json
import io
from typing import List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from json_parser import CustomJsonOutputParser

llm = ChatOpenAI(
    model='gpt-4o',
    temperature=0.2,
    model_kwargs={"response_format": {"type": "json_object"}}
)


class AnimationIdentifier(BaseModel):
    """Motion which suits according to query"""
    motion: str = Field(description="Motion required for the scene in detail")
    characters: List[str] = Field(description="Characters required for the scene in detail")


class ImageIdentifier(BaseModel):
    """Images which suits according to query"""
    images: List[int] = Field(description="IDs of the images")

def fetch_chain(inputs, type, context):
    if type == "character":
        prompt = f'''
        Your task is to analyze the human query and give the most suitable and similar characters from the below CONTEXT characters.
        
        CONTEXT:
        {context}
        
        '''
    else:
        prompt = f'''
        Your task is to analyze the human query and give the most suitable and similar props from the below CONTEXT props.

        CONTEXT:
        {context}

        '''
    parser = CustomJsonOutputParser(pydantic_object=ImageIdentifier)

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


def fetch_animation_chain(inputs):
    prompt = f'''
    Your task is to analyze the visual provided by human and give the most suitable motions and characters required for that visual.
    '''
    parser = CustomJsonOutputParser(pydantic_object=AnimationIdentifier)

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


def scene_search(query):
    scene_vectorstore = Chroma(
        collection_name="whiteboard_scenes_v1",
        persist_directory='./chroma',
        embedding_function=OpenAIEmbeddings()
    )
    character_vectorstore = Chroma(
        collection_name="whiteboard_characters_v1",
        persist_directory='./chroma',
        embedding_function=OpenAIEmbeddings()
    )
    prop_vectorstore = Chroma(
        collection_name="whiteboard_props_v1",
        persist_directory='./chroma',
        embedding_function=OpenAIEmbeddings()
    )

    scene_docs = scene_vectorstore.similarity_search_with_relevance_scores(query, k=1)
    msg = fetch_animation_chain(inputs={"query": query})
    animation_payload = json.loads(msg)
    print(f"Expected Motion: {animation_payload['motion']}")
    print(f"Expected Characters: {animation_payload['characters']}")
    for ind, scene_doc in enumerate(scene_docs):
        print(f"Scene Image: {scene_doc[0].metadata['uri']}")
        print(f"Animated motions in the scene: {scene_doc[0].metadata['motions']}")

        print("Similar Characters:")
        for ind, character in enumerate(scene_doc[0].metadata['characters'].split(",")):
            print(f"    Character {ind+1}: ", character)
            character_docs = character_vectorstore.similarity_search_with_relevance_scores(character, k=5)
            character_cxt = "\n".join([str({"id": doc[0].metadata['id'] ,"description": doc[0].metadata['visual_description']}) for doc in character_docs])
            response = fetch_chain(inputs={"query": character}, type="character", context=character_cxt)
            ans_payload = json.loads(response)
            img_ids = ans_payload['images']
            for ind, character_doc in enumerate(character_docs):
                if character_doc[0].metadata['id'] in img_ids:
                    print(f"        - {character_doc[0].metadata['uri']} {character_doc[0].metadata['visual_description']} {character_doc[1]}")

        print("Similar Props:")
        for ind, prop in enumerate(scene_doc[0].metadata['props'].split(",")):
            print(f"    Prop {ind+1}: ", prop)
            prop_docs = prop_vectorstore.similarity_search_with_relevance_scores(prop, k=5)
            prop_cxt = "\n".join(
                [str({"id": doc[0].metadata['id'], "description": doc[0].metadata['visual_description']}) for doc in
                 prop_docs])
            response = fetch_chain(inputs={"query": prop}, type="prop", context=prop_cxt)
            ans_payload = json.loads(response)
            img_ids = ans_payload['images']
            for ind, prop_doc in enumerate(prop_docs):
                if prop_doc[0].metadata['id'] in img_ids:
                    print(f"        - {prop_doc[0].metadata['uri']} {prop_doc[0].metadata['visual_description']} {prop_doc[1]}")

query = '''
A caregiver assisting an elderly patient in bed, followed by a recent hospital discharge scenario.
'''
scene_search(query=query)