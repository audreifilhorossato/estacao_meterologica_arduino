# -*- coding: utf-8 -*-
"""
Gera, a partir de geometria.py:
  - step/caixa_estacao_montada.step  (conjunto montado + componentes de referência)
  - dxf/pecas/*.dxf                  (uma peça por arquivo, camada CORTE)
  - dxf/chapa_corte_completa.dxf     (todas as peças, nas quantidades, lado a lado)
  - previa/*.png                     (imagens de conferência)
e roda verificações (furos dentro das peças, distâncias mínimas, interferências 3D).

Uso:  python gerar.py <pasta_de_saida>
"""
import math
import os
import sys
import itertools

import cadquery as cq
import ezdxf
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import geometria as G  # noqa: E402

P = G.PARAMETROS
T = P["espessura"]


# ---------------------------------------------------------------------------
# 2D -> shapely (verificação) e -> CadQuery (3D)
# ---------------------------------------------------------------------------
def furo_shapely(h):
    if h["tipo"] == "circulo":
        return Point(h["cx"], h["cy"]).buffer(h["r"], 64)
    if h["tipo"] == "poligono":
        return Polygon(h["pts"])
    r = h["larg"] / 2
    hs = h["comp"] / 2 - r
    if h["vertical"]:
        ls = LineString([(h["cx"], h["cy"] - hs), (h["cx"], h["cy"] + hs)])
    else:
        ls = LineString([(h["cx"] - hs, h["cy"]), (h["cx"] + hs, h["cy"])])
    return ls.buffer(r, 64)


def verificar_pecas(pecas, folga_min=1.0):
    problemas = []
    relat = []
    for pc in pecas:
        outer = Polygon(pc.contorno)
        if not outer.is_valid:
            problemas.append("%s: contorno inválido" % pc.nome)
            continue
        hs = [furo_shapely(h) for h in pc.furos]
        dmin_borda = 1e9
        for i, h in enumerate(hs):
            if not outer.contains(h):
                problemas.append("%s: furo %d sai da peça" % (pc.nome, i))
            dmin_borda = min(dmin_borda, h.distance(outer.exterior))
        dmin_furos = 1e9
        for (i, a), (j, b) in itertools.combinations(enumerate(hs), 2):
            d = a.distance(b)
            dmin_furos = min(dmin_furos, d)
            if d < folga_min:
                problemas.append("%s: furos %d e %d a %.2f mm" % (pc.nome, i, j, d))
        if hs and dmin_borda < folga_min:
            problemas.append("%s: furo a %.2f mm da borda" % (pc.nome, dmin_borda))
        area = outer.area - sum(h.area for h in hs)
        relat.append((pc.nome, pc.quantidade, len(hs), dmin_borda if hs else None,
                      dmin_furos if len(hs) > 1 else None, area))
    return problemas, relat


def wire_poligono(pts):
    return cq.Wire.makePolygon([cq.Vector(x, y, 0) for x, y in pts], close=True)


def wire_furo(h):
    if h["tipo"] == "circulo":
        return cq.Wire.makeCircle(h["r"], cq.Vector(h["cx"], h["cy"], 0), cq.Vector(0, 0, 1))
    if h["tipo"] == "poligono":
        return wire_poligono(h["pts"])
    r = h["larg"] / 2
    hs = h["comp"] / 2 - r
    cx, cy = h["cx"], h["cy"]
    if h["vertical"]:
        a, b, c, d = (cx + r, cy - hs), (cx + r, cy + hs), (cx - r, cy + hs), (cx - r, cy - hs)
        m1, m2 = (cx, cy + hs + r), (cx, cy - hs - r)
    else:
        a, b, c, d = (cx - hs, cy - r), (cx + hs, cy - r), (cx + hs, cy + r), (cx - hs, cy + r)
        m1, m2 = (cx + hs + r, cy), (cx - hs - r, cy)
    V = lambda p: cq.Vector(p[0], p[1], 0)  # noqa: E731
    if h["vertical"]:
        edges = [cq.Edge.makeLine(V(a), V(b)), cq.Edge.makeThreePointArc(V(b), V(m1), V(c)),
                 cq.Edge.makeLine(V(c), V(d)), cq.Edge.makeThreePointArc(V(d), V(m2), V(a))]
    else:
        edges = [cq.Edge.makeLine(V(a), V(b)), cq.Edge.makeThreePointArc(V(b), V(m1), V(c)),
                 cq.Edge.makeLine(V(c), V(d)), cq.Edge.makeThreePointArc(V(d), V(m2), V(a))]
    return cq.Wire.assembleEdges(edges)


