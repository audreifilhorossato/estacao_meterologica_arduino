
# ===========================================================================
# PARTE DO FUSION 360  (não precisa mexer daqui pra baixo)
# ===========================================================================
import traceback

import adsk.core
import adsk.fusion

CM = 0.1   # a API do Fusion trabalha em centímetros


def _p3(x, y, z=0.0):
    return adsk.core.Point3D.create(x * CM, y * CM, z * CM)


def _matriz(pos):
    origem, eu, ev, ew = pos
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(_p3(*origem),
                              adsk.core.Vector3D.create(*eu),
                              adsk.core.Vector3D.create(*ev),
                              adsk.core.Vector3D.create(*ew))
    return m


def _poligono(sk, pts):
    linhas = sk.sketchCurves.sketchLines
    primeira = None
    anterior = None
    n = len(pts)
    for i in range(n):
        a = pts[i]
        b = pts[(i + 1) % n]
        ini = anterior.endSketchPoint if anterior is not None else _p3(*a)
        fim = primeira.startSketchPoint if i == n - 1 else _p3(*b)
        ln = linhas.addByTwoPoints(ini, fim)
        if primeira is None:
            primeira = ln
        anterior = ln


def _junta_pontos(curvas):
    pts = []
    for c in curvas:
        pts.append(c.startSketchPoint)
        pts.append(c.endSketchPoint)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            try:
                if not (pts[i].isValid and pts[j].isValid):
                    continue
                if pts[i] == pts[j]:
                    continue
                if pts[i].geometry.distanceTo(pts[j].geometry) < 1e-6:
                    pts[i].merge(pts[j])
            except Exception:
                pass


def _rasgo(sk, h):
    r = h["larg"] / 2.0
    hs = h["comp"] / 2.0 - r
    cx, cy = h["cx"], h["cy"]
    if h["vertical"]:
        a, b, c, d = (cx + r, cy - hs), (cx + r, cy + hs), (cx - r, cy + hs), (cx - r, cy - hs)
        m1, m2 = (cx, cy + hs + r), (cx, cy - hs - r)
    else:
        a, b, c, d = (cx - hs, cy - r), (cx + hs, cy - r), (cx + hs, cy + r), (cx - hs, cy + r)
        m1, m2 = (cx + hs + r, cy), (cx - hs - r, cy)
    linhas = sk.sketchCurves.sketchLines
    arcos = sk.sketchCurves.sketchArcs
    l1 = linhas.addByTwoPoints(_p3(*a), _p3(*b))
    a1 = arcos.addByThreePoints(_p3(*b), _p3(*m1), _p3(*c))
    l2 = linhas.addByTwoPoints(_p3(*c), _p3(*d))
    a2 = arcos.addByThreePoints(_p3(*d), _p3(*m2), _p3(*a))
    _junta_pontos([l1, a1, l2, a2])


def _desenha_peca(comp, pc, espessura):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "corte_" + pc.nome
    sk.isComputeDeferred = True
    if pc.circulo:
        sk.sketchCurves.sketchCircles.addByCenterRadius(_p3(0, 0), pc.circulo * CM)
    else:
        _poligono(sk, pc.contorno)
    for h in pc.furos:
        if h["tipo"] == "circulo":
            sk.sketchCurves.sketchCircles.addByCenterRadius(_p3(h["cx"], h["cy"]), h["r"] * CM)
        elif h["tipo"] == "poligono":
            _poligono(sk, h["pts"])
        else:
            _rasgo(sk, h)
    sk.isComputeDeferred = False
    melhor = None
    maior = -1.0
    for i in range(sk.profiles.count):
        prof = sk.profiles.item(i)
        area = prof.areaProperties().area
        if area > maior:
            maior = area
            melhor = prof
    ext = comp.features.extrudeFeatures.addSimple(
        melhor, adsk.core.ValueInput.createByReal(espessura * CM),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    corpo = ext.bodies.item(0)
    corpo.name = pc.nome
    try:
        corpo.opacity = 0.6
    except Exception:
        pass
    return corpo


def _descricao(comp, texto):
    try:
        comp.description = texto
    except Exception:
        pass


def _referencias(comp, p):
    tbm = adsk.fusion.TemporaryBRepManager.get()
    base = comp.features.baseFeatures.add()
    base.startEdit()
    try:
        for nome, tipo, d in referencias(p):
            if tipo == "caixa":
                x0, y0, z0, dx, dy, dz = d
                obb = adsk.core.OrientedBoundingBox3D.create(
                    _p3(x0 + dx / 2.0, y0 + dy / 2.0, z0 + dz / 2.0),
                    adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                    dx * CM, dy * CM, dz * CM)
                corpo_tmp = tbm.createBox(obb)
            else:
                cx, cy, z0, diam, h = d
                corpo_tmp = tbm.createCylinderOrCone(_p3(cx, cy, z0), diam / 2.0 * CM,
                                                     _p3(cx, cy, z0 + h), diam / 2.0 * CM)
            corpo = comp.bRepBodies.add(corpo_tmp, base)
            corpo.name = nome
    finally:
        base.finishEdit()


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        try:
            design.fusionUnitsManager.distanceDisplayUnits = \
                adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        except Exception:
            pass
        root = design.rootComponent
        p = PARAMETROS
        pecas = gerar_pecas(p)

        ident = adsk.core.Matrix3D.create()
        occ_acr = root.occurrences.addNewComponent(ident)
        acr = occ_acr.component
        acr.name = "Acrilico_cortar"

        prog = ui.createProgressDialog()
        prog.isCancelButtonShown = False
        prog.show("Caixa da estação", "Desenhando %v de %m peças...", 0, len(pecas) + 1)
        for k, pc in enumerate(pecas):
            mats = [_matriz(pos) for pos in pc.posicoes]
            occ = acr.occurrences.addNewComponent(mats[0])
            comp = occ.component
            comp.name = pc.nome
            _descricao(comp, pc.descricao)
            _desenha_peca(comp, pc, p["espessura"])
            for m in mats[1:]:
                acr.occurrences.addExistingComponent(comp, m)
            prog.progressValue = k + 1
            adsk.doEvents()

        occ_ref = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        ref = occ_ref.component
        ref.name = "Referencias_nao_cortar"
        _referencias(ref, p)
        prog.progressValue = len(pecas) + 1
        prog.hide()

        app.activeViewport.fit()
        ui.messageBox(
            "Caixa criada!\n\n"
            "- Componente 'Acrilico_cortar': as peças de acrílico (cada uma tem o esboço "
            "'corte_...' — clique com o botão direito nele > Save As DXF para mandar pro laser).\n"
            "- Componente 'Referencias_nao_cortar': Arduino, LCD, bateria etc. só para conferir.\n\n"
            "Para mudar medidas, edite PARAMETROS no começo do script e rode de novo.")
    except Exception:
        if ui:
            ui.messageBox("Deu erro ao gerar a caixa:\n{}".format(traceback.format_exc()))
