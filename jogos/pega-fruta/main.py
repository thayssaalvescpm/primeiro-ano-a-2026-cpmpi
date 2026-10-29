import asyncio
import pygame
import random
import time

pygame.init()

# CONFIGURACAO
LARGURA = 500
ALTURA = 600
FPS = 60

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pega-Fruta")
relogio = pygame.time.Clock()

# CORES
AZUL_CLARO = (173, 216, 230)
PRETO = (25, 25, 25)
MARROM = (130, 75, 35)
MARROM_ESCURO = (80, 45, 20)
BRANCO = (255, 255, 255)
VERDE = (40, 150, 70)
AMARELO = (255, 220, 70)

# FONTES
fonte = pygame.font.SysFont("arial", 26)
fonte_pequena = pygame.font.SysFont("arial", 18)
fonte_grande = pygame.font.SysFont("arial", 48, bold=True)

# JOGADOR E JOGO
CESTA_LARGURA = 100
CESTA_ALTURA = 30
cesta = pygame.Rect(
    LARGURA // 2 - CESTA_LARGURA // 2,
    ALTURA - 70,
    CESTA_LARGURA,
    CESTA_ALTURA
)

pontos = 0
velocidade_fruta = 180  # pixels por segundo
velocidade_cesta = 300  # pixels por segundo
frutas = []
ultimo_spawn = 0.0
fim_de_jogo = False

TIPOS_FRUTAS = [
    ("MACA", (220, 40, 40)),
    ("BANANA", (245, 210, 45)),
    ("MORANGO", (220, 45, 80)),
    ("LARANJA", (245, 135, 30)),
    ("UVA", (130, 65, 180)),
]


def desenhar_texto(texto, fonte_usada, cor, x, y, centralizado=False):
    imagem = fonte_usada.render(str(texto), True, cor)
    if centralizado:
        retangulo = imagem.get_rect(center=(x, y))
        tela.blit(imagem, retangulo)
    else:
        tela.blit(imagem, (x, y))


def criar_fruta():
    nome, cor = random.choice(TIPOS_FRUTAS)
    x = random.randint(20, LARGURA - 20)
    frutas.append({
        "x": float(x),
        "y": -20.0,
        "nome": nome,
        "cor": cor,
        "raio": 13
    })


def reiniciar():
    global pontos, velocidade_fruta, ultimo_spawn, fim_de_jogo
    pontos = 0
    velocidade_fruta = 180
    frutas.clear()
    cesta.x = LARGURA // 2 - CESTA_LARGURA // 2
    cesta.y = ALTURA - 70
    ultimo_spawn = time.perf_counter()
    fim_de_jogo = False


def desenhar_cesta():
    # Cesta em estilo simples/pixelado
    pygame.draw.rect(tela, MARROM_ESCURO, cesta, border_radius=4)
    pygame.draw.rect(
        tela, MARROM,
        (cesta.x + 4, cesta.y + 5, cesta.width - 8, cesta.height - 7),
        border_radius=3
    )
    for x in range(cesta.x + 12, cesta.right - 8, 15):
        pygame.draw.line(
            tela, (190, 135, 75),
            (x, cesta.y + 7), (x, cesta.bottom - 4), 2
        )
    pygame.draw.line(
        tela, MARROM_ESCURO,
        (cesta.x + 4, cesta.y + 4),
        (cesta.right - 4, cesta.y + 4), 4
    )


def desenhar_fruta(fruta):
    x = int(fruta["x"])
    y = int(fruta["y"])
    cor = fruta["cor"]
    raio = fruta["raio"]

    if fruta["nome"] == "BANANA":
        pygame.draw.arc(
            tela, cor,
            (x - raio, y - raio, raio * 2, raio * 2),
            0.2, 2.8, 7
        )
        pygame.draw.circle(tela, cor, (x - 7, y + 3), 5)
        pygame.draw.circle(tela, cor, (x + 7, y + 3), 5)
    elif fruta["nome"] == "MORANGO":
        pygame.draw.circle(tela, cor, (x - 5, y - 2), 8)
        pygame.draw.circle(tela, cor, (x + 5, y - 2), 8)
        pygame.draw.polygon(
            tela, cor,
            [(x - 12, y), (x + 12, y), (x, y + 15)]
        )
    elif fruta["nome"] == "UVA":
        for ox, oy in [(-5, -5), (5, -5), (0, 3), (-5, 5), (5, 5)]:
            pygame.draw.circle(tela, cor, (x + ox, y + oy), 6)
    else:
        pygame.draw.circle(tela, cor, (x, y), raio)
        pygame.draw.rect(tela, (95, 60, 30), (x - 2, y - 17, 4, 8))
        pygame.draw.ellipse(tela, VERDE, (x + 1, y - 17, 10, 5))