def solido_peca(pc):
    if pc.circulo:
        outer = cq.Wire.makeCircle(pc.circulo, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    else:
        outer = wire_poligono(pc.contorno)
    inner = [wire_furo(h) for h in pc.furos]
    face = cq.Face.makeFromWires(outer, inner)
    return cq.Solid.extrudeLinear(face, cq.Vector(0, 0, T))


def local(pos):
    origem, eu, ev, ew = pos
    plano = cq.Plane(origin=cq.Vector(*origem), xDir=cq.Vector(*eu), normal=cq.Vector(*ew))
    return cq.Location(plano)


def solido_ref(r):
    nome, tipo, d = r
    if tipo == "caixa":
        x0, y0, z0, dx, dy, dz = d
        return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x0, y0, z0))
    cx, cy, z0, diam, h = d
    return cq.Solid.makeCylinder(diam / 2, h, cq.Vector(cx, cy, z0))


CORES_REF = {
    "Arduino": (0.0, 0.45, 0.55),
    "LCD_placa": (0.1, 0.45, 0.15),
    "LCD_moldura": (0.75, 0.75, 0.78),
    "LCD_modulo": (0.15, 0.2, 0.6),
    "Bateria": (0.85, 0.45, 0.05),
    "Chave": (0.08, 0.08, 0.08),
    "Botao": (0.15, 0.15, 0.15),
    "LED": (0.95, 0.1, 0.1),
    "LDR": (0.85, 0.65, 0.2),
    "Sensor": (0.95, 0.95, 0.92),
}


def cor_ref(nome):
    for k, c in CORES_REF.items():
        if nome.startswith(k):
            return c
    return (0.5, 0.5, 0.5)


# ---------------------------------------------------------------------------
# DXF
# ---------------------------------------------------------------------------
def dxf_novo():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    doc.layers.add("CORTE", color=1)
    doc.layers.add("TEXTO_NAO_CORTAR", color=5)
    return doc


def dxf_peca(msp, pc, dx, dy, camada="CORTE"):
    at = {"layer": camada}
    if pc.circulo:
        msp.add_circle((dx, dy), pc.circulo, dxfattribs=at)
    else:
        msp.add_lwpolyline([(x + dx, y + dy) for x, y in pc.contorno], close=True, dxfattribs=at)
    for h in pc.furos:
        if h["tipo"] == "circulo":
            msp.add_circle((h["cx"] + dx, h["cy"] + dy), h["r"], dxfattribs=at)
        elif h["tipo"] == "poligono":
            msp.add_lwpolyline([(x + dx, y + dy) for x, y in h["pts"]], close=True, dxfattribs=at)
        else:
            r = h["larg"] / 2
            hs = h["comp"] / 2 - r
            cx, cy = h["cx"] + dx, h["cy"] + dy
            if h["vertical"]:
                pts = [(cx + r, cy - hs, 0, 0, 0), (cx + r, cy + hs, 0, 0, 1),
                       (cx - r, cy + hs, 0, 0, 0), (cx - r, cy - hs, 0, 0, 1)]
            else:
                pts = [(cx - hs, cy - r, 0, 0, 0), (cx + hs, cy - r, 0, 0, 1),
                       (cx + hs, cy + r, 0, 0, 0), (cx - hs, cy + r, 0, 0, 1)]
            msp.add_lwpolyline(pts, format="xyseb", close=True, dxfattribs=at)


