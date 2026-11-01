
import pygame
import random
import math
import asyncio
import sys

pygame.init()

W, H = 1000, 700
tela = pygame.display.set_mode((W, H))
pygame.display.set_caption("🎀 Reino Rosa Mágico")
clock = pygame.time.Clock()

ROSA = (255, 105, 180)
ROSA_CLARO = (255, 215, 235)
ROXO = (180, 120, 255)
BRANCO = (255, 255, 255)
OURO = (255, 220, 90)
PRETO = (75, 40, 65)
AZUL = (100, 220, 255)
VERDE = (100, 210, 130)

fonte = pygame.font.SysFont("arial", 22, bold=True)
titulo = pygame.font.SysFont("arial", 36, bold=True)

jogadores = [
    {"r": pygame.Rect(100, 150, 32, 40),
     "cor": ROSA, "nome": "Luna", "vida": 3, "pontos": 0},
    {"r": pygame.Rect(160, 150, 32, 40),
     "cor": ROXO, "nome": "Estrela", "vida": 3, "pontos": 0}
]

mundo_w, mundo_h = 1800, 1300

obstaculos = [
    pygame.Rect(250, 200, 110, 150),
    pygame.Rect(500, 100, 150, 100),
    pygame.Rect(750, 250, 100, 170),
    pygame.Rect(1100, 160, 140, 100),
    pygame.Rect(1400, 330, 130, 150),
    pygame.Rect(350, 650, 150, 110),
    pygame.Rect(700, 600, 110, 160),
    pygame.Rect(1050, 680, 170, 110),
    pygame.Rect(1450, 800, 120, 150),
    pygame.Rect(420, 1000, 180, 100)
]

flores = [
    (random.randrange(mundo_w), random.randrange(mundo_h),
     random.choice([ROSA, ROXO, BRANCO, OURO]))
    for _ in range(300)
]

cristais = [
    pygame.Rect(random.randrange(70, mundo_w - 70),
                random.randrange(130, mundo_h - 70), 24, 24)
    for _ in range(25)
]

moedas = [
    pygame.Rect(random.randrange(70, mundo_w - 70),
                random.randrange(130, mundo_h - 70), 20, 20)
    for _ in range(15)
]

inimigos = [
    pygame.Rect(550, 330, 32, 32),
    pygame.Rect(950, 430, 32, 32),
    pygame.Rect(1450, 650, 32, 32),
    pygame.Rect(750, 900, 32, 32)
]

pocoes = [
    pygame.Rect(550, 450, 24, 28),
    pygame.Rect(1250, 880, 24, 28)
]

portal = pygame.Rect(1610, 160, 90, 110)
particulas = []
cristais_pego = 0
fim = False
vitoria = False
tempo = 0
mensagem = "Coletem 12 cristais para abrir o portal!"

def escrever(txt, x, y, cor=PRETO, f=fonte):
    tela.blit(f.render(str(txt), True, cor), (int(x), int(y)))

def explosao(x, y, cor):
    for _ in range(15):
        particulas.append([
            float(x), float(y),
            random.uniform(-100, 100),
            random.uniform(-130, 30),
            0.8, cor
        ])

