# -*- coding: utf-8 -*-
"""
Caixa da Estação Meteorológica para IMPRESSÃO 3D (versão 2).

Duas peças:
  - corpo: fundo + 4 paredes numa peça só. Nos 4 cantos tem colunas com um sextavado
    aberto por baixo: a porca M3 da tampa entra por ali depois da peça impressa (não
    precisa pausar nem de suporte) e fica justa no topo. Tem também os pés do Arduino,
    o bolso da bateria, a ventilação, a chave liga/desliga e o furo do USB.
  - tampa: parafusada de cima pra baixo (cabeças escondidas em rebaixos), com aba de
    encaixe por baixo, LCD, LED, botão 6x6 e LDR.

Tudo em mm. Coordenadas: X esquerda->direita, Y frente->trás, Z pra cima, com a
origem no canto interno da frente à esquerda, em cima do fundo.

Este arquivo só tem as medidas e a geometria. Quem exporta STL/STEP, confere e faz
as imagens é o gerar.py.
"""
import math

import cadquery as cq

# ---------------------------------------------------------------------------
# PARÂMETROS  (mude aqui e rode o gerar.py de novo)
# ---------------------------------------------------------------------------
P = {
    # caixa (medidas INTERNAS)
    "comprimento": 116.0,       # X
    "profundidade": 76.0,       # Y
    "altura": 58.0,             # Z, do fundo até a tampa
    "parede": 3.5,
    "fundo": 6.0,
    "tampa": 6.0,
    "raio_cantos": 4.0,         # cantos verticais por fora
    "raio_base": 0.0,           # borda de baixo: 0 = reta (só os cantos verticais arredondam)
    "raio_tampa": 1.5,          # borda de cima da tampa

    # impressão
    "camada": 0.2,              # altura de camada (pontes em degrau)

    # parafusos M3 (Phillips de cabeça panela)
    "furo_m3": 3.8,             # furo de passagem (v1: 3,4)
    "rebaixo_diam": 7.2,        # rebaixo da cabeça (v1: 6,6)
    "rebaixo_prof": 3.6,        # múltiplo da camada (v1: 3,5)

    # porca M3 da tampa: entra POR BAIXO da coluna, com a peça já impressa.
    # O sextavado é aberto embaixo e afina no topo: a porca sobe solta e fica justa lá
    # em cima. Quando aperta, o parafuso da tampa puxa a porca contra a coluna.
    "porca_af": 6.0,            # entre faces na entrada (a porca tem 5,5): sobe solta
    "porca_af_topo": 5.3,       # entre faces no teto: a porca fica justa e não cai
    "porca_afina": 1.0,         # altura do trecho que afina, logo abaixo do teto
    "porca_alt": 2.8,           # trecho do sextavado com a coluna inteira em volta
    "porca_cobertura": 4.4,     # do topo da coluna até o teto do sextavado

    # colunas dos cantos: parte reta só em volta da porca, e embaixo afina a 45° até o
    # canto (imprime sem suporte e deixa o sextavado aberto por baixo)
    "coluna": 12.0,             # lado (v1: 8)

    # encaixe da tampa
    "aba_espessura": 1.6,
    "aba_altura": 3.0,
    "aba_folga": 0.25,

    # Arduino Uno R3 (atrás à esquerda, girado 180°: USB virado pra direita)
    "arduino_x": 3.0,
    "arduino_folga_tras": 3.0,
    "pe_arduino_diam": 7.0,
    "pe_arduino_alt": 5.0,

    # furo do USB na parede direita, alinhado com o conector do Arduino
    "usb_larg": 17.5,           # passa o plugue USB-B com a capa de borracha
    "usb_alt": 13.5,
    "usb_raio": 2.5,
    "usb_capa": (16.0, 12.0),   # capa do plugue usada na conferência (largura x altura)

    # bateria 9 V em pé, na FRENTE à direita, num bolso com paredinhas
    "bateria_x": 26.5, "bateria_y": 17.5, "bateria_z": 48.5,
    "bateria_folga": 1.0,
    "bateria_afasta_frente": 2.0,   # afasta da parede da frente (o clip não bate na aba)
    "bolso_parede": 2.0, "bolso_altura": 30.0,

    # chave liga/desliga (a cinza) na parede direita, acima da ventilação.
    # Em volta do furo a parede é afinada por dentro, pras travinhas prenderem.
    "chave_furo_y": 12.0, "chave_furo_z": 6.0,   # medida da chave: largura x altura
    "chave_folga": 0.2,         # o furo sai um pouco menor na impressão
    "chave_y": 42.0, "chave_z": 47.5,
    "chave_parede_fina": 1.8,

    # ventilação: 3 rasgos compridos na esquerda e 3 na direita
    "vent_comp": 40.0, "vent_larg": 3.5, "vent_y": 40.0,
    "vent_z": [23.0, 30.0, 37.0],

    # shield em cima do Arduino (os sensores vão nele)
    "shield_altura": 11.0,      # da placa do Arduino até a placa do shield

    # tampa: LCD 16x2 com I2C
    "lcd_centro_x": 70.0, "lcd_centro_y": 38.0,
    "lcd_placa_x": 80.0, "lcd_placa_y": 36.0,
    "lcd_furos_x": 75.0, "lcd_furos_y": 31.0,
    "lcd_janela_x": 72.0, "lcd_janela_y": 25.0,
    "lcd_pe_alt": 2.0, "lcd_pe_diam": 7.5,

    # tampa: controles (coluna da esquerda)
    "controles_x": 13.0,
    "led_y": 16.0, "botao_y": 38.0, "ldr_y": 62.0,
    "furo_led": 5.3, "furo_ldr": 5.4,
    "botao_furo": 6.3, "botao_prof": 3.0,
    "botao_pernas_x": 6.5, "botao_pernas_y": 4.5,
    "botao_rebaixo_baixo": 2.0,
}

