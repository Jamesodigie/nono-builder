"""Search Unsplash (free licence photos only) and build labelled contact sheets,
or export picked photos as web-ready WebP with credits. Output goes to ./out."""
import io, json, os, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

UA = {"User-Agent": "nono-builder/1.0", "Accept": "application/json"}
os.makedirs("out", exist_ok=True)

def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else json.loads(data)

def search(q, n):
    url = "https://unsplash.com/napi/search/photos?" + urllib.parse.urlencode({"query": q, "per_page": n})
    res = get(url)["results"]
    return [p for p in res if not p.get("premium") and not p.get("plus") and "plus.unsplash.com" not in p["urls"]["raw"]]

def sheet(queries, n):
    font = ImageFont.load_default(size=22) if hasattr(ImageFont, "load_default") else None
    index = {}
    for qi, q in enumerate(queries):
        photos = search(q, n)
        tiles = []
        for p in photos:
            img = Image.open(io.BytesIO(get(p["urls"]["raw"] + "&w=420&h=300&fit=crop&fm=jpg&q=70", True))).convert("RGB")
            ImageDraw.Draw(img).rectangle((0, 0, 420, 30), fill="black")
            ImageDraw.Draw(img).text((6, 3), p["id"], fill="yellow", font=font)
            tiles.append(img)
            index[p["id"]] = {"q": q, "alt": p.get("alt_description"), "user": p["user"]["name"], "w": p["width"], "h": p["height"]}
        cols = 5
        rows = (len(tiles) + cols - 1) // cols or 1
        out = Image.new("RGB", (cols * 425, rows * 305 + 40), "white")
        ImageDraw.Draw(out).text((8, 8), q, fill="black", font=font)
        for i, t in enumerate(tiles):
            out.paste(t, ((i % cols) * 425, 40 + (i // cols) * 305))
        out.save(f"out/sheet_{qi:02d}.jpg", quality=70)
    json.dump(index, open("out/index.json", "w"), indent=1)

def export(picks):
    credits = {}
    for item in picks:
        name, pid = item.split("=")
        p = get(f"https://unsplash.com/napi/photos/{pid}")
        if p.get("premium") or p.get("plus"):
            print("skip premium", pid); continue
        # Record the download as the Unsplash guidelines ask.
        try: get(p["links"]["download_location"].replace("api.unsplash.com", "unsplash.com/napi"))
        except Exception as e: print("download ping failed", e)
        img = Image.open(io.BytesIO(get(p["urls"]["raw"] + "&w=2000&fm=jpg&q=85", True))).convert("RGB")
        for w in (1600, 800):
            im = img.copy(); im.thumbnail((w, w * 2))
            im.save(f"out/{name}-{w}.webp", "WEBP", quality=74, method=6)
        credits[name] = {"id": pid, "photographer": p["user"]["name"], "profile": p["user"]["links"]["html"],
                         "page": p["links"]["html"], "alt": p.get("alt_description")}
    json.dump(credits, open("out/credits.json", "w"), indent=1)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "sheet":
        sheet([q.strip() for q in os.environ["QUERIES"].split("|") if q.strip()], int(os.environ.get("PER", "15")))
    else:
        export([x.strip() for x in os.environ["PICKS"].split(",") if x.strip()])
