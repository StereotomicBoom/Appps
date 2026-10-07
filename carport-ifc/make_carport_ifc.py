"""Genererar IFC-modell av carporten på Gryningsvägen 14 (Andreas 12) ur ritningarna
A-01-1-001 (situationsplan, rev A) och A-40-1-100 (carport, rev B).

Användning: python3 make_carport_ifc.py [IFC4|IFC2X3] [utfil.ifc]
Enhet i modellen: meter. Origo: husfasadens linje (x=0), marknivå (z=0), y=0 = carportens södra/nedre kant i plan.
"""
import math, sys
import numpy as np
import ifcopenshell, ifcopenshell.api, ifcopenshell.util.placement

SCHEMA = sys.argv[1] if len(sys.argv) > 1 else "IFC4"
OUT = sys.argv[2] if len(sys.argv) > 2 else f"carport_{SCHEMA}.ifc"
IFC4 = SCHEMA == "IFC4"

# ---------------- mått (mm -> m) ----------------
mm = 0.001
X0 = 200 * mm            # avstånd husfasad -> takkant (A-01-1-001)
L = 4898 * mm            # taklängd
DEPTH = 3666 * mm        # takbredd (A-40-1-100). Situationsplanen visar 3222 mm -> ändra här vid behov
POST_CX = 2779 * mm      # c/c pelare i längdled
POST_CY = 3334 * mm      # c/c pelare i djupled
POST_X1 = 389 * mm       # första pelaren från takets vänstra kant
POST = 90 * mm           # pelare 90x90
BEAM_W, BEAM_H = 90 * mm, 360 * mm   # bärlina GL30c 360x90
JOIST_W, JOIST_H, JOIST_S = 45 * mm, 220 * mm, 600 * mm
FASCIA_H, FASCIA_T = 440 * mm, 25 * mm
H_TOP = 2717 * mm        # höjd mark -> överkant fascia vid höga änden
ANG = math.radians(4.0)  # takfall (antaget, ritningen anger endast "fall mot stuprör")
C, S = math.cos(ANG), math.sin(ANG)
ZB_HI = H_TOP - FASCIA_H                 # underkant bjälklag vid x=L
def zb(x): return ZB_HI - (L - x) * math.tan(ANG)   # underkant bjälklag (x lokalt från takets vänsterkant)

f = ifcopenshell.api.run("project.create_file", version=SCHEMA)
run = lambda _api, **kw: ifcopenshell.api.run(_api, f, **kw)
if not IFC4:  # IFC2x3 kräver OwnerHistory
    import ifcopenshell.api.owner.settings as _os
    _p = run("owner.add_person", identification="gl", family_name="Lundström", given_name="Gustav")
    _o = run("owner.add_organisation", identification="stroo", name="Ströö arkitektbyrå ab")
    _u = run("owner.add_person_and_organisation", person=_p, organisation=_o)
    _a = run("owner.add_application")
    _os.get_user = lambda file: _u
    _os.get_application = lambda file: _a
project = run("root.create_entity", ifc_class="IfcProject", name="Carport Gryningsvägen 14")
run("unit.assign_unit", length={"is_metric": True, "raw": "METERS"}, area={"is_metric": True, "raw": "METERS"}, volume={"is_metric": True, "raw": "METERS"})
ctx = run("context.add_context", context_type="Model")
body = run("context.add_context", context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)

site = run("root.create_entity", ifc_class="IfcSite", name="Andreas 12")
site.RefLatitude = None
bld = run("root.create_entity", ifc_class="IfcBuilding", name="Fristående carport")
sto = run("root.create_entity", ifc_class="IfcBuildingStorey", name="Marknivå")
sto.Elevation = 0.0
run("aggregate.assign_object", products=[site], relating_object=project)
run("aggregate.assign_object", products=[bld], relating_object=site)
run("aggregate.assign_object", products=[sto], relating_object=bld)
try:
    site.SiteAddress = f.create_entity("IfcPostalAddress", AddressLines=["Gryningsvägen 14"],
                                       PostalCode="163 51", Town="Spånga", Country="SE")
except Exception: pass

# ---------------- hjälpare ----------------
def mat4(origin, xdir, zdir):
    z = np.array(zdir, float); z /= np.linalg.norm(z)
    x = np.array(xdir, float); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m

STYLES = {}
def style(name, rgb, transp=0.0):
    if name not in STYLES:
        s = run("style.add_style", name=name)
        run("style.add_surface_style", style=s, ifc_class="IfcSurfaceStyleShading",
            attributes={"SurfaceColour": {"Name": name, "Red": rgb[0], "Green": rgb[1], "Blue": rgb[2]}, **({"Transparency": transp} if IFC4 else {})})
        STYLES[name] = s
    return STYLES[name]

