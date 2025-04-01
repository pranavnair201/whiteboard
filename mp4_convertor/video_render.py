# import json
#
#
# # Load Lottie files
# with open("demo_1.json") as f1, open("demo_2.json") as f2:
#     lottie1 = json.load(f1)
#     lottie2 = json.load(f2)
#
# # Merge layers
# merged_layers = lottie1["layers"] + lottie2["layers"]
#
# # Merge assets (if any)
# merged_assets = lottie1.get("assets", []) + lottie2.get("assets", [])
#
# # Determine new out point (op)
# merged_op = min(lottie1["op"], lottie2["op"])
#
# # Create merged Lottie JSON
# merged_lottie = {
#     "v": lottie1["v"],
#     "meta": lottie1["meta"],  # Or merge meta fields as needed
#     "metadata": lottie1.get("metadata", None),
#     "nm": "Merged Animation",
#     "ddd": 0,
#     "assets": merged_assets,
#     "w": max(lottie1["w"], lottie2["w"]),
#     "h": max(lottie1["h"], lottie2["h"]),
#     "ip": 0,
#     "op": merged_op,
#     "fr": max(lottie1["fr"], lottie2["fr"]),
#     "fonts": { "list": [] },
#     "layers": merged_layers
# }
#
# # Save to file
# with open("merged_lottie.json", "w") as out_file:
#     json.dump(merged_lottie, out_file, indent=2)
#
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip
from moviepy.video.fx import Loop  # Correct for older versions

# Load first GIF
gif_clip_1 = VideoFileClip("./output.webm", has_mask=True)
gif_clip_1 = gif_clip_1.resized(height=100)
gif_clip_1 = Loop(duration=10).apply(gif_clip_1)
gif_clip_1 = gif_clip_1.with_position((0, 0.4), relative=True)

# Load second GIF
gif_clip_2 = VideoFileClip("./output.webm", has_mask=True)
gif_clip_2 = gif_clip_2.resized(height=100)
gif_clip_2 = Loop(duration=10).apply(gif_clip_2)
gif_clip_2 = gif_clip_2.with_position((0.4, 0), relative=True)

# Create background
background = ColorClip(size=(640, 480), color=(255, 255, 255), duration=10)

# Composite everything
final_clip = CompositeVideoClip([background, gif_clip_1, gif_clip_2])

# Export to MP4
final_clip.write_videofile("output.mp4", codec="libx264", fps=24)
