
import pygame
import random
import math
import sys

pygame.init()

# CONFIGURACAO
LARGURA, ALTURA = 960, 640
TILE = 32
FPS = 60

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("APOCALIPSE PIXEL - Sobreviva!")
relogio = pygame.time.Clock()

# CORES
PRETO = (15, 18, 20)
CINZA = (55, 59, 57)
CINZA_CLARO = (90, 93, 83)
VERDE = (70, 130, 65)
VERDE_ESCURO = (35, 75, 42)
VERMELHO = (190, 45, 40)
LARANJA = (240, 130, 40)
BRANCO = (240, 240, 220)
AMARELO = (235, 205, 70)
AZUL = (70, 150, 210)
ROXO = (115, 70, 130)

fonte = pygame.font.Font(None, 28)
fonte_grande = pygame.font.Font(None, 64)
fonte_pequena = pygame.font.Font(None, 21)

# MUNDO
MUNDO_LARGURA = 2200
MUNDO_ALTURA = 1800

# JOGADOR
jogador = pygame.Rect(500, 500, 24, 28)
velocidade = 4
vida = 100
municao = 35
pontos = 0
kits = 0

# ESTADOS
zumbis = []
balas = []
itens = []
particulas = []

camera_x = 0
camera_y = 0
tempo_spawn = 0
tempo_item = 0
tempo_dano = 0
jogo_ativo = True
vitoria = False

# GERAR CENARIO
random.seed(12)
decoracoes = []

for _ in range(230):
    x = random.randint(0, MUNDO_LARGURA)
    y = random.randint(0, MUNDO_ALTURA)
    tipo = random.choice(["escombro", "sangue", "grama", "pedra"])
    decoracoes.append((x, y, tipo))

predios = []

for _ in range(35):
    x = random.randint(80, MUNDO_LARGURA - 150)
    y = random.randint(80, MUNDO_ALTURA - 150)
    w = random.randint(70, 150)
    h = random.randint(65, 130)

    predios.append(pygame.Rect(x, y, w, h))


def desenhar_texto(texto, x, y, cor=BRANCO, fonte_usada=fonte):
    imagem = fonte_usada.render(texto, False, cor)
    tela.blit(imagem, (x, y))


def desenhar_chao():
    tela.fill((65, 78, 55))

    # Textura pixelada
    for x in range(-TILE, LARGURA + TILE, TILE):
        for y in range(-TILE, ALTURA + TILE, TILE):
            wx = x + camera_x
            wy = y + camera_y

            tom = (60, 75, 52)
            pygame.draw.rect(tela, tom, (x, y, TILE, TILE))

            # Pequenos pixels de grama
            valor = (wx * 13 + wy * 7) % 19
            if valor < 4:
                pygame.draw.rect(
                    tela, VERDE_ESCURO,
                    (x + valor * 3, y + 10, 5, 4)
                )

    # Decoracoes do mundo
    for x, y, tipo in decoracoes:
        sx = x - camera_x
        sy = y - camera_y

        if -20 < sx < LARGURA + 20 and -20 < sy < ALTURA + 20:
            if tipo == "escombro":
                pygame.draw.rect(
                    tela, CINZA,
                    (sx, sy, 12, 8)
                )
                pygame.draw.rect(
                    tela, CINZA_CLARO,
                    (sx + 4, sy + 2, 5, 3)
                )

            elif tipo == "sangue":
                pygame.draw.rect(
                    tela, (95, 35, 28),
                    (sx, sy, 15, 5)
                )

            elif tipo == "grama":
                pygame.draw.rect(
                    tela, (85, 110, 55),
                    (sx, sy, 4, 10)
                )

            else:
                pygame.draw.rect(
                    tela, (90, 90, 75),
                    (sx, sy, 8, 8)
                )