MATS = {}
def material(name, category=None):
    if name not in MATS:
        MATS[name] = run("material.add_material", name=name, category=category)
    return MATS[name]

def place(el, m, container=None):
    run("geometry.edit_object_placement", product=el, matrix=m, is_si=True)
    run("spatial.assign_container", products=[el], relating_structure=container or sto)

def extrude(el, profile, depth, st=None, dir_z=(0, 0, 1)):
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=profile,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0., 0., 0.))),
                            ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=dir_z), Depth=depth)
    rep = f.create_entity("IfcShapeRepresentation", ContextOfItems=body, RepresentationIdentifier="Body",
                          RepresentationType="SweptSolid", Items=[solid])
    run("geometry.assign_representation", product=el, representation=rep)
    if st: run("style.assign_representation_styles", shape_representation=rep, styles=[st])
    return solid

def rect(w, h, off=None):
    pos = f.create_entity("IfcAxis2Placement2D", Location=f.create_entity("IfcCartesianPoint", Coordinates=tuple(off or (0., 0.))))
    return f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=w, YDim=h, Position=pos)

def poly(pts):
    ps = [f.create_entity("IfcCartesianPoint", Coordinates=tuple(float(c) for c in p)) for p in pts]
    ps.append(ps[0])
    return f.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA",
                           OuterCurve=f.create_entity("IfcPolyline", Points=ps))

def element(cls, name, ptype=None, mat=None, tag=None):
    kw = {"ifc_class": cls, "name": name}
    if ptype and IFC4: kw["predefined_type"] = ptype
    el = run("root.create_entity", **kw)
    if mat: run("material.assign_material", products=[el], material=material(mat))
    if tag: add_pset(el, tag)
    return el

def add_pset(el, props):
    ps = run("pset.add_pset", product=el, name="Stroo_Carport")
    run("pset.edit_pset", pset=ps, properties=props)

TIMBER = style("Trä", (0.82, 0.68, 0.46))
GL = style("Limträ", (0.76, 0.60, 0.38))
OAK = style("Ek, oljad", (0.55, 0.40, 0.24))
CONC = style("Betong", (0.65, 0.65, 0.65))
SEDUM = style("Sedumtak", (0.38, 0.55, 0.28))
GRAV = style("Makadam", (0.55, 0.53, 0.50))
ZINC = style("Plåt", (0.55, 0.58, 0.60))

# ---------------- pelare, plintar ----------------
posts_xy = [(X0 + POST_X1, (DEPTH - POST_CY) / 2), (X0 + POST_X1, (DEPTH + POST_CY) / 2),
            (X0 + POST_X1 + POST_CX, (DEPTH - POST_CY) / 2), (X0 + POST_X1 + POST_CX, (DEPTH + POST_CY) / 2)]
beam_top = lambda x: zb(x - X0 - BEAM_W / 2)
for i, (px, py) in enumerate(posts_xy, 1):
    ft = element("IfcFooting", f"Betongplint {i}", "PAD_FOOTING", "Betong", {"Typ": "Ledbruket Betongplint KP 500 eller likvärdigt (mått antagna)", "Stolpsko": "Justerbar, isolerad"})
    extrude(ft, rect(0.25, 0.25), 0.5, CONC)
    place(ft, mat4((px, py, -0.5), (1, 0, 0), (0, 0, 1)))
    h = beam_top(px) - BEAM_H
    col = element("IfcColumn", f"Träpelare 90x90 {i}", "COLUMN", "Trä, 90x90", {"Dimension": "90x90 mm"})
    extrude(col, rect(POST, POST), h, TIMBER)
    place(col, mat4((px, py, 0.0), (1, 0, 0), (0, 0, 1)))

# ---------------- bärlinor ----------------
for i, px in enumerate([posts_xy[0][0], posts_xy[2][0]], 1):
    bm = element("IfcBeam", f"Bärlina GL30c 360x90 {i}", "BEAM", "Limträ GL30c", {"Dimension": "360x90 mm", "Hållfasthetsklass": "GL30c"})
    extrude(bm, rect(BEAM_W, BEAM_H), DEPTH, GL)
    # lokal z = +y (längd), lokal x = +x (bredd), lokal y = z × x = +z (höjd)
    place(bm, mat4((px, 0.0, beam_top(px) - BEAM_H / 2), (1, 0, 0), (0, 1, 0)))
    # lokal y = z × x = -z: profilen är symmetrisk så geometrin blir korrekt

