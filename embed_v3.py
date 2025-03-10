import os
import json
import base64

from langchain_chroma import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0.2,
    model_kwargs={"response_format": {"type": "json_object"}}
)

path = '/home/le-106/project/whiteboard/images_v2'

image_uris = sorted(
    [
        os.path.join(path, image_name)
        for image_name in os.listdir(path)
        if image_name.endswith(".png")
    ]
)

IMG_DESC = []

class ImageInformation(BaseModel):
 """Image description"""
 description: str = Field(description="image description")

parser = JsonOutputParser(pydantic_object=ImageInformation)

def fetch_chain(inputs):
    prompt = '''
    Provide the full detailed description of the image 
    '''
    msg = llm.invoke(
        [
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
    )
    return msg.content

for img_uri in image_uris:
    with open(img_uri, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
    msg = fetch_chain(inputs={"image": f"data:image/png;base64,{base64_string}"})
    ans_payload = json.loads(msg)
    print(ans_payload['description'])
    IMG_DESC.append(ans_payload['description'])

img_vectorstore = Chroma(
    collection_name="hospital_img_openai",
    persist_directory='./chroma',
    embedding_function=OpenAIEmbeddings()
)

img_vectorstore.add_texts(texts=IMG_DESC, metadatas=[{"id": ind, "uri": uri} for ind, uri in enumerate(image_uris)])
print("Text embeddings saved successfully")
