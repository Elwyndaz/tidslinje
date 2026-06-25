# To-do

## Setup
- [x] Projektfiler skapade (ersätter `npm create vite@latest`)
- [x] Tailwind CSS konfigurerat (tailwind.config.js + postcss.config.js + index.css)
- [x] Mappstruktur skapad (`components/`, `data/`)
- [x] `src/data/events.json` skapad med alla 49 händelser
- [x] GitHub Pages konfigurerat i `vite.config.js` — **OBS: byt `base` till ditt repo-namn**

## Komponenter
- [x] `Timeline.jsx` — hämtar JSON, sorterar händelser, renderar listan
- [x] `EventCard.jsx` — tre storlekar, ikonindikationer för länktyper
- [x] `Modal.jsx` — lång text, länkikoner, stängs med klick utanför / Escape
- [x] `EpochGroup.jsx` — grupperar kort per epok, alternerande layout

## Design
- [x] Tailwind-tema med `#8B0000` som accentfärg (`accent` i tailwind.config.js)
- [x] Vertikal tidslinje-linje
- [x] Alternerande vänster/höger på desktop, höger på mobil
- [x] Ikoner för podcast / video / wiki (emoji — kan bytas till SVG senare)

## Epoker
- [x] Tre epoker definierade och namngivna (se project.md)

## Senare
- [ ] Filtrering Sverige / världen
- [ ] Sökfunktion
- [ ] Fler händelser läggs till i JSON
- [ ] SVG-ikoner (ersätt emoji om det behövs)
- [ ] `assets/`-mapp + bilder till händelserna

## Gjort ✅
- Projektstruktur, alla 14 filer skapade i en omgång (session 2)
- 49 händelser inlagda i events.json, fördelade på tre epoker
