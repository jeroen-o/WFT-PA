# PA-WFT.nl — Wft Permanent Actueel

Statische website + merkbestanden voor Wft Permanent Actueel (een dienst van DFO).

## Publiceren via GitHub Pages
1. Maak een repository en upload de inhoud van deze map (niet de map zelf) naar de root.
2. Settings → Pages → Source: `main` branch, map `/ (root)`.
3. `CNAME` bevat al `pa-wft.nl`. Zet bij je domeinregistrar:
   - A-records voor `pa-wft.nl`: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
   - CNAME `www` → `<gebruikersnaam>.github.io`
4. Vink daarna "Enforce HTTPS" aan.

## Structuur
```
index.html                  homepage met modules en pakket-check
toets.html                  PA-toets: 7 vragen per module uit 100, certificaat om naar jezelf te mailen
module-<id>.html            per module: wat komt aan bod, actueel, bronnen
vragen.html, over.html, privacy.html, 404.html
sitemap.xml, robots.txt
assets/css/style.css        stijlen (lettertype Archivo lokaal in assets/fonts, OFL-licentie)
assets/css/toets.css        stijlen van de toets
assets/js/modules.js        de 9 modules met datum "bijgewerkt"
assets/js/vragen.js         vragenbank (eerste antwoord is steeds het juiste)
assets/js/main.js           modulelijst + pakket-check
assets/js/toets.js          toets en certificaat
assets/logo/                logo's (SVG), merkteken 1024px (PNG), DFO-logo
favicon.ico / .svg / -16 / -32, apple-touch-icon.png, android-chrome-*.png
site.webmanifest, og-image.png (1200×630 deelafbeelding), CNAME
```

Let op: de repository heeft een `.nojekyll`, dus elk bestand in de repository komt online, ook mappen met een `_` ervoor. Zet interne bestanden (zoals het signaleringsoverzicht) niet in deze repository.

## Een module bijwerken
1. Pas de vragen van de module aan in `assets/js/vragen.js`.
2. Zet in `assets/js/modules.js` de datum `bijgewerkt` op vandaag; die verschijnt op de homepage, de toets en het certificaat.
3. Werk zo nodig het blok "Actueel" op `module-<id>.html` bij.

## Logo's
| Bestand | Gebruik |
|---|---|
| pa-wft-logo-horizontal.svg | Primair logo, op wit |
| pa-wft-logo-horizontal-white.svg | Op DFO-blauw of donker |
| pa-wft-logo-horizontal-black.svg | Eén kleur / zwart-wit print |
| pa-wft-logo-stacked(-white).svg | Smalle plekken |
| pa-wft-mark(-white/-black).svg | Alleen het merkteken (ring + PA) |
| pa-wft-favicon.svg | Vierkant app-icoon |

Kleuren: blauw #1462ad · donkerblauw #0b3d73 (segment Basis) · lichtblauw #8db8e3.
Lettertype: Archivo (Google Fonts). De SVG's gebruiken live tekst; laat ze voor drukwerk omzetten naar contouren (Illustrator: Tekst → Contouren maken) zodat ze ook zonder Archivo kloppen.

## Inhoud aanpassen
Moduleteksten staan bovenin `assets/js/main.js` (MODS). De koppeling diploma → module is nu 1-op-1; pas dat daar aan als de regels anders zijn.
