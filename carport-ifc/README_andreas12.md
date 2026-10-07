# Andreas 12 – IFC4-modell (ny)

`andreas12_IFC4.ifc` genereras av `make_andreas12_ifc.py` (`pip install ifcopenshell`). Enhet meter. Origo: husets östfasad, marknivå vid fasaden, y norrut.
Källor: A-01-1-001 (situationsplan), A-40-1-100/101 (carport), A-40-1-102 (entré). A-40-1-103 (renderingar) används inte för geometri; pelarplacering enligt 001 och 101.

## Innehåll
| Del | IFC-klass |
|---|---|
| Mark, plan + ramp (solida block) | IfcSlab BASESLAB |
| Urgröpningar i marken (boolesk differens = Solid Element Operations): 4 plintar med bottenplatta + stenkista | i markens geometri |
| Betongplintar | IfcFooting |
| Pelare 90x90 + beklädnadsplank 22x220 | IfcColumn + IfcWall |
| Bärlinor GL30c 90x360 (längs långsidorna), bjälkar 45x220 s600, distansbitar | IfcBeam, IfcBeam JOIST, IfcMember |
| Undertak (22 panel + 22 bärläkt) | IfcCovering CEILING |
| Sedumtak (21 plywood + 90 sedum) | IfcRoof + IfcSlab ROOF |
| Fasadpanel ek 440 mm, snedskuren | IfcWall |
| Stuprör, stenkista | IfcPipeSegment, IfcSlab |
| Befintligt hus (förenklat), entré: platta, trapplopp, 4 runda pelare, sadeltak 15° | IfcWall, IfcSlab LANDING, IfcStair/IfcStairFlight, IfcColumn, IfcRoof |

## Ritningsvärden och val
- Carport: tak 4898 x 3222; pelare 389 och 389+2779 från takets västra kant, c/c i djupled 2890 (ur 001/101). Fri höjd 2300; överkant fasad ca 2715 över mark.
- 101:s längdsektion visar pelare nära båda ändarna men 001 (nyare, mått angivna) anger 2779 c/c. Jag följde 001.
- Marken stiger 4,5° österut (ramp) från fasaden till tomtgräns; taket följer samma fall.

## Antaganden – verifiera
Plintmått (200x200x500 + platta 400x400x80), stenkista 600x1000x600, takfall = markfall 4,5°, husets höjd 5,0 m och väggtjocklek 0,35 m,
entréplanets överkant +1,80 m (9 steg), tvåkupigt takets tjocklek. Ej modellerat: räcken, husets tak/öppningar, dräneringskanal, trappans sidovägg/dörr, tomtgräns.
