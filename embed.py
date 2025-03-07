import os
import uuid

import chromadb
import numpy as np
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from PIL import Image as _PILImage

# Create chroma
vectorstore = Chroma(
    collection_name="pokemon_v2",
    persist_directory='./chroma',
    embedding_function=OpenCLIPEmbeddings(model_name = "ViT-g-14",checkpoint = "laion2b_s34b_b88k")
)

path = '/home/le-106/project/whiteboard/images'

image_uris = sorted(
    [
        os.path.join(path, image_name)
        for image_name in os.listdir(path)
        if image_name.endswith(".jpg")
    ]
)
print(image_uris)
# image_uris = ["/home/le-106/project/whiteboard/images/modi.jpg"]
# Add images
vectorstore.add_images(uris=image_uris)

# Make retriever
retriever = vectorstore.as_retriever()