def empacotar(pecas, largura_util, espaco=4.0, margem=5.0):
    """Empacotamento simples em prateleiras (sem girar)."""
    itens = []
    for pc in pecas:
        x0, y0, x1, y1 = pc.limites()
        for k in range(pc.quantidade):
            itens.append((pc, x1 - x0, y1 - y0, k))
    itens.sort(key=lambda it: (-it[2], -it[1]))
    prateleiras = []  # [y, altura, x_livre]
    pos = []
    y_topo = margem
    for pc, w, h, k in itens:
        colocado = False
        for pr in prateleiras:
            if h <= pr[1] + 1e-6 and pr[2] + w <= largura_util - margem + 1e-6:
                # empilha itens baixos dentro da mesma prateleira, em colunas
                pos.append((pc, pr[2], pr[0]))
                pr[2] += w + espaco
                colocado = True
                break
        if not colocado:
            prateleiras.append([y_topo, h, margem + w + espaco])
            pos.append((pc, margem, y_topo))
            y_topo += h + espaco
    altura = y_topo - espaco + margem
    return pos, altura


def empacotar_v2(pecas, largura_util, espaco=4.0, margem=5.0):
    """Prateleiras; dentro de uma prateleira alta, peças baixas são empilhadas em colunas."""
    itens = []
    for pc in pecas:
        x0, y0, x1, y1 = pc.limites()
        for k in range(pc.quantidade):
            itens.append([pc, x1 - x0, y1 - y0])
    itens.sort(key=lambda it: (-it[2], -it[1]))
    prateleiras = []   # cada uma: dict(y, h, colunas=[dict(x, w, y_livre)], x_livre)
    pos = []
    y_topo = margem
    for pc, w, h in itens:
        ok = False
        for pr in prateleiras:
            # tenta empilhar numa coluna existente
            for col in pr["colunas"]:
                if w <= col["w"] + 1e-6 and col["y_livre"] + h <= pr["y"] + pr["h"] + 1e-6:
                    pos.append((pc, col["x"], col["y_livre"]))
                    col["y_livre"] += h + espaco
                    ok = True
                    break
            if ok:
                break
            if pr["x_livre"] + w <= largura_util - margem + 1e-6 and h <= pr["h"] + 1e-6:
                col = {"x": pr["x_livre"], "w": w, "y_livre": pr["y"] + h + espaco}
                pr["colunas"].append(col)
                pos.append((pc, pr["x_livre"], pr["y"]))
                pr["x_livre"] += w + espaco
                ok = True
                break
        if not ok:
            pr = {"y": y_topo, "h": h, "colunas": [], "x_livre": margem}
            col = {"x": margem, "w": w, "y_livre": y_topo + h + espaco}
            pr["colunas"].append(col)
            pr["x_livre"] = margem + w + espaco
            prateleiras.append(pr)
            pos.append((pc, margem, y_topo))
            y_topo += h + espaco
    largura_usada = max(x + (pc.limites()[2] - pc.limites()[0]) for pc, x, y in pos) + margem
    altura = y_topo - espaco + margem
    return pos, largura_usada, altura