def desenhar_fada(r, cor, nome):
    x, y = r.center
    pulinho = int(math.sin(tempo * 10) * 3)

    pygame.draw.ellipse(tela, (220, 160, 200),
                        (x - 15, y + 14, 30, 8))

    # Asas magicas
    pygame.draw.ellipse(tela, BRANCO,
                        (x - 20, y - 10 + pulinho, 15, 22))
    pygame.draw.ellipse(tela, (240, 220, 255),
                        (x + 5, y - 10 + pulinho, 15, 22))

    # Vestido
    pygame.draw.polygon(tela, cor, [
        (x - 11, y - 2 + pulinho),
        (x + 11, y - 2 + pulinho),
        (x + 16, y + 13 + pulinho),
        (x - 16, y + 13 + pulinho)
    ])

    # Cabeca e cabelo
    pygame.draw.circle(tela, (120, 75, 65),
                       (x, y - 12 + pulinho), 14)
    pygame.draw.circle(tela, (255, 225, 200),
                       (x, y - 10 + pulinho), 11)

    pygame.draw.circle(tela, PRETO, (x - 4, y - 10 + pulinho), 2)
    pygame.draw.circle(tela, PRETO, (x + 4, y - 10 + pulinho), 2)
    pygame.draw.circle(tela, ROSA, (x - 7, y - 6 + pulinho), 2)
    pygame.draw.circle(tela, ROSA, (x + 7, y - 6 + pulinho), 2)

    # Lacinho ou coroa
    if nome == "Luna":
        pygame.draw.circle(tela, ROSA, (x - 10, y - 25 + pulinho), 5)
        pygame.draw.circle(tela, ROSA_CLARO,
                           (x - 15, y - 28 + pulinho), 4)
    else:
        pygame.draw.polygon(tela, OURO, [
            (x - 10, y - 23 + pulinho),
            (x - 12, y - 34 + pulinho),
            (x - 3, y - 29 + pulinho),
            (x, y - 37 + pulinho),
            (x + 4, y - 29 + pulinho),
            (x + 12, y - 34 + pulinho),
            (x + 10, y - 23 + pulinho)
        ])

    escrever(nome, x - 22, y - 47, PRETO,
             pygame.font.SysFont("arial", 14, bold=True))

def mover(j, dx, dy, dt):
    r = j["r"]
    dx *= 220 * dt
    dy *= 220 * dt

    r.x += round(dx)
    for o in obstaculos:
        if r.colliderect(o):
            if dx > 0:
                r.right = o.left
            elif dx < 0:
                r.left = o.right

    r.y += round(dy)
    for o in obstaculos:
        if r.colliderect(o):
            if dy > 0:
                r.bottom = o.top
            elif dy < 0:
                r.top = o.bottom

    r.clamp_ip(pygame.Rect(10, 100, mundo_w - 20, mundo_h - 110))

def reiniciar():
    global cristais_pego, fim, vitoria, mensagem
    cristais_pego = 0
    fim = False
    vitoria = False
    mensagem = "Nova aventura! Coletem os cristais!"

    jogadores[0]["r"].topleft = (100, 150)
    jogadores[1]["r"].topleft = (160, 150)

    for j in jogadores:
        j["vida"] = 3
        j["pontos"] = 0

    cristais.clear()
    for _ in range(25):
        cristais.append(pygame.Rect(
            random.randrange(70, mundo_w - 70),
            random.randrange(130, mundo_h - 70), 24, 24
        ))

    moedas.clear()
    for _ in range(15):
        moedas.append(pygame.Rect(
            random.randrange(70, mundo_w - 70),
            random.randrange(130, mundo_h - 70), 20, 20
        ))

