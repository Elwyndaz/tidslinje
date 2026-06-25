# To-do

## Setup
- [x] Projektfiler skapade (ersätter `npm create vite@latest`)
- [x] Tailwind CSS konfigurerat (tailwind.config.js + postcss.config.js + index.css)
- [x] Mappstruktur skapad (`components/`, `data/`)
- [x] `src/data/events.json` skapad med alla 49 händelser
- [x] GitHub Pages konfigurerat i `vite.config.js` — **OBS: byt `base` till ditt repo-namn**

## Komponenter
- [x] `Timeline.jsx` — hämtar JSON, sorterar händelser, renderar listan
- [x] `EventCard.jsx` — tre storlekar, ikonindikationer, thumbnail-stöd
- [x] `Modal.jsx` — lång text, länkikoner, stor bild högst upp, stängs med klick utanför / Escape
- [x] `EpochGroup.jsx` — grupperar kort per epok, alternerande layout

## Design
- [x] Tailwind-tema med `#8B0000` som accentfärg
- [x] Vertikal tidslinje-linje
- [x] Alternerande vänster/höger på desktop, höger på mobil
- [x] Ikoner för podcast / video / wiki (emoji)

## Epoker
- [x] Tre epoker definierade och namngivna

## Länkar
- [x] Svenska Wikipedia-länkar tillagda (43 av 49 händelser)
- [x] LO Play-videor tillagda (Sundsvallsstrejken, Amalthea, Ådalen, Saltsjöbaden)
- [x] Podcast "Vi bygger landet" (LO) tillagd för 7 händelser
- [ ] **Granska alla 54 länkar — identifiera döda och ersätt med fungerande alternativ**
- [ ] **Hitta fler podcasts** — t.ex. Historiepodden om Seskaröupproret, och andra relevanta avsnitt

## Bilder
- [x] `EventCard.jsx` visar 64×64px thumbnail (höger om titel, large/medium)
- [x] `Modal.jsx` visar stor bild (208px hög, full bredd) högst upp
- [x] `imgSrc()` hanterar Vite base-URL korrekt för GitHub Pages
- [x] Nedladdningsskript skapat: `scripts/download-images.py`
- [ ] **Kör `python scripts/download-images.py` lokalt** för att hämta bilder från Wikipedia/Commons
  - Kräver: `pip install Pillow requests`
  - Sparar WebP-filer i `public/images/` och uppdaterar events.json automatiskt
- [ ] Granska nedladdade bilder och ersätt felaktiga manuellt
- [ ] Lägg till `image`-fält manuellt för händelser skriptet inte hittar bild till

## Senare
- [ ] Filtrering Sverige / världen
- [ ] Sökfunktion
- [ ] Fler händelser läggs till i JSON
- [ ] SVG-ikoner (ersätt emoji om det behövs)

## Gjort ✅
- Projektstruktur, alla 14 filer skapade
- 49 händelser inlagda i events.json, fördelade på tre epoker
- Wikipedia-länkar, LO Play-videor och podcastavsnitt tillagda
- Bildstöd implementerat i EventCard och Modal
- Nedladdningsskript för bilder klart
