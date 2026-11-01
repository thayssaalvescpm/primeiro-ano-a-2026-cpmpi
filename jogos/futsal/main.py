import pygame
import math
import random
import asyncio

pygame.init()

# Configurações da janela
LARGURA, ALTURA = 1000, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Futebol - Pygame")

RELOGIO = pygame.time.Clock()
FONTE = pygame.font.SysFont("Arial", 30, bold=True)
FONTE_PEQUENA = pygame.font.SysFont("Arial", 18)

# Cores
VERDE = (35, 145, 65)
VERDE_CLARO = (42, 155, 72)
BRANCO = (255, 255, 255)
AZUL = (35, 100, 240)
VERMELHO = (230, 55, 55)
PRETO = (20, 20, 20)
AMARELO = (255, 220, 40)

# Campo
MARGEM = 40
GOL_ALTURA = 170
GOL_TOPO = ALTURA // 2 - GOL_ALTURA // 2
GOL_BASE = ALTURA // 2 + GOL_ALTURA // 2

# Jogadores e bola
RAIO_JOGADOR = 17
RAIO_BOLA = 10
VELOCIDADE = 4.5

jogador1 = pygame.Vector2(250, ALTURA // 2)
jogador2 = pygame.Vector2(750, ALTURA // 2)
bola = pygame.Vector2(LARGURA // 2, ALTURA // 2)
vel_bola = pygame.Vector2(0, 0)

placar1 = 0
placar2 = 0
tempo_gol = 0


def reiniciar_posicoes():
    global vel_bola
    jogador1.update(250, ALTURA // 2)
    jogador2.update(750, ALTURA // 2)
    bola.update(LARGURA // 2, ALTURA // 2)
    vel_bola.update(0, 0)


def desenhar_campo():
    TELA.fill(VERDE)

    for i in range(10):
        x = i * LARGURA // 10
        cor = VERDE_CLARO if i % 2 == 0 else VERDE
        pygame.draw.rect(TELA, cor, (x, 0, LARGURA // 10 + 1, ALTURA))

    pygame.draw.rect(TELA, BRANCO, (MARGEM, MARGEM, LARGURA - 2 * MARGEM, ALTURA - 2 * MARGEM), 3)
    pygame.draw.line(TELA, BRANCO, (LARGURA // 2, MARGEM), (LARGURA // 2, ALTURA - MARGEM), 3)
    pygame.draw.circle(TELA, BRANCO, (LARGURA // 2, ALTURA // 2), 75, 3)
    pygame.draw.circle(TELA, BRANCO, (LARGURA // 2, ALTURA // 2), 5)

    pygame.draw.rect(TELA, BRANCO, (MARGEM, 170, 120, 260), 3)
    pygame.draw.rect(TELA, BRANCO, (LARGURA - MARGEM - 120, 170, 120, 260), 3)

    pygame.draw.rect(TELA, BRANCO, (0, GOL_TOPO, MARGEM, GOL_ALTURA), 4)
    pygame.draw.rect(TELA, BRANCO, (LARGURA - MARGEM, GOL_TOPO, MARGEM, GOL_ALTURA), 4)

    placar = FONTE.render(f"{placar1}  x  {placar2}", True, BRANCO)
    TELA.blit(placar, placar.get_rect(center=(LARGURA // 2, 20)))


def desenhar_jogador(pos, cor, numero):
    pygame.draw.circle(TELA, PRETO, (int(pos.x + 2), int(pos.y + 3)), RAIO_JOGADOR)
    pygame.draw.circle(TELA, cor, (int(pos.x), int(pos.y)), RAIO_JOGADOR)
    pygame.draw.circle(TELA, BRANCO, (int(pos.x), int(pos.y)), RAIO_JOGADOR, 2)
    texto = FONTE_PEQUENA.render(str(numero), True, BRANCO)
    TELA.blit(texto, texto.get_rect(center=(int(pos.x), int(pos.y))))


def mover_jogador(pos, dx, dy):
    movimento = pygame.Vector2(dx, dy)
    if movimento.length() > 0:
        movimento = movimento.normalize() * VELOCIDADE
        pos += movimento

    pos.x = max(MARGEM + RAIO_JOGADOR, min(LARGURA - MARGEM - RAIO_JOGADOR, pos.x))
    pos.y = max(MARGEM + RAIO_JOGADOR, min(ALTURA - MARGEM - RAIO_JOGADOR, pos.y))


def chutar(jogador, direcao):
    global vel_bola
    if jogador.distance_to(bola) < 48:
        direcao = pygame.Vector2(direcao)
        if direcao.length() == 0:
            direcao = bola - jogador
        if direcao.length() == 0:
            direcao = pygame.Vector2(1, 0)
        vel_bola = direcao.normalize() * 10


def atualizar_bola():
    global placar1, placar2, tempo_gol, vel_bola

    bola.update(bola.x + vel_bola.x, bola.y + vel_bola.y)
    vel_bola *= 0.985

    if vel_bola.length() < 0.08:
        vel_bola.update(0, 0)

    if bola.y - RAIO_BOLA < MARGEM:
        bola.y = MARGEM + RAIO_BOLA
        vel_bola.y *= -0.8

    if bola.y + RAIO_BOLA > ALTURA - MARGEM:
        bola.y = ALTURA - MARGEM - RAIO_BOLA
        vel_bola.y *= -0.8

    dentro_do_gol = GOL_TOPO < bola.y < GOL_BASE

    if bola.x < MARGEM:
        if dentro_do_gol:
            placar2 += 1
            tempo_gol = pygame.time.get_ticks()
            reiniciar_posicoes()
        else:
            bola.x = MARGEM + RAIO_BOLA
            vel_bola.x *= -0.8
    elif bola.x > LARGURA - MARGEM:
        if dentro_do_gol:
            placar1 += 1
            tempo_gol = pygame.time.get_ticks()
            reiniciar_posicoes()
        else:
            bola.x = LARGURA - MARGEM - RAIO_BOLA
            vel_bola.x *= -0.8


def colisao_jogador_bola(jogador):
    global vel_bola
    diferenca = bola - jogador
    distancia = diferenca.length()
    distancia_minima = RAIO_JOGADOR + RAIO_BOLA

    if 0 < distancia < distancia_minima:
        direcao = diferenca.normalize()
        bola.update(jogador.x + direcao.x * distancia_minima, jogador.y + direcao.y * distancia_minima)
        vel_bola += direcao * 2.2
        if vel_bola.length() > 12:
            vel_bola.scale_to_length(12)


def desenhar_bola():
    pygame.draw.circle(TELA, PRETO, (int(bola.x + 2), int(bola.y + 2)), RAIO_BOLA)
    pygame.draw.circle(TELA, BRANCO, (int(bola.x), int(bola.y)), RAIO_BOLA)
    pygame.draw.circle(TELA, PRETO, (int(bola.x), int(bola.y)), RAIO_BOLA, 2)


async def main():
    global placar1, placar2
    rodando = True

    while rodando:
        RELOGIO.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_r:
                    placar1 = 0
                    placar2 = 0
                    reiniciar_posicoes()
                elif evento.key == pygame.K_SPACE:
                    teclas = pygame.key.get_pressed()
                    dx = int(teclas[pygame.K_d]) - int(teclas[pygame.K_a])
                    dy = int(teclas[pygame.K_s]) - int(teclas[pygame.K_w])
                    chutar(jogador1, (dx, dy))
                elif evento.key == pygame.K_RETURN:
                    teclas = pygame.key.get_pressed()
                    dx = int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT])
                    dy = int(teclas[pygame.K_DOWN]) - int(teclas[pygame.K_UP])
                    chutar(jogador2, (dx, dy))

        teclas = pygame.key.get_pressed()

        dx1 = int(teclas[pygame.K_d]) - int(teclas[pygame.K_a])
        dy1 = int(teclas[pygame.K_s]) - int(teclas[pygame.K_w])
        mover_jogador(jogador1, dx1, dy1)

        dx2 = int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT])
        dy2 = int(teclas[pygame.K_DOWN]) - int(teclas[pygame.K_UP])
        mover_jogador(jogador2, dx2, dy2)

        atualizar_bola()
        colisao_jogador_bola(jogador1)
        colisao_jogador_bola(jogador2)

        desenhar_campo()
        desenhar_jogador(jogador1, AZUL, 1)
        desenhar_jogador(jogador2, VERMELHO, 2)
        desenhar_bola()

        if pygame.time.get_ticks() - tempo_gol < 1300:
            mensagem = FONTE.render("GOOOOL!", True, AMARELO)
            TELA.blit(mensagem, mensagem.get_rect(center=(LARGURA // 2, 75)))

        instrucoes = FONTE_PEQUENA.render(
            "Azul: WASD + ESPACO | Vermelho: SETAS + ENTER | R: reiniciar | ESC: sair",
            True, BRANCO
        )
        TELA.blit(instrucoes, instrucoes.get_rect(center=(LARGURA // 2, ALTURA - 15)))
        pygame.display.flip()

        # Cede o controle ao event loop do asyncio.
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
