"""IFC4-modell Andreas 12, Gryningsvägen 14: mark, befintlig byggnad (förenklad), entré och fristående carport.
Källor: A-01-1-001 (situationsplan), A-40-1-100/101 (carport), A-40-1-102 (entré). A-40-1-103 (illustrationer) används ej för geometri.
Enhet meter. Origo: husets östfasad (x=0), marknivå vid fasaden (z=0), y=0 = carportens södra takkant (y norrut).
Användning: python3 make_andreas12_ifc.py [utfil.ifc]
"""
import math, sys
import numpy as np
import ifcopenshell, ifcopenshell.api

OUT = sys.argv[1] if len(sys.argv) > 1 else "andreas12_IFC4.ifc"

# ---------------- mått (m) ----------------
X0, L, W = 0.200, 4.898, 3.222            # takkant från fasad, taklängd, takbredd (A-01-1-001)
POST_X = (0.389, 0.389 + 2.779)           # pelare från takets vänstra kant
BEAM_Y = 0.166                            # bärlinans mittlinje från takkant (21 panel + 100 distans + 45)
BEAM_W, BEAM_H = 0.090, 0.360             # bärlina GL30c 90x360
POST_CORE, PLANK_T, PLANK_W = 0.090, 0.022, 0.220
JOIST_W, JOIST_H, JOIST_S = 0.045, 0.220, 0.600
CLEAR = 2.300                             # fri höjd mark -> undersida undertak (A-40-1-101)
SOFFIT_T, DECK_T, SEDUM_T = 0.044, 0.021, 0.090
FASCIA_T, FASCIA_H = 0.021, 0.440
TH = math.radians(4.5)                    # markens/takets fall (uppmätt ur A-40-1-101, ca 4-5 grader)
T, C, S = math.tan(TH), math.cos(TH), math.sin(TH)
BOUNDARY_X = X0 + L + 0.815               # tomtgräns i öster
gz = lambda x: x * T                      # marknivå i rampen (x>0)
sz = lambda x: gz(x) + CLEAR              # undersida undertak
NRM = (-S, 0.0, C)

