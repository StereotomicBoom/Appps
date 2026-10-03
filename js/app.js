(function () {
  const SV = window.SV, cfg = SV.config, $ = id => document.getElementById(id);
  const MANAD = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec'];

  // ---------- Karta ----------
  const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' });
  const sat = L.tileLayer(cfg.imageryUrl, { maxZoom: 19, attribution: 'Satellit © Esri' });
  const map = L.map('map', { layers: [osm] }).setView([62.5, 15.5], 5);
  const layersCtl = L.control.layers({ 'Karta': osm, 'Satellit': sat }, {}, { collapsed: false }).addTo(map);
  const result = L.layerGroup().addTo(map);
  layersCtl.addOverlay(result, 'Svampprognos');

  async function addWms(label, ows, layerName, picker) {
    try {
      const name = layerName || await SV.discoverLayer(ows, 'WMS', picker);
      layersCtl.addOverlay(L.tileLayer.wms(ows, { layers: name, format: 'image/png', transparent: true, opacity: .7,
        attribution: label }), label);
    } catch (e) { console.warn(label + ' kunde inte läggas till:', e.message); }
  }
  addWms('SGU jordarter', cfg.sguJordOws, cfg.sguJordLayer, SV.pickJord);
  addWms('NMD marktäckedata', cfg.nmdOws, cfg.nmdLayer, SV.pickNmd);

  // ---------- UI ----------
  const art = $('art');
  SV.species.forEach(s => art.add(new Option(s.namn, s.id)));
  function visaArt() {
    const s = SV.speciesById(art.value);
    $('artInfo').innerHTML = `<i>${s.latin}</i> · säsong ${MANAD[s.manader[0] - 1]}–${MANAD[s.manader.at(-1) - 1]}` +
      (SV.iSasong(s) ? ' (<b>i säsong nu</b>)' : ' (ej i säsong nu)') +
      `<br>${s.not}<br><a href="${SV.svampguidenUrl(s)}" target="_blank" rel="noopener">Läs mer på Svampguiden</a>`;
  }
  art.onchange = visaArt; visaArt();
  $('grid').oninput = e => $('gridVal').textContent = e.target.value;
  const status = (t, err) => { $('status').textContent = t; $('status').className = err ? 'err' : ''; };

  $('sokKnapp').onclick = $('sok').onkeydown = async function (e) {
    if (e.type === 'keydown' && e.key !== 'Enter') return;
    const q = $('sok').value.trim(); if (!q) return;
    try {
      const r = await (await fetch('https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=se&q=' + encodeURIComponent(q))).json();
      if (!r.length) return status('Hittade ingen plats.', true);
      const b = r[0].boundingbox.map(Number);
      map.fitBounds([[b[0], b[2]], [b[1], b[3]]]); status('');
    } catch (err) { status('Platssökningen misslyckades: ' + err.message, true); }
  };

  // ---------- Web Mercator ----------
  const worldPx = (lat, lon, z) => {
    const n = 256 * 2 ** z, s = Math.sin(lat * Math.PI / 180);
    return [(lon + 180) / 360 * n, (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * n];
  };

  // ---------- Satellitrutor ----------
  function pickZoom(b) {
    for (let z = 17; z >= 10; z--) {
      const [x0, y0] = worldPx(b.north, b.west, z), [x1, y1] = worldPx(b.south, b.east, z);
      const tiles = (Math.floor(x1 / 256) - Math.floor(x0 / 256) + 1) * (Math.floor(y1 / 256) - Math.floor(y0 / 256) + 1);
      if (tiles <= cfg.maxTiles) return z;
    }
    return 10;
  }
  function loadTile(z, x, y) {
    return new Promise(res => {
      const img = new Image(); img.crossOrigin = 'anonymous';
      img.onload = () => {
        const c = document.createElement('canvas'); c.width = c.height = 256;
        const ctx = c.getContext('2d', { willReadFrequently: true }); ctx.drawImage(img, 0, 0);
        try { res({ canvas: c, data: ctx.getImageData(0, 0, 256, 256).data }); } catch (e) { res({ error: 'cors' }); }
      };
      img.onerror = () => res({ error: 'load' });
      img.src = cfg.imageryUrl.replace('{z}', z).replace('{x}', x).replace('{y}', y);
    });
  }
  async function loadTiles(b, z, onProgress) {
    const [x0, y0] = worldPx(b.north, b.west, z), [x1, y1] = worldPx(b.south, b.east, z);
    const jobs = [];
    for (let x = Math.floor(x0 / 256); x <= Math.floor(x1 / 256); x++)
      for (let y = Math.floor(y0 / 256); y <= Math.floor(y1 / 256); y++) jobs.push([x, y]);
    const tiles = new Map(); let done = 0, i = 0, failed = 0;
    await Promise.all(Array.from({ length: 8 }, async () => {
      while (i < jobs.length) {
        const [x, y] = jobs[i++]; const t = await loadTile(z, x, y);
        if (t.error) failed++; else tiles.set(x + '/' + y, t);
        onProgress(++done, jobs.length);
      }
    }));
    return { tiles, failed, total: jobs.length, z };
  }

  // ---------- Analys ----------
  let current = null; // behåller satellitrutor för beskärningsbilder i popup

  $('kor').onclick = async function () {
    const btn = $('kor'); btn.disabled = true; result.clearLayers(); $('legend').hidden = true;
    try { await analyse(); } catch (e) { console.error(e); status('Fel: ' + e.message, true); }
    btn.disabled = false;
  };

  async function analyse() {
    const mb = map.getBounds();
    const b = { north: mb.getNorth(), south: mb.getSouth(), east: mb.getEast(), west: mb.getWest() };
    const wKm = map.distance([b.south, b.west], [b.south, b.east]) / 1000, hKm = map.distance([b.south, b.west], [b.north, b.west]) / 1000;
    if (Math.max(wKm, hKm) > cfg.maxRegionKm) return status(`Området är för stort (${Math.round(Math.max(wKm, hKm))} km). Zooma in till max ${cfg.maxRegionKm} km.`, true);
    if (map.getZoom() < 8) return status('Zooma in på ett område först.', true);
    const species = SV.speciesById(art.value), override = $('skog').value, n = +$('grid').value;

    // 1. Jordart
    let soil = null, warn = [];
    status('Hämtar jordartskarta från SGU …');
    try {
      const layer = $('sguLayer').value.trim() || await SV.resolveSoilLayer(cfg);
      soil = await SV.fetchSoil(cfg, layer, b);
      if (!soil.length) warn.push('SGU returnerade inga jordartsytor för området');
    } catch (e) { warn.push('jordartsdata saknas (' + e.message + ')'); }

    // 2. Satellit
    let img = null;
    if (override === 'auto') {
      const z = pickZoom(b);
      img = await loadTiles(b, z, (d, t) => status(`Hämtar satellitbilder ${d}/${t} …`));
      if (img.failed > img.total / 2) { warn.push('satellitbilder kunde inte läsas'); img = null; }
      else if (img.failed) warn.push(img.failed + ' satellitrutor saknas');
    }
    current = img;

    // 3. Rutnät
    status('Beräknar …');
    await new Promise(r => setTimeout(r, 20));
    const nx = wKm >= hKm ? n : Math.max(4, Math.round(n * wKm / hKm));
    const ny = wKm >= hKm ? Math.max(4, Math.round(n * hKm / wKm)) : n;
    const dLon = (b.east - b.west) / nx, dLat = (b.north - b.south) / ny;
    let shown = 0;
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      const west = b.west + i * dLon, east = west + dLon, north = b.north - j * dLat, south = north - dLat;
      const lon = (west + east) / 2, lat = (north + south) / 2;
      const jord = soil ? SV.soilAt(soil, lon, lat) : 'okand';
      const shares = img ? sampleCell(img, north, south, west, east, cfg.vision) : { gran: 0, tall: 0, lov: 0, oppen: 0, vatten: 0, annat: 0 };
      const p = SV.cellPoang(species, jord, shares, override);
      const farg = SV.betygFarg(p.total);
      if (!farg) continue;
      shown++;
      L.rectangle([[south, west], [north, east]], { stroke: false, fillColor: farg, fillOpacity: .55 })
        .on('click', ev => openPopup(ev.latlng, { north, south, west, east, lat, lon }, species, jord, shares, p))
        .addTo(result);
    }
    $('legend').hidden = false;
    status(`${shown} av ${nx * ny} rutor bedöms ge måttlig eller bättre förekomst av ${species.namn.toLowerCase()}.` +
      (warn.length ? ' Obs: ' + warn.join('; ') + '.' : '') + ' Klicka på en ruta för detaljer.', warn.length > 0);
    if (!SV.iSasong(species)) status($('status').textContent + ' (Arten är inte i säsong just nu.)', warn.length > 0);
  }

  function sampleCell(img, north, south, west, east, t) {
    const [x0, y0] = worldPx(north, west, img.z), [x1, y1] = worldPx(south, east, img.z);
    const step = Math.max(1, Math.floor(Math.sqrt(((x1 - x0) * (y1 - y0)) / 300)));
    const c = { gran: 0, tall: 0, lov: 0, oppen: 0, vatten: 0, annat: 0 }; let cnt = 0;
    for (let y = Math.floor(y0); y < y1; y += step) for (let x = Math.floor(x0); x < x1; x += step) {
      const tile = img.tiles.get(Math.floor(x / 256) + '/' + Math.floor(y / 256)); if (!tile) continue;
      const o = ((y & 255) * 256 + (x & 255)) * 4, d = tile.data;
      c[SV.classifyPixel(d[o], d[o + 1], d[o + 2], t)]++; cnt++;
    }
    for (const k in c) c[k] = cnt ? c[k] / cnt : 0;
    return c;
  }

  function cropCanvas(img, cell) {
    const pad = 1; // en cellbredd runt om
    const dLat = cell.north - cell.south, dLon = cell.east - cell.west;
    const [x0, y0] = worldPx(cell.north + dLat * pad, cell.west - dLon * pad, img.z);
    const [x1, y1] = worldPx(cell.south - dLat * pad, cell.east + dLon * pad, img.z);
    const w = x1 - x0, h = y1 - y0, c = document.createElement('canvas');
    c.width = 240; c.height = Math.round(240 * h / w);
    const ctx = c.getContext('2d'), k = c.width / w;
    for (let tx = Math.floor(x0 / 256); tx <= Math.floor(x1 / 256); tx++)
      for (let ty = Math.floor(y0 / 256); ty <= Math.floor(y1 / 256); ty++) {
        const t = img.tiles.get(tx + '/' + ty); if (t) ctx.drawImage(t.canvas, (tx * 256 - x0) * k, (ty * 256 - y0) * k, 256 * k, 256 * k);
      }
    // markera själva rutan
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
    const [cx0, cy0] = worldPx(cell.north, cell.west, img.z), [cx1, cy1] = worldPx(cell.south, cell.east, img.z);
    ctx.strokeRect((cx0 - x0) * k, (cy0 - y0) * k, (cx1 - cx0) * k, (cy1 - cy0) * k);
    return c;
  }

  const pct = v => Math.round(v * 100) + ' %';
  function openPopup(latlng, cell, species, jord, shares, p) {
    const el = document.createElement('div'); el.className = 'pop';
    const gm = `https://www.google.com/maps/@${cell.lat.toFixed(6)},${cell.lon.toFixed(6)},250m/data=!3m1!1e3`;
    el.innerHTML = `<b>${SV.betyg(p.total)} chans – ${species.namn}</b>
      <table>
        <tr><td>Jordart</td><td>${SV.JORD_NAMN[jord]} (passar ${pct(p.jord)})</td></tr>
        <tr><td>Skogstyp</td><td>${current ? `gran ${pct(shares.gran)}, tall ${pct(shares.tall)}, löv ${pct(shares.lov)}, öppet ${pct(shares.oppen)}` : 'manuellt vald'} (passar ${pct(p.skog)})</td></tr>
      </table>`;
    if (current) { el.appendChild(cropCanvas(current, cell)); }
    el.insertAdjacentHTML('beforeend', `<a href="${gm}" target="_blank" rel="noopener">Google Maps satellit</a>
      <a href="https://www.google.com/maps?q=&layer=c&cbll=${cell.lat},${cell.lon}" target="_blank" rel="noopener">Street View</a>
      <a href="${SV.svampguidenUrl(species)}" target="_blank" rel="noopener">Svampguiden</a>
      <br><small>Kontrollera skogstypen visuellt – färgklassningen är en grov gissning.</small>`);
    L.popup({ minWidth: 250 }).setLatLng(latlng).setContent(el).openOn(map);
  }
})();