def desenhar_predios():
    for predio in predios:
        sx = predio.x - camera_x
        sy = predio.y - camera_y

        if (
            sx < -200 or sy < -200
            or sx > LARGURA + 100
            or sy > ALTURA + 100
        ):
            continue

        # Sombra
        pygame.draw.rect(
            tela, (25, 28, 25),
            (sx + 8, sy + 8, predio.w, predio.h)
        )

        # Predio destruido
        pygame.draw.rect(
            tela, (75, 73, 65),
            (sx, sy, predio.w, predio.h)
        )

        pygame.draw.rect(
            tela, (100, 95, 80),
            (sx, sy, predio.w, 8)
        )

        # Janelas
        for wx in range(12, predio.w - 10, 25):
            for wy in range(18, predio.h - 10, 27):
                cor = random_window_color(predio.x, predio.y, wx, wy)
                pygame.draw.rect(
                    tela, cor,
                    (sx + wx, sy + wy, 11, 12)
                )

        # Rachadura
        pygame.draw.line(
            tela, PRETO,
            (sx + predio.w // 2, sy + 10),
            (sx + predio.w // 2 - 12, sy + predio.h // 2),
            3
        )


def random_window_color(x, y, wx, wy):
    valor = (x + y + wx * 5 + wy * 3) % 4
    if valor == 0:
        return (30, 35, 35)
    if valor == 1:
        return (120, 85, 55)
    if valor == 2:
        return (45, 50, 45)
    return (85, 70, 55)


def desenhar_jogador():
    x = jogador.x - camera_x
    y = jogador.y - camera_y

    # Sombra
    pygame.draw.rect(tela, (25, 30, 25), (x + 2, y + 22, 23, 8))

    # Pernas
    pygame.draw.rect(tela, (40, 45, 55), (x + 4, y + 17, 7, 11))
    pygame.draw.rect(tela, (40, 45, 55), (x + 14, y + 17, 7, 11))

    # Corpo e mochila
    pygame.draw.rect(tela, (45, 100, 65), (x + 3, y + 9, 19, 13))
    pygame.draw.rect(tela, (100, 65, 40), (x - 1, y + 11, 7, 12))

    # Cabeca
    pygame.draw.rect(tela, (210, 170, 125), (x + 6, y, 13, 11))

    # Cabelo
    pygame.draw.rect(tela, (50, 35, 25), (x + 5, y, 15, 4))

    # Olhos
    pygame.draw.rect(tela, PRETO, (x + 15, y + 5, 2, 2))

    # Arma
    pygame.draw.rect(tela, (45, 45, 45), (x + 18, y + 12, 13, 4))
    pygame.draw.rect(tela, (120, 120, 115), (x + 25, y + 11, 7, 3))


def desenhar_zumbi(z):
    x = int(z["x"] - camera_x)
    y = int(z["y"] - camera_y)

    # Sombra
    pygame.draw.rect(tela, (30, 35, 25), (x, y + 22, 25, 7))

    # Pernas
    pygame.draw.rect(tela, (65, 70, 45), (x + 3, y + 17, 7, 11))
    pygame.draw.rect(tela, (65, 70, 45), (x + 15, y + 17, 7, 11))

    # Corpo
    pygame.draw.rect(tela, (65, 115, 55), (x + 2, y + 8, 22, 14))

    # Roupa rasgada
    pygame.draw.rect(tela, (90, 45, 40), (x + 4, y + 15, 7, 4))

    # Cabeca
    pygame.draw.rect(tela, (115, 145, 75), (x + 5, y, 15, 12))

    # Olhos vermelhos
    pygame.draw.rect(tela, VERMELHO, (x + 7, y + 4, 3, 3))
    pygame.draw.rect(tela, VERMELHO, (x + 15, y + 4, 3, 3))

    # Boca
    pygame.draw.rect(tela, PRETO, (x + 10, y + 9, 7, 2))


def desenhar_item(item):
    x = int(item["x"] - camera_x)
    y = int(item["y"] - camera_y)

    if item["tipo"] == "municao":
        pygame.draw.rect(tela, AMARELO, (x, y, 20, 18))
        pygame.draw.rect(tela, (130, 90, 25), (x + 4, y + 3, 12, 12))
        pygame.draw.rect(tela, BRANCO, (x + 7, y + 5, 6, 8))

    elif item["tipo"] == "vida":
        pygame.draw.rect(tela, BRANCO, (x, y, 20, 20))
        pygame.draw.rect(tela, VERMELHO, (x + 8, y + 3, 5, 14))
        pygame.draw.rect(tela, VERMELHO, (x + 3, y + 8, 15, 5))

    else:
        pygame.draw.rect(tela, (150, 100, 50), (x, y, 22, 22))
        pygame.draw.rect(tela, (210, 160, 80), (x + 3, y + 3, 16, 16))
        pygame.draw.rect(tela, (100, 65, 30), (x + 8, y + 7, 6, 8))


def criar_zumbi():
    lado = random.randint(0, 3)

    if lado == 0:
        x = jogador.x + random.randint(-450, 450)
        y = jogador.y - 500
    elif lado == 1:
        x = jogador.x + random.randint(-450, 450)
        y = jogador.y + 500
    elif lado == 2:
        x = jogador.x - 500
        y = jogador.y + random.randint(-400, 400)
    else:
        x = jogador.x + 500
        y = jogador.y + random.randint(-400, 400)

    x = max(0, min(MUNDO_LARGURA - 30, x))
    y = max(0, min(MUNDO_ALTURA - 30, y))

    zumbis.append({
        "x": float(x),
        "y": float(y),
        "vida": 2,
        "vel": random.uniform(1.0, 1.65)
    })


def criar_item():
    tipo = random.choice(["municao", "vida", "caixa"])
    x = max(20, min(MUNDO_LARGURA - 40, jogador.x + random.randint(-400, 400)))
    y = max(20, min(MUNDO_ALTURA - 40, jogador.y + random.randint(-350, 350)))

    itens.append({
        "x": x,
        "y": y,
        "tipo": tipo
    })


def reiniciar():
    global jogador, vida, municao, pontos, kits
    global zumbis, balas, itens, camera_x, camera_y
    global tempo_spawn, tempo_item, tempo_dano
    global jogo_ativo, vitoria

    jogador = pygame.Rect(500, 500, 24, 28)
    vida = 100
    municao = 35
    pontos = 0
    kits = 0
    zumbis = []
    balas = []
    itens = []
    camera_x = 0
    camera_y = 0
    tempo_spawn = 0
    tempo_item = 0
    tempo_dano = 0
    jogo_ativo = True
    vitoria = False


# LOOP PRINCIPAL
while True:
    dt = relogio.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if evento.key == pygame.K_r and not jogo_ativo:
                reiniciar()

            if evento.key == pygame.K_SPACE and jogo_ativo and municao > 0:
                mx, my = pygame.mouse.get_pos()
                px = jogador.centerx - camera_x
                py = jogador.centery - camera_y

                dx = mx - px
                dy = my - py
                dist = math.hypot(dx, dy)

                if dist > 0:
                    balas.append({
                        "x": float(jogador.centerx),
                        "y": float(jogador.centery),
                        "dx": dx / dist * 10,
                        "dy": dy / dist * 10,
                        "vida": 55
                    })
                    municao -= 1

    if jogo_ativo:
        teclas = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy -= velocidade
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy += velocidade
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx -= velocidade
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx += velocidade

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        jogador.x += int(dx)
        jogador.y += int(dy)

        jogador.clamp_ip(pygame.Rect(0, 0, MUNDO_LARGURA, MUNDO_ALTURA))

        # Camera acompanha o jogador
        camera_x = jogador.centerx - LARGURA // 2
        camera_y = jogador.centery - ALTURA // 2

        camera_x = max(0, min(MUNDO_LARGURA - LARGURA, camera_x))
        camera_y = max(0, min(MUNDO_ALTURA - ALTURA, camera_y))

        # Gerar zumbis
        tempo_spawn += 1
        if tempo_spawn > 75:
            criar_zumbi()
            tempo_spawn = 0

        # Gerar suprimentos
        tempo_item += 1
        if tempo_item > 420:
            criar_item()
            tempo_item = 0

        # Movimento dos zumbis
        for z in zumbis[:]:
            zx = z["x"] - jogador.centerx
            zy = z["y"] - jogador.centery
            dist = math.hypot(zx, zy)

            if dist > 0:
                z["x"] -= zx / dist * z["vel"]
                z["y"] -= zy / dist * z["vel"]

            rect_zumbi = pygame.Rect(int(z["x"]), int(z["y"]), 25, 28)

            if jogador.colliderect(rect_zumbi):
                if tempo_dano <= 0:
                    vida -= 10
                    tempo_dano = 35

        if tempo_dano > 0:
            tempo_dano -= 1

        # Movimento das balas e dano nos zumbis
        for bala in balas[:]:
            bala["x"] += bala["dx"]
            bala["y"] += bala["dy"]
            bala["vida"] -= 1

            if bala["vida"] <= 0:
                balas.remove(bala)
                continue

            bala_rect = pygame.Rect(
                int(bala["x"] - 3),
                int(bala["y"] - 3),
                6, 6
            )

            atingiu = False

            for z in zumbis[:]:
                z_rect = pygame.Rect(int(z["x"]), int(z["y"]), 25, 28)

                if bala_rect.colliderect(z_rect):
                    z["vida"] -= 1
                    atingiu = True

                    if z["vida"] <= 0:
                        zumbis.remove(z)
                        pontos += 10

                    break

            if atingiu and bala in balas:
                balas.remove(bala)

        # Coletar itens
        for item in itens[:]:
            item_rect = pygame.Rect(int(item["x"]), int(item["y"]), 22, 22)

            if jogador.colliderect(item_rect):
                if item["tipo"] == "municao":
                    municao += 15
                elif item["tipo"] == "vida":
                    vida = min(100, vida + 25)
                else:
                    kits += 1
                    pontos += 5

                itens.remove(item)

        if vida <= 0:
            vida = 0
            jogo_ativo = False

        # Objetivo de sobrevivencia
        if pontos >= 500:
            vitoria = True
            jogo_ativo = False

    # DESENHO
    desenhar_chao()
    desenhar_predios()

    for item in itens:
        desenhar_item(item)

    for z in zumbis:
        desenhar_zumbi(z)

    desenhar_jogador()

    # Balas
    for bala in balas:
        bx = int(bala["x"] - camera_x)
        by = int(bala["y"] - camera_y)
        pygame.draw.rect(tela, AMARELO, (bx, by, 6, 6))

    # HUD
    pygame.draw.rect(tela, (20, 20, 20), (12, 12, 245, 112))
    desenhar_texto("SOBREVIVENTE", 22, 17, AMARELO)

    pygame.draw.rect(tela, (70, 20, 20), (22, 48, 200, 18))
    pygame.draw.rect(
        tela, (50, 200, 70),
        (22, 48, int(200 * vida / 100), 18)
    )
    desenhar_texto(f"VIDA: {vida}", 22, 70)
    desenhar_texto(f"MUNICAO: {municao}", 22, 94)

    desenhar_texto(f"PONTOS: {pontos}", LARGURA - 180, 20, AMARELO)
    desenhar_texto(f"ZUMBIS: {len(zumbis)}", LARGURA - 180, 50)
    desenhar_texto(f"KITS: {kits}", LARGURA - 180, 80, AZUL)

    # Mira do mouse
    if jogo_ativo:
        mx, my = pygame.mouse.get_pos()
        pygame.draw.rect(tela, BRANCO, (mx - 7, my, 15, 2))
        pygame.draw.rect(tela, BRANCO, (mx, my - 7, 2, 15))

    if not jogo_ativo:
        camada = pygame.Surface((LARGURA, ALTURA))
        camada.set_alpha(210)
        camada.fill(PRETO)
        tela.blit(camada, (0, 0))

        if vitoria:
            titulo = "VOCE SOBREVIVEU!"
            cor_titulo = AMARELO
        else:
            titulo = "VOCE FOI DERROTADO"
            cor_titulo = VERMELHO

        imagem = fonte_grande.render(titulo, False, cor_titulo)
        tela.blit(imagem, imagem.get_rect(center=(LARGURA // 2, 250)))

        desenhar_texto(
            f"Pontuacao final: {pontos}",
            LARGURA // 2 - 100, 310, BRANCO
        )

        desenhar_texto(
            "Pressione R para jogar novamente",
            LARGURA // 2 - 145, 365, AMARELO
        )

    # Controles
    if jogo_ativo:
        desenhar_texto(
            "WASD/SETAS: mover | MOUSE: mirar | ESPACO: atirar",
            15, ALTURA - 28, BRANCO, fonte_pequena
        )

    pygame.display.flip()
