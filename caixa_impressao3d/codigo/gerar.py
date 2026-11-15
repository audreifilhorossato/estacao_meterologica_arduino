# -*- coding: utf-8 -*-
"""
Gera tudo da caixa impressa em 3D a partir do caixa3d.py:

  imprimir/corpo.stl                         (já na posição de imprimir)
  imprimir/tampa.stl
  fusion/caixa_montada.step                  (corpo, tampa e componentes de referência)
  fusion/corpo.step, fusion/tampa.step       (cada peça sozinha)
  fotos/*.png                                (imagens de conferência)

e confere: peças válidas, nada batendo em nada, caminho do plugue USB, parafusos, se a
porca da tampa sobe por baixo e trava no topo, altura livre em cima do shield, formato
das camadas no teto do sextavado e o que a impressora vai ter que fazer de ponte.

Uso:  python gerar.py [pasta_de_saida]
      sem pasta, ele grava em cima da própria pasta da caixa (a que tem o LEIA-ME)
Precisa de: pip install cadquery   (o VTK vem junto)
"""
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import caixa3d as C   # noqa: E402
from caixa3d import P, caixa, cilindro, cor   # noqa: E402

BRANCO = (0.93, 0.93, 0.9)
FUNDO = (0.86, 0.89, 0.93)      # fundo azulado das imagens de detalhe
LATAO = (0.85, 0.6, 0.15)       # porca em destaque


def volume_comum(a, b):
    return a.intersect(b).Volume()


