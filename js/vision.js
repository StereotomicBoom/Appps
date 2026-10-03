// Optisk bedömning: klassar satellitbildens pixlar till gran/tall/löv/öppet/vatten.
// Det är en grov färgbaserad gissning (ljushet + nyans) – inte en riktig trädslagskarta.
(function (root) {
  const SV = root.SV = root.SV || {};
  const DEF = { granMaxV: 0.30, tallMaxV: 0.42, lovMinHue: 80, openMinV: 0.60 };

  SV.classifyPixel = function (r, g, b, t) {
    t = t || DEF;
    const max = Math.max(r, g, b), min = Math.min(r, g, b), v = max / 255, d = max - min;
    const s = max ? d / max : 0;
    if (b >= g * 0.95 && b >= r && v < 0.5) return 'vatten';
    let h = 0;
    if (d) {
      if (max === r) h = ((g - b) / d) % 6; else if (max === g) h = (b - r) / d + 2; else h = (r - g) / d + 4;
      h *= 60; if (h < 0) h += 360;
    }
    if (s < 0.12) return 'annat';                 // vägar, hus, kalt berg
    if (h < 50 || h > 170) return 'oppen';       // åker/hygge/bar mark
    if (v >= t.openMinV) return 'oppen';          // ljusa ängar och fält
    if (v < t.granMaxV) return 'gran';
    if (v < t.tallMaxV) return h >= t.lovMinHue + 15 ? 'lov' : 'tall';
    return h >= t.lovMinHue ? 'lov' : 'tall';
  };

  // pixels: Uint8ClampedArray RGBA. Returnerar andelar.
  SV.classifyPixels = function (data, step, t) {
    const c = { gran: 0, tall: 0, lov: 0, oppen: 0, vatten: 0, annat: 0 };
    let n = 0;
    for (let i = 0; i < data.length; i += 4 * (step || 1)) { c[SV.classifyPixel(data[i], data[i + 1], data[i + 2], t)]++; n++; }
    for (const k in c) c[k] = n ? c[k] / n : 0;
    return c;
  };

  if (typeof module !== 'undefined') module.exports = SV;
})(typeof window !== 'undefined' ? window : globalThis);
