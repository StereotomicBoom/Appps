// Poängsättning: kombinerar jordart och skogstyp mot artens preferenser.
(function (root) {
  const SV = root.SV = root.SV || {};

  // shares: {gran,tall,lov,oppen,vatten,annat} (andelar 0–1). override: null|'gran'|'tall'|'lov'|'bland'
  SV.skogPoang = function (species, shares, override) {
    let mix;
    if (override && override !== 'auto') {
      mix = override === 'bland' ? { gran: .34, tall: .33, lov: .33 }
        : { gran: 0, tall: 0, lov: 0, [override]: 1 };
      return { poang: Object.entries(mix).reduce((a, [k, w]) => a + w * species.skog[k], 0), skogAndel: 1, mix };
    }
    const tree = shares.gran + shares.tall + shares.lov;
    if (tree <= 0) return { poang: 0, skogAndel: 0, mix: { gran: 0, tall: 0, lov: 0 } };
    mix = { gran: shares.gran / tree, tall: shares.tall / tree, lov: shares.lov / tree };
    const pref = mix.gran * species.skog.gran + mix.tall * species.skog.tall + mix.lov * species.skog.lov;
    return { poang: pref * Math.min(1, tree / 0.5), skogAndel: tree, mix }; // kräver ~50 % träd för full poäng
  };

  SV.cellPoang = function (species, jordKlass, shares, override) {
    const jord = jordKlass === 'okand' ? 0.5 : (species.jord[jordKlass] ?? 0.5);
    const sk = SV.skogPoang(species, shares, override);
    return { jord, skog: sk.poang, skogAndel: sk.skogAndel, mix: sk.mix, total: Math.sqrt(jord * sk.poang) };
  };

  SV.betyg = function (p) {
    return p >= 0.7 ? 'Mycket god' : p >= 0.5 ? 'God' : p >= 0.3 ? 'Måttlig' : 'Låg';
  };
  SV.betygFarg = function (p) {
    return p >= 0.7 ? '#1a7f37' : p >= 0.5 ? '#7cb518' : p >= 0.3 ? '#f2b705' : null;
  };
  SV.iSasong = (species, date) => species.manader.includes((date || new Date()).getMonth() + 1);

  if (typeof module !== 'undefined') module.exports = SV;
})(typeof window !== 'undefined' ? window : globalThis);