# ---------------------------------------------------------------------------
# Render (VTK offscreen)
# ---------------------------------------------------------------------------
def render(objetos, arquivo, camera, tamanho=(1600, 1100), titulo=None):
    import vtk
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    ren.SetUseDepthPeeling(1)
    ren.SetMaximumNumberOfPeels(8)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetAlphaBitPlanes(1)
    win.SetMultiSamples(0)
    win.AddRenderer(ren)
    win.SetSize(*tamanho)
    for shape, cor, opac, arestas in objetos:
        verts, tris = shape.tessellate(0.05, 0.3)
        pts = vtk.vtkPoints()
        for v in verts:
            pts.InsertNextPoint(v.x, v.y, v.z)
        cells = vtk.vtkCellArray()
        for a, b, c in tris:
            cells.InsertNextCell(3)
            cells.InsertCellPoint(a)
            cells.InsertCellPoint(b)
            cells.InsertCellPoint(c)
        pd = vtk.vtkPolyData()
        pd.SetPoints(pts)
        pd.SetPolys(cells)
        nrm = vtk.vtkPolyDataNormals()
        nrm.SetInputData(pd)
        nrm.SetFeatureAngle(30)
        nrm.SplittingOn()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nrm.GetOutputPort())
        act = vtk.vtkActor()
        act.SetMapper(mp)
        act.GetProperty().SetColor(*cor)
        act.GetProperty().SetOpacity(opac)
        act.GetProperty().SetSpecular(0.2)
        ren.AddActor(act)
        if arestas:
            fe = vtk.vtkFeatureEdges()
            fe.SetInputData(pd)
            fe.BoundaryEdgesOn()
            fe.FeatureEdgesOn()
            fe.SetFeatureAngle(30)
            fe.ManifoldEdgesOff()
            fe.NonManifoldEdgesOff()
            fe.ColoringOff()
            m2 = vtk.vtkPolyDataMapper()
            m2.SetInputConnection(fe.GetOutputPort())
            a2 = vtk.vtkActor()
            a2.SetMapper(m2)
            a2.GetProperty().SetColor(0.15, 0.3, 0.45)
            a2.GetProperty().SetLineWidth(1.5)
            a2.GetProperty().SetOpacity(min(1.0, opac + 0.5))
            ren.AddActor(a2)
    cam = ren.GetActiveCamera()
    pos, foco, up = camera
    cam.SetPosition(*pos)
    cam.SetFocalPoint(*foco)
    cam.SetViewUp(*up)
    ren.ResetCamera()
    cam.Zoom(1.15)
    if titulo:
        txt = vtk.vtkTextActor()
        txt.SetInput(titulo)
        txt.GetTextProperty().SetFontSize(28)
        txt.GetTextProperty().SetColor(0.1, 0.1, 0.1)
        txt.SetPosition(20, tamanho[1] - 50)
        ren.AddActor2D(txt)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(arquivo)
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()


