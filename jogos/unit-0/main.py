
import pygame
import math
import random

pygame.init()

# Configurações
LARGURA, ALTURA = 1000, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("RETRO DOOM - FPS")
RELOGIO = pygame.time.Clock()
FONTE = pygame.font.SysFont("consolas", 24)
FONTE_GRANDE = pygame.font.SysFont("consolas", 42, bold=True)

# Cores
PRETO = (10, 10, 15)
CINZA = (90, 90, 100)
VERMELHO = (220, 35, 25)
BRANCO = (240, 240, 240)
VERDE = (50, 220, 80)

# Mapa: # = parede, . = chão
MAPA = [
    "############",
    "#..........#",
    "#..##......#",
    "#..........#",
    "#......##..#",
    "#..........#",
    "#.##.......#",
    "#..........#",
    "#......#...#",
    "#..........#",
    "############",
]

TAM = 64
FOV = math.pi / 3
RAIOS = 160
PASSO_ANGULO = FOV / RAIOS
DIST_MAX = 800

# Jogador
px, py = 100.0, 100.0
angulo = 0.0
vida = 100
municao = 50
pontos = 0

# Inimigos
inimigos = [
    {"x": 400.0, "y": 200.0, "vida": 2},
    {"x": 550.0, "y": 450.0, "vida": 2},
    {"x": 200.0, "y": 500.0, "vida": 2},
]

