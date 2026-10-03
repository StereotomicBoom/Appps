// Svampdata. Värdena (0–1) är en förenklad sammanställning av allmän svampkunskap
// (bl.a. Svampguiden, Artdatabanken/Artfakta, Svenska Botaniska Föreningen) – inte exakta mätvärden.
// Nycklar för jord: moran, sand, grus, silt, lera, torv, berg, vatten
// Nycklar för skog: gran, tall, lov (björk, bok, ek, hassel m.fl.)
window.SV = window.SV || {};
SV.species = [
  { id: 'karljohan', namn: 'Karl Johan (stensopp)', latin: 'Boletus edulis', manader: [7,8,9,10],
    jord: { moran:.9, sand:.8, grus:.7, silt:.4, lera:.2, torv:.05, berg:.3, vatten:0 },
    skog: { gran:.85, tall:.8, lov:.7 },
    not: 'Mykorrhiza med gran, tall, björk, bok och ek. Trivs i väldränerad, mossig eller lingonrik mark på morän och sand.' },
  { id: 'kantarell', namn: 'Kantarell', latin: 'Cantharellus cibarius', manader: [7,8,9,10],
    jord: { moran:1, sand:.7, grus:.6, silt:.4, lera:.3, torv:.05, berg:.35, vatten:0 },
    skog: { gran:1, tall:.6, lov:.8 },
    not: 'Gran- och blandskog, gärna mossig morän, samt ek-, bok- och björkskog. Fuktig men väldränerad mark.' },
  { id: 'trattkantarell', namn: 'Trattkantarell', latin: 'Craterellus tubaeformis', manader: [8,9,10,11],
    jord: { moran:1, sand:.6, grus:.4, silt:.3, lera:.2, torv:.2, berg:.3, vatten:0 },
    skog: { gran:1, tall:.7, lov:.2 },
    not: 'Mossrik granskog och fuktig barrskog, ofta sent på säsongen.' },
  { id: 'svarttrumpet', namn: 'Svart trumpetsvamp', latin: 'Craterellus cornucopioides', manader: [7,8,9,10],
    jord: { moran:.8, sand:.4, grus:.4, silt:.5, lera:.5, torv:.1, berg:.3, vatten:0 },
    skog: { gran:.2, tall:.05, lov:1 },
    not: 'Lövskog (bok, ek, hassel), helst kalkrik och mullrik mark. Berggrund/kalkhalt påverkar mycket – kontrollera med SGU:s berggrundskarta.' },
  { id: 'smorsopp', namn: 'Smörsopp', latin: 'Suillus luteus', manader: [8,9,10],
    jord: { moran:.7, sand:1, grus:.9, silt:.3, lera:.1, torv:.05, berg:.3, vatten:0 },
    skog: { gran:.15, tall:1, lov:.05 },
    not: 'Tallskog på sandig, torr mark, särskilt yngre tallbestånd.' },
  { id: 'sandsopp', namn: 'Sandsopp', latin: 'Suillus variegatus', manader: [7,8,9,10],
    jord: { moran:.6, sand:1, grus:.9, silt:.2, lera:.1, torv:.1, berg:.3, vatten:0 },
    skog: { gran:.15, tall:1, lov:.05 },
    not: 'Tallskog på sandiga och grusiga marker, ofta ljung- eller lavrik tallhed.' },
  { id: 'taggsvamp', namn: 'Gul taggsvamp', latin: 'Hydnum repandum', manader: [8,9,10,11],
    jord: { moran:.9, sand:.6, grus:.5, silt:.5, lera:.4, torv:.05, berg:.3, vatten:0 },
    skog: { gran:.9, tall:.5, lov:.9 },
    not: 'Både barr- och lövskog, ofta i grupper på mossig mark.' },
  { id: 'strawsopp', namn: 'Strävsopp (björkboletus)', latin: 'Leccinum scabrum', manader: [7,8,9,10],
    jord: { moran:.8, sand:.7, grus:.6, silt:.5, lera:.3, torv:.4, berg:.3, vatten:0 },
    skog: { gran:.1, tall:.3, lov:1 },
    not: 'Bundna till björk – björkskog, björkhagar och skogsbryn, ofta på något fuktigare mark.' }
];
SV.speciesById = id => SV.species.find(s => s.id === id);
SV.svampguidenUrl = s => 'https://www.svampguiden.com/?s=' + encodeURIComponent(s.namn.split(' (')[0]);
