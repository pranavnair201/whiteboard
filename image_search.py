from IPython.display import HTML, display
import io
from PIL import Image
import base64
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings

# Create chroma
vectorstore = Chroma(
    collection_name="pokemon_v2",
    persist_directory='./chroma',
    embedding_function=OpenCLIPEmbeddings(model_name = "ViT-g-14",checkpoint = "laion2b_s34b_b88k")
)

retriever = vectorstore.as_retriever()
docs = vectorstore.similarity_search_with_relevance_scores("pikachu", k=10)
for ind, doc in enumerate(docs):
    print(doc[1])
    img_bytes = base64.b64decode(doc[0].page_content)
    img = Image.open(io.BytesIO(img_bytes)).save(f"./predicted_images/images_{ind}.jpg")
