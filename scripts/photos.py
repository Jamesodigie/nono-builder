"""Download chosen free Unsplash photos (picked through the Unsplash API by a
person), save web-ready WebP copies and a labelled contact sheet in ./out.
PICKS: name=photo-path, comma separated (photo-path from images.unsplash.com)."""
import io, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

os.makedirs("out", exist_ok=True)
UA = {"User-Agent": "nono-builder/1.0"}

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        return r.read()

picks = [x.strip().split("=", 1) for x in os.environ["PICKS"].split(",") if x.strip()]
tiles = []
for name, path in picks:
    img = Image.open(io.BytesIO(fetch(f"https://images.unsplash.com/{path}?w=2000&fm=jpg&q=85"))).convert("RGB")
    for w in (1600, 800):
        c = img.copy(); c.thumbnail((w, w * 2))
        c.save(f"out/{name}-{w}.webp", "WEBP", quality=72, method=6)
    t = img.copy(); t.thumbnail((480, 480))
    d = ImageDraw.Draw(t); d.rectangle((0, 0, t.width, 34), fill="black")
    d.text((6, 4), name, fill="yellow", font=ImageFont.load_default(size=24))
    tiles.append(t)
cols = 4
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 490, rows * 490), "white")
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * 490, (i // cols) * 490))
sheet.save("out/sheet.jpg", quality=72)
