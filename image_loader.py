import io
from PIL import Image
import pandas as pd
import base64
import ast

df = pd.read_csv('train.csv')

for ind, image in enumerate(df['image']):
    image_data = Image.open(io.BytesIO((ast.literal_eval(image)['bytes']))).save(f"./images/image_{ind}.jpg")

    print(f"Image {ind} saved successfully!")

