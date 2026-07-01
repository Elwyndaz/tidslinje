# Arbetarrörelsens Tidslinje — Projektspec

## Syfte
Interaktiv tidslinje om arbetarrörelsen. Lärprojekt + faktisk publicering. Begriplighet prioriteras över snabbhet.

## Målgrupp
Fackmedlemmar, kursdeltagare i fackliga kurser, fackligt nyfikna. Kan kontexten — behöver inte grunderna förklarade.

## Tech
- React + Vite
- Tailwind CSS
- GitHub Pages (deploy via gh-pages)
- Data: `src/data/events.json` (redigeras manuellt i texteditor)

## Design
- Logotyp: `src/components/Logo.jsx` (inline SVG, horisontell variant — se `design_handoff_tidslinje_logga`-paketet för primär/mörk/favicon-varianter)
- Accentfärg: dämpad tegelröd `#B0342B` (definierad som `accent` i tailwind.config.js)
- Bakgrund: varm krämvit `#EFEBE4` (`cream`), kort i vitt (`paper`)
- Typografi i loggan: Fraunces (serif, 500) + Archivo (versal grotesk, 800), laddade via Google Fonts i `index.html`
- Vertikal tidslinje
- Desktop: händelser alternerande vänster/höger
- Mobil: alla kort till höger
- Tre kortstorlekar: `large | medium | small` (styrs per händelse i JSON)
- Modal öppnas vid klick på kort
- Ikonindikationer på korten: 🎙️ podcast · 🎬 video · wiki (egen SVG, `src/components/icons.jsx`)

## Språk
Svenska. Inga hårdkodade strängar i koden — öppet för flerspråk senare.

## Funktioner

### Byggs nu ✅
- Vertikal tidslinje med klickbara kort
- Tre kortstorlekar
- Modal med lång beskrivning + klickbara länkikoner
- Ikonindikationer på kort
- Epoker definierade och namngivna

### Byggs senare
- Filtrering Sverige / världen (`country`-fält finns i JSON)
- Sökning (`tags`-fält finns i JSON)
- Fler händelser löpande

### Troligen aldrig
- Persons-sida (`persons`-fält finns i JSON men byggs ej ut nu)

---

## Epoker

| Slug | Titel | År |
|------|-------|----|
| `informera-och-agitera` | Informera och agitera | 1846–1931 |
| `folkhemmet-och-valfardsstaten` | Folkhemmet och välfärdsstaten | 1932–1983 |
| `forvaltande` | Förvaltande | 1985–2026 |

---

## JSON-schema

Datafil: `src/data/events.json`

```json
{
  "id": "1898-lo",
  "year": 1898,
  "title": "LO bildas",
  "epoch": "informera-och-agitera",
  "country": "sverige",
  "size": "large",
  "short": "Kort beskrivning — visas på kortet",
  "long": "Lång text — visas i modalen",
  "tags": ["organisation", "bildande"],
  "persons": [],
  "links": [
    { "type": "podcast", "url": "https://..." },
    { "type": "video", "url": "https://..." },
    { "type": "wiki", "url": "https://..." }
  ]
}
```

**Bildregel:** Börjar `image` med `http` → extern URL. Annars → `public/images/{image}`.
(image-fältet är valfritt — utelämnas om ingen bild finns)

**Fältguide:**
| Fält | Värden |
|------|--------|
| `size` | `large` · `medium` · `small` |
| `country` | `sverige` · `världen` |
| `links[].type` | `podcast` · `video` · `wiki` |
| `epoch` | se tabellen ovan |

---

## Beslut
- Epoker namnges och definieras i `Timeline.jsx` i konstanten `EPOCHS`.
- `persons`-fält finns i JSON men ingen persons-sida byggs nu.
- Inga UI-bibliotek utöver Tailwind.
- GitHub Pages som hosting — `base` i `vite.config.js` måste matcha repo-namnet.
