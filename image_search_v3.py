import io
from PIL import Image
import base64
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings


query = "female doctor"
txt_vectorstore = Chroma(
    collection_name="hospital_img_openai",#"pokemon_text_v4",
    persist_directory='./chroma',
    embedding_function=OpenAIEmbeddings()
)

txt_results = []
docs = txt_vectorstore.similarity_search_with_relevance_scores(query, k=1)
for ind, doc in enumerate(docs):
    print(doc[0].metadata['uri'], doc[0].metadata['id'], doc[0].page_content, doc[1])
