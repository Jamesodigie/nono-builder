"""Search Unsplash (free licence photos only) and build labelled contact sheets,
or export picked photos as web-ready WebP with credits. Output goes to ./out."""
import io, json, os, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36", "Accept-Language": "en"}
os.makedirs("out", exist_ok=True)

def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else json.loads(data)

def search(q, n):
    """Read the public search page and pull free (images.unsplash.com) photos."""
    import re, html as H
    slug = urllib.parse.quote(q.replace(" ", "-"))
    page = get(f"https://unsplash.com/s/photos/{slug}?license=free", True).decode("utf8", "ignore")
    seen, out = set(), []
    # Each result links to /photos/<slug>-<id> and shows images.unsplash.com/photo-...
    for m in re.finditer(r'href="/photos/([A-Za-z0-9_-]+)"', page):
        full = m.group(1)
        pid = full.rsplit("-", 1)[-1] if len(full.rsplit("-", 1)[-1]) == 11 else full[-11:]
        if pid in seen: continue
        window = page[m.end(): m.end() + 4000]
        im = re.search(r'https://images\.unsplash\.com/(photo-[0-9a-z-]+)', window)
        if not im: continue
        alt = re.search(r'alt="([^"]*)"', window)
        seen.add(pid)
        out.append({"id": pid, "raw": "https://images.unsplash.com/" + im.group(1) + "?ixlib=rb-4.0.3",
                    "alt": H.unescape(alt.group(1)) if alt else "", "slug": full})
        if len(out) >= n: break
    return out

def sheet(queries, n):
    font = ImageFont.load_default(size=22) if hasattr(ImageFont, "load_default") else None
    index = {}
    for qi, q in enumerate(queries):
        photos = search(q, n)
        tiles = []
        for p in photos:
            img = Image.open(io.BytesIO(get(p["raw"] + "&w=420&h=300&fit=crop&fm=jpg&q=70", True))).convert("RGB")
            ImageDraw.Draw(img).rectangle((0, 0, 420, 30), fill="black")
            ImageDraw.Draw(img).text((6, 3), p["id"], fill="yellow", font=font)
            tiles.append(img)
            index[p["id"]] = {"q": q, "alt": p["alt"], "raw": p["raw"], "slug": p["slug"]}
        cols = 5
        rows = (len(tiles) + cols - 1) // cols or 1
        out = Image.new("RGB", (cols * 425, rows * 305 + 40), "white")
        ImageDraw.Draw(out).text((8, 8), q, fill="black", font=font)
        for i, t in enumerate(tiles):
            out.paste(t, ((i % cols) * 425, 40 + (i // cols) * 305))
        out.save(f"out/sheet_{qi:02d}.jpg", quality=70)
    json.dump(index, open("out/index.json", "w"), indent=1)

def export(picks):
    import re, html as H
    credits = {}
    for item in picks:
        name, pid = item.split("=")
        page = get(f"https://unsplash.com/photos/{pid}", True).decode("utf8", "ignore")
        if "plus.unsplash.com" in page[:20000] and "images.unsplash.com/photo-" not in page:
            print("skip premium", pid); continue
        im = re.search(r'https://images\.unsplash\.com/(photo-[0-9a-z-]+)', page)
        og = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', page) or re.search(r'<title>([^<]*)</title>', page)
        title = H.unescape(og.group(1)) if og else ""
        by = re.search(r'Photo by ([^|<]+?) on Unsplash', page)
        img = Image.open(io.BytesIO(get("https://images.unsplash.com/" + im.group(1) + "?w=2000&fm=jpg&q=85", True))).convert("RGB")
        for w in (1600, 800):
            c = img.copy(); c.thumbnail((w, w * 2))
            c.save(f"out/{name}-{w}.webp", "WEBP", quality=74, method=6)
        credits[name] = {"id": pid, "photographer": by.group(1).strip() if by else "", "page": f"https://unsplash.com/photos/{pid}", "title": title}
    json.dump(credits, open("out/credits.json", "w"), indent=1)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "sheet":
        sheet([q.strip() for q in os.environ["QUERIES"].split("|") if q.strip()], int(os.environ.get("PER", "15")))
    else:
        export([x.strip() for x in os.environ["PICKS"].split(",") if x.strip()])
