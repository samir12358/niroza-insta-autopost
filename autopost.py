#!/usr/bin/env python3
"""
Niroza Ayurvedic - Instagram Auto Post
--------------------------------------
Har run par products.csv ki list se agla product uthata hai,
uski photo Instagram ke size mein JPG banata hai, caption banata hai
aur Instagram API se post kar deta hai.

Commands:
  python autopost.py post        -> agla 1 product post karo
  python autopost.py dry-run     -> sirf dikhao kya post hoga (post nahi karega)
  python autopost.py check       -> token, account aur product list check karo
  python autopost.py import      -> aapke Instagram ke purane posts se products.csv banao
  python autopost.py refresh     -> access token ko aur 60 din ke liye badhao

Zaroori environment variable:
  IG_ACCESS_TOKEN  -> Meta developer dashboard se mila Instagram access token
"""

import csv
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
PRODUCTS_FILE = ROOT / "products.csv"
CONFIG_FILE = ROOT / "config.json"
STATE_FILE = ROOT / "state.json"
IMAGES_DIR = ROOT / "images"
READY_DIR = ROOT / "ready"
QUEUE_FILE = ROOT / "posts.json"
POSTS_DIR = ROOT / "posts"

API_VERSION = os.environ.get("IG_API_VERSION", "v23.0")
GRAPH = f"https://graph.instagram.com/{API_VERSION}"
IST = timezone(timedelta(hours=5, minutes=30))

CSV_FIELDS = ["active", "name", "description", "price", "image", "hashtags", "caption"]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".gif", ".tif", ".tiff"}


# ----------------------------------------------------------------- helpers
def log(msg):
    print(f"[{datetime.now(IST):%Y-%m-%d %H:%M IST}] {msg}", flush=True)


def fail(msg):
    print(f"\n❌ ERROR: {msg}\n", file=sys.stderr, flush=True)
    sys.exit(1)


def load_json(path, default):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_config():
    cfg = {
        "footer": "📩 Order karne ke liye DM karein",
        "default_hashtags": "#ayurveda #ayurvedic #herbal #natural #niroza",
        "price_prefix": "💰 Price: ₹",
        "min_gap_minutes": 90,
        "background_color": "#FFFFFF",
    }
    cfg.update(load_json(CONFIG_FILE, {}))
    return cfg


def slugify(text):
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "product"


def token():
    t = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not t:
        fail("IG_ACCESS_TOKEN nahi mila. GitHub repo -> Settings -> Secrets -> "
             "Actions mein IG_ACCESS_TOKEN naam ka secret daliye.")
    return t


def api(method, path, **params):
    """Instagram Graph API call with clear error messages."""
    url = path if path.startswith("http") else f"{GRAPH}/{path.lstrip('/')}"
    params["access_token"] = token()
    for attempt in range(3):
        try:
            if method == "GET":
                r = requests.get(url, params=params, timeout=60)
            else:
                r = requests.post(url, data=params, timeout=60)
        except requests.RequestException as e:
            if attempt == 2:
                fail(f"Instagram se connect nahi ho paya: {e}")
            time.sleep(5)
            continue
        try:
            data = r.json()
        except ValueError:
            data = {"raw": r.text[:500]}
        if r.status_code >= 500 and attempt < 2:
            time.sleep(10)
            continue
        if r.status_code != 200 or "error" in data:
            err = data.get("error", data)
            msg = err.get("message") if isinstance(err, dict) else str(err)
            code = err.get("code") if isinstance(err, dict) else None
            hint = ""
            if code == 190:
                hint = ("\n👉 Token expire ya galat hai. Meta dashboard se naya token "
                        "banakar IG_ACCESS_TOKEN secret update karein.")
            elif code in (9, 4, 17, 32, 613):
                hint = "\n👉 Instagram ki limit lag gayi. Thodi der baad apne aap theek ho jayega."
            elif code == 10 or code == 200:
                hint = ("\n👉 Permission missing. Token banate waqt "
                        "instagram_business_content_publish permission allow karein.")
            fail(f"Instagram API error ({code}): {msg}{hint}")
        return data
    fail("Instagram API se jawab nahi mila.")