UNO_PLACA = (68.58, 53.34)
UNO_FUROS = [(13.97, 2.54), (15.24, 50.80), (66.04, 7.62), (66.04, 35.56)]
# conectores no sistema do Uno: (x, y, comprimento, largura, altura)
UNO_USB = (-6.35, 32.0, 16.2, 12.0, 10.9)
UNO_P4 = (-1.8, 3.3, 14.2, 9.0, 11.0)
PCB = 1.6


# ---------------------------------------------------------------------------
# posições
# ---------------------------------------------------------------------------
def origem_arduino(p=P):
    return p["arduino_x"], p["profundidade"] - p["arduino_folga_tras"] - UNO_PLACA[1]


def uno_para_caixa(ux, uy, dx, dy, p=P):
    """Retângulo nas coordenadas do Uno -> caixa (o Arduino está girado 180°)."""
    x0, y0 = origem_arduino(p)
    bx, by = UNO_PLACA
    return x0 + bx - (ux + dx), y0 + by - (uy + dy), dx, dy


def furos_arduino(p=P):
    x0, y0 = origem_arduino(p)
    bx, by = UNO_PLACA
    return [(x0 + bx - hx, y0 + by - hy) for hx, hy in UNO_FUROS]


def centro_usb(p=P):
    """(y, z) do centro da boca do conector USB-B do Arduino."""
    ux, uy, dx, dy, dz = UNO_USB
    _, y, _, _ = uno_para_caixa(ux, uy, dx, dy, p)
    return y + dy / 2, p["pe_arduino_alt"] + PCB + dz / 2


def boca_usb_x(p=P):
    """X da boca do conector USB (onde o plugue encosta)."""
    ux, uy, dx, dy, _ = UNO_USB
    x, _, dx, _ = uno_para_caixa(ux, uy, dx, dy, p)
    return x + dx


def lcd_furos(p=P):
    cx, cy = p["lcd_centro_x"], p["lcd_centro_y"]
    hx, hy = p["lcd_furos_x"] / 2, p["lcd_furos_y"] / 2
    return [(cx - hx, cy - hy), (cx + hx, cy - hy), (cx + hx, cy + hy), (cx - hx, cy + hy)]


def centros_colunas(p=P):
    L, W, c = p["comprimento"], p["profundidade"], p["coluna"] / 2
    return [(c, c), (L - c, c), (c, W - c), (L - c, W - c)]


def alojamento_porca_z(p=P):
    """(teto, base) do trecho do sextavado com a coluna inteira em volta, em Z do modelo.
    A parte reta da coluna começa na base; abaixo dela a coluna afina a 45°."""
    zt = p["altura"] - p["porca_cobertura"]
    return zt, zt - p["porca_alt"]


