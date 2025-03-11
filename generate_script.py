from openai import OpenAI

from image_search_v3 import scene_search

client = OpenAI()

def generate_script(topic):
    """Generates a structured script based on the given topic."""
    prompt = (
        f"Generate a structured training script for {topic} in the following format:\n"
        "Scene 1: [Title]\n"
        "Visual: [Description of the scene]\n"
        "Narration: [Narration for the scene]\n"
        "Text on Screen: [Text displayed on screen]\n"
        "Divide each scene with '---' \n"
        "\nGenerate at least three scenes following this structure. Only Return scenes in the output no extra texts"
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a professional scriptwriter for training videos."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
    )
    for chunk in chat_completion:
        if chunk[0] == 'choices':
            return chunk[1][0].message.content

    return ""


if __name__ == "__main__":
    topic = input("Enter a topic for the script: ")
    script = generate_script(topic)
    print("\nGenerated Script:\n")
    print(script)
    scenes = script.split("---")
    print(scenes)
    for scene in scenes:
        visual = [i for i in scene.split('\n') if i.startswith('Visual')]
        print(f'Find Relevant Image for Scene: {visual[0]}')
        scene_search(query=visual[0])