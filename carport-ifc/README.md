# Carport Gryningsvägen 14 – IFC-modell

Genererad ur A-01-1-001 (situationsplan, rev A) och A-40-1-100 (carport, rev B).

- `carport_IFC4.ifc` – för Revit (2019+) och ArchiCAD (IFC4). Importera/länka via *Open/Link IFC*.
- `carport_IFC2X3.ifc` – reservfil om äldre programversion eller import krånglar.
- `make_carport_ifc.py` – generatorn (`pip install ifcopenshell`; `python3 make_carport_ifc.py IFC4 ut.ifc`). Alla mått är parametrar i skriptets topp.

Enhet meter. Origo: husfasadens linje, marknivå. Takkant 200 mm från fasaden.

## Innehåll (IFC-klass -> väntat element)
- 4 betongplintar: IfcFooting (Revit: Structural Foundation)
- 4 träpelare 90x90: IfcColumn (pelare)
- 2 bärlinor GL30c 360x90 och 7 bjälkar 220x45 c600: IfcBeam (BEAM / JOIST) (balk)
- Sedumtak: IfcRoof + IfcSlab ROOF med materialskikt (tak)
- Fascia i sågad ek 440 mm, 4 st: IfcWall med snedskuret över-/underkant (vägg)
- Stenkista: IfcSlab BASESLAB (bjälklag/platta)
- Integrerat stuprör: IfcPipeSegment (IFC2x3: IfcFlowSegment)
Varje kategori har typobjekt (IFC4), material och property sets. Inga IfcBuildingElementProxy används.

## Antaganden – verifiera
- **Takdjup 3666 mm** (A-40-1-100) – situationsplanen visar 3222 mm. Ändra `DEPTH` i skriptet.
- Takfall 4° (ritningen anger bara "fall mot stuprör"), lågt mot huset. Höjd 2717 mm vid höga änden.
- Plintmått 250x250x500, stenkista 600x800x600 och sedumtakets skikttjocklekar är antagna.
- Bjälkarna ligger ovanpå bärlinorna (ritningen anger balksko). Dräneringskanal, befintligt hus, ramp och mark är inte modellerade. I ArchiCAD kan IfcFooting och IfcPipeSegment bli Object om IFC-typmappningen i översättaren inte ändras (Footing -> Column/Slab).