def desenho_chapa_png(pos, largura, altura, arquivo, titulo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly
    fig, ax = plt.subplots(figsize=(largura / 25.4 * 0.9, altura / 25.4 * 0.9), dpi=110)
    ax.add_patch(plt.Rectangle((0, 0), largura, altura, fill=False, ec="0.6", lw=0.8, ls="--"))
    for pc, x, y in pos:
        x0, y0, _, _ = pc.limites()
        dx, dy = x - x0, y - y0
        geom = Polygon([(a + dx, b + dy) for a, b in pc.contorno])
        for h in pc.furos:
            hh = furo_shapely(h)
            from shapely.affinity import translate
            geom = geom.difference(translate(hh, dx, dy))
        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for g in polys:
            ax.add_patch(MPoly(list(g.exterior.coords), closed=True, fc=(0.75, 0.88, 0.97), ec="#c0392b", lw=0.6))
            for it in g.interiors:
                ax.add_patch(MPoly(list(it.coords), closed=True, fc="white", ec="#c0392b", lw=0.6))
        cxp, cyp = geom.representative_point().x, geom.representative_point().y
        if (pc.limites()[2] - pc.limites()[0]) > 25:
            ax.text(x + (pc.limites()[2] - pc.limites()[0]) / 2, y + 2.5, pc.nome.replace("_", " "),
                    ha="center", va="bottom", fontsize=7, color="#1f3a5f")
    ax.set_xlim(-5, largura + 5)
    ax.set_ylim(-5, altura + 5)
    ax.set_aspect("equal")
    ax.set_title(titulo, fontsize=10)
    ax.set_xlabel("mm")
    fig.tight_layout()
    fig.savefig(arquivo)
    plt.close(fig)


# ---------------------------------------------------------------------------
def main(saida):
    os.makedirs(os.path.join(saida, "step"), exist_ok=True)
    os.makedirs(os.path.join(saida, "dxf", "pecas"), exist_ok=True)
    os.makedirs(os.path.join(saida, "previa"), exist_ok=True)

    pecas = G.gerar_pecas(P)
    refs = G.referencias(P)

    # ---- verificações 2D
    problemas, relat = verificar_pecas(pecas)
    print("== Peças ==")
    for nome, qtd, nf, db, dfu, area in relat:
        print("  %-26s x%-2d furos=%-3d borda_min=%s furo_furo_min=%s" % (
            nome, qtd, nf, "%.2f" % db if db is not None else "-",
            "%.2f" % dfu if dfu is not None else "-"))
    if problemas:
        print("!! PROBLEMAS 2D:")
        for pb in problemas:
            print("   ", pb)

    # ---- sólidos
    solidos_peca = {pc.nome: solido_peca(pc) for pc in pecas}
    colocados = []   # (nome, shape_movido, tipo)
    assy = cq.Assembly(name="caixa_estacao")
    acr = cq.Assembly(name="acrilico_cortar")
    ref = cq.Assembly(name="referencias_nao_cortar")
    cor_acr = cq.Color(0.55, 0.78, 0.95, 0.55)
    for pc in pecas:
        for i, pos in enumerate(pc.posicoes):
            nome = pc.nome if pc.quantidade == 1 else "%s_%02d" % (pc.nome, i + 1)
            loc = local(pos)
            acr.add(solidos_peca[pc.nome], name=nome, loc=loc, color=cor_acr)
            colocados.append((nome, solidos_peca[pc.nome].moved(loc), "peca"))
    for r in refs:
        s = solido_ref(r)
        c = cor_ref(r[0])
        ref.add(s, name=r[0], color=cq.Color(c[0], c[1], c[2], 1.0))
        colocados.append((r[0], s, "ref"))
    assy.add(acr)
    assy.add(ref)
    arq_step = os.path.join(saida, "step", "caixa_estacao_montada.step")
    assy.export(arq_step)
    print("STEP:", arq_step)

    # ---- interferências 3D
    print("== Interferências 3D (volume > 0.01 mm³) ==")
    n_int = 0
    for (n1, s1, t1), (n2, s2, t2) in itertools.combinations(colocados, 2):
        if t1 == "ref" and t2 == "ref":
            continue
        b1, b2 = s1.BoundingBox(), s2.BoundingBox()
        if (b1.xmax < b2.xmin or b2.xmax < b1.xmin or b1.ymax < b2.ymin or b2.ymax < b1.ymin
                or b1.zmax < b2.zmin or b2.zmax < b1.zmin):
            continue
        v = s1.intersect(s2).Volume()
        if v > 0.01:
            n_int += 1
            print("  %s x %s : %.2f mm³" % (n1, n2, v))
    if n_int == 0:
        print("  nenhuma")

    # ---- DXF por peça
    for pc in pecas:
        doc = dxf_novo()
        x0, y0, _, _ = pc.limites()
        dxf_peca(doc.modelspace(), pc, -x0, -y0)
        nome = pc.nome + ("_x%d" % pc.quantidade if pc.quantidade > 1 else "") + ".dxf"
        doc.saveas(os.path.join(saida, "dxf", "pecas", nome))

    # ---- DXF da chapa completa
    pos, larg, alt = empacotar_v2(pecas, largura_util=360.0)
    doc = dxf_novo()
    msp = doc.modelspace()
    for pc, x, y in pos:
        x0, y0, _, _ = pc.limites()
        dxf_peca(msp, pc, x - x0, y - y0)
    doc.saveas(os.path.join(saida, "dxf", "chapa_corte_completa.dxf"))
    print("Chapa completa: %.0f x %.0f mm" % (larg, alt))
    desenho_chapa_png(pos, larg, alt, os.path.join(saida, "previa", "chapa_corte.png"),
                      "Chapa de corte - acrílico %.0f mm - área %.0f x %.0f mm (vermelho = corte)" % (T, larg, alt))

    # ---- imagens 3D
    L, W, H = P["comprimento"], P["profundidade"], P["altura"]
    foco = (L / 2, W / 2, H / 2)
    iso = ((L / 2 - 260, W / 2 - 330, H / 2 + 260), foco, (0, 0, 1))
    objs = []
    for nome, s, tp in colocados:
        if tp == "peca":
            objs.append((s, (0.62, 0.82, 0.96), 0.35, True))
        else:
            objs.append((s, cor_ref(nome), 1.0, False))
    render(objs, os.path.join(saida, "previa", "montada.png"), iso,
           titulo="Caixa montada (acrilico transparente) com Arduino, LCD, bateria e sensores")

    # explodida
    objs = []
    for nome, s, tp in colocados:
        dz = dx = dy = 0.0
        if nome.startswith("tampa") or nome.startswith("suporte_botao") or nome.startswith("LCD") \
                or nome.startswith("Botao") or nome.startswith("LED") or nome.startswith("LDR"):
            dz = 70
        elif nome.startswith("arruela") and s.BoundingBox().zmin > H / 2:
            dz = 70
        elif nome.startswith("fundo") or nome.startswith("pe"):
            dz = -45
        elif nome.startswith("parede_frente"):
            dy = -60
        elif nome.startswith("parede_tras"):
            dy = 60
        elif nome.startswith("parede_esquerda"):
            dx = -60
        elif nome.startswith("parede_direita") or nome.startswith("Chave"):
            dx = 60
        s2 = s.moved(cq.Location(cq.Vector(dx, dy, dz)))
        if tp == "peca":
            objs.append((s2, (0.62, 0.82, 0.96), 0.45, True))
        else:
            objs.append((s2, cor_ref(nome), 1.0, False))
    render(objs, os.path.join(saida, "previa", "explodida.png"),
           ((L / 2 - 330, W / 2 - 420, H / 2 + 330), foco, (0, 0, 1)),
           titulo="Vista explodida")

    # tampa vista de cima
    objs = []
    for nome, s, tp in colocados:
        if nome == "tampa" or nome.startswith("LCD_moldura") or nome.startswith("Botao") \
                or nome.startswith("LED") or nome.startswith("LDR"):
            if tp == "peca":
                objs.append((s, (0.62, 0.82, 0.96), 0.9, True))
            else:
                objs.append((s, cor_ref(nome), 1.0, False))
    render(objs, os.path.join(saida, "previa", "tampa_de_cima.png"),
           ((L / 2, W / 2, 500), (L / 2, W / 2, H), (0, 1, 0)), tamanho=(1500, 1050),
           titulo="Tampa vista de cima: LED (vermelho), botao, LDR e LCD")

    # interior sem tampa
    objs = []
    for nome, s, tp in colocados:
        if nome == "tampa" or nome.startswith("LCD") or nome.startswith("suporte_botao") \
                or nome.startswith("Botao") or nome.startswith("LED") or nome.startswith("LDR"):
            continue
        if nome.startswith("arruela") and s.BoundingBox().zmin > H / 2:
            continue
        if tp == "peca":
            objs.append((s, (0.62, 0.82, 0.96), 0.4, True))
        else:
            objs.append((s, cor_ref(nome), 1.0, False))
    render(objs, os.path.join(saida, "previa", "interior_sem_tampa.png"),
           ((L / 2 - 120, W / 2 - 300, H / 2 + 380), foco, (0, 0, 1)),
           titulo="Interior sem a tampa: Arduino nos espacadores, bateria no canto, sensores na frente")
    return problemas, n_int


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "saida")
    main(out)
