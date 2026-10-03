# Svampkartan – projektkontext

Svensk webbapp (Leaflet, vanilla JS, ingen build). Kombinerar SGU:s jordartskarta (WFS) med skogstyp från
Esri-satellitbilder och artdata (`js/species.js`) till en prognoskarta för svampförekomst. Logiktest: `node test/test.js`.

## Status
- Skriven i en molnsession utan nätåtkomst: appen är **aldrig körd mot riktiga tjänster**.
- Osäkert/otestat: SGU-lagernamn (autodetekteras i `js/soil.js`), NMD-lagernamn, färgtrösklar i `js/config.js` (`vision`).
- Ikon i `icons/` i samma stil som användarens övriga appar (svart bläck på pergament, kvadratisk).

## Att göra lokalt (Mac)
1. Läs `~/Applications/JobbbAppp.app` (Contents/Info.plist, Contents/MacOS/*, Resources) och räkna ut hur den är byggd.
   Gör Svampkartan till en app av samma slag (justera `install-mac.sh` – nuvarande version är en gissning och otestad).
2. Kör `python3 -m http.server`, öppna appen i en riktig webbläsare och verifiera mot SGU/Esri/Naturvårdsverket:
   rätt lagernamn, att WFS-svar innehåller jordartstext, att satellitrutor går att läsa (CORS), rimliga färgtrösklar.
3. Kör `bash install-mac.sh`, kontrollera att appen startar med dubbelklick och att ikonen syns.
4. Granska artdata i `js/species.js` mot Svampguiden/Artfakta.
