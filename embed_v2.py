import os
import uuid
import pandas as pd
import chromadb
import numpy as np
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings

IMAGE_DESC = [
    "A cartoon illustration of a doctor with a stethoscope, smiling.",
    "A cartoon tooth with a happy face, symbolizing dental care.",
    "A medical scene with a doctor treating a patient lying on a hospital bed, along with symbols like a syringe and an eye.",
    "An ambulance vehicle with a medical cross symbol on its side.",
    "A medicine bottle with a cross sign on the label, representing medication or vaccines.",
    "A woman sitting in a wheelchair, accompanied by pills or coins.",
    "A hospital building with ambulances parked outside, and medical symbols like pills and a glucose drip.",
    "A female doctor with a stethoscope around her neck, looking serious.",
    "A worried woman sitting in front of a monitor displaying a heart rate or medical chart.",
    "A microscope, representing laboratory testing or research.",
    "A black screen with a white heartbeat or ECG-like waveform, representing medical monitoring or health status.",
    "An ambulance vehicle with a siren on top, indicating emergency medical transport.",
    "A patient wrapped in bandages lying on a hospital stretcher, suggesting an injured or recovering person.",
    "A nurse or medical professional wearing a mask, scrub cap, and scrubs, holding a syringe, symbolizing healthcare and medical care.",
    "A doctor or healthcare professional with glasses holding a clipboard, indicating patient diagnosis or medical consultation."
]

# Create chroma
img_vectorstore = Chroma(
    collection_name="hospital_img_v1",
    persist_directory='./chroma',
    embedding_function=OpenCLIPEmbeddings(model_name = "ViT-g-14",checkpoint = "laion2b_s34b_b88k")
)

path = '/home/le-106/project/whiteboard/images_v2'

image_uris = sorted(
    [
        os.path.join(path, image_name)
        for image_name in os.listdir(path)
        if image_name.endswith(".png")
    ]
)
#
img_vectorstore.add_images(uris=image_uris, metadatas=[{"id": ind, "uri": uri} for ind, uri in enumerate(image_uris)])
#
print("Images embeddings saved successfully")

# df = pd.read_csv('train.csv')

txt_vectorstore = Chroma(
    collection_name="hospital_text_v1",
    persist_directory='./chroma',
    embedding_function=OpenAIEmbeddings()
)

# print(len(df['text']), len(image_uris))
txt_vectorstore.add_texts(texts=IMAGE_DESC, metadatas=[{"id": ind, "uri": uri} for ind, uri in enumerate(image_uris)])
print("Text embeddings saved successfully")
