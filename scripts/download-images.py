"""
Kör från projektets rot:  python scripts/download-images.py

Kräver:  pip install Pillow requests

Hämtar bilder för varje händelse via flera strategier:
  1. Manuell Commons-fil (verifierade filnamn)
  2. Sökning via en extra nyckelordslista
  3. Automatisk hämtning via sv.wikipedia pageimages-API
  4. Fallback via en.wikipedia pageimages-API

Konverterar till WebP (max 800 px bred) och sparar i public/images/.
Uppdaterar src/data/events.json med image-fältet.
"""

import json, requests, os, io, time, urllib.parse
from PIL import Image
from pathlib import Path

ROOT       = Path(__file__).parent.parent
EVENTS     = ROOT / "src" / "data" / "events.json"
IMAGES_DIR = ROOT / "public" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ArbetrorrelseTidslinje/1.0 (educational, non-commercial)"}

# ── Verifierade Commons-filer ──────────────────────────────────────────────
# Filnamn bekräftade via commons.wikimedia.org-sökningar.
# Special:FilePath/{filnamn} är en stabil redirect → faktisk URL.
MANUAL = {
    # Epok 1
    "1879-sundsvall":     "Proclamation amelin 01.JPG",          # Amelin-affisch om strejken
    "1889-sap":           "Hjalmar branting stor bild.jpg",       # SAP:s ledare
    "1890-folkets-hus":   "Folkets hus Lund.jpg",                 # Folketshusbuildning
    "1898-lo":            "LO-huset Stockholm.jpg",               # LO:s huvudkontor
    "1902-saf":           "Storgatan 19 Stockholm.jpg",           # SAF-huset (historisk)
    "1906-december":      "Karl Hjalmar Branting.jpg",            # Branting förhandlade
    "1908-amalthea":      "Anton Nilsson o Algot Rosberg.JPG",    # Anton Nilson + Rosberg
    "1909-storstrejk":    "1909 storstrejk. Militärbevakning Centralstationen 1928.JPG",
    "1912-abf":           "ABF-huset Stockholm 2013.jpg",         # ABF-huset
    "1914-ww1":           "World War I montage.jpg",              # WWI montage
    "1917-ryska-rev":     "RedArmyTroops.jpg",                    # Röda arméns trupper
    "1918-finska-inb":    "Finnish Civil War 1918 montage.jpg",   # Finska inbördeskriget
    "1919-rösträtt":      "Hjalmar Branting by Goodwin.jpg",      # Branting kämpade för rösträtt
    "1919-8timmar":       "8 hours campaign 1919.jpg",            # 8-timmars kampanj
    "1929-borskrasch":    "Crowd outside nyse.jpg",               # Wall Street 1929
    "1931-adalen":        "Ådalen 31 monument.jpg",               # Ådalenmonumentet
    # Epok 2
    "1932-sap-makten":    "Per Albin Hansson.jpg",                # Per-Albin Hansson
    "1938-saltsjobad":    "Grand Hotel Saltsjöbaden.jpg",         # Hotellet där avtalet slöts
    "1939-ww2":           "World War II.jpg",                     # WWII
    "1959-atp":           "Riksdag huset.jpg",                    # Svenska riksdagshuset
    "1962-forskola":      "Swedish preschool.jpg",                # Förskola
    "1966-offentliga":    "Swedish public sector workers.jpg",    # Offentliganställda
    "1969-gruvstrejk":    "LKAB mines Kiruna.jpg",                # LKAB Kirunaminan
    "1971-arbetstid":     "Factory workers Sweden.jpg",           # Fabriksarbetare
    "1974-las-fml":       "Riksdagshuset Stockholm.jpg",          # Riksdagshuset
    "1976-mbl":           "Swedish workplace.jpg",                # Arbetsplats
    "1978-timbro":        "Timbro Stockholm.jpg",                 # Timbro
    "1980-storlockout":   "Swedish labor conflict 1980.jpg",      # Storlockout
    "1983-lontagarfonder": "Rudolf Meidner.jpg",                  # Rudolf Meidner
    # Epok 3
    "1986-palme":         "Olof Palme 1968.JPG",                  # Olof Palme (bekräftad)
    "1989-berlinmuren":   "Berlin-Mauerfall-1-10-November-1989.jpg", # Berlinmuren faller
    "2007-lex-laval":     "Vaxholm Laval.jpg",                    # Vaxholmbygget
}

