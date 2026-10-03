// Jordartsdata från SGU (WFS) och punkt-i-polygon-uppslag.
(function (root) {
  const SV = root.SV = root.SV || {};

  // Översätt SGU:s jordartsbeskrivning (fritext) till vår förenklade klass.
  // Matchar på nyckelord i alla textfält, så att det fungerar oavsett fältnamn.
  const RULES = [
    [/vatten|sjö|hav\b/, 'vatten'],
    [/torv|mosse|myr|gyttja/, 'torv'],
    [/berg|tunt.*jordt|osammanh/, 'berg'],
    [/lera|ler\b/, 'lera'],
    [/silt|mjäla|mo\b|finsediment/, 'silt'],
    [/grus|isälv|rullsten|block/, 'grus'],
    [/sand|svall|vindavl|flygsand|dyn/, 'sand'],
    [/morän|moran|glacial/, 'moran'],
    [/fyllning|artificiell|bebyggd/, 'berg']
  ];
  SV.jordKlass = function (text) {
    const t = String(text || '').toLowerCase();
    // Morän före lera/sand så att "lerig morän"/"sandig morän" blir morän.
    if (/morän|moran/.test(t) && !/torv|vatten/.test(t)) return 'moran';
    for (const [re, k] of RULES) if (re.test(t)) return k;
    return 'okand';
  };
  SV.JORD_NAMN = { moran: 'Morän', sand: 'Sand', grus: 'Grus/isälvssediment', silt: 'Silt/mjäla', lera: 'Lera',
    torv: 'Torv/myr', berg: 'Berg/tunt jordtäcke', vatten: 'Vatten', okand: 'Okänd jordart' };

  function featureText(props) {
    return Object.values(props || {}).filter(v => typeof v === 'string').join(' ');
  }

  function ringContains(ring, x, y) {
    let inside = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  }
  function polyContains(poly, x, y) {
    if (!ringContains(poly[0], x, y)) return false;
    for (let h = 1; h < poly.length; h++) if (ringContains(poly[h], x, y)) return false;
    return true;
  }

  // Förbered features: klass + bbox per polygon för snabb filtrering.
  SV.prepareSoil = function (geojson) {
    const out = [];
    for (const f of (geojson.features || [])) {
      if (!f.geometry) continue;
      const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates]
        : f.geometry.type === 'MultiPolygon' ? f.geometry.coordinates : [];
      const klass = SV.jordKlass(featureText(f.properties));
      for (const p of polys) {
        let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        for (const [x, y] of p[0]) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
        out.push({ klass, poly: p, bbox: [x0, y0, x1, y1], props: f.properties });
      }
    }
    return out;
  };
  SV.soilAt = function (prepared, lon, lat) {
    for (const p of prepared) {
      const b = p.bbox;
      if (lon < b[0] || lon > b[2] || lat < b[1] || lat > b[3]) continue;
      if (polyContains(p.poly, lon, lat)) return p.klass;
    }
    return 'okand';
  };

  // ---- Nätverk (endast webbläsare) ----
  async function getText(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error('HTTP ' + r.status + ' från ' + url.split('?')[0]);
    return r.text();
  }
  // Hitta lagernamn via GetCapabilities om inget är angivet.
  SV.discoverLayer = async function (ows, service, pick) {
    const xml = await getText(ows + '?service=' + service + '&request=GetCapabilities');
    const names = [...xml.matchAll(/<(?:\w+:)?Name>([^<]+)<\/(?:\w+:)?Name>/g)].map(m => m[1]);
    const best = pick(names);
    if (!best) throw new Error('Hittade inget passande lager i ' + ows);
    return best;
  };
  const pickJord = names => {
    const c = names.filter(n => /jord/i.test(n) && !/linje|line|punkt|point|djup|lagerf/i.test(n));
    for (const key of ['25', '50', '100', '250']) { const m = c.find(n => n.includes(key)); if (m) return m; }
    return c[0];
  };
  const pickNmd = names => names.find(n => /nmd/i.test(n) && /mark|klass|basskikt|v1|v2/i.test(n)) || names.find(n => /nmd/i.test(n));
  SV.pickJord = pickJord; SV.pickNmd = pickNmd;

  SV.resolveSoilLayer = async function (cfg) {
    return cfg.sguJordLayer || SV.discoverLayer(cfg.sguJordOws, 'WFS', pickJord);
  };
  SV.fetchSoil = async function (cfg, layer, b) {
    // WFS 1.0.0 → axelordning lon,lat; GeoServer ger GeoJSON i lon/lat.
    const url = cfg.sguJordOws + '?service=WFS&version=1.0.0&request=GetFeature&typeName=' + encodeURIComponent(layer) +
      '&outputFormat=application/json&srsName=EPSG:4326&maxFeatures=30000&bbox=' +
      [b.west, b.south, b.east, b.north].join(',') + ',EPSG:4326';
    const gj = JSON.parse(await getText(url));
    return SV.prepareSoil(gj);
  };

  if (typeof module !== 'undefined') module.exports = SV;
})(typeof window !== 'undefined' ? window : globalThis);
