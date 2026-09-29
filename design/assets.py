"""Product cutouts ko saaf karta hai (render se pehle). Same code GitHub par bhi chalta hai."""
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage


def _largest(rgba, open_px=0):
    a = np.array(rgba)[:, :, 3]
    solid = a > 40
    if open_px:
        solid = ndimage.binary_opening(solid, structure=np.ones((open_px, open_px)))
    lab, n = ndimage.label(solid)
    if n >= 1:
        sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
        keep = 1 + int(np.argmax(sizes))
        region = lab == keep
        if open_px:
            region = ndimage.binary_dilation(region, structure=np.ones((open_px // 2 + 1, open_px // 2 + 1)))
        arr = np.array(rgba)
        arr[:, :, 3] = np.where(region, arr[:, :, 3], 0)
        rgba = Image.fromarray(arr)
    return rgba.crop(rgba.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())


def _grabcut(path, box):
    img = cv2.imread(str(path))
    h, w = img.shape[:2]
    l, t, r, b = box
    rect = (int(l * w), int(t * h), int((r - l) * w), int((b - t) * h))
    mask = np.zeros((h, w), np.uint8)
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, rect, bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    m = cv2.GaussianBlur(m, (5, 5), 0)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    rgba = np.dstack([rgb, m])
    return _largest(Image.fromarray(rgba))


def prepare(root: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for name, src in (("seabuckthorn", "seabuckthorn_b"), ("b12", "b12")):
        im = _largest(Image.open(root / "assets" / f"{src}.png").convert("RGBA"), open_px=25)
        if name == "seabuckthorn":
            im = im.crop((0, 0, im.width, int(im.height * 0.975)))
        im.thumbnail((900, 1100))
        p = out / f"{name}.png"; im.save(p); res[name] = p
    dg = Image.open(root / "assets" / "digest_niroza.webp").convert("RGBA")
    p = out / "digest.png"; dg.save(p); res["digest"] = p
    lg = Image.open(root / "assets" / "logo.webp").convert("RGBA")
    p = out / "logo.png"; lg.save(p); res["logo"] = p
    return res


if __name__ == "__main__":
    import sys
    r = prepare(Path(sys.argv[1]), Path(sys.argv[2]))
    for k, v in r.items():
        print(k, Image.open(v).size)
