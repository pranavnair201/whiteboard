import os
import numpy as np
from rlottie_python import LottieAnimation
from moviepy import ImageSequenceClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, \
    concatenate_audioclips, ImageClip, vfx
from moviepy.video.fx import Loop
import json

with open("./animation_assets/project.json") as f:
    PAYLOAD = json.load(f)

scenes = PAYLOAD.get("scenes")
scene_clips = []
for ind, scene in enumerate(scenes[:1]):
    os.makedirs(f"frames/{ind}", exist_ok=True)

    anim = LottieAnimation.from_file(scene['lottie'])

    for i in range(anim.lottie_animation_get_totalframe()):
        frame_path = f"./frames/{ind}/frame_{i:03d}.png"
        anim.save_frame(frame_path, frame_num=i)

    print("Total frames:", anim.lottie_animation_get_totalframe())
    print("Frame Rate:", anim.lottie_animation_get_framerate())
    print("Frame Duration:", anim.lottie_animation_get_duration())
    lottie_duration = anim.lottie_animation_get_duration()
    frames = [f"./frames/{ind}/frame_{i:03d}.png" for i in range(anim.lottie_animation_get_totalframe())]
    clip = ImageSequenceClip(frames, fps=anim.lottie_animation_get_framerate())
    # clip = concatenate_videoclips([clip] * int(np.ceil(15//lottie_duration)))
    clip = Loop(duration=scene.get('duration', 10)).apply(clip)
    texts = scene.get('text', [])
    text_clips = []
    for text in texts:
        text_data = text['textData']
        text_color = tuple(int(value.strip()) for value in text_data['formats']['containerStyle']['color'].strip("rgb()").split(","))
        text_clip = TextClip(
            text=text_data['htmlText'],
            font_size=int(text_data['formats']['containerStyle']['fontSize'].replace("px", "")),
            color=text_color,
            # stroke_width=10 if text_data['formats']['containerStyle']['fontWeight']=='bold' else 1,
            font= f"./{text_data['formats']['containerStyle']['fontFamily']}.woff2")

        text_clip = text_clip.with_position((text['x'], text['y'])).with_duration(clip.duration)
        text_clip =  vfx.Scroll(w=100, h=100, x_speed=0, y_speed=4).apply(text_clip)
        text_clips.append(text_clip)

    background_clip = ImageClip(scene['background_image']).with_duration(clip.duration)
    background_clip = background_clip.resized((800, 450))

    branding_clip = ImageClip("./company_logo.webp").with_duration(clip.duration).with_position(("right", "bottom")).resized((100, 25)).with_opacity(0.5)

    final_clip = CompositeVideoClip([background_clip, clip] + text_clips + [branding_clip])

    scene_clips.append(final_clip)

output_video = concatenate_videoclips(scene_clips, method='compose')


audios = PAYLOAD.get("audio")
print("audios -=> ", audios)
audio_clips = []
for audio in audios:
    audio_clip = AudioFileClip(audio['audio_path']) # .subclipped(0, clip.duration)
    audio_clips.append(audio_clip)
output_audio = concatenate_audioclips(audio_clips).subclipped(0, output_video.duration)


final_video = output_video.with_audio(output_audio)
final_video.write_videofile("output-4.mp4", codec="libx264", audio_codec="aac")
