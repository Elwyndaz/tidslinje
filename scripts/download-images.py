"""
Kör från projektets rot:  python scripts/download-images.py

Kräver:  pip install Pillow requests

Hämtar bilder för varje händelse via flera strategier, i tur och ordning:
  1. Manuell Commons-fil (bara för fall där automatiken väljer fel bild)
  2. sv.wikipedia pageimages-API — Wikipedias egen "huvudbild" för artikeln
  3. sv.wikipedia — alla bilder som faktiskt förekommer i artikeln (prop=images),
     i den ordning de nämns, med ikoner/loggor/kartor/små bilder bortfiltrerade
  4. Samma två steg (2+3) mot en.wikipedia, för händelser med en EN_WIKI-post

Steg 3 är den nya, smartare delen: istället för att bara lita på Wikipedias
auto-vald "sidbild" (som ofta saknas) letar den upp riktiga foton som redan
ligger inbäddade i artikeln — samma sätt som att öppna artikeln och ta första
rimliga bilden, fast automatiskt.

Konverterar till WebP (max 800 px bred) och sparar i public/images/.
Uppdaterar src/data/events.json med image-fältet.
"""

import json, requests, os, io, time, sys, urllib.parse
from PIL import Image
from pathlib import Path

# Windows-konsolen är ofta cp1252 och kraschar på ✓/→ annars.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

ROOT       = Path(__file__).parent.parent
EVENTS     = ROOT / "src" / "data" / "events.json"
IMAGES_DIR = ROOT / "public" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ArbetrorrelseTidslinje/1.0 (educational, non-commercial)"}

# Filnamnsmönster som nästan alltid är ikoner/loggor/kartor/vapen — inte foton.
SKIP_PATTERNS = [
    "logo", "icon", "symbol", "flag_of", "ambox", "nuvola", "crystal",
    "disambig", "edit-icon", "padlock", "question_book", "oojs",
    "commons-logo", "wiktionary", "wikisource", "wikidata", "folder",
    "merge-symbol", "portal", "stub", "pd-icon", "cc-by", "gnu-",
    "loudspeaker", "sound-icon", "_map", "map_of", "locator", "wappen",
    "coat_of_arms", "crest", "signature",
]
MIN_WIDTH = 200

# ── Manuella overrides — används bara när automatiken väljer fel bild ─────
# Format: event-id → Commons-filnamn (utan "File:"-prefix).
MANUAL = {}

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

def is_probably_icon(filename):
    lower = filename.lower()
    if lower.endswith(".svg") or lower.endswith(".gif"):
        return True
    return any(p in lower for p in SKIP_PATTERNS)

def api_get(url, params, retries=3):
    """GET med enkel backoff mot 429/5xx — MediaWiki-API:et är flaggigt
    under skurar av förfrågningar, men brukar svara normalt efter en kort paus."""
    wait = 2
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=12)
        except Exception as e:
            print(f"    nätverksfel: {e}")
            return None
        if r.status_code == 200:
            return r
        if r.status_code in (429, 500, 502, 503) and attempt < retries - 1:
            print(f"    HTTP {r.status_code} — väntar {wait}s och försöker igen")
            time.sleep(wait)
            wait *= 2
            continue
        print(f"    HTTP {r.status_code}")
        return None
    return None

def wiki_pageimage(lang, article):
    """Wikipedias egen auto-valda 'sidbild', om den finns."""
    r = api_get(
        f"https://{lang}.wikipedia.org/w/api.php",
        {"action": "query", "titles": article, "redirects": 1,
         "prop": "pageimages", "pithumbsize": 800, "format": "json"},
    )
    if r is None:
        return None
    pages = r.json()["query"]["pages"]
    for page in pages.values():
        if "thumbnail" in page:
            return page["thumbnail"]["source"]
    return None