def me():
    return api("GET", "me", fields="user_id,username,account_type")


# ----------------------------------------------------------------- products
def read_products():
    if not PRODUCTS_FILE.exists():
        return []
    with open(PRODUCTS_FILE, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return [{k: (v or "").strip() for k, v in row.items() if k} for row in rows]


def active_products():
    items = []
    for p in read_products():
        if p.get("active", "yes").lower() in ("no", "n", "0", "false", "off"):
            continue
        if not p.get("image"):
            continue
        items.append(p)
    return items


def find_image(name):
    path = IMAGES_DIR / name
    if path.exists():
        return path
    # case-insensitive / extension-less match, kyunki log naam alag likh dete hain
    stem = Path(name).stem.lower()
    for f in IMAGES_DIR.glob("*"):
        if f.name.lower() == name.lower() or f.stem.lower() == stem:
            return f
    return None


def build_caption(p, cfg):
    if p.get("caption"):
        caption = p["caption"].replace("\\n", "\n")
    else:
        parts = []
        if p.get("name"):
            parts.append(f"🌿 {p['name']}")
        if p.get("description"):
            parts.append(p["description"].replace("\\n", "\n"))
        if p.get("price"):
            parts.append(f"{cfg['price_prefix']}{p['price']}")
        if cfg.get("footer"):
            parts.append(cfg["footer"])
        caption = "\n\n".join(parts)

    tags = p.get("hashtags") or cfg.get("default_hashtags", "")
    if tags and tags not in caption:
        caption = f"{caption}\n\n{tags}".strip()

    # Instagram limit: max 30 hashtags, max 2200 characters
    seen, out = 0, []
    for word in re.split(r"(\s+)", caption):
        if word.startswith("#"):
            seen += 1
            if seen > 30:
                continue
        out.append(word)
    caption = "".join(out).strip()
    return caption[:2200]


def prepare_image(src, bg_color="#FFFFFF"):
    """Photo ko Instagram ke niyam ke hisaab se JPG banata hai (4:5 se 1.91:1 ratio, max 1440px)."""
    READY_DIR.mkdir(exist_ok=True)
    out = READY_DIR / f"{slugify(src.stem)}.jpg"
    try:
        img = Image.open(src)
    except Exception as e:
        fail(f"Photo khul nahi rahi: {src.name} ({e}). JPG/PNG photo upload karein.")
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        base = Image.new("RGB", img.size, bg_color)
        base.paste(img, mask=img.split()[-1])
        img = base
    else:
        img = img.convert("RGB")

    w, h = img.size
    ratio = w / h
    if ratio < 0.8:          # bahut lambi photo -> side mein padding (4:5)
        new_w = int(round(h * 0.8))
        canvas = Image.new("RGB", (new_w, h), bg_color)
        canvas.paste(img, ((new_w - w) // 2, 0))
        img = canvas
    elif ratio > 1.91:       # bahut chaudi photo -> upar-neeche padding
        new_h = int(round(w / 1.91))
        canvas = Image.new("RGB", (w, new_h), bg_color)
        canvas.paste(img, (0, (new_h - h) // 2))
        img = canvas

    if img.width > 1440:
        img = img.resize((1440, int(round(img.height * 1440 / img.width))), Image.LANCZOS)
    if img.width < 320:
        img = img.resize((320, int(round(img.height * 320 / img.width))), Image.LANCZOS)

    quality = 92
    while True:
        img.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
        if out.stat().st_size <= 8 * 1024 * 1024 or quality <= 60:
            break
        quality -= 8
    return out


# ----------------------------------------------------------------- git (GitHub Actions)
def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, check=check,
                          capture_output=True, text=True).stdout.strip()


def git_push(message, paths):
    if not os.environ.get("GITHUB_ACTIONS"):
        return None
    git("config", "user.name", "insta-autopost-bot")
    git("config", "user.email", "insta-autopost-bot@users.noreply.github.com")
    git("add", *[str(p) for p in paths])
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0:
        git("commit", "-m", message)
        for attempt in range(3):
            r = subprocess.run(["git", "push"], cwd=ROOT, capture_output=True, text=True)
            if r.returncode == 0:
                break
            git("pull", "--rebase", check=False)
        else:
            fail(f"GitHub par save nahi ho paya: {r.stderr}")
    return git("rev-parse", "HEAD")


def public_url(local_path, sha):
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        fail("Public photo link sirf GitHub Actions ke andar ban sakta hai.")
    rel = local_path.relative_to(ROOT).as_posix()
    return f"https://raw.githubusercontent.com/{repo}/{sha}/{rel}"


# ----------------------------------------------------------------- commands
def pick_next(products, state):
    idx = state.get("next_index", 0) % len(products)
    return idx, products[idx]


def publish_image(img_path, caption):
    """Photo ko GitHub ke public link se Instagram par post karta hai."""
    sha = git_push(f"Photo ready: {img_path.name}", [img_path])
    image_url = public_url(img_path, sha or git("rev-parse", "HEAD"))
    for _ in range(12):
        try:
            if requests.head(image_url, timeout=20).status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(5)
    else:
        fail("Photo ka public link nahi khul raha. Repo PUBLIC hona chahiye.")
    user = me()
    ig_id = user["user_id"]
    cid = api("POST", f"{ig_id}/media", image_url=image_url, caption=caption)["id"]
    for _ in range(30):
        status = api("GET", cid, fields="status_code,status").get("status_code")
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            fail(f"Instagram ne photo reject kar di (status {status}).")
        time.sleep(5)
    media_id = api("POST", f"{ig_id}/media_publish", creation_id=cid)["id"]
    link = api("GET", media_id, fields="permalink").get("permalink", "")
    log(f"✅ Post ho gaya @{user.get('username')}: {link}")
    return media_id, link


def cmd_post_queue(dry=False):
    """posts.json ki nayi posts ek-ek karke (repeat nahi)."""
    cfg = load_config()
    posts = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    state = load_json(STATE_FILE, {"history": []})
    idx = state.get("next_post", 0)
    last = state.get("last_posted_at")
    if last and not dry and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
        gap = datetime.now(timezone.utc) - datetime.fromisoformat(last)
        if gap < timedelta(minutes=cfg["min_gap_minutes"]):
            log(f"Pichhla post sirf {int(gap.total_seconds() // 60)} min pehle hua tha - is baar skip.")
            return
    if idx >= len(posts):
        fail(f"Saari {len(posts)} nayi posts ho chuki hain. Nayi posts banwaiye (posts.json + posts/ folder).")
    p = posts[idx]
    img = POSTS_DIR / f"{p['id']}.jpg"
    if not img.exists():
        fail(f"Post ki photo nahi mili: posts/{img.name}. 'Render posts' workflow chalaiye.")
    log(f"Nayi post {idx + 1} of {len(posts)}: {p['id']}")
    print("----- CAPTION -----\n" + p["caption"] + "\n-------------------", flush=True)
    if dry:
        log("DRY RUN - kuch post nahi kiya gaya. Agli 3 posts: " + ", ".join(q["id"] for q in posts[idx:idx + 3]))
        return
    media_id, link = publish_image(img, p["caption"][:2200])
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state["next_post"] = idx + 1
    state["last_posted_at"] = now
    hist = state.setdefault("history", [])
    hist.append({"at": now, "post": p["id"], "media_id": media_id, "link": link})
    state["history"] = hist[-300:]
    save_json(STATE_FILE, state)
    git_push(f"Posted: {p['id']}", [STATE_FILE])
    left = len(posts) - idx - 1
    if left <= 6:
        log(f"⚠️ Sirf {left} nayi posts bachi hain - jaldi nayi posts banwa lijiye.")


def cmd_post(dry=False):
    if QUEUE_FILE.exists():
        return cmd_post_queue(dry)
    cfg = load_config()
    products = active_products()
    if not products:
        fail("products.csv mein koi active product nahi hai (image column zaroor bharein).")
    state = load_json(STATE_FILE, {"next_index": 0, "history": []})

    # Galti se ek hi slot mein 2 baar post na ho
    last = state.get("last_posted_at")
    if last and not dry and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
        gap = datetime.now(timezone.utc) - datetime.fromisoformat(last)
        if gap < timedelta(minutes=cfg["min_gap_minutes"]):
            log(f"Pichhla post sirf {int(gap.total_seconds() // 60)} min pehle hua tha - is baar skip.")
            return

    idx, p = pick_next(products, state)
    src = find_image(p["image"])
    if not src:
        fail(f"Photo nahi mili: images/{p['image']} (product: {p.get('name')}). "
             "images folder mein same naam ki photo upload karein.")
    caption = build_caption(p, cfg)
    ready = prepare_image(src, cfg["background_color"])

    log(f"Product #{idx + 1} of {len(products)}: {p.get('name') or p['image']}")
    log(f"Photo: {ready.relative_to(ROOT)} ({Image.open(ready).size[0]}x{Image.open(ready).size[1]})")
    print("----- CAPTION -----\n" + caption + "\n-------------------", flush=True)

    if dry:
        log("DRY RUN - kuch post nahi kiya gaya. Agle 3 products:")
        for i in range(3):
            q = products[(idx + i) % len(products)]
            print(f"   {i + 1}. {q.get('name') or q['image']}")
        return

    sha = git_push(f"Photo ready: {ready.name}", [READY_DIR])
    image_url = public_url(ready, sha)

    # GitHub raw link ko live hone mein kuch second lag sakte hain
    for _ in range(12):
        try:
            if requests.head(image_url, timeout=20).status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(5)
    else:
        fail("Photo ka public link nahi khul raha. Repo PUBLIC hona chahiye.")

    user = me()
    ig_id = user["user_id"]
    container = api("POST", f"{ig_id}/media", image_url=image_url, caption=caption)
    cid = container["id"]

    for _ in range(30):
        status = api("GET", cid, fields="status_code,status").get("status_code")
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            fail(f"Instagram ne photo reject kar di (status {status}).")
        time.sleep(5)

    result = api("POST", f"{ig_id}/media_publish", creation_id=cid)
    media_id = result["id"]
    link = api("GET", media_id, fields="permalink").get("permalink", "")
    log(f"✅ Post ho gaya @{user.get('username')}: {link}")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state["next_index"] = (idx + 1) % len(products)
    state["last_posted_at"] = now
    hist = state.setdefault("history", [])
    hist.append({"at": now, "product": p.get("name") or p["image"], "media_id": media_id, "link": link})
    state["history"] = hist[-200:]
    save_json(STATE_FILE, state)
    git_push(f"Posted: {p.get('name') or p['image']}", [STATE_FILE])


def cmd_check():
    user = me()
    log(f"✅ Token sahi hai. Account: @{user.get('username')} ({user.get('account_type')})")
    lim = api("GET", f"{user['user_id']}/content_publishing_limit", fields="quota_usage,config")
    data = (lim.get("data") or [{}])[0]
    log(f"Pichhle 24 ghante mein API se posts: {data.get('quota_usage')} "
        f"(limit {data.get('config', {}).get('quota_total', '?')})")
    if QUEUE_FILE.exists():
        posts = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        st = load_json(STATE_FILE, {})
        i = st.get("next_post", 0)
        missing = [q["id"] for q in posts if not (POSTS_DIR / f"{q['id']}.jpg").exists()]
        log(f"Nayi posts: {len(posts)} | ho chuki: {i} | baaki: {len(posts) - i}")
        log("Photos missing: " + (", ".join(missing[:10]) if missing else "koi nahi ✅"))
        log("Agli 3: " + ", ".join(q["id"] for q in posts[i:i + 3]))
        return
    products = active_products()
    log(f"Active products: {len(products)}")
    missing = [p["image"] for p in products if not find_image(p["image"])]
    if missing:
        log("⚠️  Ye photos images/ folder mein nahi mili: " + ", ".join(missing))
    else:
        log("Saari photos mil gayi ✅")
    state = load_json(STATE_FILE, {"next_index": 0})
    if products:
        idx = state.get("next_index", 0) % len(products)
        log("Agle 3 posts: " + " | ".join(
            products[(idx + i) % len(products)].get("name") or products[(idx + i) % len(products)]["image"]
            for i in range(3)))


def cmd_refresh():
    r = requests.get("https://graph.instagram.com/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": token()}, timeout=60)
    data = r.json()
    if "access_token" not in data:
        fail(f"Token refresh nahi hua: {data}")
    days = int(data.get("expires_in", 0)) // 86400
    new = data["access_token"]
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::add-mask::{new}")
    out = os.environ.get("NEW_TOKEN_FILE")
    if out:
        Path(out).write_text(new, encoding="utf-8")
    log(f"✅ Token refresh ho gaya - ab {days} din tak valid hai.")


def cmd_import(limit=100):
    """Aapke Instagram ke purane photo posts ko products.csv mein daal deta hai."""
    IMAGES_DIR.mkdir(exist_ok=True)
    existing = read_products()
    have = {p.get("image") for p in existing}
    rows = list(existing)
    added = 0
    url = f"{GRAPH}/me/media"
    params = {"fields": "id,caption,media_type,media_url,children{media_type,media_url}", "limit": 50}
    fetched = 0
    while url and fetched < limit:
        page = api("GET", url, **params)
        params = {}
        for m in page.get("data", []):
            fetched += 1
            img_url = None
            if m.get("media_type") == "IMAGE":
                img_url = m.get("media_url")
            elif m.get("media_type") == "CAROUSEL_ALBUM":
                for c in (m.get("children") or {}).get("data", []):
                    if c.get("media_type") == "IMAGE":
                        img_url = c.get("media_url")
                        break
            if not img_url:
                continue
            fname = f"ig_{m['id']}.jpg"
            if fname in have:
                continue
            resp = requests.get(img_url, timeout=60)
            if resp.status_code != 200:
                continue
            (IMAGES_DIR / fname).write_bytes(resp.content)

            cap = (m.get("caption") or "").strip()
            tags = " ".join(dict.fromkeys(re.findall(r"#\w+", cap)))
            body = re.sub(r"(?:\s*#\w+)+\s*$", "", cap).strip()
            lines = [l for l in body.splitlines() if l.strip()]
            name = re.sub(r"^[^\w]+", "", lines[0]).strip()[:80] if lines else ""
            desc = "\\n".join(lines[1:]) if len(lines) > 1 else ""
            rows.append({"active": "yes", "name": name, "description": desc, "price": "",
                         "image": fname, "hashtags": tags, "caption": ""})
            have.add(fname)
            added += 1
        url = (page.get("paging") or {}).get("next")

    with open(PRODUCTS_FILE, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})
    log(f"✅ {added} naye products Instagram se import hue. Kul products: {len(rows)}")
    log("Ab products.csv khol kar naam/price check karein aur jo repeat nahi karne unme active = no likhein.")
    git_push(f"Imported {added} products from Instagram", [PRODUCTS_FILE, IMAGES_DIR])


def main():
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "post").lower()
    if cmd == "post":
        cmd_post()
    elif cmd in ("dry-run", "dry", "preview"):
        cmd_post(dry=True)
    elif cmd == "check":
        cmd_check()
    elif cmd == "refresh":
        cmd_refresh()
    elif cmd == "import":
        cmd_import()
    else:
        fail(f"Unknown command: {cmd}. Use: post | dry-run | check | import | refresh")


if __name__ == "__main__":
    main()