# ---------------------------------------------------------------------------
# conferências
# ---------------------------------------------------------------------------
def conferir(corpo, tampa, refs, p=P):
    L, H = p["comprimento"], p["altura"]
    w, tt = p["parede"], p["tampa"]
    c_s, t_s = corpo.val(), tampa.val()
    n = 0
    print("== Interferências (> 0.01 mm³) ==")
    pares = [("corpo", c_s), ("tampa", t_s)]
    for nome, s in pares:
        for rn, rw in refs:
            v = volume_comum(s, rw.val())
            if v > 0.01:
                n += 1
                print("  %s x %s: %.2f" % (nome, rn, v))
    v = volume_comum(c_s, t_s)
    if v > 0.01:
        n += 1
        print("  corpo x tampa: %.2f" % v)
    if n == 0:
        print("  nenhuma")

    # caminho do plugue USB: a capa do plugue tem que passar pelo furo da parede
    # e ir reto até a boca do conector do Arduino, sem bater em nada
    print("== Caminhos dos plugues ==")
    yu, zu = C.centro_usb(p)
    xb = C.boca_usb_x(p)
    cw, ch = p["usb_capa"]
    caminhos = {
        "USB (capa %.0fx%.0f, de fora até o Arduino)" % (cw, ch):
            caixa(xb + 1.0, yu - cw / 2, zu - ch / 2, L + w + 10 - xb, cw, ch).val(),
        "P4 (por dentro)": caixa(74.0, 60.5, 7, L - 74.0, 9.5, 11).val(),
    }
    outros = [(rn, rw.val()) for rn, rw in refs
              if not rn.startswith(("Arduino", "Parafuso_Arduino", "Porca_Arduino", "Shield",
                                    "Cabo_USB"))]
    for cn, cam in caminhos.items():
        bloq = []
        for nome, s in pares + outros:
            if volume_comum(s, cam) > 0.01:
                bloq.append(nome)
        if bloq:
            n += 1
            print("  %s: BLOQUEADO por %s" % (cn, ", ".join(bloq)))
        else:
            print("  %s: livre" % cn)
    # folga do furo do USB em volta da capa do plugue
    print("  furo do USB: %.1f x %.1f mm, centro em y=%.2f z=%.2f (capa %.0f x %.0f: "
          "folga de %.2f mm de cada lado)" % (p["usb_larg"], p["usb_alt"], yu, zu, cw, ch,
                                             min(p["usb_larg"] - cw, p["usb_alt"] - ch) / 2))

    # parafusos da tampa: de M3 x 10 a x 20 têm que entrar sem bater em nada e pegar a
    # porca inteira (a porca de 5,5 trava no trecho que afina, um pouco abaixo do teto)
    print("== Parafusos da tampa ==")
    apoio = H + tt - p["rebaixo_prof"]
    zt, zp = C.alojamento_porca_z(p)
    zn = C.porca_topo_z(p)
    outros_refs = [(rn, rw.val()) for rn, rw in refs
                   if not rn.startswith(("Parafuso_tampa", "Porca_tampa"))]
    for comp in (10, 12, 16, 20):
        bate = []
        for x, y in C.centros_colunas(p):
            haste = cilindro(x, y, apoio - comp, 3.0, comp).val()
            if volume_comum(c_s, haste) > 0.01:
                bate.append("corpo")
            for rn, s in outros_refs:
                if volume_comum(s, haste) > 0.01:
                    bate.append(rn)
        rosca = min(2.4, max(0.0, zn - (apoio - comp)))
        print("  M3 x %d: ponta em z=%.1f, %s, pega %.1f mm da porca de 2,4" % (
            comp, apoio - comp, "entra livre" if not bate else "BATE em " + ", ".join(bate),
            rosca))
        if bate or rosca < 2.4:
            n += 1

    # porca da tampa: tem que subir livre por baixo da coluna e travar no trecho que
    # afina. Testa uma porca de 5,5 x 2,4 em várias alturas na coluna da frente-esquerda.
    print("== Porca da tampa: entra por baixo da coluna ==")
    c = p["coluna"] / 2
    s_col = p["coluna"]
    zb = zp - s_col
    perto = c_s.intersect(caixa(-w - 1, -w - 1, zb - 15, s_col + 15, s_col + 15,
                                H + 1 - (zb - 15)).val())

    def bate_porca(z_topo, af=5.5):
        return volume_comum(perto, C.hexagono(c, c, z_topo - 2.4, af, 2.4).val())

    alturas = [zb - 6 + k for k in range(int(zt - p["porca_afina"] - (zb - 6)) + 1)]
    presas = [z for z in alturas if bate_porca(z) > 0.001]
    if presas:
        n += 1
        print("  BATE subindo, com o topo da porca em z=%s" % ", ".join("%.1f" % z for z in presas))
    else:
        print("  sobe livre desde embaixo da coluna (topo em z=%.1f) até z=%.1f" % (
            alturas[0], alturas[-1]))
    lo, hi = zt - p["porca_afina"], zt
    for _ in range(14):
        meio = (lo + hi) / 2
        if bate_porca(meio) > 0.001:
            hi = meio
        else:
            lo = meio
    print("  trava com o topo em z=%.2f (%.2f mm abaixo do teto; previsto %.2f)" % (
        lo, zt - lo, zt - zn))
    for af in (5.32, 5.4, 5.5):
        print("  porca de %.2f entre faces: no teto ela aperta %.3f mm³ de plástico" % (
            af, bate_porca(zt - 0.01, af)))
    if abs(lo - zn) > 0.05:
        n += 1
        print("  ATENÇÃO: travou fora do previsto")

    # formato das camadas no teto do sextavado (pontes em degrau)
    print("== Camadas no teto do sextavado (coluna da frente-esquerda) ==")
    tf = p["fundo"]
    for dz, nome in ((-0.1, "última camada do sextavado (já afinado)"),
                     (0.1, "1ª camada do teto (rasgo)"),
                     (0.3, "2ª camada (quadrado)"),
                     (0.5, "3ª camada (furo redondo)")):
        z = zt + dz
        fatia = caixa(c - 4.5, c - 4.5, z - 0.005, 9.0, 9.0, 0.01).val()
        vazio = 81.0 - volume_comum(c_s, fatia) / 0.01
        print("  z=%.1f (Z de impressão %.1f): vazio de %.1f mm² - %s" % (z, z + tf, vazio, nome))

    # altura livre em cima do shield (grade)
    ax0, ay0 = C.origem_arduino(p)
    zs = p["pe_arduino_alt"] + C.PCB + p["shield_altura"] + C.PCB
    obst = [c_s, t_s] + [rw.val() for rn, rw in refs
                         if rn.startswith(("LCD", "Botao", "LED", "LDR", "Parafuso_tampa",
                                           "Parafuso_LCD", "Porca", "Chave"))]
    folgas = []
    for gx in range(4, 68, 4):
        for gy in range(4, 52, 4):
            x, y = ax0 + gx, ay0 + gy
            haste = cq.Workplane("XY").rect(1, 1).extrude(60).translate((x, y, zs)).val()
            zmin = H + tt
            for o in obst:
                i = haste.intersect(o)
                if i.Volume() > 1e-6:
                    zmin = min(zmin, i.BoundingBox().zmin)
            folgas.append((zmin - zs, x, y))
    folgas.sort()
    print("== Altura livre em cima do shield (topo da placa em z=%.1f) ==" % zs)
    print("  mínima %.1f mm em (%.0f, %.0f); máxima %.1f mm" % (
        folgas[0][0], folgas[0][1], folgas[0][2], folgas[-1][0]))
    for lim in (15, 20, 25, 30, 35):
        print("  >= %d mm em %d%% da área" % (
            lim, 100 * sum(1 for f in folgas if f[0] >= lim) / len(folgas)))
    baixas = [f for f in folgas if f[0] < 20]
    if baixas:
        xs = [f[1] for f in baixas]
        ys = [f[2] for f in baixas]
        print("  menos de 20 mm só em x %.0f..%.0f, y %.0f..%.0f" % (min(xs), max(xs), min(ys), max(ys)))
    return n


