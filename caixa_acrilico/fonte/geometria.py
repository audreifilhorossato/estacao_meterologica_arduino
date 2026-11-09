# -*- coding: utf-8 -*-
"""
Geometria paramétrica da caixa de acrílico da Estação Meteorológica.

Tudo em milímetros. Python puro (sem bibliotecas), para o mesmo código rodar
no gerador de STEP/DXF e dentro do script do Fusion 360.

Sistema de coordenadas (visto de cima, com o LCD na tampa de frente pra você):
    X = da esquerda para a direita     (0 = face interna da parede esquerda)
    Y = da frente para trás            (0 = face interna da parede da frente)
    Z = de baixo para cima             (0 = face de cima do fundo)
"""
import math

# ---------------------------------------------------------------------------
# PARÂMETROS - mude aqui e gere de novo
# ---------------------------------------------------------------------------
PARAMETROS = {
    # Chapa de acrílico
    "espessura": 3.0,           # meça a chapa com paquímetro (3 mm costuma variar 2,8-3,2)
    "folga_encaixe": 0.2,       # folga total dos rasgos onde as abas entram

    # Caixa: medidas INTERNAS
    "comprimento": 110.0,       # X
    "profundidade": 76.0,       # Y
    "altura": 58.0,             # Z (entre o fundo e a tampa)
    "aba_externa": 4.0,         # quanto fundo e tampa sobram para fora das paredes
    "raio_canto": 3.0,          # cantos arredondados do fundo e da tampa
    "segmentos_canto": 5,       # dedos nos cantos verticais (número ímpar)
    "comprimento_aba": 14.0,    # abas das paredes que entram no fundo e na tampa

    # Parafusos M3 com porca presa em rasgo T na borda das paredes
    "furo_m3": 3.2,
    "parafuso_comp": 12.0,      # comprimento do parafuso dos rasgos T (M3 x 12)
    "porca_largura": 5.6,       # porca M3 = 5,5 mm entre faces
    "porca_espessura": 2.5,     # porca M3 = 2,4 mm
    "porca_distancia": 3.5,     # da borda da parede até a porca

    # Arduino Uno R3 no fundo, atrás à esquerda (girado 180°: USB virado pro meio)
    "arduino_x": 3.0,           # folga até a parede esquerda
    "arduino_folga_tras": 3.0,  # folga até a parede de trás
    "arduino_arruelas": 2,      # arruelas de acrílico empilhadas em cada pé (2 x 3 mm = 6 mm)
    "arruela_diam": 7.0,        # diâmetro externo das arruelas espaçadoras

    # LCD 16x2 com módulo I2C, preso por baixo da tampa (1 arruela de 3 mm por furo)
    "lcd_centro_x": 67.0,
    "lcd_centro_y": 38.0,
    "lcd_placa_x": 80.0, "lcd_placa_y": 36.0,
    "lcd_furos_x": 75.0, "lcd_furos_y": 31.0,
    "lcd_janela_x": 72.0, "lcd_janela_y": 25.0,   # moldura metálica 71 x 24 + folga

    # Controles na tampa (coluna da esquerda, ao lado do LCD)
    "controles_x": 13.0,
    "led_y": 15.0,
    "botao_y": 38.0,
    "ldr_y": 62.0,
    "furo_led": 5.1,            # LED 5 mm (a aba de 5,8 mm segura por baixo)
    "furo_ldr": 5.3,            # LDR 5 mm
    "botao_furo": 6.3,          # furo quadrado para o corpo do botão 6x6
    "botao_pernas_x": 6.5,      # distância entre as fileiras de pernas do botão 6x6
    "botao_pernas_y": 4.5,
    "suporte_botao_x": 28.0, "suporte_botao_y": 14.0,
    "suporte_botao_furos": 20.0,
    "suporte_botao_girado": True,   # plaquinha em pé (comprida no sentido Y)

    # Chave liga/desliga (mini gangorra KCD11) na parede direita
    "chave": True,
    "chave_furo_y": 13.5, "chave_furo_z": 8.5,
    "chave_y": 50.0, "chave_z": 38.0,

    # Bateria 9 V em pé no canto de trás, à direita
    "bateria_x": 26.5, "bateria_y": 17.5, "bateria_z": 48.5,
    "bateria_folga": 1.0,
    "divisoria_altura": 30.0,

    # Ventilação: poucos rasgos só nas paredes da esquerda e da direita,
    # na frente, onde ficam os sensores
    "vent_paredes": ["esquerda", "direita"],
    "vent_largura": 3.0,
    "vent_comp": 18.0,
    "vent_espaco": 6.0,
    "vent_passo": 7.0,
    "vent_y_min": 4.0, "vent_y_max": 28.0,
    "vent_z_min": 17.0, "vent_z_max": 38.0,

    # Ventilação na tampa (desligada)
    "tampa_ventilacao": False,
    "tampa_vent_comp": 18.0,
    "tampa_vent_passo": 8.0,

    # Pés (discos de acrílico colados embaixo, cobrem as cabeças dos parafusos)
    "pe_diam": 10.0,
    "pe_camadas": 2,
}

