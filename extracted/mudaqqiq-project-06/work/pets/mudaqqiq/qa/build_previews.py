from pathlib import Path
import shutil
from PIL import Image, ImageDraw

run = Path("work/pets/mudaqqiq")
out = Path("outputs")
preview = out / "mudaqqiq-previews"
preview.mkdir(parents=True, exist_ok=True)
atlas = Image.open(run / "final/spritesheet-extended.png").convert("RGBA")
states = dict(zip(
    ("idle", "running-right", "running-left", "waving", "jumping",
     "failed", "waiting", "running", "review", "look"),
    (6, 8, 8, 4, 5, 8, 6, 6, 6, 16),
))

def frame(row, col):
    box = (col * 192, row * 208, (col + 1) * 192, (row + 1) * 208)
    bg = Image.new("RGBA", (192, 208), "#f0ece5")
    return Image.alpha_composite(bg, atlas.crop(box)).convert("RGB")

def gif(path, frames, timing):
    frames[0].save(path, save_all=True, append_images=frames[1:], loop=0,
                   duration=timing, disposal=2)

def label(im, caption):
    output = Image.new("RGB", (192, 232), "#f0ece5")
    output.paste(im, (0, 0))
    ImageDraw.Draw(output).text((9, 213), caption, fill="#282321")
    return output

motions = {}
for row, (state, count) in enumerate(states.items()):
    frames = [frame(row + col // 8, col % 8) for col in range(count)]
    motions[state] = frames
    gif(preview / f"{state}.gif", frames, 140 if state == "look" else 120)

transition = motions["idle"] + motions["jumping"] + motions["idle"]
gif(preview / "idle-jump-idle.gif", transition, 120)
all_frames = [
    label(im, state) for state, frames in motions.items()
    for im in frames * (2 if state != "look" else 1)
]
gif(out / "mudaqqiq-motion.gif", all_frames, 120)
stills = [
    ("Idle", motions["idle"][0]), ("Wave", motions["waving"][2]),
    ("Jump apex", motions["jumping"][2]), ("Look up-right", motions["look"][2]),
]
strip = Image.new("RGB", (192 * len(stills), 232))
for index, (caption, im) in enumerate(stills):
    strip.paste(label(im, caption), (192 * index, 0))
strip.save(out / "mudaqqiq-stills.png")
for source, target in [
    ("final/spritesheet-extended.png", "mudaqqiq-v2.png"),
    ("qa/contact-sheet-extended.png", "mudaqqiq-contact-sheet.png"),
    ("qa/directions.png", "mudaqqiq-directions.png"),
    ("qa/pet-quality.json", "mudaqqiq-quality.json"),
]:
    shutil.copyfile(run / source, out / target)

for path in [out / "mudaqqiq-motion.gif", *preview.glob("*.gif")]:
    with Image.open(path) as im:
        assert im.n_frames > 1, path
        print(path.name, im.n_frames, im.size)