def pontes(solido, nome):
    """Faces planas viradas pra baixo (na posição de impressão), fora da mesa."""
    print("== %s: tetos/pontes que a impressora faz sem suporte ==" % nome)
    lst = []
    for f in solido.Faces():
        if f.geomType() != "PLANE":
            continue
        nz = f.normalAt().z
        bb = f.BoundingBox()
        if nz < -0.99 and bb.zmin > 0.05:
            lst.append((round(bb.zmin, 2), bb.xlen, bb.ylen, f.Area()))
    lst.sort()
    grupos = {}
    for z, dx, dy, a in lst:
        g = grupos.setdefault(z, [])
        g.append((min(dx, dy), max(dx, dy), a))
    for z, g in sorted(grupos.items()):
        vao = max(v[0] for v in g)
        print("  Z=%6.2f: %2d face(s), maior vão %.1f mm (lado maior %.1f), área %.0f mm²" % (
            z, len(g), vao, max(v[1] for v in g), sum(v[2] for v in g)))


# ---------------------------------------------------------------------------
# imagens
# ---------------------------------------------------------------------------
def imagens(saida, corpo, tampa, refs, p=P):
    import render
    L, W, H = p["comprimento"], p["profundidade"], p["altura"]
    w, tt = p["parede"], p["tampa"]
    c_s, t_s = corpo.val(), tampa.val()
    pasta = os.path.join(saida, "fotos")

    def grupo(*prefixos):
        return [(rn, rw.val()) for rn, rw in refs if rn.startswith(prefixos)]

    na_tampa = ("LCD", "Botao", "LED", "LDR", "Parafuso_tampa", "Parafuso_LCD", "Porca_LCD")

    # 1) montada, vista da frente-direita (USB, ventilação e chave)
    objs = [(c_s, BRANCO, 1.0, True), (t_s, BRANCO, 1.0, True)]
    for rn, s in grupo("Chave", "LCD_moldura", "Botao", "LED", "LDR"):
        objs.append((s, cor(rn), 1.0, False))
    render.render(objs, os.path.join(pasta, "montada.png"),
                  ((L / 2 + 250, W / 2 - 290, H / 2 + 220), (L / 2, W / 2, H / 2), (0, 0, 1)),
                  titulo="Caixa montada: furo do USB, ventilacao e chave na lateral direita")

    # 2) lateral direita reta, com nomes
    objs = [(c_s, BRANCO, 1.0, True), (t_s, BRANCO, 1.0, True)]
    for rn, s in grupo("Chave", "Arduino_USB", "Arduino_placa", "Shield", "Bateria"):
        objs.append((s, cor(rn), 1.0, False))
    yu, zu = C.centro_usb(p)
    xr = L + w + 2
    rot = [("Chave liga/desliga", (xr, p["chave_y"] + p["chave_furo_y"] / 2 + 3, p["chave_z"])),
           ("Ventilação (3 rasgos)", (xr, p["vent_y"] + p["vent_comp"] / 2 + 3, p["vent_z"][1])),
           ("USB (conector do Arduino)", (xr, yu + p["usb_larg"] / 2 + 3, zu))]
    render.render(objs, os.path.join(pasta, "lateral_direita.png"),
                  ((L + 400, W / 2, H / 2), (L, W / 2, H / 2), (0, 0, 1)), tamanho=(1500, 1000),
                  titulo="Lateral direita (vista de fora)", paralela=True, zoom=1.25,
                  fundo=(0.86, 0.89, 0.93), rotulos=rot)

    # 3) explodida (corpo transparente)
    sobe = cq.Location(cq.Vector(0, 0, 50))
    objs = [(c_s, BRANCO, 0.35, True), (t_s.moved(sobe), BRANCO, 0.6, True)]
    for rn, rw in refs:
        s = rw.val()
        if rn.startswith(na_tampa):
            s = s.moved(sobe)
        objs.append((s, cor(rn), 0.55 if rn.startswith("Shield") else 1.0, False))
    render.render(objs, os.path.join(pasta, "explodida.png"),
                  ((L / 2 + 270, W / 2 - 330, H / 2 + 300), (L / 2, W / 2, H / 2 + 20), (0, 0, 1)),
                  titulo="Vista explodida (corpo transparente para ver dentro)")

    # 4) interior visto de cima, com o cabo USB plugado
    objs = [(c_s, BRANCO, 1.0, True)]
    for rn, rw in refs:
        if rn.startswith(na_tampa):
            continue
        objs.append((rw.val(), cor(rn), 0.55 if rn.startswith("Shield") else 1.0, False))
    render.render(objs, os.path.join(pasta, "interior.png"),
                  ((L / 2 + 30, W / 2 - 80, H + 400), (L / 2 + 8, W / 2, H / 3), (0, 1, 0)),
                  titulo="Por dentro: Arduino com shield, bateria na frente e cabo USB plugado")

    # 5) fundo por baixo
    render.render([(c_s, BRANCO, 1.0, True)], os.path.join(pasta, "corpo_por_baixo.png"),
                  ((L / 2 - 150, W / 2 - 250, -300), (L / 2, W / 2, 0), (0, 0, 1)),
                  titulo="Fundo por baixo: rebaixos dos parafusos do Arduino")

    # 6) tampa por baixo
    render.render([(t_s, BRANCO, 1.0, True)], os.path.join(pasta, "tampa_por_baixo.png"),
                  ((L / 2 + 60, W / 2 - 200, H - 300), (L / 2, W / 2, H), (0, 0, 1)),
                  titulo="Tampa por baixo: aba de encaixe e pes do LCD")

    # 7) tampa de cima
    objs = [(t_s, BRANCO, 1.0, True)]
    for rn, s in grupo("LCD_moldura", "Botao", "LED", "LDR", "Parafuso_tampa", "Parafuso_LCD"):
        objs.append((s, cor(rn), 1.0, False))
    render.render(objs, os.path.join(pasta, "tampa_de_cima.png"),
                  ((L / 2, W / 2 - 120, H + 400), (L / 2, W / 2, H), (0, 1, 0)),
                  titulo="Tampa de cima: LED, botao, LDR, LCD e parafusos escondidos")

    # 8) corte pela coluna da frente-esquerda (só o pedaço em volta dela)
    c = p["coluna"] / 2
    zt, zp = C.alojamento_porca_z(p)
    zb = zp - p["coluna"]
    zn = C.porca_topo_z(p)
    z_baixo = zb - 3
    # sem a parede da frente, pra coluna aparecer contra o fundo
    pedaco = caixa(-w - 1, 0.0, z_baixo, p["coluna"] + 14, c, H + tt + 2 - z_baixo).val()
    objs = [(c_s.intersect(pedaco), BRANCO, 1.0, True), (t_s.intersect(pedaco), BRANCO, 1.0, True)]
    for rn, rw in refs:
        if rn.startswith(("Parafuso_tampa_1", "Porca_tampa_1")):
            s = rw.val().intersect(pedaco)
            if s.Volume() > 0:
                objs.append((s, LATAO if rn.startswith("Porca") else cor(rn), 1.0, False))
    xr = p["coluna"] + 2.5
    yr = c + 4
    rot = [("tampa", (xr, yr, H + tt / 2)),
           ("parafuso M3 x 10", (xr, yr, H - 2.0)),
           ("porca M3: fica justa aqui", (xr, yr, zn - 1.2)),
           ("sextavado aberto embaixo", (xr, yr, zp - 4.5)),
           ("coluna 12 x 12 mm", (xr, yr, zb + 2.5))]
    render.render(objs, os.path.join(pasta, "corte_coluna.png"),
                  ((c + 45, c + 160, H + 30), (c + 6, c, zp), (0, 0, 1)), tamanho=(1400, 1000),
                  titulo="Corte na coluna: a porca entra por baixo e o parafuso puxa ela pra cima",
                  zoom=1.0, fundo=FUNDO, rotulos=rot)

    # 9) onde colocar a porca: canto da frente-esquerda visto por dentro, de baixo
    canto = caixa(-w - 1, -w - 1, zb - 14, 23, 23, H + 1 - (zb - 14)).val()
    objs = [(c_s.intersect(canto), BRANCO, 1.0, True),
            (C.hexagono(c, c, zb - 10, 5.5, 2.4).val(), LATAO, 1.0, False)]
    rot = [("sextavado aberto", (c + 9, c + 9, zp - 5)),
           ("porca M3: empurre pra cima", (c + 6, c + 6, zb - 9))]
    render.render(objs, os.path.join(pasta, "colocar_porcas.png"),
                  ((c + 150, c + 120, zb - 95), (c, c, zp - 6), (0, 0, 1)), tamanho=(1400, 1000),
                  titulo="Embaixo de cada coluna, por dentro: a porca sobe pelo sextavado",
                  zoom=1.0, fundo=FUNDO, rotulos=rot)

    # 10) corte no eixo do USB
    yu, zu = C.centro_usb(p)
    faca = caixa(-20, -20, -20, L + 60, yu + 20, H + 40).val()
    objs = [(c_s.cut(faca), BRANCO, 1.0, True)]
    for rn, rw in refs:
        if rn.startswith(("Arduino", "Shield", "Cabo_USB")):
            s = rw.val().cut(faca)
            if s.Volume() > 0:
                objs.append((s, cor(rn), 0.55 if rn.startswith("Shield") else 1.0, False))
    render.render(objs, os.path.join(pasta, "corte_usb.png"),
                  ((L / 2 + 40, yu - 260, zu + 90), (L / 2 + 20, yu, zu + 8), (0, 0, 1)),
                  tamanho=(1500, 1000), zoom=1.6,
                  titulo="Corte no USB: o plugue passa pelo furo e vai reto ate o Arduino")