async def main():
    global tempo, cristais_pego, fim, vitoria, mensagem
    rodando = True

    while rodando:
        dt = min(clock.tick(60) / 1000, 0.035)
        tempo += dt

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                if evento.key == pygame.K_r and fim:
                    reiniciar()

        teclas = pygame.key.get_pressed()

        if not fim:
            controles = [
                (int(teclas[pygame.K_d]) - int(teclas[pygame.K_a]),
                 int(teclas[pygame.K_s]) - int(teclas[pygame.K_w])),
                (int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT]),
                 int(teclas[pygame.K_DOWN]) - int(teclas[pygame.K_UP]))
            ]

            for j, (dx, dy) in zip(jogadores, controles):
                if dx and dy:
                    dx *= 0.707
                    dy *= 0.707
                mover(j, dx, dy, dt)

            # Coletar cristais
            for c in cristais[:]:
                for j in jogadores:
                    if j["r"].colliderect(c):
                        cristais.remove(c)
                        cristais_pego += 1
                        j["pontos"] += 1
                        explosao(c.centerx, c.centery, AZUL)
                        mensagem = "Cristal magico coletado!"
                        break

            # Coletar moedas
            for m in moedas[:]:
                for j in jogadores:
                    if j["r"].colliderect(m):
                        moedas.remove(m)
                        j["pontos"] += 2
                        explosao(m.centerx, m.centery, OURO)
                        mensagem = "Moeda magica! +2 pontos!"
                        break

            # Pocoes
            for p in pocoes[:]:
                for j in jogadores:
                    if j["r"].colliderect(p) and j["vida"] < 3:
                        j["vida"] += 1
                        pocoes.remove(p)
                        explosao(p.centerx, p.centery, VERDE)
                        mensagem = "Vida recuperada!"
                        break

            # Inimigos perseguem as jogadoras
            for e in inimigos:
                alvo = min(jogadores, key=lambda j: math.hypot(
                    j["r"].centerx - e.centerx,
                    j["r"].centery - e.centery
                ))

                vx = alvo["r"].centerx - e.centerx
                vy = alvo["r"].centery - e.centery
                dist = math.hypot(vx, vy)

                if 0 < dist < 330:
                    e.x += round(vx / dist * 70 * dt)
                    e.y += round(vy / dist * 70 * dt)

                for j in jogadores:
                    if e.colliderect(j["r"]):
                        if j.get("protecao", 0) <= 0:
                            j["vida"] -= 1
                            j["protecao"] = 1.5
                            explosao(j["r"].centerx, j["r"].centery, ROSA)
                            mensagem = j["nome"] + " foi atingida!"

                            if j["vida"] <= 0:
                                fim = True
                                vitoria = False
                            break

            for j in jogadores:
                j["protecao"] = max(0, j.get("protecao", 0) - dt)

            # Portal final
            if cristais_pego >= 12:
                juntas = all(math.hypot(
                    j["r"].centerx - portal.centerx,
                    j["r"].centery - portal.centery
                ) < 140 for j in jogadores)

                if juntas:
                    fim = True
                    vitoria = True

        # Particulas
        for p in particulas[:]:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 150 * dt
            p[4] -= dt
            if p[4] <= 0:
                particulas.remove(p)

        # Camera acompanha as duas
        cx = sum(j["r"].centerx for j in jogadores) / 2
        cy = sum(j["r"].centery for j in jogadores) / 2
        camx = max(0, min(mundo_w - W, cx - W / 2))
        camy = max(0, min(mundo_h - H, cy - H / 2))

        def pos(x, y):
            return int(x - camx), int(y - camy)

        # Fundo rosa
        tela.fill((255, 230, 242))

        # Flores
        for x, y, cor in flores:
            sx, sy = pos(x, y)
            if -10 < sx < W + 10 and -10 < sy < H + 10:
                pygame.draw.circle(tela, cor, (sx, sy), 3)
                pygame.draw.circle(tela, OURO, (sx, sy), 1)

        # Caminhos
        caminhos = [
            pygame.Rect(0, 430, mundo_w, 90),
            pygame.Rect(600, 100, 90, mundo_h - 100),
            pygame.Rect(600, 850, mundo_w - 600, 80)
        ]

        for c in caminhos:
            sx, sy = pos(c.x, c.y)
            pygame.draw.rect(tela, (255, 240, 225),
                             (sx, sy, c.width, c.height))

        # Arvores rosas
        for x, y, r in [
            (random_x, random_y, raio)
            for random_x, random_y, raio in []
        ]:
            pass

        # Decoracao fixa
        for x, y in [(100, 280), (420, 450), (900, 300),
                     (1200, 700), (800, 1100), (1600, 950)]:
            sx, sy = pos(x, y)
            pygame.draw.rect(tela, (145, 90, 90),
                             (sx - 4, sy, 8, 24))
            pygame.draw.circle(tela, (255, 155, 205), (sx, sy), 23)
            pygame.draw.circle(tela, (255, 200, 225), (sx - 7, sy - 8), 12)

        # Obstaculos
        for o in obstaculos:
            sx, sy = pos(o.x, o.y)
            pygame.draw.rect(tela, (205, 125, 165),
                             (sx + 5, sy + 5, o.width, o.height),
                             border_radius=16)
            pygame.draw.rect(tela, (255, 180, 215),
                             (sx, sy, o.width, o.height),
                             border_radius=16)
            pygame.draw.rect(tela, (255, 235, 245),
                             (sx + 8, sy + 8, o.width - 16, 10),
                             border_radius=5)

        # Portal
        px, py = pos(portal.x, portal.y)
        cor_portal = ROXO if cristais_pego >= 12 else (190, 65, 130)
        pygame.draw.ellipse(tela, cor_portal,
                            (px, py, portal.width, portal.height))
        pygame.draw.ellipse(tela, BRANCO,
                            (px + 12, py + 12, portal.width - 24,
                             portal.height - 24))
        pygame.draw.ellipse(tela, ROXO,
                            (px + 25, py + 20, portal.width - 50,
                             portal.height - 40))

        # Cristais
        for c in cristais:
            sx, sy = pos(c.x, c.y)
            brilho = math.sin(tempo * 4 + c.x) * 3
            pygame.draw.polygon(tela, AZUL, [
                (sx + 12, sy - 3 + brilho),
                (sx + 24, sy + 10),
                (sx + 12, sy + 25),
                (sx, sy + 10)
            ])
            pygame.draw.line(tela, BRANCO,
                             (sx + 12, sy), (sx + 12, sy + 19), 3)

        # Moedas
        for m in moedas:
            sx, sy = pos(m.x, m.y)
            pygame.draw.circle(tela, OURO, (sx + 10, sy + 10), 10)
            pygame.draw.circle(tela, BRANCO, (sx + 10, sy + 10), 5)

        # Pocoes
        for p in pocoes:
            sx, sy = pos(p.x, p.y)
            pygame.draw.rect(tela, BRANCO, (sx + 5, sy, 14, 7))
            pygame.draw.rect(tela, VERDE, (sx, sy + 6, 24, 22),
                             border_radius=6)

        # Monstrinhos
        for e in inimigos:
            sx, sy = pos(e.x, e.y)
            pygame.draw.circle(tela, (235, 85, 145), (sx + 16, sy + 16), 17)
            pygame.draw.circle(tela, BRANCO, (sx + 10, sy + 13), 5)
            pygame.draw.circle(tela, BRANCO, (sx + 22, sy + 13), 5)
            pygame.draw.circle(tela, PRETO, (sx + 10, sy + 13), 2)
            pygame.draw.circle(tela, PRETO, (sx + 22, sy + 13), 2)

        # Fadas
        for j in jogadores:
            sx, sy = pos(j["r"].x, j["r"].y)
            desenhar_fada(pygame.Rect(sx, sy, 32, 40),
                          j["cor"], j["nome"])

        # Particulas magicas
        for p in particulas:
            sx, sy = pos(p[0], p[1])
            if 0 <= sx < W and 0 <= sy < H:
                pygame.draw.circle(tela, p[5], (sx, sy),
                                   max(1, int(5 * min(1, p[4] * 2))))

        # Interface
        pygame.draw.rect(tela, (255, 245, 252), (0, 0, W, 100))
        pygame.draw.line(tela, ROSA, (0, 100), (W, 100), 3)
        escrever("REINO ROSA MAGICO", 20, 10, ROSA, titulo)
        escrever("Luna: WASD", 25, 62, ROSA)
        escrever("Estrela: SETAS", 180, 62, ROXO)

        for i, j in enumerate(jogadores):
            x = 570 + i * 205
            escrever(j["nome"], x, 8, j["cor"])
            escrever("Pontos: " + str(j["pontos"]),
                     x, 36, PRETO, pygame.font.SysFont("arial", 16))
            for n in range(3):
                cor = ROSA if n < j["vida"] else (225, 205, 215)
                pygame.draw.circle(tela, cor, (x + n * 22 + 5, 76), 7)

        escrever(f"Cristais: {cristais_pego}/12", 20, 110, ROSA)
        escrever(
            "Portal aberto! Vao juntas ate ele!" if cristais_pego >= 12
            else "Coletem cristais, moedas e pocoes!",
            20, 140, ROXO
        )

        if mensagem:
            pygame.draw.rect(tela, BRANCO, (250, 650, 500, 35),
                             border_radius=12)
            escrever(mensagem, 270, 657, ROSA)

        if fim:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((70, 25, 80, 170))
            tela.blit(overlay, (0, 0))
            pygame.draw.rect(tela, BRANCO, (150, 210, 700, 260),
                             border_radius=30)

            if vitoria:
                escrever("MISSAO CONCLUIDA!", 290, 245, ROSA, titulo)
                escrever("As amigas salvaram o reino!", 290, 315, ROXO)
            else:
                escrever("FIM DA AVENTURA", 320, 245, ROSA, titulo)
                escrever("Tentem novamente!", 350, 315, ROXO)

            escrever("Aperte R para recomecar", 340, 410, ROSA)

        pygame.display.flip()

        # Permite que o asyncio processe outras tarefas assíncronas.
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
