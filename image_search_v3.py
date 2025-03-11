import io
from PIL import Image
import base64
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings


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
    for ind, scene_doc in enumerate(scene_docs):
        print(f"Scene Image: {scene_doc[0].metadata['uri']}")
        print(f"Animated motions in the scene: {scene_doc[0].metadata['motions']}")
        print("Similar Characters:")
        for ind, character in enumerate(scene_doc[0].metadata['characters'].split(",")):
            print(f"    Character {ind+1}: ", character)
            character_docs = character_vectorstore.similarity_search_with_relevance_scores(character, k=5)
            for ind, character_doc in enumerate(character_docs):
                print(f"        - {character_doc[0].metadata['uri']} {character_doc[0].metadata['visual_description']} {character_doc[1]}")
        print("Similar Props:")
        for ind, prop in enumerate(scene_doc[0].metadata['props'].split(",")):
            print(f"    Prop {ind+1}: ", prop)
            prop_docs = prop_vectorstore.similarity_search_with_relevance_scores(prop, k=5)
            for ind, prop_doc in enumerate(prop_docs):
                print(f"        - {prop_doc[0].metadata['uri']} {prop_doc[0].metadata['visual_description']} {prop_doc[1]}")

query = '''
A calm hospice setting. A hospice care worker is gently washing their hands.
'''
scene_search(query=query)