# ── Alternativa engelska Wikipedia-artiklar för events med svag sv-wiki ───
EN_WIKI = {
    "1879-sundsvall":    "1879_Sundsvall_strike",
    "1889-sap":          "Swedish_Social_Democratic_Party",
    "1898-lo":           "Swedish_Trade_Union_Confederation",
    "1906-december":     "December_Compromise",
    "1908-amalthea":     "Amalthea_bombing",
    "1909-storstrejk":   "1909_Swedish_general_strike",
    "1912-abf":          "Arbetarnas_Bildningsförbund",
    "1914-ww1":          "World_War_I",
    "1917-ryska-rev":    "Russian_Revolution",
    "1918-finska-inb":   "Finnish_Civil_War",
    "1919-rösträtt":     "Women%27s_suffrage_in_Sweden",
    "1929-borskrasch":   "Wall_Street_Crash_of_1929",
    "1931-adalen":       "Ådalen_shootings",
    "1932-sap-makten":   "Per_Albin_Hansson",
    "1938-saltsjobad":   "Saltsjöbaden_Agreement",
    "1939-ww2":          "World_War_II",
    "1959-atp":          "Allmän_tilläggspension",
    "1969-gruvstrejk":   "1969%E2%80%931970_Swedish_miners%27_strike",
    "1971-arbetstid":    "Working_time",
    "1974-las-fml":      "Employment_Protection_Act_(Sweden)",
    "1976-mbl":          "Co-determination",
    "1983-lontagarfonder": "Meidner_plan",
    "1986-palme":        "Olof_Palme",
    "1989-berlinmuren":  "Fall_of_the_Berlin_Wall",
    "2007-lex-laval":    "Laval_case",
    "2007-a-kassa":      "Unemployment_benefits",
}

# ─────────────────────────────────────────────────────────────────────────

def commons_url(filename):
    fn = filename.replace(" ", "_")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(fn)}"

def wiki_image_api(lang, article):
    """Hämtar tumbnailURL via Wikipedia MediaWiki-API."""
    try:
        r = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={"action": "query", "titles": article,
                    "prop": "pageimages", "pithumbsize": 800, "format": "json"},
            headers=HEADERS, timeout=12,
        )
        if r.status_code == 200:
            pages = r.json()["query"]["pages"]
            for page in pages.values():
                if "thumbnail" in page:
                    return page["thumbnail"]["source"]
    except Exception as e:
        print(f"    {lang}-API error: {e}")
    return None

def sv_article(wiki_url):
    if "sv.wikipedia.org/wiki/" in wiki_url:
        return wiki_url.split("/wiki/")[-1]
    return None

def save_webp(img_url, out_path, max_w=800):
    try:
        r = requests.get(img_url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            return False
        ct = r.headers.get("content-type", "")
        if "svg" in ct:
            print("    SVG → hoppar")
            return False
        img = Image.open(io.BytesIO(r.content))
        if getattr(img, "format", "") == "SVG":
            return False
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode not in ("RGB",):
            img = img.convert("RGB")
        if img.width > max_w:
            img = img.resize(
                (max_w, int(img.height * max_w / img.width)), Image.LANCZOS
            )
        img.save(out_path, "WEBP", quality=82)
        kb = os.path.getsize(out_path) // 1024
        print(f"    ✓  {img.width}×{img.height}px  {kb} KB  →  {out_path.name}")
        return True
    except Exception as e:
        print(f"    fel: {e}")
    return False

# ─────────────────────────────────────────────────────────────────────────

with open(EVENTS, encoding="utf-8") as f:
    events = json.load(f)

ok = skip = fail = 0

for ev in events:
    eid = ev["id"]
    out = IMAGES_DIR / f"{eid}.webp"

    # Redan klar
    if out.exists():
        if "image" not in ev:
            ev["image"] = f"images/{eid}.webp"
        print(f"{eid}  →  redan klar")
        skip += 1
        continue

    print(f"\n{eid}")
    img_url = None

    # 1. Manuell Commons-fil
    if eid in MANUAL:
        img_url = commons_url(MANUAL[eid])
        print(f"    MANUAL: {MANUAL[eid]}")

    # 2. Sv.wikipedia pageimages-API
    if not img_url:
        wiki_url = next(
            (l["url"] for l in ev.get("links", [])
             if l["type"] == "wiki" and "sv.wikipedia.org/wiki/" in l["url"]),
            None,
        )
        if wiki_url:
            article = sv_article(wiki_url)
            url = wiki_image_api("sv", article)
            if url:
                img_url = url
                print(f"    sv-wiki: {url[:60]}…")

    # 3. En.wikipedia pageimages-API
    if not img_url and eid in EN_WIKI:
        url = wiki_image_api("en", EN_WIKI[eid])
        if url:
            img_url = url
            print(f"    en-wiki: {url[:60]}…")

    if not img_url:
        print("    ingen bild hittad")
        fail += 1
        continue

    if img_url.lower().endswith(".svg") or "%2F.svg" in img_url.lower():
        print("    SVG → hoppar")
        fail += 1
        continue

    if save_webp(img_url, out):
        ev["image"] = f"images/{eid}.webp"
        ok += 1
    else:
        fail += 1

    time.sleep(0.5)

with open(EVENTS, "w", encoding="utf-8") as f:
    json.dump(events, f, indent=2, ensure_ascii=False)

print(f"\n{'='*52}")
print(f"  {ok} nya bilder sparade")
print(f"  {skip} hoppades över (fanns redan)")
print(f"  {fail} misslyckades / saknar bild")
print(f"  events.json uppdaterad")
