// Konfiguration – justera här om en tjänst byter adress eller lagernamn.
window.SV = window.SV || {};
SV.config = {
  // SGU:s öppna geodatatjänster (jordarter). Lagernamnet upptäcks automatiskt via GetCapabilities,
  // men kan sättas manuellt i appens "Avancerat"-ruta eller här.
  sguJordOws: 'https://maps3.sgu.se/geoserver/jord/ows',
  sguJordLayer: '',           // t.ex. 'jord:SE.GOV.SGU.JORD.GRUNDLAGER.25K' om automatiken missar
  // Naturvårdsverkets Nationella marktäckedata (NMD) – visas bara som kontrollager.
  nmdOws: 'https://geodata.naturvardsverket.se/geoserver/ows',
  nmdLayer: '',
  // Satellitbilder för optisk bedömning av skogstyp (Esri World Imagery, fri visning).
  imageryUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  maxRegionKm: 12,            // största tillåtna sida på analysområdet
  maxTiles: 140,              // tak för antal satellitrutor som hämtas
  // Trösklar för färgbaserad skogstypsgissning (V = ljushet 0–1).
  vision: { granMaxV: 0.30, tallMaxV: 0.42, lovMinHue: 80, openMinV: 0.60 }
};