def wiki_article_images(lang, article, limit=10):
    """Bilder som faktiskt förekommer i artikeln, i nämnd ordning."""
    r = api_get(
        f"https://{lang}.wikipedia.org/w/api.php",
        {"action": "query", "titles": article, "redirects": 1,
         "prop": "images", "imlimit": 50, "format": "json"},
    )
    if r is None:
        return []
    pages = r.json()["query"]["pages"]
    names = []
    for page in pages.values():
        for img in page.get("images", []):
            name = img["title"].split(":", 1)[-1]
            if not is_probably_icon(name):
                names.append(name)
    return names[:limit]

def best_photo_url(filenames):
    """Slår upp riktiga mått/mime för kandidaterna (via Commons imageinfo)
    och returnerar URL:en för första som är ett tillräckligt stort foto."""
    if not filenames:
        return None
    titles = "|".join(f"File:{f}" for f in filenames)
    r = api_get(
        "https://commons.wikimedia.org/w/api.php",
        {"action": "query", "titles": titles,
         "prop": "imageinfo", "iiprop": "url|size|mime", "format": "json"},
    )
    if r is not None:
        pages = r.json()["query"]["pages"]
        by_name = {}
        for page in pages.values():
            info = page.get("imageinfo")
            if info:
                key = page["title"].split(":", 1)[-1].replace(" ", "_")
                by_name[key] = info[0]
        for name in filenames:
            info = by_name.get(name.replace(" ", "_"))
            if not info:
                continue
            if info.get("mime") not in ("image/jpeg", "image/png"):
                continue
            if info.get("width", 0) < MIN_WIDTH:
                continue
            return info["url"]
    return None

def find_image(lang, article):
    """Steg 2+3 för ett givet språk: pageimage, annars bästa artikelbild."""
    url = wiki_pageimage(lang, article)
    if url:
        return url, "pageimages"
    candidates = wiki_article_images(lang, article)
    url = best_photo_url(candidates)
    if url:
        return url, "artikelbild"
    return None, None

def sv_article(wiki_url):
    if "sv.wikipedia.org/wiki/" in wiki_url:
        # Wiki-URL:er i events.json är ofta procentkodade (Ådalen → %C3%85dalen).
        # Måste avkodas innan de skickas som titles= — annars dubbelkodas de.
        return urllib.parse.unquote(wiki_url.split("/wiki/")[-1])
    return None

def save_webp(img_url, out_path, max_w=800):
    try:
        wait = 2
        for attempt in range(3):
            r = requests.get(img_url, headers=HEADERS, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                break
            if r.status_code in (429, 500, 502, 503) and attempt < 2:
                print(f"    HTTP {r.status_code} — väntar {wait}s och försöker igen")
                time.sleep(wait)
                wait *= 2
                continue
            print(f"    HTTP {r.status_code}")
            return False
        ct = r.headers.get("content-type", "")
        if "svg" in ct:
            print("    SVG -> hoppar")
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
        print(f"    OK  {img.width}x{img.height}px  {kb} KB  ->  {out_path.name}")
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
        print(f"{eid}  ->  redan klar")
        skip += 1
        continue

    print(f"\n{eid}")
    img_url = None

    # 1. Manuell Commons-fil
    if eid in MANUAL:
        img_url = commons_url(MANUAL[eid])
        print(f"    MANUAL: {MANUAL[eid]}")

    # 2+3. sv.wikipedia — pageimage, sedan artikelns egna bilder
    if not img_url:
        wiki_url = next(
            (l["url"] for l in ev.get("links", [])
             if l["type"] == "wiki" and "sv.wikipedia.org/wiki/" in l["url"]),
            None,
        )
        if wiki_url:
            article = sv_article(wiki_url)
            url, method = find_image("sv", article)
            if url:
                img_url = url
                print(f"    sv-wiki ({method}): {url[:70]}...")

    # 4. en.wikipedia — samma två steg
    if not img_url and eid in EN_WIKI:
        url, method = find_image("en", EN_WIKI[eid])
        if url:
            img_url = url
            print(f"    en-wiki ({method}): {url[:70]}...")

    if not img_url:
        print("    ingen bild hittad")
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
