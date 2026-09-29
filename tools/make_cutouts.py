"""Purani posts se product ki photo kaat kar background hataata hai -> assets/*.png"""
from pathlib import Path
from PIL import Image
from rembg import remove, new_session

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

# name, source image, crop box as fractions (left, top, right, bottom)
SPECS = [
    ("seabuckthorn", "ig_17873405001617558.jpg", (0.31, 0.31, 0.68, 0.86)),
    ("seabuckthorn_b", "ig_17905374618437697.jpg", (0.25, 0.22, 0.69, 0.77)),
    ("b12", "ig_18592320076000970.jpg", (0.26, 0.21, 0.73, 0.81)),
    ("digest", "ig_18118521427538304.jpg", (0.48, 0.25, 0.86, 0.80)),
]

session = new_session("isnet-general-use")
for name, src, (l, t, r, b) in SPECS:
    im = Image.open(ROOT / "images" / src).convert("RGB")
    w, h = im.size
    crop = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
    crop.save(OUT / f"{name}_crop.jpg", quality=92)
    cut = remove(crop, session=session, post_process_mask=True)
    bbox = cut.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()
    if bbox:
        cut = cut.crop(bbox)
    cut.save(OUT / f"{name}.png", optimize=True)
    print(name, cut.size)