def parede(x, y):
    mx = int(x // TAM)
    my = int(y // TAM)

    if my < 0 or my >= len(MAPA):
        return True
    if mx < 0 or mx >= len(MAPA[0]):
        return True

    return MAPA[my][mx] == "#"


def raycast():
    profundidades = []

    for i in range(RAIOS):
        ang = angulo - FOV / 2 + i * PASSO_ANGULO
        distancia = 0
        atingiu_parede = False

        while distancia < DIST_MAX:
            distancia += 4
            x = px + math.cos(ang) * distancia
            y = py + math.sin(ang) * distancia

            if parede(x, y):
                atingiu_parede = True
                break

        if not atingiu_parede:
            distancia = DIST_MAX

        # Corrige distorção de perspectiva
        corrigida = max(
            1, distancia * math.cos(ang - angulo)
        )
        profundidades.append(corrigida)

        altura_parede = min(
            ALTURA, int(ALTURA * 55 / corrigida)
        )

        brilho = max(
            25, 210 - int(corrigida * 0.23)
        )

        cor = (brilho, brilho, min(255, brilho + 10))

        x_tela = int(i * LARGURA / RAIOS)
        largura_coluna = LARGURA // RAIOS + 1
        topo = ALTURA // 2 - altura_parede // 2

        pygame.draw.rect(
            TELA,
            cor,
            (x_tela, topo, largura_coluna, altura_parede)
        )

    return profundidades


def desenhar_cenario():
    # Céu
    TELA.fill(PRETO)
    pygame.draw.rect(
        TELA, (65, 35, 35),
        (0, 0, LARGURA, ALTURA // 2)
    )

    # Chão
    pygame.draw.rect(
        TELA, (45, 43, 40),
        (0, ALTURA // 2, LARGURA, ALTURA // 2)
    )

    # Linhas do chão
    for y in range(ALTURA // 2, ALTURA, 35):
        pygame.draw.line(
            TELA, (65, 60, 55),
            (0, y), (LARGURA, y)
        )


def desenhar_inimigos(profundidades):
    # Desenha primeiro os inimigos mais distantes
    for inimigo in sorted(
        inimigos,
        key=lambda e: math.hypot(e["x"] - px, e["y"] - py),
        reverse=True
    ):
        dx = inimigo["x"] - px
        dy = inimigo["y"] - py
        distancia = math.hypot(dx, dy)

        if distancia < 1:
            continue

        ang = math.atan2(dy, dx) - angulo
        ang = (ang + math.pi) % (2 * math.pi) - math.pi

        if abs(ang) > FOV / 2:
            continue

        tela_x = int(
            (ang + FOV / 2) / FOV * LARGURA
        )

        tamanho = min(
            ALTURA,
            int(ALTURA * 45 / distancia)
        )

        indice = int(tela_x / LARGURA * RAIOS)
        indice = max(0, min(RAIOS - 1, indice))

        if distancia * math.cos(ang) > profundidades[indice]:
            continue

        centro_y = ALTURA // 2

        # Corpo do inimigo
        pygame.draw.rect(
            TELA, (110, 15, 20),
            (tela_x - tamanho // 3,
             centro_y - tamanho // 3,
             tamanho * 2 // 3,
             tamanho * 2 // 3)
        )

        # Cabeça
        pygame.draw.circle(
            TELA, (220, 60, 45),
            (tela_x, centro_y - tamanho // 3),
            max(3, tamanho // 4)
        )

        # Olhos
        olho = max(2, tamanho // 14)
        pygame.draw.circle(
            TELA, BRANCO,
            (tela_x - tamanho // 10,
             centro_y - tamanho // 3),
            olho
        )
        pygame.draw.circle(
            TELA, BRANCO,
            (tela_x + tamanho // 10,
             centro_y - tamanho // 3),
            olho
        )


def atirar():
    global municao, pontos

    if municao <= 0:
        return

    municao -= 1

    alvo = None
    menor_distancia = float("inf")

    for inimigo in inimigos:
        dx = inimigo["x"] - px
        dy = inimigo["y"] - py
        distancia = math.hypot(dx, dy)

        direcao = math.atan2(dy, dx) - angulo
        direcao = (direcao + math.pi) % (2 * math.pi) - math.pi

        # Mira no centro da tela
        if abs(direcao) < 0.10 and distancia < menor_distancia:
            bloqueado = False
            passos = max(1, int(distancia / 8))

            for n in range(1, passos):
                d = distancia * n / passos
                if parede(px + math.cos(angulo) * d,
                          py + math.sin(angulo) * d):
                    bloqueado = True
                    break

            if not bloqueado:
                alvo = inimigo
                menor_distancia = distancia

    if alvo:
        alvo["vida"] -= 1
        if alvo["vida"] <= 0:
            inimigos.remove(alvo)
            pontos += 100


def mover_inimigos(dt):
    global vida

    for inimigo in inimigos:
        dx = px - inimigo["x"]
        dy = py - inimigo["y"]
        distancia = math.hypot(dx, dy)

        if distancia > 28:
            velocidade = 45 * dt
            nx = inimigo["x"] + dx / distancia * velocidade
            ny = inimigo["y"] + dy / distancia * velocidade

            if not parede(nx, inimigo["y"]):
                inimigo["x"] = nx
            if not parede(inimigo["x"], ny):
                inimigo["y"] = ny


def desenhar_hud():
    pygame.draw.rect(
        TELA, (10, 10, 10),
        (0, ALTURA - 65, LARGURA, 65)
    )

    texto = (
        f"VIDA: {vida}    "
        f"MUNICAO: {municao}    "
        f"PONTOS: {pontos}"
    )

    TELA.blit(
        FONTE.render(texto, True, VERDE),
        (20, ALTURA - 48)
    )

    # Mira
    cx, cy = LARGURA // 2, ALTURA // 2
    pygame.draw.line(
        TELA, BRANCO, (cx - 9, cy), (cx + 9, cy), 2
    )
    pygame.draw.line(
        TELA, BRANCO, (cx, cy - 9), (cx, cy + 9), 2
    )


def desenhar_arma():
    # Arma simples na parte inferior da tela
    cx = LARGURA // 2
    base = ALTURA - 65

    pygame.draw.rect(
        TELA, (45, 45, 50),
        (cx - 35, base - 95, 70, 100)
    )
    pygame.draw.rect(
        TELA, (100, 100, 110),
        (cx - 20, base - 120, 40, 70)
    )
    pygame.draw.rect(
        TELA, (20, 20, 25),
        (cx - 10, base - 125, 20, 55)
    )


def tela_final(vitoria):
    TELA.fill(PRETO)

    titulo = "VOCE VENCEU!" if vitoria else "GAME OVER"
    cor = VERDE if vitoria else VERMELHO

    texto = FONTE_GRANDE.render(titulo, True, cor)
    TELA.blit(
        texto,
        texto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40))
    )

    info = FONTE.render(
        f"Pontuacao: {pontos}  |  ESC para sair",
        True, BRANCO
    )
    TELA.blit(
        info,
        info.get_rect(center=(LARGURA // 2, ALTURA // 2 + 25))
    )
    pygame.display.flip()


# Loop principal
rodando = True
fim = False
vitoria = False
ultimo_dano = 0

pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

while rodando:
    dt = min(RELOGIO.tick(60) / 1000, 0.05)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False

            if not fim and evento.key == pygame.K_SPACE:
                atirar()

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if not fim and evento.button == 1:
                atirar()

        elif evento.type == pygame.MOUSEMOTION and not fim:
            angulo += evento.rel[0] * 0.003
            angulo %= 2 * math.pi

    if not fim:
        teclas = pygame.key.get_pressed()

        velocidade = 160 * dt

        # WASD: andar e recuar
        frente = 0
        lado = 0

        if teclas[pygame.K_w]:
            frente += velocidade
        if teclas[pygame.K_s]:
            frente -= velocidade
        if teclas[pygame.K_d]:
            lado += velocidade
        if teclas[pygame.K_a]:
            lado -= velocidade

        # Movimento relativo à direção da câmera
        dx = (
            math.cos(angulo) * frente
            + math.cos(angulo + math.pi / 2) * lado
        )
        dy = (
            math.sin(angulo) * frente
            + math.sin(angulo + math.pi / 2) * lado
        )

        if not parede(px + dx, py):
            px += dx
        if not parede(px, py + dy):
            py += dy

        mover_inimigos(dt)

        # Inimigos causam dano ao encostar
        agora = pygame.time.get_ticks()

        for inimigo in inimigos:
            distancia = math.hypot(
                inimigo["x"] - px,
                inimigo["y"] - py
            )

            if distancia < 35 and agora - ultimo_dano > 700:
                vida = max(0, vida - 10)
                ultimo_dano = agora

        if vida <= 0:
            fim = True
            vitoria = False
        elif not inimigos:
            fim = True
            vitoria = True

        desenhar_cenario()
        profundidades = raycast()
        desenhar_inimigos(profundidades)
        desenhar_arma()
        desenhar_hud()

    else:
        tela_final(vitoria)

    pygame.display.flip()

pygame.quit()