# ---------------------------------------------------------------------------
def main(saida):
    for d in ("imprimir", "fusion", "fotos"):
        os.makedirs(os.path.join(saida, d), exist_ok=True)
    p = P
    corpo = C.fazer_corpo(p)
    tampa = C.fazer_tampa(p)
    refs = C.referencias(p)
    c_s, t_s = corpo.val(), tampa.val()
    for nome, s, wp in (("corpo", c_s, corpo), ("tampa", t_s, tampa)):
        bb = s.BoundingBox()
        print("%s: válido=%s, %d sólido(s), %.1f cm³, %.1f x %.1f x %.1f mm" % (
            nome, s.isValid(), len(wp.solids().vals()), s.Volume() / 1000, bb.xlen, bb.ylen, bb.zlen))

    n = conferir(corpo, tampa, refs, p)

    # STEP montado (corpo, tampa e referências em grupos)
    assy = cq.Assembly(name="caixa_estacao_3d")
    assy.add(corpo, name="corpo", color=cq.Color(*BRANCO))
    assy.add(tampa, name="tampa", color=cq.Color(*BRANCO))
    comp = cq.Assembly(name="componentes_nao_imprimir")
    fix = cq.Assembly(name="parafusos_e_porcas")
    for rn, rw in refs:
        alvo = fix if rn.startswith(("Parafuso", "Porca")) else comp
        k = cor(rn)
        alvo.add(rw, name=rn, color=cq.Color(k[0], k[1], k[2]))
    assy.add(comp)
    assy.add(fix)
    assy.export(os.path.join(saida, "fusion", "caixa_montada.step"))
    cq.exporters.export(corpo, os.path.join(saida, "fusion", "corpo.step"))
    cq.exporters.export(tampa, os.path.join(saida, "fusion", "tampa.step"))

    # STL na posição de impressão
    H, W, tt, tf = p["altura"], p["profundidade"], p["tampa"], p["fundo"]
    nome_corpo = "corpo.stl"
    corpo_imp = corpo.translate((0, 0, tf))
    tampa_imp = tampa.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, W, H + tt))
    cq.exporters.export(corpo_imp, os.path.join(saida, "imprimir", nome_corpo),
                        tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(tampa_imp, os.path.join(saida, "imprimir", "tampa.stl"),
                        tolerance=0.02, angularTolerance=0.1)
    print("STL: %s zmin=%.2f  tampa.stl zmin=%.2f (devem ser 0)" % (
        nome_corpo, corpo_imp.val().BoundingBox().zmin, tampa_imp.val().BoundingBox().zmin))
    pontes(corpo_imp.val(), "corpo")
    pontes(tampa_imp.val(), "tampa")

    imagens(saida, corpo, tampa, refs, p)
    print("== Problemas: %d ==" % n)
    return n


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(AQUI))
