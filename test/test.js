global.window = global; global.SV = {};
require('../js/species.js'); require('../js/soil.js'); require('../js/vision.js'); require('../js/score.js');
const assert = require('assert');
const S = global.SV;
// jordart
assert.equal(S.jordKlass('Sandig morän'), 'moran');
assert.equal(S.jordKlass('Isälvssediment, sand'), 'grus');
assert.equal(S.jordKlass('Torv'), 'torv');
assert.equal(S.jordKlass('Postglacial lera'), 'lera');
assert.equal(S.jordKlass('Berg i dagen'), 'berg');
assert.equal(S.jordKlass('Svallsand'), 'sand');
// punkt-i-polygon med hål
const gj = { features: [{ properties: { JORDART: 'Morän' }, geometry: { type: 'Polygon', coordinates: [
  [[0,0],[10,0],[10,10],[0,10],[0,0]], [[4,4],[6,4],[6,6],[4,6],[4,4]]] } },
  { properties: { JORDART: 'Torv' }, geometry: { type: 'Polygon', coordinates: [[[4,4],[6,4],[6,6],[4,6],[4,4]]] } }] };
const p = S.prepareSoil(gj);
assert.equal(S.soilAt(p, 1, 1), 'moran'); assert.equal(S.soilAt(p, 5, 5), 'torv'); assert.equal(S.soilAt(p, 20, 1), 'okand');
// pixlar
assert.equal(S.classifyPixel(10, 40, 15), 'gran');
assert.equal(S.classifyPixel(20, 25, 120), 'vatten');
assert.equal(S.classifyPixel(150, 220, 80), 'oppen');
assert.equal(S.classifyPixel(90, 120, 40), 'lov');
// poäng
const kant = S.speciesById('kantarell'), smor = S.speciesById('smorsopp');
const gran = { gran: .8, tall: 0, lov: 0, oppen: .2, vatten: 0, annat: 0 };
const tall = { gran: 0, tall: .8, lov: 0, oppen: .2, vatten: 0, annat: 0 };
assert(S.cellPoang(kant, 'moran', gran).total > S.cellPoang(kant, 'torv', gran).total);
assert(S.cellPoang(smor, 'sand', tall).total > S.cellPoang(smor, 'sand', gran).total);
assert(S.cellPoang(smor, 'sand', { gran:0,tall:0,lov:0,oppen:1,vatten:0,annat:0 }).total === 0);
assert(S.pickJord(['jord:SE.GOV.SGU.JORD.LINJE.25K','jord:SE.GOV.SGU.JORD.YTA.50K','jord:SE.GOV.SGU.JORD.YTA.25K']).endsWith('YTA.25K'));
console.log('OK');
