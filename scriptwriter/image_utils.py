import requests
from openai import OpenAI

from PIL import Image
from io import BytesIO

openai_client = OpenAI()


def fetch_img_url(img_desc, img_type="background"):
    additional_ins, size = "", ""
    if img_type=="character":
        size = "1024x1024"
        additional_ins = " The image should strictly have a black coloured background. Only the full body of the cartoon illustrated character should be visible."
    elif img_type=="background":
        additional_ins = " The background image should be cartoon illustrated and no characters should be seen in it."
        size="1792x1024"
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=img_desc + additional_ins,
        size=size,
        quality="standard",
        n=1
    )
    return response.data[0].url

def download_img(img_url, filename,img_type="background"):

    response = requests.get(img_url)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))

        # # Step 2: Resize the image
        # new_size = (300, 300)  # Set new width and height
        # resized_img = img.resize(new_size, Image.ANTIALIAS)

        if img_type=='character':
            img = img.convert("RGBA")
            pixels = img.load()

            width, height = img.size
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    if r == 0 and g == 0 and b == 0:
                        pixels[x, y] = (0, 0, 0, 0)

        # Step 3: Save the image
        img.save(filename)
        print(f"{filename} saved successfully.")
        return filename
    else:
        print(f"Failed to download the image {filename}")
