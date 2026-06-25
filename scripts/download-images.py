"""
Kör från projektets rot:  python scripts/download-images.py

Kräver:  pip install Pillow requests

Hämtar huvudbilden för varje händelse vars Wikipedia-länk pekar på sv.wikipedia.org,
konverterar till WebP (max 800 px bred) och sparar i public/images/.
Uppdaterar sedan src/data/events.json med image-fältet.
"""

import json, requests, os, io, time
from PIL import Image
from pathlib import Path

ROOT       = Path(__file__).parent.parent
EVENTS     = ROOT / "src" / "data" / "events.json"
IMAGES_DIR = ROOT / "public" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ArbetrorrelseTidslinje/1.0 (educational, non-commercial)"}

# Manuella overrides — Wikimedia Commons-filnamn för händelser där Wikipedia
# REST-API inte returnerar någon bild men vi vet att en bra bild finns.
# Format: event-id → Commons-filnamn (utan "File:" prefix)
MANUAL = {
    "1879-sundsvall":      "Sundsvall_strikes_1879.jpg",
    "1908-amalthea":       "Amalthea 1908.jpg",
    "1909-storstrejk":     "Storstrejken 1909.jpg",
    "1917-ryska-rev":      "Petrograd 1917.jpg",
    "1918-finska-inb":     "Finnish Civil War 1918.jpg",
    "1929-borskrasch":     "Crowd outside nyse.jpg",
    "1931-adalen":         "Ådalen 1931.jpg",
    "1932-sap-makten":     "Per Albin Hansson.jpg",
    "1938-saltsjobad":     "Saltsjöbadsavtalet 1938.jpg",
    "1939-ww2":            "Second world war europe 1941 map de.png",
    "1969-gruvstrejk":     "LKAB Kiruna mine.jpg",
    "1986-palme":          "Olof Palme.jpg",
    "1989-berlinmuren":    "Mauerfall Brandenburger Tor.jpg",
    "1914-ww1":            "Fotothek df ps 0000010 Schlachtfeld.jpg",
}

def wiki_article(url):
    if "sv.wikipedia.org/wiki/" in url:
        return url.split("/wiki/")[-1]
    return None

def commons_url(filename):
    """Stable redirect URL for a Wikimedia Commons file."""
    fn = filename.replace(" ", "_")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{requests.utils.quote(fn)}"

def sv_wiki_image(article):
    """Try to get the main image URL from Swedish Wikipedia via MediaWiki API."""
    try:
        r = requests.get(
            "https://sv.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": article,
                "prop": "pageimages",
                "pithumbsize": 800,
                "format": "json",
            },
            headers=HEADERS,
            timeout=10,
        )
        if r.status_code == 200:
            pages = r.json()["query"]["pages"]
            for page in pages.values():
                if "thumbnail" in page:
                    return page["thumbnail"]["source"]
    except Exception as e:
        print(f"    API error: {e}")
    return None

def save_webp(img_url, out_path, max_w=800):
    try:
        r = requests.get(img_url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            return False
        ct = r.headers.get("content-type", "")
        if "svg" in ct:
            print("    SVG — hoppar över")
            return False
        img = Image.open(io.BytesIO(r.content))
        if img.format == "SVG":
            print("    SVG — hoppar över")
            return False
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode not in ("RGB",):
            img = img.convert("RGB")
        if img.width > max_w:
            h = int(img.height * max_w / img.width)
            img = img.resize((max_w, h), Image.LANCZOS)
        img.save(out_path, "WEBP", quality=82)
        kb = os.path.getsize(out_path) // 1024
        print(f"    ✓  {img.width}×{img.height}px  {kb} KB  →  {out_path.name}")
        return True
    except Exception as e:
        print(f"    save error: {e}")
        return False

with open(EVENTS, encoding="utf-8") as f:
    events = json.load(f)

ok = skip = fail = 0

for ev in events:
    eid = ev["id"]

    # Hoppa över om bilden redan finns på disk
    out = IMAGES_DIR / f"{eid}.webp"
    if out.exists():
        if "image" not in ev:
            ev["image"] = f"images/{eid}.webp"
        print(f"{eid}  →  redan finns")
        skip += 1
        continue

    print(f"{eid}")

    img_url = None

    # 1. Manuell override via Commons
    if eid in MANUAL:
        img_url = commons_url(MANUAL[eid])
        print(f"    Commons: {MANUAL[eid]}")

    # 2. Automatisk hämtning via sv.wikipedia
    if not img_url:
        wiki_url = next(
            (l["url"] for l in ev.get("links", [])
             if l["type"] == "wiki" and "sv.wikipedia.org/wiki/" in l["url"]),
            None,
        )
        if wiki_url:
            article = wiki_article(wiki_url)
            img_url = sv_wiki_image(article)
            if img_url:
                print(f"    Wikipedia API: {img_url[:60]}…")

    if not img_url:
        print("    ingen bild hittad")
        fail += 1
        continue

    if img_url.lower().endswith(".svg"):
        print("    SVG — hoppar över")
        fail += 1
        continue

    if save_webp(img_url, out):
        ev["image"] = f"images/{eid}.webp"
        ok += 1
    else:
        fail += 1

    time.sleep(0.5)  # snäll mot Wikimedia

with open(EVENTS, "w", encoding="utf-8") as f:
    json.dump(events, f, indent=2, ensure_ascii=False)

print(f"\n{'='*50}")
print(f"  {ok} bilder sparade")
print(f"  {skip} hoppades över (fanns redan)")
print(f"  {fail} misslyckades / saknar bild")
print(f"  events.json uppdaterad")