# ---------------- bjälklag ----------------
n = int((DEPTH - JOIST_W) // JOIST_S) + 1
for k in range(n):
    y = JOIST_W / 2 + k * JOIST_S
    j = element("IfcMember", f"Bjälke 220x45 c600 #{k+1}", "MEMBER", "Konstruktionsvirke C30", {"Dimension": "220x45 mm", "Hållfasthetsklass": "C30", "Centrumavstånd": "600 mm"})
    extrude(j, rect(JOIST_W, JOIST_H), L / C, TIMBER)
    zc = zb(0) + (JOIST_H / 2) / C
    place(j, mat4((X0, y, zc), (0, 1, 0), (C, 0, S)))

# ---------------- tak (sedum) ----------------
roof = element("IfcRoof", "Sedumtak", "FLAT_ROOF" if IFC4 else None)
if not IFC4: roof.ShapeType = "FLAT_ROOF"
slab_t = FASCIA_H * C - JOIST_H
slab = element("IfcSlab", "Sedumtak, uppbyggnad", "ROOF", None, {"Utförande": "Sedumtak 4,5x3,25 m enl. leverantörens anvisning", "Fall": "ca 4° (antaget) mot stuprör", "Bjälklag": "fäst mot bärlina med balksko"})
ls = run("material.add_material_set", name="Sedumtak", set_type="IfcMaterialLayerSet")
for nm, t in (("Råspont/underlagsskiva", 0.020), ("Tätskikt och dränerande skikt", 0.040), ("Växtsubstrat med sedum", slab_t - 0.060)):
    lay = run("material.add_layer", layer_set=ls, material=material(nm))
    run("material.edit_layer", layer=lay, attributes={"LayerThickness": t})
run("material.assign_material", products=[slab], type="IfcMaterialLayerSetUsage", material=ls)
extrude(slab, rect(L / C, DEPTH, (L / C / 2, DEPTH / 2)), slab_t, SEDUM)
# lokal x längs fallet, lokal z = normal uppåt
place(slab, mat4((X0, 0.0, zb(0) + JOIST_H / C), (C, 0, S), (-S, 0, C)))
run("aggregate.assign_object", products=[slab], relating_object=roof)
run("spatial.assign_container", products=[roof], relating_structure=sto)

# ---------------- fascia / beklädnad, sågad ek ----------------
def cladding(name):
    return element("IfcCovering", name, "CLADDING", "Sågad ek, oljad", {"Beklädnad": "Sågad ek. Oljas in.", "Höjd": "440 mm"})

dz = zb(L) - zb(0)
for nm, y0 in (("Fascia söder", FASCIA_T), ("Fascia norr", DEPTH)):
    cov = cladding(nm)
    extrude(cov, poly([(0, 0), (L, dz), (L, dz + FASCIA_H), (0, FASCIA_H)]), FASCIA_T, OAK)
    place(cov, mat4((X0, y0, zb(0)), (1, 0, 0), (0, -1, 0)))   # lokal y = uppåt, extrusion mot -y
for nm, x0 in (("Fascia vänster gavel", X0), ("Fascia höger gavel", X0 + L - FASCIA_T)):
    cov = cladding(nm)
    extrude(cov, rect(FASCIA_T, DEPTH, (FASCIA_T / 2, DEPTH / 2)), FASCIA_H, OAK)
    place(cov, mat4((x0, 0.0, zb(x0 - X0 + FASCIA_T / 2)), (1, 0, 0), (0, 0, 1)))

# ---------------- integrerat stuprör (bakom pelare nära stenkistan) ----------------
pipe_cls = "IfcPipeSegment" if IFC4 else "IfcFlowSegment"
pipe = element(pipe_cls, "Integrerat stuprör", "RIGIDSEGMENT" if IFC4 else None, "Plåt", {"Placering": "Dolt bakom pelare (sett från vägen), dränering mot stenkista"})
extrude(pipe, f.create_entity("IfcCircleProfileDef", ProfileType="AREA", Radius=0.03, Position=f.create_entity("IfcAxis2Placement2D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0., 0.)))), zb(POST_X1 - POST / 2 - 0.06), ZINC)
place(pipe, mat4((posts_xy[0][0] - POST / 2 - 0.03, posts_xy[0][1], 0.0), (1, 0, 0), (0, 0, 1)))

# ---------------- stenkista (mått delvis antagna) ----------------
sk = element("IfcBuildingElementProxy", "Stenkista", None, "Makadam", {"Bredd": "600 mm (A-40-1-100)", "Längd/djup": "antagna 800 x 600 mm - verifiera"})
extrude(sk, rect(0.6, 0.8, (0.3, 0.4)), 0.6, GRAV)
place(sk, mat4((0.0, -0.8, -0.6), (1, 0, 0), (0, 0, 1)))

# ---------------- projektinfo ----------------
add_pset(project, {"Fastighet": "Andreas 12", "Adress": "Gryningsvägen 14, 163 51 Spånga", "Ritningar": "A-01-1-001 rev A, A-40-1-100 rev B",
                   "Arkitekt": "Ströö arkitektbyrå ab", "Takdjup": "3666 mm enl. A-40-1-100 (A-01-1-001 visar 3222 mm)"})
f.write(OUT)
print("skrev", OUT)