f = ifcopenshell.api.run("project.create_file", version="IFC4")
run = lambda _api, **kw: ifcopenshell.api.run(_api, f, **kw)
project = run("root.create_entity", ifc_class="IfcProject", name="Andreas 12 - Gryningsvägen 14")
M = {"is_metric": True, "raw": "METERS"}
run("unit.assign_unit", length=M, area=M, volume=M)
ctx = run("context.add_context", context_type="Model")
body = run("context.add_context", context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
site = run("root.create_entity", ifc_class="IfcSite", name="Andreas 12")
site.SiteAddress = f.create_entity("IfcPostalAddress", AddressLines=["Gryningsvägen 14"], PostalCode="163 51", Town="Spånga", Country="SE")
bld = run("root.create_entity", ifc_class="IfcBuilding", name="Andreas 12")
sto = run("root.create_entity", ifc_class="IfcBuildingStorey", name="Marknivå"); sto.Elevation = 0.0
run("aggregate.assign_object", products=[site], relating_object=project)
run("aggregate.assign_object", products=[bld], relating_object=site)
run("aggregate.assign_object", products=[sto], relating_object=bld)

# ---------------- hjälpare ----------------
def mat4(origin, xdir, zdir):
    z = np.array(zdir, float); z /= np.linalg.norm(z)
    x = np.array(xdir, float); x /= np.linalg.norm(x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, np.cross(z, x), z, origin
    return m
P3 = lambda *c: f.create_entity("IfcCartesianPoint", Coordinates=tuple(float(v) for v in c))
D3 = lambda *c: f.create_entity("IfcDirection", DirectionRatios=tuple(float(v) for v in c))
def ax3(loc=(0, 0, 0), z=None, x=None):
    return f.create_entity("IfcAxis2Placement3D", Location=P3(*loc), Axis=D3(*z) if z else None, RefDirection=D3(*x) if x else None)

STY = {}
def style(name, rgb):
    if name not in STY:
        s = run("style.add_style", name=name)
        run("style.add_surface_style", style=s, ifc_class="IfcSurfaceStyleShading",
            attributes={"SurfaceColour": {"Name": name, "Red": rgb[0], "Green": rgb[1], "Blue": rgb[2]}, "Transparency": 0.0})
        STY[name] = s
    return STY[name]
MAT = {}
def material(n):
    if n not in MAT: MAT[n] = run("material.add_material", name=n)
    return MAT[n]

def element(cls, name, ptype=None, mat=None, props=None, pset=None):
    kw = {"ifc_class": cls, "name": name}
    if ptype: kw["predefined_type"] = ptype
    el = run("root.create_entity", **kw)
    if mat: run("material.assign_material", products=[el], material=material(mat))
    if props: run("pset.edit_pset", pset=run("pset.add_pset", product=el, name=pset or "Stroo_Andreas12"), properties=props)
    return el
def place(el, m, container=None):
    run("geometry.edit_object_placement", product=el, matrix=m, is_si=True)
    run("spatial.assign_container", products=[el], relating_structure=container or sto)
def rect(w, h, off=None):
    return f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=w, YDim=h,
                           Position=f.create_entity("IfcAxis2Placement2D", Location=f.create_entity("IfcCartesianPoint", Coordinates=tuple(off or (0., 0.)))))
def circle(r):
    return f.create_entity("IfcCircleProfileDef", ProfileType="AREA", Radius=r,
                           Position=f.create_entity("IfcAxis2Placement2D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0., 0.))))
def poly(pts):
    ps = [f.create_entity("IfcCartesianPoint", Coordinates=(float(a), float(b))) for a, b in pts]; ps.append(ps[0])
    return f.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=f.create_entity("IfcPolyline", Points=ps))
def solid(profile, depth, pos=None):
    return f.create_entity("IfcExtrudedAreaSolid", SweptArea=profile, Position=pos or ax3(), ExtrudedDirection=D3(0, 0, 1), Depth=depth)
def box(x0, y0, z0, dx, dy, dz):   # hörnförankrad låda i världskoordinater
    return solid(rect(dx, dy, (dx / 2, dy / 2)), dz, ax3((x0, y0, z0)))
def rep(el, items, st=None, rtype="SweptSolid"):
    r = f.create_entity("IfcShapeRepresentation", ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType=rtype, Items=items)
    run("geometry.assign_representation", product=el, representation=r)
    if st: run("style.assign_representation_styles", shape_representation=r, styles=[st])
def plane(loc, flag_remove_below):
    pl = f.create_entity("IfcPlane", Position=ax3(loc, NRM, (C, 0, S)))
    return pl
def clip(sol, loc, remove_below):
    return f.create_entity("IfcBooleanClippingResult", Operator="DIFFERENCE", FirstOperand=sol,
                           SecondOperand=f.create_entity("IfcHalfSpaceSolid", BaseSurface=plane(loc, remove_below), AgreementFlag=remove_below))
def cut(sol, cutters):
    for c in cutters: sol = f.create_entity("IfcBooleanResult", Operator="DIFFERENCE", FirstOperand=sol, SecondOperand=c)
    return sol

WOOD, GL, OAK = style("Trä", (0.80, 0.66, 0.44)), style("Limträ", (0.74, 0.58, 0.36)), style("Ek, oljad", (0.52, 0.38, 0.23))
CONC, SEDUM, GRAV = style("Betong", (0.68, 0.68, 0.66)), style("Sedum", (0.38, 0.55, 0.28)), style("Makadam", (0.58, 0.55, 0.50))
SOIL, PLAST, ZINC = style("Jord", (0.36, 0.27, 0.19)), style("Puts", (0.93, 0.78, 0.30)), style("Plåt", (0.55, 0.58, 0.60))
TILE = style("Tegel", (0.72, 0.30, 0.18))

# ======================= CARPORT =======================
posts = [(X0 + px, y) for px in POST_X for y in (BEAM_Y, W - BEAM_Y)]
plinth_cutters = []
for i, (px, py) in enumerate(posts, 1):
    g = gz(px); zb = g + 0.05 - 0.50          # plintens underkant (överkant 50 mm över mark)
    ft = element("IfcFooting", f"Betongplint {i}", "PAD_FOOTING", "Betong",
                 {"Typ": "Ledbruket Betongplint KP 500 med bottenplatta eller likvärdigt (mått antagna)", "Stolpsko": "Justerbar, isolerad"}, "Stroo_Carport")
    rep(ft, [box(-0.10, -0.10, 0.0, 0.20, 0.20, 0.50), box(-0.20, -0.20, -0.08, 0.40, 0.40, 0.08)], CONC)
    place(ft, mat4((px, py, zb), (1, 0, 0), (0, 0, 1)))
    plinth_cutters += [box(px - 0.10, py - 0.10, zb, 0.20, 0.20, 0.50), box(px - 0.20, py - 0.20, zb - 0.08, 0.40, 0.40, 0.08)]
    zbase = g + 0.05; h = sz(px) - zbase
    col = element("IfcColumn", f"Pelare 90x90 {i}", "COLUMN", "Trä, kvadratisk pelare 90x90", {"Dimension": "90x90 mm"}, "Stroo_Carport")
    rep(col, [solid(rect(POST_CORE, POST_CORE), h)], WOOD); place(col, mat4((px, py, zbase), (1, 0, 0), (0, 0, 1)))
    for sgn in (-1, 1):
        pl = element("IfcWall", f"Pelarbeklädnad plank {i}{'a' if sgn < 0 else 'b'}", "STANDARD", "Trä, plank 22x220", {"Dimension": "22x220 mm"}, "Stroo_Carport")
        rep(pl, [solid(rect(PLANK_W, PLANK_T), h)], WOOD)
        place(pl, mat4((px, py + sgn * (POST_CORE / 2 + PLANK_T / 2), zbase), (1, 0, 0), (0, 0, 1)))

# bärlinor (sluttar parallellt med marken), underkant = undersida undertak
for k, yb in enumerate((BEAM_Y, W - BEAM_Y), 1):
    c0 = np.array((X0, yb, sz(X0))) + np.array(NRM) * (BEAM_H / 2)
    b = element("IfcBeam", f"Bärlina GL30c 90x360 {k}", "BEAM", "Limträ GL30c", {"Dimension": "90x360 mm", "Hållfasthetsklass": "GL30c"}, "Stroo_Carport")
    rep(b, [solid(rect(BEAM_W, BEAM_H), L / C)], GL); place(b, mat4(c0, (0, 1, 0), (C, 0, S)))

# bjälkar (horisontella, mellan bärlinorna, s600) och distansbitar
span = W - 2 * BEAM_Y - BEAM_W
xs = [FASCIA_T + JOIST_W / 2 + JOIST_S * k for k in range(8)] + [L - FASCIA_T - JOIST_W / 2]
for k, xl in enumerate(xs, 1):
    xw = X0 + xl
    j = element("IfcBeam", f"Bjälke 220x45 s600 #{k}", "JOIST", "Konstruktionsvirke C30", {"Dimension": "45x220 mm", "Hållfasthetsklass": "C30", "Centrumavstånd": "600 mm", "Fäste": "Balksko mot bärlina"}, "Stroo_Carport")
    rep(j, [solid(rect(JOIST_W, JOIST_H), span)], WOOD)
    place(j, mat4((xw, BEAM_Y + BEAM_W / 2, sz(xw) + SOFFIT_T + JOIST_H / 2), (1, 0, 0), (0, 1, 0)))
    for yy in (FASCIA_T, W - FASCIA_T - 0.100):
        d = element("IfcMember", f"Distansbit 100 #{k}", "MEMBER", "Konstruktionsvirke C30", {"Funktion": "Distansbit s600 mellan fasadpanel och bärlina"}, "Stroo_Carport")
        rep(d, [solid(rect(JOIST_W, 0.100), BEAM_H)], WOOD)
        place(d, mat4((xw, yy + 0.05, sz(xw) + BEAM_H / 2 * 0 ), (1, 0, 0), (0, 0, 1)))

# undertak (ytterpanel 22 + bärläkt 22)
ce = element("IfcCovering", "Undertak ytterpanel 22 + bärläkt 22", "CEILING", None, {"Panel": "Ytterpanel 22x70 s80", "Bärläkt": "22 mm s600"}, "Stroo_Carport")
ls = run("material.add_material_set", name="Undertak", set_type="IfcMaterialLayerSet")
for nm, t in (("Ytterpanel 22x70", 0.022), ("Bärläkt 22", 0.022)):
    ly = run("material.add_layer", layer_set=ls, material=material(nm)); run("material.edit_layer", layer=ly, attributes={"LayerThickness": t})
run("material.assign_material", products=[ce], type="IfcMaterialLayerSetUsage", material=ls)
lx = (L - 2 * FASCIA_T) / C
rep(ce, [solid(rect(lx, span, (lx / 2, span / 2)), SOFFIT_T)], OAK)
place(ce, mat4((X0 + FASCIA_T, BEAM_Y + BEAM_W / 2, sz(X0 + FASCIA_T)), (C, 0, S), NRM))

# sedumtak: plywood 21 + sedum 90 ovanpå bjälkarna
roof = element("IfcRoof", "Sedumtak", "FLAT_ROOF")
deck = element("IfcSlab", "Sedumtak, uppbyggnad", "ROOF", None, {"Utförande": "Sedumtak enl. leverantörens anvisning", "Fall": "Mot stuprör i nedre änden (mot huset)"}, "Stroo_Carport")
ls = run("material.add_material_set", name="Sedumtak", set_type="IfcMaterialLayerSet")
for nm, t in (("Plywood 21", DECK_T), ("Sedumtak 90", SEDUM_T)):
    ly = run("material.add_layer", layer_set=ls, material=material(nm)); run("material.edit_layer", layer=ly, attributes={"LayerThickness": t})
run("material.assign_material", products=[deck], type="IfcMaterialLayerSetUsage", material=ls)
rep(deck, [solid(rect(lx, span, (lx / 2, span / 2)), DECK_T + SEDUM_T)], SEDUM)
place(deck, mat4((X0 + FASCIA_T, BEAM_Y + BEAM_W / 2, sz(X0 + FASCIA_T) + SOFFIT_T + JOIST_H), (C, 0, S), NRM))
run("aggregate.assign_object", products=[deck], relating_object=roof); run("spatial.assign_container", products=[roof], relating_structure=sto)

# fasadpanel (ek) 440 mm, snedskuren parallellt med taket
def fascia(name, x0, y0, w, d, sloped):
    wl = element("IfcWall", name, "STANDARD", "Sågad ek, oljad", {"Beklädnad": "Sågad ek. Oljas in.", "Höjd": "440 mm"}, "Stroo_Carport")
    z0 = sz(x0) - 0.025
    if sloped:
        s0 = solid(rect(w, d, (w / 2, d / 2)), w * T + FASCIA_H + 0.05)
        rep(wl, [clip(clip(s0, (0, 0, 0), True), (0, 0, FASCIA_H), False)], OAK, "Clipping")
    else:
        rep(wl, [solid(rect(w, d, (w / 2, d / 2)), FASCIA_H)], OAK)
    place(wl, mat4((x0, y0, z0), (1, 0, 0), (0, 0, 1)))
    run("pset.edit_pset", pset=run("pset.add_pset", product=wl, name="Pset_WallCommon"), properties={"IsExternal": True, "LoadBearing": False})
fascia("Fasadpanel söder", X0, 0.0, L, FASCIA_T, True)
fascia("Fasadpanel norr", X0, W - FASCIA_T, L, FASCIA_T, True)
fascia("Fasadpanel västra gaveln", X0, FASCIA_T, FASCIA_T, W - 2 * FASCIA_T, False)
fascia("Fasadpanel östra gaveln", X0 + L - FASCIA_T, FASCIA_T, FASCIA_T, W - 2 * FASCIA_T, False)

# integrerat stuprör bakom sydvästra pelaren, ned mot stenkistan
px, py = posts[0]
pipe = element("IfcPipeSegment", "Integrerat stuprör", "RIGIDSEGMENT", "Plåt", {"Placering": "Dolt bakom pelare, dränering mot stenkista"}, "Stroo_Carport")
rep(pipe, [solid(circle(0.03), sz(px - 0.11) + 0.10 - gz(px - 0.11))], ZINC)
place(pipe, mat4((px - 0.11, py, gz(px - 0.11)), (1, 0, 0), (0, 0, 1)))

# stenkista vid husväggen (bredd 600 enl. ritning, övrigt antaget)
SK = (0.0, -0.90, 0.60, 1.00, 0.60)    # x0, y0, dx, dy, djup
zsk = gz(0.3) - SK[4]
sk = element("IfcSlab", "Stenkista", "BASESLAB", "Makadam", {"Bredd": "600 mm (A-40-1-100)", "Längd och djup": "1000 x 600 mm, antagna"}, "Stroo_Carport")
rep(sk, [box(0, 0, 0, SK[2], SK[3], SK[4])], GRAV); place(sk, mat4((SK[0], SK[1], zsk), (1, 0, 0), (0, 0, 1)))
sk_cutter = box(SK[0], SK[1], zsk, SK[2], SK[3], SK[4])

# ======================= MARK (solida element, urgröpta för fundament och stenkista) =======================
Y0, Y1 = -10.0, 12.0
g1 = element("IfcSlab", "Mark, plan", "BASESLAB", "Jord", {"Not": "Plan mark runt huset (z=0)"}, "Stroo_Mark")
rep(g1, [solid(rect(13.0, Y1 - Y0, (6.5, (Y1 - Y0) / 2)), 1.0, ax3((-13.0, Y0, -1.0)))], SOIL, "SweptSolid")
place(g1, np.eye(4))
H = 1.0 + BOUNDARY_X * T + 0.10
g2 = element("IfcSlab", "Mark, ramp", "BASESLAB", "Jord", {"Fall": "4,5 grader stigande österut (ramp mot källardörr)", "Urgröpningar": "Betongplintar och stenkista (boolesk differens)"}, "Stroo_Mark")
s0 = solid(rect(BOUNDARY_X, Y1 - Y0, (BOUNDARY_X / 2, (Y1 - Y0) / 2)), H, ax3((0, Y0, -1.0)))
topclip = clip(s0, (0, 0, 0), False)                       # planet ligger i elementets koordinatsystem (=världen)
rep(g2, [cut(topclip, plinth_cutters + [sk_cutter])], SOIL, "CSG")
place(g2, np.eye(4))

# ======================= BEFINTLIG BYGGNAD (förenklad) =======================
HT, HH = 0.35, 5.0
xw_, xb_, ys_, yn_, ym_ = -10.96, -5.60, -3.79, 9.44, 3.79
def hwall(name, x0, x1, y0, y1):
    w = element("IfcWall", name, "STANDARD", "Puts på bärande vägg (förenklad)", {"Status": "Befintlig, förenklad (inga öppningar/tak). Höjd antagen."}, "Stroo_Befintlig")
    rep(w, [box(0, 0, 0, x1 - x0, y1 - y0, HH)], PLAST); place(w, mat4((x0, y0, 0.0), (1, 0, 0), (0, 0, 1)))
    run("pset.edit_pset", pset=run("pset.add_pset", product=w, name="Pset_WallCommon"), properties={"IsExternal": True, "LoadBearing": True})
hwall("Befintlig östfasad", -HT, 0.0, ys_, yn_)
hwall("Befintlig sydfasad", xw_, -HT, ys_, ys_ + HT)
hwall("Befintlig västfasad", xw_, xw_ + HT, ys_ + HT, ym_)
hwall("Befintlig nordvägg, västra delen", xw_ + HT, xb_ + HT, ym_ - HT, ym_)
hwall("Befintlig västvägg, östra flygeln", xb_, xb_ + HT, ym_, yn_ - HT)
hwall("Befintlig nordfasad", xb_, -HT, yn_ - HT, yn_)

# ======================= ENTRÉ (A-40-1-102) =======================
XC, YS, ZL = -5.493, ys_, 1.80
EW = 2.150
land = element("IfcSlab", "Entréplan, gjuten betongplatta", "LANDING", "Betong", {"Överkant": "1800 mm över mark (antagen)", "Tjocklek": "390 mm (1410 fri höjd)"}, "Stroo_Entre")
rep(land, [solid(rect(EW, 1.2, (EW / 2, 0.6)), 0.39)], CONC); place(land, mat4((XC - EW / 2, YS - 1.2, ZL - 0.39), (1, 0, 0), (0, 0, 1)))
d = 2.59 / 8; pts = [(0, 0)]
for k in range(1, 9): pts += [((k - 1) * d, ZL - 0.2 * k), (k * d, ZL - 0.2 * k)]
pts += [(2.59, 0)]
stair = element("IfcStair", "Entrétrappa", "STRAIGHT_RUN_STAIR")
flight = element("IfcStairFlight", "Trapplopp, gjuten", "STRAIGHT", "Betong", {"Bredd": "2150 mm", "Antal stigningar": "9 (antagen)", "Material": "Gjuten/prefab betong, stenplattor granit/råbetong"}, "Stroo_Entre")
flight.NumberOfRisers, flight.NumberOfTreads, flight.RiserHeight, flight.TreadLength = 9, 8, 0.2, d
rep(flight, [solid(poly(pts), EW)], CONC)
place(flight, mat4((XC + EW / 2, YS - 1.2, 0.0), (0, -1, 0), (0, 0, 1)))
# profilens x (=s) -> -y, profilens y -> z, extrusion mot -x
m = mat4((XC + EW / 2, YS - 1.2, 0.0), (0, -1, 0), (-1, 0, 0)); run("geometry.edit_object_placement", product=flight, matrix=m, is_si=True)
run("aggregate.assign_object", products=[flight], relating_object=stair); run("spatial.assign_container", products=[stair], relating_structure=sto)
for i, (cx, cy) in enumerate([(XC + sx * 0.95, YS - dy) for sx in (-1, 1) for dy in (0.10, 1.10)], 1):
    cc = element("IfcColumn", f"Takpelare rund D150 {i}", "COLUMN", "Betong, platsgjuten", {"Diameter": "150 mm"}, "Stroo_Entre")
    rep(cc, [solid(circle(0.075), 2.4)], CONC); place(cc, mat4((cx, cy, ZL), (1, 0, 0), (0, 0, 1)))
ang = math.radians(15); ca, sa = math.cos(ang), math.sin(ang)
pr = element("IfcRoof", "Entrétak", "GABLE_ROOF")
depth = 1.2 + 0.155; half = 1.125; z0 = ZL + 2.4; slope_len = half / ca
for nm, org, xd, zd in (("Entrétak vä", (XC - half, YS - depth, z0), (ca, 0, sa), (-sa, 0, ca)),
                        ("Entrétak hö", (XC, YS - depth, z0 + half * math.tan(ang)), (ca, 0, -sa), (sa, 0, ca))):
    sl = element("IfcSlab", nm, "ROOF", "Tvåkupiga tegelpannor", {"Taklutning": "15 grader", "Tjocklek": "100 mm (antagen)"}, "Stroo_Entre")
    rep(sl, [solid(rect(slope_len, depth, (slope_len / 2, depth / 2)), 0.10)], TILE)
    place(sl, mat4(org, xd, zd)); run("aggregate.assign_object", products=[sl], relating_object=pr)
run("spatial.assign_container", products=[pr], relating_structure=sto)

# ======================= typer =======================
def types(cls, groups):
    for nm, pred, els in groups:
        if not els: continue
        kw = {"ifc_class": cls, "name": nm}
        if pred: kw["predefined_type"] = pred
        te = run("root.create_entity", **kw); run("type.assign_type", related_objects=els, relating_type=te)
by = lambda cls, pre: [e for e in f.by_type(cls) if (e.Name or "").startswith(pre)]
types("IfcColumnType", [("Pelare 90x90", "COLUMN", by("IfcColumn", "Pelare")), ("Takpelare rund D150", "COLUMN", by("IfcColumn", "Takpelare"))])
types("IfcBeamType", [("Bärlina GL30c 90x360", "BEAM", by("IfcBeam", "Bärlina")), ("Bjälke 45x220 C30", "JOIST", by("IfcBeam", "Bjälke"))])
types("IfcFootingType", [("Betongplint KP 500", "PAD_FOOTING", by("IfcFooting", "Betongplint"))])
types("IfcWallType", [("Pelarbeklädnad 22x220", "STANDARD", by("IfcWall", "Pelarbeklädnad")), ("Fasadpanel ek 440", "STANDARD", by("IfcWall", "Fasadpanel")), ("Befintlig yttervägg", "STANDARD", by("IfcWall", "Befintlig"))])

run("pset.edit_pset", pset=run("pset.add_pset", product=project, name="Stroo_Projekt"),
    properties={"Fastighet": "Andreas 12", "Adress": "Gryningsvägen 14, 163 51 Spånga", "Ritningar": "A-01-1-001 A, A-40-1-100 B, A-40-1-101 A, A-40-1-102, A-40-1-103"})
f.write(OUT); print("skrev", OUT)