def porca_topo_z(p=P, af_porca=5.5):
    """Z do topo da porca quando ela trava no trecho que afina (porca de af_porca entre
    faces, impressão na medida certa)."""
    zt, _ = alojamento_porca_z(p)
    a0, a1, ha = p["porca_af"], p["porca_af_topo"], p["porca_afina"]
    if af_porca >= a0:
        return zt - ha
    if af_porca <= a1:
        return zt
    return zt - ha + ha * (a0 - af_porca) / (a0 - a1)


def bolso_bateria(p=P):
    """(x0, x1, y0, y1) do espaço interno do bolso da bateria (frente à direita)."""
    L = p["comprimento"]
    f = p["bateria_folga"]
    x1 = L - p["coluna"] - 0.5
    x0 = x1 - p["bateria_x"] - f
    y0 = p["bateria_afasta_frente"]
    y1 = y0 + p["bateria_y"] + f
    return x0, x1, y0, y1


# ---------------------------------------------------------------------------
# primitivas
# ---------------------------------------------------------------------------
def caixa(x0, y0, z0, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


def cilindro(cx, cy, z0, d, h):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((cx, cy, z0))


def hexagono(cx, cy, z0, af, h):
    """Prisma sextavado (af = medida entre faces), com as faces viradas pra +-Y."""
    return (cq.Workplane("XY").polygon(6, af / math.cos(math.pi / 6)).extrude(h)
            .translate((cx, cy, z0)))


def hexagono_afinando(cx, cy, z0, af0, af1, h):
    """Sextavado que vai de af0 (em z0) até af1 (em z0 + h), faces viradas pra +-Y."""
    angulo = math.degrees(math.atan((af0 - af1) / 2 / h))
    return (cq.Workplane("XY").polygon(6, af0 / math.cos(math.pi / 6)).extrude(h, taper=angulo)
            .translate((cx, cy, z0)))


def rasgo_x(x0, esp, cy, cz, comp, larg):
    """Rasgo oblongo atravessando uma parede de normal X (comprido em Y)."""
    return cq.Workplane("YZ").slot2D(comp, larg, 0).extrude(esp).translate((x0, cy, cz))


def furo_em_degrau(cx, cy, z0, sentido, d, cavidade, comp, p=P):
    """
    Furo redondo de diâmetro d saindo de uma cavidade maior (rebaixo da cabeça ou
    alojamento da porca). z0 é a face onde a cavidade termina; sentido = +1 se, NA
    IMPRESSÃO, o furo fica acima da cavidade em +Z do modelo, -1 se fica em -Z.
    cavidade(z, h) devolve o sólido da cavidade entre z e z+h.

    As 2 camadas logo depois da cavidade são "pontes em degrau": a 1ª deixa só um
    rasgo da largura do furo, a 2ª só um quadrado, e daí pra frente o furo é redondo.
    Assim a impressora só faz pontes retas e curtas: não precisa de suporte e não cai
    rebarba dentro do furo.
    """
    h, e, s = p["camada"], 0.01, sentido

    def faixa(a, b):
        lo, hi = min(a, b), max(a, b)
        return lo - e, hi - lo + 2 * e

    za = faixa(z0, z0 + s * h)
    zb = faixa(z0 + s * h, z0 + s * 2 * h)
    zr = faixa(z0 + s * 2 * h, z0 + s * comp)
    L = 4 * d + 20
    rasgo = caixa(cx - L / 2, cy - d / 2, za[0], L, d, za[1]).intersect(cavidade(*za))
    quadrado = caixa(cx - d / 2, cy - d / 2, zb[0], d, d, zb[1])
    redondo = cilindro(cx, cy, zr[0], d, zr[1])
    return rasgo.union(quadrado).union(redondo)


def espelhar(wp, em_x, em_y, p=P):
    L, W = p["comprimento"], p["profundidade"]
    if em_x:
        wp = wp.mirror("YZ", (L / 2, 0, 0))
    if em_y:
        wp = wp.mirror("XZ", (0, W / 2, 0))
    return wp


# ---------------------------------------------------------------------------
# CORPO
# ---------------------------------------------------------------------------
def coluna_canto(p=P):
    """Coluna do canto frente-esquerda (as outras são espelhadas).

    Por dentro, de cima pra baixo: furo de passagem, 2 camadas de ponte em degrau, o
    trecho em que o sextavado afina (é ali que a porca fica presa) e o sextavado reto,
    aberto embaixo, por onde a porca sobe. A parte reta da coluna vai só do topo até a
    base do sextavado; dali pra baixo ela afina a 45° até o canto, sem precisar de
    suporte, e o sextavado sai aberto nessa parte afinada.
    """
    H, s = p["altura"], p["coluna"]
    c = s / 2
    zt, zp = alojamento_porca_z(p)
    zb = zp - s                             # ponta de baixo da parte afinada
    perfil = [(0, zb), (s, zb + s), (s, H), (0, H)]
    a = cq.Workplane("XZ").polyline(perfil).close().extrude(-s)      # extrude em +Y
    b = cq.Workplane("YZ").polyline(perfil).close().extrude(s)       # extrude em +X
    col = a.intersect(b)
    af, af1, ha = p["porca_af"], p["porca_af_topo"], p["porca_afina"]
    sext = hexagono(c, c, zb - 1, af, (zt - ha) - (zb - 1))
    sext = sext.union(hexagono_afinando(c, c, zt - ha, af, af1, ha)).clean()
    col = col.cut(sext)
    col = col.cut(furo_em_degrau(c, c, zt, +1, p["furo_m3"],
                                 lambda z, h: hexagono(c, c, z, af1, h), H - zt + 1, p))
    return col


def fazer_corpo(p=P):
    L, W, H = p["comprimento"], p["profundidade"], p["altura"]
    w, tf = p["parede"], p["fundo"]
    ext = (cq.Workplane("XY").box(L + 2 * w, W + 2 * w, H + tf, centered=False)
           .translate((-w, -w, -tf)))
    ext = ext.edges("|Z").fillet(p["raio_cantos"])
    if p["raio_base"] > 0:
        ext = ext.faces("<Z").edges().fillet(p["raio_base"])
    corpo = ext.cut(caixa(0, 0, 0, L, W, H + 1))

    # colunas dos cantos (a porca da tampa entra por baixo delas)
    col = coluna_canto(p)
    for ex in (False, True):
        for ey in (False, True):
            corpo = corpo.union(espelhar(col, ex, ey, p))

    # pés do Arduino + furos + rebaixos por baixo (com pontes em degrau)
    ard = furos_arduino(p)
    for (x, y) in ard:
        corpo = corpo.union(cilindro(x, y, -0.5, p["pe_arduino_diam"], p["pe_arduino_alt"] + 0.5))
    rd, rp = p["rebaixo_diam"], p["rebaixo_prof"]
    for (x, y) in ard:
        corpo = corpo.cut(cilindro(x, y, -tf - 1, rd, rp + 1))
        corpo = corpo.cut(furo_em_degrau(
            x, y, -tf + rp, +1, p["furo_m3"],
            lambda z, h, x=x, y=y: cilindro(x, y, z, rd, h),
            tf - rp + p["pe_arduino_alt"] + 1, p))

    # bolso da bateria na frente (paredinhas dos lados e de trás + calço na frente)
    bx0, bx1, by0, by1 = bolso_bateria(p)
    e, hb = p["bolso_parede"], p["bolso_altura"]
    corpo = corpo.union(caixa(bx0 - e, -0.5, -0.5, e, by1 + e + 0.5, hb + 0.5))
    corpo = corpo.union(caixa(bx1, -0.5, -0.5, e, by1 + e + 0.5, hb + 0.5))
    corpo = corpo.union(caixa(bx0 - e, by1, -0.5, bx1 - bx0 + 2 * e, e, hb + 0.5))
    if by0 > 0:
        corpo = corpo.union(caixa(bx0 - e, -0.5, -0.5, bx1 - bx0 + 2 * e, by0 + 0.5, hb + 0.5))

    # ventilação: paredes esquerda e direita
    for z in p["vent_z"]:
        for x0 in (-w - 1, L - 1):
            corpo = corpo.cut(rasgo_x(x0, w + 2, p["vent_y"], z, p["vent_comp"], p["vent_larg"]))

    # furo do USB na parede direita, alinhado com o conector do Arduino
    yu, zu = centro_usb(p)
    furo_usb = (cq.Workplane("YZ").rect(p["usb_larg"], p["usb_alt"]).extrude(w + 2)
                .edges("|X").fillet(p["usb_raio"]).translate((L - 1, yu, zu)))
    corpo = corpo.cut(furo_usb)

    # chave liga/desliga na parede direita + parede afinada por dentro
    cy, cz = p["chave_y"], p["chave_z"]
    fy = p["chave_furo_y"] + p["chave_folga"]
    fz = p["chave_furo_z"] + p["chave_folga"]
    corpo = corpo.cut(caixa(L - 1, cy - fy / 2, cz - fz / 2, w + 2, fy, fz))
    fino = w - p["chave_parede_fina"]
    corpo = corpo.cut(caixa(L - 0.5, cy - fy / 2 - 2.0, cz - fz / 2 - 2.0, fino + 0.5,
                            fy + 4.0, fz + 4.0))
    return corpo


# ---------------------------------------------------------------------------
# TAMPA
# ---------------------------------------------------------------------------
def furo_tampa(x, y, p=P):
    """Rebaixo da cabeça por cima + furo de passagem. A tampa imprime de cabeça pra
    baixo, então as pontes em degrau ficam logo abaixo do fundo do rebaixo."""
    zt = p["altura"] + p["tampa"]
    rd, rp = p["rebaixo_diam"], p["rebaixo_prof"]
    z0 = zt - rp
    reb = cilindro(x, y, z0, rd, rp + 1)
    furo = furo_em_degrau(x, y, z0, -1, p["furo_m3"],
                          lambda z, h: cilindro(x, y, z, rd, h), p["tampa"] + 10, p)
    return reb.union(furo)


def fazer_tampa(p=P):
    L, W, H = p["comprimento"], p["profundidade"], p["altura"]
    w, tt = p["parede"], p["tampa"]
    zt = H + tt
    tampa = (cq.Workplane("XY").box(L + 2 * w, W + 2 * w, tt, centered=False)
             .translate((-w, -w, H)))
    tampa = tampa.edges("|Z").fillet(p["raio_cantos"])
    tampa = tampa.faces(">Z").edges().fillet(p["raio_tampa"])

    # aba de encaixe (entra por dentro das paredes), cortada nas colunas
    g, ea, ha = p["aba_folga"], p["aba_espessura"], p["aba_altura"]
    aba = caixa(g, g, H - ha, L - 2 * g, W - 2 * g, ha + 0.5)
    aba = aba.cut(caixa(g + ea, g + ea, H - ha - 1, L - 2 * g - 2 * ea, W - 2 * g - 2 * ea, ha + 2))
    s = p["coluna"] + 0.4
    for (cx, cy) in [(0, 0), (L - s, 0), (0, W - s), (L - s, W - s)]:
        aba = aba.cut(caixa(cx, cy, H - ha - 1, s, s, ha + 2))
    tampa = tampa.union(aba)

    # pés do LCD por baixo
    for (x, y) in lcd_furos(p):
        tampa = tampa.union(cilindro(x, y, H - p["lcd_pe_alt"], p["lcd_pe_diam"], p["lcd_pe_alt"] + 0.5))

    # parafusos da tampa (colunas) e do LCD: rebaixo por cima + furo
    for (x, y) in centros_colunas(p) + lcd_furos(p):
        tampa = tampa.cut(furo_tampa(x, y, p))

    # janela do LCD
    cx, cy = p["lcd_centro_x"], p["lcd_centro_y"]
    jx, jy = p["lcd_janela_x"], p["lcd_janela_y"]
    tampa = tampa.cut(caixa(cx - jx / 2, cy - jy / 2, H - 5, jx, jy, tt + 10))

    # LED e LDR
    kx = p["controles_x"]
    tampa = tampa.cut(cilindro(kx, p["led_y"], H - 5, p["furo_led"], tt + 10))
    tampa = tampa.cut(cilindro(kx, p["ldr_y"], H - 5, p["furo_ldr"], tt + 10))

    # botão 6x6: entra por cima num rebaixo quadrado; as pernas atravessam
    by = p["botao_y"]
    bf, bp = p["botao_furo"], p["botao_prof"]
    tampa = tampa.cut(caixa(kx - bf / 2, by - bf / 2, zt - bp, bf, bf, bp + 1))
    px = p["botao_pernas_x"] / 2
    for sx in (-1, 1):
        tampa = tampa.cut(caixa(kx + sx * px - 0.65, by - 3.0, H - 5, 1.3, 6.0, tt + 10))
    rb = p["botao_rebaixo_baixo"]
    tampa = tampa.cut(caixa(kx - 5.0, by - 5.0, H - 5, 10.0, 10.0, 5 + rb))
    return tampa


# ---------------------------------------------------------------------------
# REFERÊNCIAS (não imprimir): componentes, cabo USB, parafusos e porcas
# ---------------------------------------------------------------------------
def referencias(p=P, cabo_usb=True):
    """Lista de (nome, Workplane). Os nomes começam pelo grupo (Arduino, LCD...)."""
    L, H = p["comprimento"], p["altura"]
    tt, tf, w = p["tampa"], p["fundo"], p["parede"]
    refs = []
    bx, by = UNO_PLACA
    x0, y0 = origem_arduino(p)
    z0 = p["pe_arduino_alt"]

    def uno(ux, uy, dx, dy):
        return uno_para_caixa(ux, uy, dx, dy, p)

    refs.append(("Arduino_placa", caixa(x0, y0, z0, bx, by, PCB)))
    xx, yy, dx, dy = uno(*UNO_USB[:4])
    refs.append(("Arduino_USB", caixa(xx, yy, z0 + PCB, dx, dy, UNO_USB[4])))
    xx, yy, dx, dy = uno(*UNO_P4[:4])
    refs.append(("Arduino_P4", caixa(xx, yy, z0 + PCB, dx, dy, UNO_P4[4])))
    xx, yy, dx, dy = uno(17.5, 49.0, 48.5, 2.6)
    refs.append(("Arduino_barra_digital", caixa(xx, yy, z0 + PCB, dx, dy, 8.5)))
    xx, yy, dx, dy = uno(27.0, 1.3, 38.0, 2.6)
    refs.append(("Arduino_barra_analog", caixa(xx, yy, z0 + PCB, dx, dy, 8.5)))
    zs = z0 + PCB + p["shield_altura"]
    refs.append(("Shield_placa", caixa(x0, y0, zs, bx, by, PCB)))

    if cabo_usb:
        yu, zu = centro_usb(p)
        xb = boca_usb_x(p)
        cw, ch = p["usb_capa"]
        refs.append(("Cabo_USB_plugue", caixa(xb - 1.0, yu - 4.2, zu - 3.9, 2.0, 8.4, 7.8)))
        refs.append(("Cabo_USB_capa", caixa(xb + 1.0, yu - cw / 2, zu - ch / 2, 28.0, cw, ch)))
        cabo = (cq.Workplane("YZ").circle(2.25).extrude(L + w + 25 - (xb + 29.0))
                .translate((xb + 29.0, yu, zu)))
        refs.append(("Cabo_USB_fio", cabo))

    cx, cy = p["lcd_centro_x"], p["lcd_centro_y"]
    lx, ly = p["lcd_placa_x"], p["lcd_placa_y"]
    zf = H - p["lcd_pe_alt"]
    refs.append(("LCD_placa", caixa(cx - lx / 2, cy - ly / 2, zf - PCB, lx, ly, PCB)))
    refs.append(("LCD_moldura", caixa(cx - 71.2 / 2, cy - 24.2 / 2, zf, 71.2, 24.2, 7.0)))
    refs.append(("LCD_modulo_I2C", caixa(cx - lx / 2 + 6.0, cy + ly / 2 - 21.0, zf - PCB - 12.0,
                                         41.5, 19.0, 11.0)))

    bx0, bx1, by0, by1 = bolso_bateria(p)
    f = p["bateria_folga"]
    refs.append(("Bateria_9V", caixa(bx0 + f / 2, by0 + f / 2, 0.0,
                                     p["bateria_x"], p["bateria_y"], p["bateria_z"])))
    refs.append(("Bateria_clip", caixa(bx0 + f / 2 + 0.5, by0 + f / 2 + 0.5, p["bateria_z"],
                                       p["bateria_x"] - 1.0, p["bateria_y"] - 1.0, 7.0)))

    chy, chz = p["chave_y"], p["chave_z"]
    # chave genérica do tamanho do furo: corpo + terminais por dentro, borda por fora
    cfy, cfz = p["chave_furo_y"] - 0.2, p["chave_furo_z"] - 0.2
    refs.append(("Chave_corpo", caixa(L + w - 16.0, chy - cfy / 2, chz - cfz / 2, 16.0, cfy, cfz)))
    refs.append(("Chave_moldura", caixa(L + w, chy - (cfy + 2.2) / 2, chz - (cfz + 2.2) / 2,
                                        1.5, cfy + 2.2, cfz + 2.2)))

    kx = p["controles_x"]
    zt = H + tt
    bp = p["botao_prof"]
    refs.append(("Botao_corpo", caixa(kx - 3.0, p["botao_y"] - 3.0, zt - bp, 6.0, 6.0, 3.5)))
    refs.append(("Botao_haste", cilindro(kx, p["botao_y"], zt - bp + 3.5, 3.5, 1.5)))
    refs.append(("LED_5mm", cilindro(kx, p["led_y"], H - 1.0, 5.0, 8.6)))
    refs.append(("LED_aba", cilindro(kx, p["led_y"], H - 1.0, 5.8, 1.0)))
    refs.append(("LDR_5mm", cilindro(kx, p["ldr_y"], zt - 2.0, 5.0, 2.0)))

    # parafusos e porcas
    def parafuso(nome, x, y, z_apoio, comp, para_baixo):
        cab = 2.4
        if para_baixo:   # cabeça em cima, rosca descendo
            refs.append((nome + "_cabeca", cilindro(x, y, z_apoio, 5.6, cab)))
            refs.append((nome + "_rosca", cilindro(x, y, z_apoio - comp, 3.0, comp)))
        else:            # cabeça embaixo, rosca subindo
            refs.append((nome + "_cabeca", cilindro(x, y, z_apoio - cab, 5.6, cab)))
            refs.append((nome + "_rosca", cilindro(x, y, z_apoio, 3.0, comp)))

    def porca(nome, x, y, zb):
        refs.append((nome, hexagono(x, y, zb, 5.5, 2.4)))

    apoio_tampa = zt - p["rebaixo_prof"]
    z_porca = porca_topo_z(p)       # onde a porca de 5,5 trava, no trecho que afina
    for i, (x, y) in enumerate(centros_colunas(p)):
        parafuso("Parafuso_tampa_%d" % (i + 1), x, y, apoio_tampa, 10.0, True)
        porca("Porca_tampa_%d" % (i + 1), x, y, z_porca - 2.4)
    for i, (x, y) in enumerate(lcd_furos(p)):
        parafuso("Parafuso_LCD_%d" % (i + 1), x, y, apoio_tampa, 10.0, True)
        porca("Porca_LCD_%d" % (i + 1), x, y, zf - PCB - 2.4)
    apoio_fundo = -tf + p["rebaixo_prof"]
    for i, (x, y) in enumerate(furos_arduino(p)):
        parafuso("Parafuso_Arduino_%d" % (i + 1), x, y, apoio_fundo, 12.0, False)
        porca("Porca_Arduino_%d" % (i + 1), x, y, z0 + PCB)
    return refs


CORES = {
    "Arduino": (0.0, 0.45, 0.55), "LCD_placa": (0.1, 0.45, 0.15), "LCD_moldura": (0.75, 0.75, 0.78),
    "LCD_modulo": (0.15, 0.2, 0.6), "Bateria": (0.85, 0.45, 0.05), "Chave": (0.08, 0.08, 0.08),
    "Botao": (0.15, 0.15, 0.15), "LED": (0.95, 0.1, 0.1), "LDR": (0.85, 0.65, 0.2),
    "Shield": (0.1, 0.5, 0.2), "Parafuso": (0.55, 0.55, 0.6), "Porca": (0.7, 0.7, 0.72),
    "Cabo_USB_plugue": (0.75, 0.75, 0.78), "Cabo_USB": (0.12, 0.12, 0.14),
}


def cor(nome):
    for k, c in CORES.items():
        if nome.startswith(k):
            return c
    return (0.5, 0.5, 0.5)
