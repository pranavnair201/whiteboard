import io
from PIL import Image
import base64
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings


query = "ambulance running on the road"
txt_vectorstore = Chroma(
    collection_name="hospital_text_v1",#"pokemon_text_v4",
    persist_directory='./chroma',
    embedding_function=OpenAIEmbeddings()
)

txt_results = []
docs = txt_vectorstore.similarity_search_with_relevance_scores(query, k=10)
for ind, doc in enumerate(docs):
    print(doc[0].metadata['id'], doc[0].page_content, doc[1])
    txt_results.append(doc[0].metadata['id'])

print("Text results fetched successfully!", txt_results)

img_vectorstore = Chroma(
    collection_name="hospital_img_v1",#'"pokemon_img_v3",
    persist_directory='./chroma',
    embedding_function=OpenCLIPEmbeddings(model_name = "ViT-g-14",checkpoint = "laion2b_s34b_b88k")
)
docs = img_vectorstore.similarity_search_with_relevance_scores(query, k=2, filter={"id": {"$in": txt_results}})
for ind, doc in enumerate(docs):
    print("Image Result", doc[0].metadata['id'], doc[1])
    img_bytes = base64.b64decode(doc[0].page_content)
    img = Image.open(io.BytesIO(img_bytes)).save(f"./predicted_images/images_{ind}_{doc[0].metadata['id']}.jpg")
