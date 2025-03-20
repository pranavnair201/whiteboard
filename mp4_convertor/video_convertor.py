# ---------------------------------------------Approach 1 --------------------------------------------
# from rlottie_python import LottieAnimation
# from moviepy import VideoFileClip
#
# anim = LottieAnimation.from_file("./scene_1.json")
# anim.save_animation("./scene_1.webp")
# clip = VideoFileClip("./scene_1.webp")
#
# # Write it as MP4
# clip.write_videofile("./output.mp4", codec="libx264")



# ---------------------------------------------- Approach 2 ------------------------------------------
# from lottie.exporters import exporters
# from lottie.importers import importers
#
# importer = importers.get_from_filename("scene_1.json")
# an = importer.process("scene_1.json")
#
# exporter = exporters.get_from_filename("scene_1.mp4")
# exporter.process(an, "scene_1.mp4", **{'format': None})

# ---------------------------------------------- Approach 3 ------------------------------------------
import os
import numpy as np
from rlottie_python import LottieAnimation
from moviepy import ImageSequenceClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, \
    concatenate_audioclips
from moviepy.video.fx import Loop

PAYLOAD = {
    "audio": [{"audio_path": "bg.mp3"}],
    "scenes": [
        {
            "lottie": "./demo_6.json",
            "text": [
                {
                    "src": "",
                    "thumb": "text1.png",
                    "enterStart": 0,
                    "exitEnd": 10,
                    "exitEffectName": "no_Effect",
                    "index": 1,
                    "enterEffectName": "handWriteAsian",
                    "enterEnd": 0.5,
                    "exitStart": 0,
                    "flipPosition": 0,
                    "height": 50,
                    "isMultimove": False,
                    "opacity": 1,
                    "subType": "DTXT",
                    "type": "TEXT",
                    "width": 150,
                    "x": 316,
                    "y": 186,
                    "angle": 0,
                    "assetId": "",
                    "textData": {
                        "splittedText": "Hello there",
                        "isDefault": True,
                        "formats": {
                            "containerStyle": {
                                "margin": "0px",
                                "fontFamily": "Sniglet-Regular",
                                "color": "rgb(0, 0, 0)",
                                "textAlign": "left",
                                "fontSize": "20px",
                                "lineHeight": 24.8,
                                "fontStyle": "normal",
                                "fontWeight": "400"
                            },
                            "bullet": {
                                "type": "none",
                                "bulletSpace": 10
                            },
                            "others": {
                                "isItalic": False,
                                "isAutoFontSize": False,
                                "sizeFixed": True,
                                "isUserFont": False,
                                "family": "Sniglet",
                                "isRTL": False,
                                "isFixedWidth": True,
                                "isBold": False
                            }
                        },
                        "langId": "fo.he.tx",
                        "htmlText": "Hello there"
                    }
                }
            ]
        },
        {
            "lottie": "./merged_lottie.json",
            "text": [
                {
                    "src": "",
                    "thumb": "text1.png",
                    "enterStart": 0,
                    "exitEnd": 10,
                    "exitEffectName": "no_Effect",
                    "index": 1,
                    "enterEffectName": "handWriteAsian",
                    "enterEnd": 0.5,
                    "exitStart": 0,
                    "flipPosition": 0,
                    "height": 50,
                    "isMultimove": False,
                    "opacity": 1,
                    "subType": "DTXT",
                    "type": "TEXT",
                    "width": 150,
                    "x": 22,
                    "y": 28,
                    "angle": 0,
                    "assetId": "",
                    "textData": {
                        "splittedText": "How are you?",
                        "isDefault": True,
                        "formats": {
                            "containerStyle": {
                                "margin": "0px",
                                "fontFamily": "Sniglet-Regular",
                                "color": "rgb(0, 0, 0)",
                                "textAlign": "left",
                                "fontSize": "20px",
                                "lineHeight": 24.8,
                                "fontStyle": "normal",
                                "fontWeight": "400"
                            },
                            "bullet": {
                                "type": "none",
                                "bulletSpace": 10
                            },
                            "others": {
                                "isItalic": False,
                                "isAutoFontSize": False,
                                "sizeFixed": True,
                                "isUserFont": False,
                                "family": "Sniglet",
                                "isRTL": False,
                                "isFixedWidth": True,
                                "isBold": False
                            }
                        },
                        "langId": "fo.he.tx",
                        "htmlText": "How are you?"
                    }
                }
            ]
        },
    ]
}

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
    clip = Loop(duration=20).apply(clip)
    texts = scene.get('text', [])
    text_clips = []
    for text in texts:
        text_clip = TextClip(text=text['textData']['htmlText'],
                    font_size=int(text['textData']['formats']['containerStyle']['fontSize'].replace("px", "")), color='black', font= "./demo.ttf")
        text_clip = text_clip.with_position((text['x'], text['y'])).with_duration(clip.duration)
        text_clips.append(text_clip)

    final_clip = CompositeVideoClip([clip]+text_clips)
    scene_clips.append(final_clip)

output_video = concatenate_videoclips(scene_clips, method='compose')


audios = PAYLOAD.get("audio")
audio_clips = []
for audio in audios:
    audio_clip = AudioFileClip(audio['audio_path']) # .subclipped(0, clip.duration)
    audio_clips.append(audio_clip)
output_audio = concatenate_audioclips(audio_clips).subclipped(0, output_video.duration)


final_video = output_video.with_audio(output_audio)
final_video.write_videofile("output.mp4", codec="libx264", audio_codec="aac")