def desenhar_fundo():
    tela.fill(AZUL_CLARO)

    # Nuvens decorativas
    pygame.draw.circle(tela, BRANCO, (70, 105), 18)
    pygame.draw.circle(tela, BRANCO, (92, 98), 23)
    pygame.draw.circle(tela, BRANCO, (116, 106), 17)

    pygame.draw.circle(tela, BRANCO, (360, 160), 16)
    pygame.draw.circle(tela, BRANCO, (382, 151), 22)
    pygame.draw.circle(tela, BRANCO, (405, 160), 16)

    # Chão
    pygame.draw.rect(tela, (125, 190, 105), (0, ALTURA - 28, LARGURA, 28))
    pygame.draw.line(tela, VERDE, (0, ALTURA - 28), (LARGURA, ALTURA - 28), 4)


async def main():
    global pontos, velocidade_fruta, ultimo_spawn, fim_de_jogo

    rodando = True
    ultimo_tempo = time.perf_counter()
    ultimo_spawn = ultimo_tempo

    while rodando:
        # Delta time para manter o movimento consistente
        agora = time.perf_counter()
        dt = min(agora - ultimo_tempo, 0.05)
        ultimo_tempo = agora

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif fim_de_jogo and evento.key in (pygame.K_RETURN, pygame.K_r):
                    reiniciar()

        teclas = pygame.key.get_pressed()

        if not fim_de_jogo:
            # Movimento da cesta: WASD ou setas
            dx = 0
            dy = 0

            if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
                dx -= velocidade_cesta * dt
            if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
                dx += velocidade_cesta * dt
            if teclas[pygame.K_w] or teclas[pygame.K_UP]:
                dy -= velocidade_cesta * dt
            if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
                dy += velocidade_cesta * dt

            cesta.x += round(dx)
            cesta.y += round(dy)
            cesta.clamp_ip(tela.get_rect())

            # Cria uma fruta a cada 0,8 segundo
            if agora - ultimo_spawn >= 0.8:
                criar_fruta()
                ultimo_spawn = agora

            # Move as frutas e verifica coleta
            cesta_colisao = cesta.inflate(-8, 0)
            for fruta in frutas[:]:
                fruta["y"] += velocidade_fruta * dt
                fruta_rect = pygame.Rect(
                    int(fruta["x"] - fruta["raio"]),
                    int(fruta["y"] - fruta["raio"]),
                    fruta["raio"] * 2,
                    fruta["raio"] * 2
                )

                if cesta_colisao.colliderect(fruta_rect):
                    frutas.remove(fruta)
                    pontos += 1
                    if pontos % 5 == 0:
                        velocidade_fruta += 20
                elif fruta["y"] - fruta["raio"] > ALTURA:
                    frutas.remove(fruta)

        # DESENHO
        desenhar_fundo()

        for fruta in frutas:
            desenhar_fruta(fruta)

        desenhar_cesta()

        pygame.draw.rect(tela, (245, 245, 235), (10, 10, 175, 42), border_radius=8)
        pygame.draw.rect(tela, MARROM, (10, 10, 175, 42), 2, border_radius=8)
        desenhar_texto(f"Pontos: {pontos}", fonte, PRETO, 22, 17)

        desenhar_texto(
            "WASD ou SETAS para mover",
            fonte_pequena, PRETO, LARGURA // 2, 35, centralizado=True
        )

        if fim_de_jogo:
            camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            camada.fill((0, 0, 0, 175))
            tela.blit(camada, (0, 0))
            desenhar_texto(
                "FIM DE JOGO", fonte_grande, AMARELO,
                LARGURA // 2, ALTURA // 2 - 45, centralizado=True
            )
            desenhar_texto(
                f"Pontuacao final: {pontos}", fonte, BRANCO,
                LARGURA // 2, ALTURA // 2 + 5, centralizado=True
            )
            desenhar_texto(
                "Pressione ENTER ou R para reiniciar",
                fonte_pequena, BRANCO,
                LARGURA // 2, ALTURA // 2 + 50, centralizado=True
            )

        pygame.display.flip()
        relogio.tick(FPS)

        # Necessário para ceder o controle ao navegador no Pygbag.
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