# Arduino Uno R3: placa e furos (origem no canto do lado do USB/plug P4)
UNO_PLACA = (68.58, 53.34)
UNO_FUROS = [(13.97, 2.54), (15.24, 50.80), (66.04, 7.62), (66.04, 35.56)]


# ---------------------------------------------------------------------------
# Utilidades 2D
# ---------------------------------------------------------------------------
def _limpa(pts, tol=1e-6):
    """Remove pontos repetidos e pontos no meio de retas."""
    out = []
    for p in pts:
        if out and abs(p[0] - out[-1][0]) < tol and abs(p[1] - out[-1][1]) < tol:
            continue
        out.append((round(p[0], 4), round(p[1], 4)))
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < tol and abs(out[0][1] - out[-1][1]) < tol:
        out.pop()
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if abs(cross) < tol:
                out.pop(i)
                changed = True
                break
    return out


def retangulo_arredondado(cx, cy, w, h, r, n=8):
    if r <= 0:
        return retangulo(cx, cy, w, h)
    pts = []
    cantos = [(cx + w / 2 - r, cy - h / 2 + r, -90), (cx + w / 2 - r, cy + h / 2 - r, 0),
              (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180)]
    for ox, oy, a0 in cantos:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def retangulo(cx, cy, w, h):
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
            (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


def furo_circulo(cx, cy, d):
    return {"tipo": "circulo", "cx": cx, "cy": cy, "r": d / 2.0}


def furo_poligono(pts):
    return {"tipo": "poligono", "pts": _limpa(pts)}


def furo_rasgo(cx, cy, comp, larg, vertical=False):
    """Rasgo oblongo (ponta redonda). comp = comprimento total."""
    return {"tipo": "rasgo", "cx": cx, "cy": cy, "comp": comp, "larg": larg,
            "vertical": vertical}


def grade_rasgos(u0, u1, v0, v1, comp, larg, espaco, passo, vertical=False):
    """Preenche a caixa [u0,u1]x[v0,v1] com rasgos, centralizados."""
    furos = []
    if not vertical:
        n_u = int((u1 - u0 + espaco) // (comp + espaco))
        n_v = int((v1 - v0 - larg) // passo) + 1
        if n_u < 1 or n_v < 1:
            return furos
        tot_u = n_u * comp + (n_u - 1) * espaco
        u_ini = (u0 + u1) / 2 - tot_u / 2 + comp / 2
        v_ini = (v0 + v1) / 2 - (n_v - 1) * passo / 2
        for i in range(n_u):
            for j in range(n_v):
                furos.append(furo_rasgo(u_ini + i * (comp + espaco), v_ini + j * passo, comp, larg))
    else:
        n_u = int((u1 - u0 - larg) // passo) + 1
        n_v = int((v1 - v0 + espaco) // (comp + espaco))
        if n_u < 1 or n_v < 1:
            return furos
        u_ini = (u0 + u1) / 2 - (n_u - 1) * passo / 2
        tot_v = n_v * comp + (n_v - 1) * espaco
        v_ini = (v0 + v1) / 2 - tot_v / 2 + comp / 2
        for i in range(n_u):
            for j in range(n_v):
                furos.append(furo_rasgo(u_ini + i * passo, v_ini + j * (comp + espaco), comp, larg, True))
    return furos


def posicoes_abas(comp_parede, n):
    return [comp_parede * (i + 0.5) / n for i in range(n)]


def posicoes_tslots(abas):
    return [(abas[i] + abas[i + 1]) / 2 for i in range(len(abas) - 1)]


def n_abas(comp_parede):
    return max(2, int(round(comp_parede / 40.0)))


# ---------------------------------------------------------------------------
# Peças
# ---------------------------------------------------------------------------
class Peca(object):
    """Uma peça plana: contorno + furos no plano (u, v); espessura em +w.

    posicoes: lista de (origem, eixo_u, eixo_v, eixo_w) que levam a peça
    para o lugar dela na caixa montada.
    """

    def __init__(self, nome, contorno, furos, posicoes, descricao="", circulo=None):
        self.nome = nome
        self.circulo = circulo          # raio, quando o contorno é um círculo (centro 0,0)
        self.contorno = _limpa(contorno)
        self.furos = furos
        self.posicoes = posicoes
        self.descricao = descricao

    @property
    def quantidade(self):
        return len(self.posicoes)

    def limites(self):
        xs = [p[0] for p in self.contorno]
        ys = [p[1] for p in self.contorno]
        return min(xs), min(ys), max(xs), max(ys)


EIXOS_XY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
EIXOS_FRENTE = ((1, 0, 0), (0, 0, 1), (0, -1, 0))   # u->X, v->Z, w->-Y
EIXOS_LADO = ((0, 1, 0), (0, 0, 1), (1, 0, 0))      # u->Y, v->Z, w->+X
EIXOS_GIRADO = ((0, 1, 0), (-1, 0, 0), (0, 0, 1))   # deitada, girada 90° (u->Y)


def _tslot(c, v0, sentido, p):
    """Rasgo em T na borda (parafuso entra pela borda, porca presa no T)."""
    t = p["espessura"]
    ws = p["furo_m3"]
    nw = p["porca_largura"]
    nt = p["porca_espessura"]
    d = p["porca_distancia"]
    sl = p["parafuso_comp"] - t + 1.0
    seq = [(-ws / 2, 0), (-ws / 2, d), (-nw / 2, d), (-nw / 2, d + nt), (-ws / 2, d + nt),
           (-ws / 2, sl), (ws / 2, sl), (ws / 2, d + nt), (nw / 2, d + nt), (nw / 2, d),
           (ws / 2, d), (ws / 2, 0)]
    if sentido > 0:
        return [(c + du, v0 + dv) for du, dv in seq]
    return [(c - du, v0 - dv) for du, dv in seq]


def contorno_parede(comp_parede, p, dedos_nos_pares, abas, tslots):
    """Parede com dedos nos cantos, abas em cima/embaixo e rasgos T."""
    t = p["espessura"]
    H = p["altura"]
    n = int(p["segmentos_canto"])
    a = p["comprimento_aba"]
    seg = H / n

    def dedo(k):
        return (k % 2 == 0) == dedos_nos_pares

    feats = sorted([(c, "aba") for c in abas] + [(c, "t") for c in tslots])
    pts = []
    # borda de baixo, esquerda -> direita
    pts.append((-t if dedo(0) else 0.0, 0.0))
    for c, k in feats:
        if k == "aba":
            pts += [(c - a / 2, 0), (c - a / 2, -t), (c + a / 2, -t), (c + a / 2, 0)]
        else:
            pts += _tslot(c, 0.0, +1, p)
    # lado direito, subindo
    for k in range(n):
        x = comp_parede + t if dedo(k) else comp_parede
        pts += [(x, k * seg), (x, (k + 1) * seg)]
    # borda de cima, direita -> esquerda
    for c, k in reversed(feats):
        if k == "aba":
            pts += [(c + a / 2, H), (c + a / 2, H + t), (c - a / 2, H + t), (c - a / 2, H)]
        else:
            pts += _tslot(c, H, -1, p)
    # lado esquerdo, descendo
    for k in reversed(range(n)):
        x = -t if dedo(k) else 0.0
        pts += [(x, (k + 1) * seg), (x, k * seg)]
    return pts


def contorno_divisoria(comp, altura, p, abas):
    t = p["espessura"]
    a = min(8.0, comp / 3.0)
    pts = [(0, 0)]
    for c in abas:
        pts += [(c - a / 2, 0), (c - a / 2, -t), (c + a / 2, -t), (c + a / 2, 0)]
    pts += [(comp, 0), (comp, altura), (0, altura)]
    return pts, a


def arduino_furos_caixa(p):
    """Furos do Uno no sistema da caixa (placa girada 180°)."""
    W = p["profundidade"]
    bx, by = UNO_PLACA
    x0 = p["arduino_x"]
    y0 = W - p["arduino_folga_tras"] - by
    return [(x0 + bx - hx, y0 + by - hy) for hx, hy in UNO_FUROS], (x0, y0)


def bolso_bateria(p):
    L, W, t = p["comprimento"], p["profundidade"], p["espessura"]
    f = p["bateria_folga"]
    xb = L - p["bateria_x"] - f        # face interna da divisória lateral
    yb = W - p["bateria_y"] - f        # face interna da divisória da frente
    return xb, yb


def lcd_furos(p):
    cx, cy = p["lcd_centro_x"], p["lcd_centro_y"]
    hx, hy = p["lcd_furos_x"] / 2, p["lcd_furos_y"] / 2
    return [(cx - hx, cy - hy), (cx + hx, cy - hy), (cx + hx, cy + hy), (cx - hx, cy + hy)]


def gerar_pecas(p=None):
    if p is None:
        p = PARAMETROS
    t = p["espessura"]
    L, W, H = p["comprimento"], p["profundidade"], p["altura"]
    m = p["aba_externa"]
    f = p["folga_encaixe"]
    a = p["comprimento_aba"]

    abas_x = posicoes_abas(L, n_abas(L))
    abas_y = posicoes_abas(W, n_abas(W))
    ts_x = posicoes_tslots(abas_x)
    ts_y = posicoes_tslots(abas_y)

    pecas = []

    # ---------------- paredes ----------------
    vz0, vz1 = p["vent_z_min"], p["vent_z_max"]
    vl, vc, ve, vp = p["vent_largura"], p["vent_comp"], p["vent_espaco"], p["vent_passo"]

    vpar = p["vent_paredes"]
    vy0, vy1 = p["vent_y_min"], p["vent_y_max"]

    def vent(nome, comp_parede):
        if nome not in vpar:
            return []
        if nome in ("esquerda", "direita"):
            return grade_rasgos(vy0, vy1, vz0, vz1, vc, vl, ve, vp)
        return grade_rasgos(10, comp_parede - 10, vz0, vz1, vc, vl, ve, vp)

    frente = contorno_parede(L, p, True, abas_x, ts_x)
    pecas.append(Peca("parede_frente", frente, vent("frente", L),
                      [((0, 0, 0),) + EIXOS_FRENTE],
                      "Parede da frente"))

    tras = contorno_parede(L, p, True, abas_x, ts_x)
    pecas.append(Peca("parede_tras", tras, vent("tras", L),
                      [((0, W + t, 0),) + EIXOS_FRENTE],
                      "Parede de trás"))

    esq = contorno_parede(W, p, False, abas_y, ts_y)
    pecas.append(Peca("parede_esquerda", esq, vent("esquerda", W),
                      [((-t, 0, 0),) + EIXOS_LADO],
                      "Parede esquerda, com ventilação"))

    dir_ = contorno_parede(W, p, False, abas_y, ts_y)
    furos_dir = []
    if p["chave"]:
        furos_dir.append(furo_poligono(retangulo(p["chave_y"], p["chave_z"],
                                                 p["chave_furo_y"], p["chave_furo_z"])))
    furos_dir += vent("direita", W)
    pecas.append(Peca("parede_direita", dir_, furos_dir,
                      [((L, 0, 0),) + EIXOS_LADO],
                      "Parede direita, com chave liga/desliga e ventilação"))

    # ---------------- fundo ----------------
    def furos_borda():
        fs = []
        # rasgos para as abas das paredes
        for c in abas_x:
            fs.append(furo_poligono(retangulo(c, -t / 2, a + f, t + f)))
            fs.append(furo_poligono(retangulo(c, W + t / 2, a + f, t + f)))
        for c in abas_y:
            fs.append(furo_poligono(retangulo(-t / 2, c, t + f, a + f)))
            fs.append(furo_poligono(retangulo(L + t / 2, c, t + f, a + f)))
        # parafusos dos rasgos T
        for c in ts_x:
            fs.append(furo_circulo(c, -t / 2, p["furo_m3"]))
            fs.append(furo_circulo(c, W + t / 2, p["furo_m3"]))
        for c in ts_y:
            fs.append(furo_circulo(-t / 2, c, p["furo_m3"]))
            fs.append(furo_circulo(L + t / 2, c, p["furo_m3"]))
        return fs

    placa = retangulo_arredondado(L / 2, W / 2, L + 2 * t + 2 * m, W + 2 * t + 2 * m,
                                  p["raio_canto"])

    furos_fundo = furos_borda()
    ard, _ = arduino_furos_caixa(p)
    for (x, y) in ard:
        furos_fundo.append(furo_circulo(x, y, p["furo_m3"]))

    # divisórias da bateria
    xb, yb = bolso_bateria(p)
    comp_d1 = L - (xb - t)                 # da divisória lateral até a parede direita
    comp_d2 = W - yb                       # da divisória da frente até a parede de trás
    hd = p["divisoria_altura"]
    abas_d1 = [comp_d1 * 0.25, comp_d1 * 0.75]
    abas_d2 = [comp_d2 * 0.5]
    cont_d1, a_d1 = contorno_divisoria(comp_d1, hd, p, abas_d1)
    cont_d2, a_d2 = contorno_divisoria(comp_d2, hd, p, abas_d2)
    for c in abas_d1:
        furos_fundo.append(furo_poligono(retangulo(xb - t + c, yb - t / 2, a_d1 + f, t + f)))
    for c in abas_d2:
        furos_fundo.append(furo_poligono(retangulo(xb - t / 2, yb + c, t + f, a_d2 + f)))

    pecas.append(Peca("fundo", placa, furos_fundo,
                      [((0, 0, -t),) + EIXOS_XY],
                      "Fundo: furos do Arduino Uno e encaixes da bateria"))

    pecas.append(Peca("divisoria_bateria_frente", cont_d1, [],
                      [((xb - t, yb, 0),) + EIXOS_FRENTE],
                      "Divisória da bateria (frente do bolso)"))
    pecas.append(Peca("divisoria_bateria_lado", cont_d2, [],
                      [((xb - t, yb, 0),) + EIXOS_LADO],
                      "Divisória da bateria (lado do bolso)"))

    # ---------------- tampa ----------------
    furos_tampa = furos_borda()
    cx, cy = p["lcd_centro_x"], p["lcd_centro_y"]
    furos_tampa.append(furo_poligono(retangulo(cx, cy, p["lcd_janela_x"], p["lcd_janela_y"])))
    for (x, y) in lcd_furos(p):
        furos_tampa.append(furo_circulo(x, y, p["furo_m3"]))
    kx = p["controles_x"]
    furos_tampa.append(furo_circulo(kx, p["led_y"], p["furo_led"]))
    furos_tampa.append(furo_circulo(kx, p["ldr_y"], p["furo_ldr"]))
    furos_tampa.append(furo_poligono(retangulo(kx, p["botao_y"], p["botao_furo"], p["botao_furo"])))
    sf = p["suporte_botao_furos"] / 2
    girado = p.get("suporte_botao_girado", False)
    if girado:
        furos_tampa.append(furo_circulo(kx, p["botao_y"] - sf, p["furo_m3"]))
        furos_tampa.append(furo_circulo(kx, p["botao_y"] + sf, p["furo_m3"]))
    else:
        furos_tampa.append(furo_circulo(kx - sf, p["botao_y"], p["furo_m3"]))
        furos_tampa.append(furo_circulo(kx + sf, p["botao_y"], p["furo_m3"]))
    if p.get("tampa_ventilacao", False):
        tv, tp = p["tampa_vent_comp"], p["tampa_vent_passo"]
        yv1 = W - 6.0
        yv0 = yv1 - tv - 0.01
        furos_tampa += grade_rasgos(8, L - 8, yv0, yv1, tv, vl, ve, tp, vertical=True)
    pecas.append(Peca("tampa", placa, furos_tampa,
                      [((0, 0, H),) + EIXOS_XY],
                      "Tampa: LCD, LDR, LED e botão"))

    # ---------------- suporte do botão (embaixo da tampa) ----------------
    sx, sy = p["suporte_botao_x"], p["suporte_botao_y"]
    px_, py_ = p["botao_pernas_x"] / 2, p["botao_pernas_y"] / 2
    furos_sup = [furo_circulo(-sf, 0, p["furo_m3"]), furo_circulo(sf, 0, p["furo_m3"])]
    for sgn in (-1, 1):
        furos_sup.append(furo_poligono(retangulo(sgn * px_, 0, 1.6, 2 * py_ + 2.5)))
    pecas.append(Peca("suporte_botao", retangulo(0, 0, sx, sy), furos_sup,
                      [((kx, p["botao_y"], H - t),) + (EIXOS_GIRADO if girado else EIXOS_XY)],
                      "Plaquinha que segura o botão 6x6 por baixo da tampa"))

    # ---------------- arruelas espaçadoras ----------------
    posi = []
    for (x, y) in ard:
        for k in range(int(p["arduino_arruelas"])):
            posi.append(((x, y, k * t),) + EIXOS_XY)
    for (x, y) in lcd_furos(p):
        posi.append(((x, y, H - t),) + EIXOS_XY)
    d = p["arruela_diam"]
    circ = [(d / 2 * math.cos(2 * math.pi * i / 48), d / 2 * math.sin(2 * math.pi * i / 48))
            for i in range(48)]
    pecas.append(Peca("arruela_espacadora", circ, [furo_circulo(0, 0, p["furo_m3"])], posi,
                      "Espaçadores (passadores) do Arduino e do LCD", circulo=d / 2))

    # ---------------- pés ----------------
    dp = p["pe_diam"]
    circ_pe = [(dp / 2 * math.cos(2 * math.pi * i / 64), dp / 2 * math.sin(2 * math.pi * i / 64))
               for i in range(64)]
    off = -t - m + dp / 2 + 2.0
    cantos = [(off, off), (L - off, off), (L - off, W - off), (off, W - off)]
    posp = []
    for (x, y) in cantos:
        for k in range(int(p["pe_camadas"])):
            posp.append(((x, y, -t - (k + 1) * t),) + EIXOS_XY)
    pecas.append(Peca("pe", circ_pe, [], posp,
                      "Pés colados embaixo do fundo (cobrem as cabeças dos parafusos)",
                      circulo=dp / 2))
    return pecas


# ---------------------------------------------------------------------------
# Componentes de referência (NÃO são cortados; só para conferir encaixe)
# ---------------------------------------------------------------------------
def referencias(p=None):
    """Lista de ('nome', 'caixa', (x0,y0,z0,dx,dy,dz)) ou ('nome','cilindro',(cx,cy,z0,d,h))."""
    if p is None:
        p = PARAMETROS
    t = p["espessura"]
    L, W, H = p["comprimento"], p["profundidade"], p["altura"]
    refs = []

    # Arduino Uno (girado 180°): a borda do USB fica do lado de x maior
    bx, by = UNO_PLACA
    _, (x0, y0) = arduino_furos_caixa(p)
    z0 = int(p["arduino_arruelas"]) * t
    pcb = 1.6

    def uno(ux, uy, dx, dy):
        # converte retângulo no sistema da placa (origem lado USB) para a caixa
        return (x0 + bx - (ux + dx), y0 + by - (uy + dy), dx, dy)

    refs.append(("Arduino_placa", "caixa", (x0, y0, z0, bx, by, pcb)))
    xx, yy, dx, dy = uno(-6.35, 32.0, 16.2, 12.0)
    refs.append(("Arduino_USB", "caixa", (xx, yy, z0 + pcb, dx, dy, 10.9)))
    xx, yy, dx, dy = uno(-1.8, 3.3, 14.2, 9.0)
    refs.append(("Arduino_P4", "caixa", (xx, yy, z0 + pcb, dx, dy, 11.0)))
    xx, yy, dx, dy = uno(17.5, 49.0, 48.5, 2.6)
    refs.append(("Arduino_barra_digital", "caixa", (xx, yy, z0 + pcb, dx, dy, 8.5)))
    xx, yy, dx, dy = uno(27.0, 1.3, 38.0, 2.6)
    refs.append(("Arduino_barra_analog", "caixa", (xx, yy, z0 + pcb, dx, dy, 8.5)))

    # LCD 16x2 + módulo I2C (placa presa 3 mm abaixo da tampa)
    cx, cy = p["lcd_centro_x"], p["lcd_centro_y"]
    lx, ly = p["lcd_placa_x"], p["lcd_placa_y"]
    z_frente = H - t
    refs.append(("LCD_placa", "caixa", (cx - lx / 2, cy - ly / 2, z_frente - pcb, lx, ly, pcb)))
    refs.append(("LCD_moldura", "caixa", (cx - 71.2 / 2, cy - 24.2 / 2, z_frente, 71.2, 24.2, 7.0)))
    refs.append(("LCD_modulo_I2C", "caixa", (cx - lx / 2 + 6.0, cy + ly / 2 - 21.0,
                                            z_frente - pcb - 12.0, 41.5, 19.0, 12.0 - 1.0)))

    # Bateria 9 V em pé
    xb, yb = bolso_bateria(p)
    f = p["bateria_folga"]
    refs.append(("Bateria_9V", "caixa", (xb + f / 2, yb + f / 2, 0.0,
                                        p["bateria_x"], p["bateria_y"], p["bateria_z"])))

    # Chave KCD11 na parede direita
    if p["chave"]:
        cyy, czz = p["chave_y"], p["chave_z"]
        refs.append(("Chave_corpo", "caixa", (L - 12.0, cyy - 13.0 / 2, czz - 8.2 / 2, 12.0 + t, 13.0, 8.2)))
        refs.append(("Chave_moldura", "caixa", (L + t, cyy - 15.0 / 2, czz - 10.0 / 2, 2.0, 15.0, 10.0)))

    # Botão 6x6 (corpo encostado no suporte, embaixo da tampa)
    kx = p["controles_x"]
    refs.append(("Botao_corpo", "caixa", (kx - 3.0, p["botao_y"] - 3.0, H, 6.0, 6.0, 3.5)))
    refs.append(("Botao_haste", "cilindro", (kx, p["botao_y"], H + 3.5, 3.5, 1.5)))
    refs.append(("LED_5mm", "cilindro", (kx, p["led_y"], H - 1.0, 5.0, 8.6)))
    refs.append(("LED_aba", "cilindro", (kx, p["led_y"], H - 2.0, 5.8, 1.0)))
    refs.append(("LDR_5mm", "cilindro", (kx, p["ldr_y"], H + 0.5, 5.0, 2.0)))

    # Sensores na frente, à direita, encostados na ventilação (só referência)
    refs.append(("Sensor_DHT22", "caixa", (L - 1.5 - 7.7, 6.0, 0.0, 7.7, 15.1, 25.0)))
    refs.append(("Sensor_BMP280", "caixa", (L - 26.0, 6.0, 0.0, 2.5, 15.0, 13.0)))
    refs.append(("Sensor_LM35", "caixa", (L - 36.0, 8.0, 0.0, 3.6, 4.6, 14.0)))
    return refs
