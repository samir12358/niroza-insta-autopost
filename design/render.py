"""posts.json ki har post ko 1080x1350 JPG mein banata hai -> posts/NNN.jpg"""
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import assets  # noqa: E402

PRODUCTS = {
    "sb": {"asset": "seabuckthorn", "name": "Niroza Sea Buckthorn",
           "c": {"bg1": "#FFF3E4", "bg2": "#FFD9B0", "main": "#E8621A", "deep": "#6B2A0A", "acc": "#FFC23D", "soft": "#FFE1C2", "ink": "#3B2314"}},
    "b12": {"asset": "b12", "name": "Niroza Vitamin B12",
            "c": {"bg1": "#E8F6F3", "bg2": "#BFE6DE", "main": "#0E8C7F", "deep": "#0B4A44", "acc": "#FFC940", "soft": "#CFEEE8", "ink": "#12302D"}},
    "dg": {"asset": "digest", "name": "Arogyam+ Digest Powder",
           "c": {"bg1": "#F4F9E9", "bg2": "#DDEFC2", "main": "#4E8A1E", "deep": "#23480E", "acc": "#F5C331", "soft": "#E3F1CC", "ink": "#22321A"}},
}


def main(fonts_dir, out_dir="posts", only=None):
    fonts_dir = Path(fonts_dir).resolve()
    out = ROOT / out_dir
    out.mkdir(exist_ok=True)
    tmp = ROOT / ".build"
    ready = assets.prepare(ROOT, tmp / "assets")
    env = Environment(loader=FileSystemLoader(str(HERE)))
    tpl = env.get_template("template.html")
    posts = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        for p in posts:
            if only and p["id"] not in only:
                continue
            prod = PRODUCTS[p["product"]]
            html = tpl.render(p=p, v=p.get("v", 0), c=prod["c"], prod=prod["asset"],
                              prod_name=prod["name"], img=ready[prod["asset"]].as_uri(),
                              fonts=fonts_dir.as_uri())
            f = tmp / f"{p['id']}.html"
            f.write_text(html, encoding="utf-8")
            page.goto(f.as_uri())
            page.evaluate("document.fonts.ready")
            png = tmp / f"{p['id']}.png"
            page.screenshot(path=str(png))
            Image.open(png).convert("RGB").save(out / f"{p['id']}.jpg", quality=90, optimize=True)
            print("rendered", p["id"])
        browser.close()


if __name__ == "__main__":
    only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "posts", only)
