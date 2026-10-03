# Svampkartan

Webbapp (svenska, ingen byggprocess) som markerar områden där en vald svamp troligen växer, genom att kombinera
jordart från SGU:s öppna WFS med skogstyp bedömd från satellitbild, mot artdata (Svampguiden m.fl.).

Kör: `python3 -m http.server` i mappen och öppna http://localhost:8000. Test av logiken: `node test/test.js`.

Justera tjänsteadresser/lagernamn i `js/config.js`, artdata i `js/species.js`.
