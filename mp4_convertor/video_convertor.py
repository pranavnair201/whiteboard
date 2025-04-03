import os
import numpy as np
from rlottie_python import LottieAnimation
from moviepy import ImageSequenceClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, \
    concatenate_audioclips, ImageClip, vfx
from moviepy.video.fx import Loop
import json


def custom_txt_animation(txt_clip, anim_obj, rotation=0):
    ANIM_MAP = {
        "fadeIn": vfx.CrossFadeIn(duration=anim_obj["duration"]),
        "fadeOut": vfx.CrossFadeOut(duration=anim_obj["duration"]),
        "blink": vfx.Blink(duration_on=1, duration_off=1)
    }
    txt_clip = vfx.Rotate(rotation).apply(txt_clip)
    txt_clip = ANIM_MAP[anim_obj['type']].apply(txt_clip)
    return txt_clip


with open("./animation_assets/project.json") as f:
    PAYLOAD = json.load(f)

scenes = PAYLOAD.get("scenes")
scene_clips = []
text_clips = []

for ind, scene in enumerate(scenes):
    if scene['type'] == "lottie":
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

        background_clip = ImageClip(scene['background_image']).with_duration(clip.duration)
        background_clip = background_clip.resized((800, 450))

        branding_clip = ImageClip("./company_logo.webp").with_duration(clip.duration).with_position(("right", "bottom")).resized((100, 25)).with_opacity(0.5)
        final_clip = CompositeVideoClip([background_clip, clip] + [branding_clip])
        scene_clips.append(final_clip)

    elif scene['type'] == "text":
        texts = scene.get('text', [])
        for text in texts:
            text_data = text['actions'][0]['data']
            txt_duration = text['actions'][0]['end'] - text['actions'][0]['start']
            text_clip = TextClip(
                text=text_data['text'],
                font_size=int(text_data['formatting']['fontSize'].replace("px", "")),
                color=text_data['formatting']['fontColor'],
                bg_color=text_data['formatting']['backgroundColor'] if not text_data['formatting']['transparent'] else None,
                margin=(10,10),
                font= f"./{text_data['formatting']['fontFamily']}.woff2")

            text_clip = text_clip.with_position(
                (text_data['position']['translate'][0],
                 text_data['position']['translate'][1])).with_start(
                text['actions'][0]['start']).with_duration(txt_duration)
            text_clip =  custom_txt_animation(txt_clip=text_clip,
                                              anim_obj=text_data['animation'],
                                              rotation=text_data["position"]['rotate'])
            text_clips.append(text_clip)

output_video = concatenate_videoclips(scene_clips, method='compose')
output_video = CompositeVideoClip([output_video] + text_clips)

audios = PAYLOAD.get("audio")
print("audios -=> ", audios)
audio_clips = []
for audio in audios:
    audio_clip = AudioFileClip(audio['audio_path']) # .subclipped(0, clip.duration)
    audio_clips.append(audio_clip)
output_audio = concatenate_audioclips(audio_clips).subclipped(0, output_video.duration)


final_video = output_video.with_audio(output_audio)
final_video.write_videofile("output-4.mp4", codec="libx264", audio_codec="aac")
