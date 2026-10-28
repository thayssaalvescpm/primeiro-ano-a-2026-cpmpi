import asyncio
import math
import random
import pygame

pygame.init()

# ==================================================
# CONFIGURAÇÕES
# ==================================================

LARGURA, ALTURA = 1000, 700
FPS = 60

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Campo Sombrio - Sobrevivência")

RELOGIO = pygame.time.Clock()

FONTE = pygame.font.Font(None, 27)
FONTE_MEDIA = pygame.font.Font(None, 42)
FONTE_GRANDE = pygame.font.Font(None, 68)

BRANCO = (235, 237, 222)
AMARELO = (255, 220, 130)
VERMELHO = (190, 60, 55)


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def texto(msg, fonte, cor, pos, centro=False):
    # Se houver emoji, tenta usar a fonte de emojis do Windows.
    # Para textos comuns, mantém a fonte original do jogo.
    tem_emoji = any(
        ord(caractere) >= 0x1F000
        or 0x2600 <= ord(caractere) <= 0x27BF
        for caractere in msg
    )

    if tem_emoji:
        tamanho = max(16, fonte.get_height())
        try:
            fonte_usada = pygame.font.SysFont("Segoe UI Emoji", tamanho)
            imagem = fonte_usada.render(msg, True, cor)
        except (pygame.error, TypeError):
            imagem = fonte.render(msg, True, cor)
    else:
        imagem = fonte.render(msg, True, cor)

    rect = imagem.get_rect()
    if centro:
        rect.center = pos
    else:
        rect.topleft = pos

    TELA.blit(imagem, rect)


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def distancia(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def ponto_no_cone(px, py, origem, direcao, alcance, angulo):
    """
    Verifica se um ponto está dentro do cone da lanterna.
    """

    dx = px - origem.x
    dy = py - origem.y

    dist = math.hypot(dx, dy)

    if dist > alcance or dist == 0:
        return False

    vetor = pygame.Vector2(dx, dy).normalize()

    produto = max(-1, min(1, direcao.dot(vetor)))
    angulo_entre = math.degrees(math.acos(produto))

    return angulo_entre <= angulo


# ==================================================
# JOGADOR
# ==================================================

class Jogador:
    def __init__(self):
        self.x = LARGURA / 2
        self.y = ALTURA / 2

        self.raio = 14
        self.velocidade = 245

        self.vida = 100
        self.vida_max = 100

        self.invuln = 0

        # Direção inicial da lanterna.
        self.direcao = pygame.Vector2(1, 0)

        # Configurações da lanterna.
        self.alcance_lanterna = 255
        self.angulo_lanterna = 32
        self.lanterna_ligada = False

    def atualizar(self, dt, teclas, obstaculos):
        movimento = pygame.Vector2(0, 0)

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            movimento.x -= 1

        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            movimento.x += 1

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            movimento.y -= 1

        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            movimento.y += 1

        if movimento.length_squared() > 0:
            movimento = movimento.normalize()
            self.direcao = movimento

        dx = movimento.x * self.velocidade * dt
        dy = movimento.y * self.velocidade * dt

        # Movimento horizontal.
        self.x = limitar(
            self.x + dx,
            20,
            LARGURA - 20
        )

        if self.colide(obstaculos):
            self.x -= dx

        # Movimento vertical.
        self.y = limitar(
            self.y + dy,
            48,
            ALTURA - 20
        )

        if self.colide(obstaculos):
            self.y -= dy

        self.invuln = max(0, self.invuln - dt)

    def colide(self, obstaculos):
        for obstaculo in obstaculos:
            px = limitar(
                self.x,
                obstaculo.left,
                obstaculo.right
            )

            py = limitar(
                self.y,
                obstaculo.top,
                obstaculo.bottom
            )

            if distancia(self.x, self.y, px, py) < self.raio:
                return True

        return False

    def dano(self, valor):
        if self.invuln <= 0:
            self.vida -= valor
            self.invuln = 0.7

    def origem_lanterna(self):
        """
        Posição da lanterna na frente do personagem.
        """

        return pygame.Vector2(
            self.x + self.direcao.x * 17,
            self.y - 17 + self.direcao.y * 17
        )

    def desenhar_lanterna(self):
        """
        Desenha o cone de luz usando transparência.
        """

        if not self.lanterna_ligada:
            return

        origem = self.origem_lanterna()
        direcao = self.direcao.normalize()

        alcance = self.alcance_lanterna
        angulo = self.angulo_lanterna

        # Vetores que delimitam as bordas do cone.
        angulo_central = math.atan2(
            direcao.y,
            direcao.x
        )

        angulo_esquerdo = angulo_central - math.radians(angulo)
        angulo_direito = angulo_central + math.radians(angulo)

        # Camada transparente para o feixe.
        luz = pygame.Surface(
            (LARGURA, ALTURA),
            pygame.SRCALPHA
        )

        # Pontos que formam o cone.
        pontos = [
            (int(origem.x), int(origem.y))
        ]

        quantidade_pontos = 35

        for i in range(quantidade_pontos + 1):
            proporcao = i / quantidade_pontos

            a = (
                angulo_esquerdo
                + (angulo_direito - angulo_esquerdo) * proporcao
            )

            px = origem.x + math.cos(a) * alcance
            py = origem.y + math.sin(a) * alcance

            pontos.append((int(px), int(py)))

        # Cone externo: luz amarelada suave.
        pygame.draw.polygon(
            luz,
            (255, 220, 130, 42),
            pontos
        )

        # Cone intermediário: região mais iluminada.
        alcance_medio = alcance * 0.76
        angulo_medio = math.radians(angulo * 0.72)

        pontos_medios = [
            (int(origem.x), int(origem.y))
        ]

        for i in range(quantidade_pontos + 1):
            proporcao = i / quantidade_pontos

            a = (
                angulo_central - angulo_medio
                + proporcao * angulo_medio * 2
            )

            px = origem.x + math.cos(a) * alcance_medio
            py = origem.y + math.sin(a) * alcance_medio

            pontos_medios.append((int(px), int(py)))

        pygame.draw.polygon(
            luz,
            (255, 231, 165, 32),
            pontos_medios
        )

        # Região central mais clara.
        alcance_central = alcance * 0.48
        angulo_central_luz = math.radians(angulo * 0.40)

        pontos_centrais = [
            (int(origem.x), int(origem.y))
        ]

        for i in range(quantidade_pontos + 1):
            proporcao = i / quantidade_pontos

            a = (
                angulo_central - angulo_central_luz
                + proporcao * angulo_central_luz * 2
            )

            px = origem.x + math.cos(a) * alcance_central
            py = origem.y + math.sin(a) * alcance_central

            pontos_centrais.append((int(px), int(py)))

        pygame.draw.polygon(
            luz,
            (255, 245, 205, 35),
            pontos_centrais
        )

        TELA.blit(luz, (0, 0))

    def desenhar(self):
        x = int(self.x)
        y = int(self.y)

        pisca = (
            self.invuln > 0
            and int(pygame.time.get_ticks() / 80) % 2 == 0
        )

        # Sombra.
        pygame.draw.ellipse(
            TELA,
            (10, 17, 13),
            (x - 18, y - 1, 36, 17)
        )

        # Pernas.
        pygame.draw.line(
            TELA,
            (40, 48, 62),
            (x - 5, y - 5),
            (x - 7, y + 8),
            5
        )

        pygame.draw.line(
            TELA,
            (40, 48, 62),
            (x + 5, y - 5),
            (x + 7, y + 8),
            5
        )

        # Tênis.
        pygame.draw.ellipse(
            TELA,
            (35, 38, 42),
            (x - 14, y + 4, 13, 7)
        )

        pygame.draw.ellipse(
            TELA,
            (35, 38, 42),
            (x + 1, y + 4, 13, 7)
        )

        # Camiseta.
        cor_camisa = BRANCO if pisca else (55, 133, 197)

        pygame.draw.ellipse(
            TELA,
            (25, 52, 72),
            (x - 12, y - 21, 24, 25)
        )

        pygame.draw.ellipse(
            TELA,
            cor_camisa,
            (x - 11, y - 22, 22, 24)
        )

        # Bermuda.
        pygame.draw.rect(
            TELA,
            (47, 66, 91),
            (x - 10, y - 7, 20, 9),
            border_radius=3
        )

        # Cabeça.
        pygame.draw.circle(
            TELA,
            (190, 126, 83),
            (x - 9, y - 29),
            3
        )

        pygame.draw.circle(
            TELA,
            (190, 126, 83),
            (x + 9, y - 29),
            3
        )

        pygame.draw.ellipse(
            TELA,
            (224, 174, 126),
            (x - 9, y - 40, 18, 21)
        )

        # Cabelo castanho.
        pygame.draw.ellipse(
            TELA,
            (75, 43, 27),
            (x - 10, y - 44, 20, 12)
        )

        pygame.draw.circle(
            TELA,
            (75, 43, 27),
            (x - 6, y - 38),
            5
        )

        pygame.draw.circle(
            TELA,
            (75, 43, 27),
            (x + 1, y - 40),
            5
        )

        pygame.draw.polygon(
            TELA,
            (75, 43, 27),
            [
                (x - 8, y - 35),
                (x - 3, y - 37),
                (x - 1, y - 33),
                (x + 3, y - 37),
                (x + 7, y - 34),
                (x + 7, y - 31),
                (x - 8, y - 31)
            ]
        )

        # Olhos.
        pygame.draw.circle(
            TELA,
            (35, 29, 24),
            (x - 4, y - 31),
            1
        )

        pygame.draw.circle(
            TELA,
            (35, 29, 24),
            (x + 4, y - 31),
            1
        )

        # Braços segurando a lanterna.
        d = self.direcao.normalize()
        lateral = pygame.Vector2(-d.y, d.x)

        ombro1 = pygame.Vector2(x, y - 17) + lateral * 7
        ombro2 = pygame.Vector2(x, y - 17) - lateral * 7

        mao1 = pygame.Vector2(x, y - 17) + d * 11 + lateral * 3
        mao2 = pygame.Vector2(x, y - 17) + d * 7 - lateral * 3

        # Braço esquerdo.
        pygame.draw.line(
            TELA,
            (45, 107, 164),
            (int(ombro1.x), int(ombro1.y)),
            (int(mao1.x), int(mao1.y)),
            6
        )

        # Braço direito.
        pygame.draw.line(
            TELA,
            (45, 107, 164),
            (int(ombro2.x), int(ombro2.y)),
            (int(mao2.x), int(mao2.y)),
            6
        )

        # Corpo da lanterna.
        inicio_lanterna = pygame.Vector2(x, y - 17) + d * 9
        fim_lanterna = inicio_lanterna + d * 12

        pygame.draw.line(
            TELA,
            (35, 37, 40),
            (int(inicio_lanterna.x), int(inicio_lanterna.y)),
            (int(fim_lanterna.x), int(fim_lanterna.y)),
            7
        )

        pygame.draw.line(
            TELA,
            (155, 164, 165),
            (int(inicio_lanterna.x), int(inicio_lanterna.y)),
            (int(fim_lanterna.x), int(fim_lanterna.y)),
            3
        )

        # Lente da lanterna.
        pygame.draw.circle(
            TELA,
            (255, 235, 155),
            (int(fim_lanterna.x), int(fim_lanterna.y)),
            4
        )

        # Mãos.
        pygame.draw.circle(
            TELA,
            (224, 174, 126),
            (int(mao1.x), int(mao1.y)),
            4
        )

        pygame.draw.circle(
            TELA,
            (224, 174, 126),
            (int(mao2.x), int(mao2.y)),
            4
        )


# ==================================================
# MONSTROS
# ==================================================

class Inimigo:
    def __init__(self, x, y, fase, boss=False):
        self.x = float(x)
        self.y = float(y)

        self.boss = boss

        # Cada monstro comum recebe um visual e características próprias.
        self.tipo = "chefe" if boss else random.choice(
            ["sombrio", "venenoso", "fantasma", "brutamontes"]
        )

        tamanhos = {
            "sombrio": random.randint(12, 15),
            "venenoso": random.randint(12, 16),
            "fantasma": random.randint(11, 14),
            "brutamontes": random.randint(17, 20),
        }

        self.raio = 29 if boss else tamanhos[self.tipo]

        # Vida, velocidade e dano variam conforme o tipo.
        atributos = {
            "sombrio": (35, random.uniform(75, 94), 8, 55),
            "venenoso": (42, random.uniform(55, 72), 7, 60),
            "fantasma": (25, random.uniform(95, 115), 6, 48),
            "brutamontes": (65, random.uniform(42, 56), 14, 70),
        }

        if boss:
            self.vida_max = 900
            self.velocidade = 62 + fase * 2
            self.dano = 18
            self.dano_luz = 85
        else:
            (self.vida_max, velocidade_base, self.dano, self.dano_luz) = atributos[self.tipo]
            self.velocidade = velocidade_base + fase * 1.8

        self.vida = self.vida_max
        self.cooldown = 1.6 if boss else 0

    def atualizar(self, dt, jogador, obstaculos, balas_inimigas):
        direcao = pygame.Vector2(
            jogador.x - self.x,
            jogador.y - self.y
        )

        if direcao.length_squared() > 0:
            direcao = direcao.normalize()

        velocidade = self.velocidade

        if self.boss:
            velocidade *= (
                0.75
                + 0.25 * math.sin(
                    pygame.time.get_ticks() / 500
                )
            )

        ox, oy = self.x, self.y

        self.x += direcao.x * velocidade * dt
        self.y += direcao.y * velocidade * dt

        self.x = limitar(self.x, 18, LARGURA - 18)
        self.y = limitar(self.y, 45, ALTURA - 18)

        # Colisão com obstáculos.
        for obstaculo in obstaculos:
            px = limitar(
                self.x,
                obstaculo.left,
                obstaculo.right
            )

            py = limitar(
                self.y,
                obstaculo.top,
                obstaculo.bottom
            )

            if distancia(self.x, self.y, px, py) < self.raio:
                self.x, self.y = ox, oy
                break

        # O chefe ainda pode atacar o jogador.
        if self.boss:
            self.cooldown -= dt

            if self.cooldown <= 0:
                direcao_tiro = pygame.Vector2(
                    jogador.x - self.x,
                    jogador.y - self.y
                )

                if direcao_tiro.length_squared():
                    direcao_tiro = direcao_tiro.normalize()

                balas_inimigas.append(
                    BalaInimiga(
                        self.x,
                        self.y,
                        direcao_tiro.x,
                        direcao_tiro.y
                    )
                )

                if self.vida < self.vida_max * 0.5:
                    lateral = pygame.Vector2(
                        -direcao_tiro.y,
                        direcao_tiro.x
                    ) * 0.35

                    balas_inimigas.append(
                        BalaInimiga(
                            self.x,
                            self.y,
                            direcao_tiro.x + lateral.x,
                            direcao_tiro.y + lateral.y
                        )
                    )

                    balas_inimigas.append(
                        BalaInimiga(
                            self.x,
                            self.y,
                            direcao_tiro.x - lateral.x,
                            direcao_tiro.y - lateral.y
                        )
                    )

                self.cooldown = 1.25

    def desenhar(self):
        if self.boss:
            pygame.draw.ellipse(
                TELA,
                (10, 16, 14),
                (self.x - 34, self.y + 8, 68, 20)
            )

            pygame.draw.circle(
                TELA,
                (75, 34, 75),
                (int(self.x), int(self.y - 7)),
                self.raio + 4
            )

            pygame.draw.circle(
                TELA,
                (125, 52, 112),
                (int(self.x), int(self.y - 8)),
                self.raio
            )

            pygame.draw.circle(
                TELA,
                (255, 180, 94),
                (int(self.x - 9), int(self.y - 14)),
                4
            )

            pygame.draw.circle(
                TELA,
                (255, 180, 94),
                (int(self.x + 9), int(self.y - 14)),
                4
            )

            # Barra de vida do chefe.
            largura_barra = 90

            pygame.draw.rect(
                TELA,
                (35, 15, 24),
                (self.x - 45, self.y - 48, largura_barra, 7)
            )

            pygame.draw.rect(
                TELA,
                VERMELHO,
                (
                    self.x - 45,
                    self.y - 48,
                    largura_barra * max(0, self.vida) / self.vida_max,
                    7
                )
            )

        else:
            x, y = int(self.x), int(self.y)

            # Sombra no chão.
            pygame.draw.ellipse(
                TELA, (10, 18, 14),
                (x - self.raio, y + 1, self.raio * 2, 11)
            )

            if self.tipo == "sombrio":
                # Monstro clássico: corpo vermelho e olhos claros.
                pygame.draw.circle(TELA, (99, 43, 39), (x, y - 6), self.raio)
                pygame.draw.circle(TELA, (153, 61, 49), (x, y - 8), self.raio - 4)
                olho = (255, 220, 145)
                pygame.draw.circle(TELA, olho, (x - 4, y - 11), 2)
                pygame.draw.circle(TELA, olho, (x + 4, y - 11), 2)

            elif self.tipo == "venenoso":
                # Monstro verde, com manchas e olhos amarelos.
                pygame.draw.circle(TELA, (31, 83, 48), (x, y - 6), self.raio)
                pygame.draw.circle(TELA, (66, 150, 69), (x, y - 8), self.raio - 4)
                pygame.draw.circle(TELA, (145, 199, 71), (x - 6, y - 3), 3)
                pygame.draw.circle(TELA, (145, 199, 71), (x + 5, y - 13), 2)
                pygame.draw.circle(TELA, (255, 235, 105), (x - 4, y - 11), 2)
                pygame.draw.circle(TELA, (255, 235, 105), (x + 4, y - 11), 2)

            elif self.tipo == "fantasma":
                # Corpo azul-violeta com pequenas pontas na base.
                pygame.draw.circle(TELA, (62, 65, 126), (x, y - 8), self.raio)
                pygame.draw.ellipse(
                    TELA, (113, 132, 205),
                    (x - self.raio + 3, y - self.raio - 2,
                     (self.raio - 3) * 2, self.raio + 10)
                )
                pygame.draw.polygon(
                    TELA, (113, 132, 205),
                    [(x - 9, y + 1), (x - 4, y + 7), (x, y + 1),
                     (x + 5, y + 7), (x + 10, y + 1)]
                )
                pygame.draw.circle(TELA, (240, 250, 255), (x - 4, y - 10), 2)
                pygame.draw.circle(TELA, (240, 250, 255), (x + 4, y - 10), 2)

            elif self.tipo == "brutamontes":
                # Maior e mais resistente, com chifres e olhos vermelhos.
                pygame.draw.circle(TELA, (65, 35, 31), (x, y - 6), self.raio)
                pygame.draw.circle(TELA, (119, 65, 47), (x, y - 8), self.raio - 4)
                pygame.draw.polygon(
                    TELA, (85, 72, 61),
                    [(x - 11, y - self.raio), (x - 7, y - 8), (x - 2, y - 15)]
                )
                pygame.draw.polygon(
                    TELA, (85, 72, 61),
                    [(x + 11, y - self.raio), (x + 7, y - 8), (x + 2, y - 15)]
                )
                pygame.draw.circle(TELA, (255, 70, 55), (x - 6, y - 12), 3)
                pygame.draw.circle(TELA, (255, 70, 55), (x + 6, y - 12), 3)

            # Barra de vida pequena quando o monstro está sendo iluminado.
            if getattr(self, "iluminado", False):
                largura = self.raio * 2
                pygame.draw.rect(
                    TELA, (55, 20, 20),
                    (x - self.raio, y - self.raio - 8, largura, 4)
                )
                pygame.draw.rect(
                    TELA, (220, 70, 65),
                    (x - self.raio, y - self.raio - 8,
                     largura * max(0, self.vida) / self.vida_max, 4)
                )


# ==================================================
# PROJÉTEIS DO CHEFE
# ==================================================

class BalaInimiga:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y

        d = pygame.Vector2(dx, dy)

        if d.length_squared() == 0:
            d = pygame.Vector2(1, 0)

        self.direcao = d.normalize()
        self.velocidade = 245
        self.raio = 7

    def atualizar(self, dt):
        self.x += self.direcao.x * self.velocidade * dt
        self.y += self.direcao.y * self.velocidade * dt

    def desenhar(self):
        pygame.draw.circle(
            TELA,
            (240, 75, 65),
            (int(self.x), int(self.y)),
            self.raio
        )

        pygame.draw.circle(
            TELA,
            (255, 190, 130),
            (int(self.x), int(self.y)),
            3
        )


# ==================================================
# JOGO
# ==================================================

class Jogo:
    def __init__(self):
        self.fase = 1
        self.pontos = 0
        self.estado = "menu"

        self.jogador = Jogador()

        self.carregar_fase()
        self.estado = "menu"

    def carregar_fase(self):
        self.jogador.x = LARGURA / 2
        self.jogador.y = ALTURA / 2
        self.jogador.direcao = pygame.Vector2(1, 0)

        self.obstaculos = []
        self.decoracoes = []
        self.inimigos = []
        self.balas_inimigas = []

        self.tempo = 18 + min(
            10,
            (self.fase - 1) * 0.7
        )

        self.spawn = 1.0
        self.banner = 2.0

        # Criação de obstáculos.
        tentativas = 0
        quantidade = min(8 + self.fase // 2, 19)

        while len(self.obstaculos) < quantidade and tentativas < 500:
            tentativas += 1

            w, h = random.choice([
                (34, 34),
                (43, 30),
                (52, 38),
                (29, 43)
            ])

            x = random.randint(35, LARGURA - w - 35)
            y = random.randint(80, ALTURA - h - 30)

            rect = pygame.Rect(x, y, w, h)

            if distancia(
                x + w / 2,
                y + h / 2,
                LARGURA / 2,
                ALTURA / 2
            ) < 100:
                continue

            if any(
                rect.inflate(25, 25).colliderect(obstaculo)
                for obstaculo in self.obstaculos
            ):
                continue

            self.obstaculos.append(rect)

        # Decorações estáticas.
        for _ in range(180):
            self.decoracoes.append((
                random.randrange(8, LARGURA - 8),
                random.randrange(48, ALTURA - 8),
                random.choice([
                    "capim",
                    "capim",
                    "pedra",
                    "poça",
                    "galho"
                ])
            ))

        # Chefe final.
        if self.fase == 20:
            self.inimigos.append(
                Inimigo(130, 125, self.fase, True)
            )
        else:
            for _ in range(min(3 + self.fase // 2, 12)):
                self.criar_inimigo()

        self.estado = "jogando"

    def criar_inimigo(self):
        lado = random.randrange(4)

        if lado == 0:
            x = random.randint(20, LARGURA - 20)
            y = 55
        elif lado == 1:
            x = random.randint(20, LARGURA - 20)
            y = ALTURA - 20
        elif lado == 2:
            x = 20
            y = random.randint(55, ALTURA - 20)
        else:
            x = LARGURA - 20
            y = random.randint(55, ALTURA - 20)

        self.inimigos.append(
            Inimigo(x, y, self.fase)
        )

    def atualizar(self, dt):
        if self.estado != "jogando":
            return

        teclas = pygame.key.get_pressed()

        self.jogador.lanterna_ligada = teclas[pygame.K_SPACE]

        self.jogador.atualizar(
            dt,
            teclas,
            self.obstaculos
        )

        self.tempo -= dt
        self.spawn -= dt
        self.banner = max(0, self.banner - dt)

        # Criar novos monstros nas fases normais.
        if self.fase < 20 and self.spawn <= 0:
            if len(self.inimigos) < min(5 + self.fase, 16):
                self.criar_inimigo()

            self.spawn = max(
                0.5,
                1.8 - self.fase * 0.055
            )

        # Atualizar monstros e verificar o efeito da lanterna.
        origem = self.jogador.origem_lanterna()
        direcao = self.jogador.direcao.normalize()

        for inimigo in list(self.inimigos):
            inimigo.atualizar(
                dt,
                self.jogador,
                self.obstaculos,
                self.balas_inimigas
            )

            # Dano por contato.
            if distancia(
                inimigo.x,
                inimigo.y,
                self.jogador.x,
                self.jogador.y
            ) < inimigo.raio + self.jogador.raio:
                self.jogador.dano(inimigo.dano)

            # Dano causado pela luz.
            if self.jogador.lanterna_ligada:
                dentro_do_cone = ponto_no_cone(
                    inimigo.x,
                    inimigo.y - 8,
                    origem,
                    direcao,
                    self.jogador.alcance_lanterna,
                    self.jogador.angulo_lanterna
                )

                if dentro_do_cone:
                    inimigo.vida -= inimigo.dano_luz * dt * 2

                    # Brilho visual quando atingido pela luz.
                    inimigo.iluminado = True
                else:
                    inimigo.iluminado = False
            else:
                inimigo.iluminado = False

            if inimigo.vida <= 0:
                self.inimigos.remove(inimigo)

                if inimigo.boss:
                    self.pontos += 100
                else:
                    self.pontos += 10

        # Atualizar projéteis do chefe.
        for bala in list(self.balas_inimigas):
            bala.atualizar(dt)

            if (
                bala.x < -10
                or bala.x > LARGURA + 10
                or bala.y < 42
                or bala.y > ALTURA + 10
            ):
                self.balas_inimigas.remove(bala)

            elif distancia(
                bala.x,
                bala.y,
                self.jogador.x,
                self.jogador.y
            ) < bala.raio + self.jogador.raio:

                self.jogador.dano(12)
                self.balas_inimigas.remove(bala)

        # Estados do jogo.
        if self.jogador.vida <= 0:
            self.estado = "derrota"

        elif self.fase == 20 and not self.inimigos:
            self.estado = "vitoria"

        elif self.fase < 20 and self.tempo <= 0:
            self.estado = "fase_concluida"

    # ==================================================
    # CENÁRIO
    # ==================================================

    def desenhar_cenario(self):
        TELA.fill((23, 34, 27))

        # Textura do terreno.
        for x in range(0, LARGURA, 64):
            for y in range(42, ALTURA, 64):
                cor = (
                    (27, 40, 30)
                    if (x // 64 + y // 64) % 2 == 0
                    else (31, 44, 32)
                )

                pygame.draw.rect(
                    TELA,
                    cor,
                    (x, y, 64, 64)
                )

        # Trilha.
        pygame.draw.polygon(
            TELA,
            (57, 49, 39),
            [
                (-20, 435),
                (100, 397),
                (255, 414),
                (420, 356),
                (570, 380),
                (735, 330),
                (1020, 359),
                (1020, 404),
                (738, 384),
                (580, 423),
                (410, 400),
                (255, 451),
                (100, 438),
                (-20, 472)
            ]
        )

        # Detalhes da trilha.
        pygame.draw.lines(
            TELA,
            (78, 66, 48),
            False,
            [
                (0, 452),
                (125, 418),
                (260, 434),
                (420, 380),
                (575, 400),
                (740, 354),
                (1000, 384)
            ],
            2
        )

        # Decorações.
        for x, y, tipo in self.decoracoes:
            if tipo == "capim":
                pygame.draw.line(
                    TELA,
                    (39, 53, 34),
                    (x, y),
                    (x - 2, y - 7),
                    2
                )

                pygame.draw.line(
                    TELA,
                    (39, 53, 34),
                    (x, y),
                    (x + 4, y - 6),
                    2
                )

            elif tipo == "poça":
                pygame.draw.ellipse(
                    TELA,
                    (18, 29, 29),
                    (x, y, 17, 6)
                )

            elif tipo == "galho":
                pygame.draw.line(
                    TELA,
                    (52, 41, 32),
                    (x - 4, y + 2),
                    (x + 6, y - 3),
                    2
                )

            else:
                pygame.draw.ellipse(
                    TELA,
                    (51, 59, 51),
                    (x, y, 8, 5)
                )

        # Obstáculos.
        for obstaculo in sorted(
            self.obstaculos,
            key=lambda r: r.bottom
        ):
            pygame.draw.ellipse(
                TELA,
                (11, 18, 13),
                (
                    obstaculo.x - 4,
                    obstaculo.bottom - 4,
                    obstaculo.width + 10,
                    13
                )
            )

            if obstaculo.width >= 40:
                pygame.draw.ellipse(
                    TELA,
                    (51, 62, 48),
                    obstaculo
                )

                pygame.draw.ellipse(
                    TELA,
                    (68, 77, 58),
                    (
                        obstaculo.x + 4,
                        obstaculo.y + 3,
                        max(8, obstaculo.width - 8),
                        max(8, obstaculo.height // 2)
                    )
                )

            else:
                pygame.draw.rect(
                    TELA,
                    (48, 38, 30),
                    (
                        obstaculo.centerx - 4,
                        obstaculo.y + obstaculo.height // 2,
                        8,
                        obstaculo.height // 2
                    )
                )

                pygame.draw.circle(
                    TELA,
                    (21, 41, 27),
                    (obstaculo.centerx, obstaculo.y + 8),
                    max(15, obstaculo.width // 2)
                )

                pygame.draw.circle(
                    TELA,
                    (30, 51, 32),
                    (obstaculo.centerx - 4, obstaculo.y + 4),
                    max(10, obstaculo.width // 3)
                )

        # Escurecimento geral do cenário.
        sombra = pygame.Surface(
            (LARGURA, ALTURA),
            pygame.SRCALPHA
        )

        sombra.fill((0, 0, 0, 65))
        TELA.blit(sombra, (0, 0))

    # ==================================================
    # INTERFACE
    # ==================================================

    def desenhar_interface(self):
        pygame.draw.rect(
            TELA,
            (13, 20, 18),
            (0, 0, LARGURA, 42)
        )

        texto(
            f"FASE {self.fase}/20",
            FONTE,
            BRANCO,
            (14, 10)
        )

        texto(
            f"PONTOS {self.pontos}",
            FONTE,
            AMARELO,
            (145, 10)
        )

        if self.fase == 20:
            texto(
                "CHEFE FINAL",
                FONTE,
                BRANCO,
                (300, 10)
            )
        else:
            texto(
                f"TEMPO {max(0, self.tempo):04.1f}s",
                FONTE,
                BRANCO,
                (300, 10)
            )

        texto(
            "VIDA",
            FONTE,
            BRANCO,
            (470, 10)
        )

        pygame.draw.rect(
            TELA,
            (67, 28, 28),
            (520, 11, 170, 19),
            border_radius=4
        )

        largura_vida = (
            170 * max(0, self.jogador.vida)
            / self.jogador.vida_max
        )

        pygame.draw.rect(
            TELA,
            (69, 173, 91),
            (520, 11, int(largura_vida), 19),
            border_radius=4
        )

        texto(
            "ESPAÇO: lanterna",
            FONTE,
            BRANCO,
            (710, 10)
        )

    def overlay(self, titulo, linha, dica=""):
        camada = pygame.Surface(
            (LARGURA, ALTURA),
            pygame.SRCALPHA
        )

        camada.fill((5, 8, 8, 215))
        TELA.blit(camada, (0, 0))

        texto(
            titulo,
            FONTE_GRANDE,
            BRANCO,
            (LARGURA // 2, ALTURA // 2 - 70),
            True
        )

        texto(
            linha,
            FONTE_MEDIA,
            BRANCO,
            (LARGURA // 2, ALTURA // 2),
            True
        )

        if dica:
            texto(
                dica,
                FONTE,
                AMARELO,
                (LARGURA // 2, ALTURA // 2 + 48),
                True
            )

    def desenhar_menu(self):
        """Tela inicial atmosférica, com animações leves e instruções."""
        tempo = pygame.time.get_ticks() / 1000

        # Fundo em degradê noturno.
        for y in range(ALTURA):
            fator = y / ALTURA
            cor = (
                int(5 + 9 * fator),
                int(9 + 10 * fator),
                int(17 + 13 * fator)
            )
            pygame.draw.line(TELA, cor, (0, y), (LARGURA, y))

        # Lua e halo.
        halo = pygame.Surface((260, 260), pygame.SRCALPHA)
        pygame.draw.circle(halo, (155, 190, 180, 13), (130, 130), 120)
        pygame.draw.circle(halo, (155, 190, 180, 22), (130, 130), 86)
        TELA.blit(halo, (690, 55))
        pygame.draw.circle(TELA, (204, 215, 194), (820, 185), 48)
        pygame.draw.circle(TELA, (180, 194, 177), (805, 170), 7)
        pygame.draw.circle(TELA, (180, 194, 177), (837, 199), 10)
        pygame.draw.circle(TELA, (180, 194, 177), (829, 158), 5)

        # Silhuetas de árvores nas laterais.
        for x, altura in [(25, 240), (95, 190), (165, 150),
                          (860, 170), (925, 235), (980, 200)]:
            base_y = ALTURA - 25
            pygame.draw.rect(TELA, (8, 15, 17),
                             (x - 5, base_y - altura // 2, 10, altura // 2))
            for lado in (-1, 1):
                for i in range(4):
                    yy = base_y - altura + i * (altura // 5)
                    ponta = x + lado * (30 + i * 5)
                    pygame.draw.polygon(
                        TELA, (8, 17, 18),
                        [(x, yy - 35), (ponta, yy + 30), (x, yy + 15)]
                    )

        # Névoa baixa e discreta.
        nevoa = pygame.Surface((LARGURA, 150), pygame.SRCALPHA)
        for i in range(5):
            deslocamento = int(math.sin(tempo * 0.45 + i) * 35)
            pygame.draw.ellipse(
                nevoa, (125, 155, 145, 10),
                (-100 + deslocamento, 25 + i * 18, LARGURA + 180, 50)
            )
        TELA.blit(nevoa, (0, ALTURA - 165))

        # Partículas luminosas flutuando.
        for i in range(34):
            x = (i * 137 + int(tempo * (9 + i % 5))) % LARGURA
            y = (i * 83 + int(tempo * (7 + i % 3))) % ALTURA
            brilho = 100 + int(70 * (0.5 + 0.5 * math.sin(tempo * 2 + i)))
            pygame.draw.circle(TELA, (brilho, brilho, brilho - 18), (x, y), 1 + i % 2)

        # Painel central.
        painel = pygame.Surface((700, 485), pygame.SRCALPHA)
        pygame.draw.rect(
            painel, (7, 13, 17, 218), (0, 0, 700, 485),
            border_radius=24
        )
        pygame.draw.rect(
            painel, (108, 137, 120, 155), (1, 1, 698, 483),
            width=2, border_radius=24
        )
        TELA.blit(painel, (150, 105))

        # Título com sombra e brilho pulsante.
        brilho_titulo = 205 + int(35 * (0.5 + 0.5 * math.sin(tempo * 2)))
        titulo_cor = (brilho_titulo, min(235, brilho_titulo + 8), 190)
        titulo = pygame.font.Font(None, 76)
        texto("👻 CAMPO SOMBRIO 🔦", titulo, (0, 0, 0),
              (LARGURA // 2 + 3, 178 + 3), True)
        texto("👻 CAMPO SOMBRIO 🔦", titulo, titulo_cor,
              (LARGURA // 2, 178), True)

        fonte_sub = pygame.font.Font(None, 30)
        texto("SOBREVIVÊNCIA", fonte_sub, (154, 181, 162),
              (LARGURA // 2, 224), True)

        pygame.draw.line(TELA, (96, 125, 105),
                         (310, 249), (690, 249), 2)

        texto("A escuridão está viva. Sua lanterna é sua única defesa.",
              FONTE, (218, 222, 207), (LARGURA // 2, 274), True)

        # Botão iniciar pulsante.
        pulsacao = 1 + 0.025 * math.sin(tempo * 3)
        bw, bh = int(270 * pulsacao), int(58 * pulsacao)
        botao = pygame.Rect(0, 0, bw, bh)
        botao.center = (LARGURA // 2, 354)
        pygame.draw.rect(TELA, (45, 76, 57), botao, border_radius=13)
        pygame.draw.rect(TELA, (159, 192, 139), botao, 2, border_radius=13)
        texto("INICIAR JOGO", FONTE_MEDIA, (238, 241, 220),
              botao.center, True)
        texto("Pressione ENTER para começar",
              FONTE, (180, 193, 177), (LARGURA // 2, 401), True)

        # Controles em cartões.
        cards = [
            ("🎮 CONTROLES", "Mover personagem"),
            ("🔦 LANTERNA", "Ligar a lanterna"),
            ("🧟 SOBREVIVA", "Sobreviva às 20 fases")
        ]
        card_w = 190
        gap = 18
        start_x = (LARGURA - (3 * card_w + 2 * gap)) // 2
        for i, (cabecalho, descricao) in enumerate(cards):
            rect = pygame.Rect(start_x + i * (card_w + gap), 438, card_w, 68)
            pygame.draw.rect(TELA, (17, 27, 28), rect, border_radius=10)
            pygame.draw.rect(TELA, (64, 88, 72), rect, 1, border_radius=10)
            texto(cabecalho, FONTE, (207, 220, 183),
                  (rect.centerx, rect.y + 21), True)
            fonte_menor = pygame.font.Font(None, 21)
            texto(descricao, fonte_menor, (177, 190, 180),
                  (rect.centerx, rect.y + 46), True)

        texto("Prepare-se. Nem tudo que se move está vivo.",
              FONTE, (128, 147, 132), (LARGURA // 2, 548), True)

    # ==================================================
    # DESENHO DO JOGO
    # ==================================================

    def desenhar(self):
        self.desenhar_cenario()

        # A lanterna ilumina o cenário antes de desenhar os personagens.
        self.jogador.desenhar_lanterna()

        # Personagens em ordem de profundidade.
        objetos = (
            [(inimigo.y, inimigo) for inimigo in self.inimigos]
            + [(self.jogador.y, self.jogador)]
        )

        for _, objeto in sorted(
            objetos,
            key=lambda item: item[0]
        ):
            objeto.desenhar()

            if isinstance(objeto, Inimigo) and getattr(
                objeto, "iluminado", False
            ):
                # Contorno dourado quando o monstro é atingido pela luz.
                pygame.draw.circle(
                    TELA,
                    (255, 230, 145),
                    (int(objeto.x), int(objeto.y - 8)),
                    objeto.raio + 3,
                    2
                )

        for bala in self.balas_inimigas:
            bala.desenhar()

        self.desenhar_interface()

        if self.estado == "menu":
            self.desenhar_menu()

        elif self.estado == "fase_concluida":
            self.overlay(
                f"FASE {self.fase} CONCLUÍDA",
                f"Pontuação: {self.pontos}",
                "ENTER: avançar para a próxima fase"
            )

        elif self.estado == "derrota":
            self.overlay(
                "VOCÊ FOI DERROTADO",
                f"Você chegou à fase {self.fase}",
                "R: tentar novamente nesta fase | ESC: sair"
            )

        elif self.estado == "vitoria":
            self.overlay(
                "VITÓRIA!",
                f"Chefe derrotado! Pontuação: {self.pontos}",
                "R: começar uma nova partida | ESC: sair"
            )

        elif self.banner > 0 and self.estado == "jogando":
            titulo = (
                "CHEFE FINAL"
                if self.fase == 20
                else f"FASE {self.fase}"
            )

            texto(
                titulo,
                FONTE_GRANDE,
                BRANCO,
                (LARGURA // 2, 112),
                True
            )

        pygame.display.flip()

    # ==================================================
    # LOOP PRINCIPAL
    # ==================================================

    async def executar(self):
        rodando = True

        while rodando:
            dt = min(
                RELOGIO.tick(FPS) / 1000,
                0.035
            )

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        rodando = False

                    elif evento.key == pygame.K_RETURN:
                        if self.estado == "menu":
                            self.carregar_fase()

                        elif self.estado == "fase_concluida":
                            self.pontos += self.fase * 20
                            self.fase += 1
                            self.carregar_fase()

                    elif (
                        evento.key == pygame.K_r
                        and self.estado == "derrota"
                    ):
                        fase_atual = self.fase
                        pontos_atuais = self.pontos

                        self.jogador = Jogador()
                        self.fase = fase_atual
                        self.pontos = pontos_atuais

                        self.carregar_fase()

                    elif (
                        evento.key == pygame.K_r
                        and self.estado == "vitoria"
                    ):
                        self.fase = 1
                        self.pontos = 0
                        self.jogador = Jogador()

                        self.carregar_fase()

            self.atualizar(dt)
            self.desenhar()

            # Devolve o controle ao navegador, necessário em ambientes web.
            await asyncio.sleep(0)

        pygame.quit()


# ==================================================
# INÍCIO DO PROGRAMA
# ==================================================

async def main():
    jogo = Jogo()
    await jogo.executar()


if __name__ == "__main__":
    asyncio.run(main())
