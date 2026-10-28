
import pygame
import random
import sys

pygame.init()

# Configuração da janela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Desafio de Matemática")

# Cores
BRANCO = (255, 255, 255)
PRETO = (30, 30, 30)
AZUL = (50, 100, 230)
VERDE = (40, 180, 80)
VERMELHO = (230, 50, 50)
CINZA = (220, 220, 220)
FUNDO = (225, 240, 255)

# Fontes
fonte = pygame.font.SysFont("arial", 30)
titulo = pygame.font.SysFont("arial", 55)
fonte_grande = pygame.font.SysFont("arial", 40)

relogio = pygame.time.Clock()

# Estados do jogo
INICIO = 0
JOGANDO = 1
FIM = 2
estado = INICIO

# Variáveis do jogo
pontuacao = 0
pergunta_numero = 0
tempo_limite = 10
inicio_tempo = 0
pergunta = ""
resposta_correta = 0
alternativas = []
mensagem = ""


def escrever(texto, fonte_usada, cor, x, y):
    imagem = fonte_usada.render(str(texto), True, cor)
    retangulo = imagem.get_rect(center=(x, y))
    tela.blit(imagem, retangulo)


def gerar_pergunta():
    global pergunta, resposta_correta, alternativas
    global inicio_tempo, pergunta_numero, mensagem

    operacao = random.choice(["+", "-", "*"])
    a = random.randint(1, 10)
    b = random.randint(1, 10)

    if operacao == "+":
        resposta_correta = a + b
    elif operacao == "-":
        # Evita resultados negativos
        if a < b:
            a, b = b, a
        resposta_correta = a - b
    else:
        resposta_correta = a * b

    pergunta = f"Quanto e {a} {operacao} {b}?"
    alternativas = [resposta_correta]

    while len(alternativas) < 4:
        opcao = resposta_correta + random.randint(-10, 10)
        if opcao >= 0 and opcao not in alternativas:
            alternativas.append(opcao)

    random.shuffle(alternativas)
    inicio_tempo = pygame.time.get_ticks()
    pergunta_numero += 1
    mensagem = ""


def iniciar_jogo():
    global pontuacao, pergunta_numero, estado
    pontuacao = 0
    pergunta_numero = 0
    estado = JOGANDO
    gerar_pergunta()


def responder(opcao):
    global pontuacao, estado, mensagem

    if opcao == resposta_correta:
        pontuacao += 1

    gerar_pergunta()


# Posições dos botões
botoes = [
    pygame.Rect(120, 300, 250, 70),
    pygame.Rect(430, 300, 250, 70),
    pygame.Rect(120, 400, 250, 70),
    pygame.Rect(430, 400, 250, 70)
]

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if estado == INICIO and evento.key == pygame.K_RETURN:
                iniciar_jogo()

            elif estado == FIM and evento.key == pygame.K_RETURN:
                iniciar_jogo()

            elif estado == JOGANDO:
                # Teclas 1, 2, 3 e 4 escolhem respostas
                if evento.key in (
                    pygame.K_1, pygame.K_2,
                    pygame.K_3, pygame.K_4
                ):
                    indice = evento.key - pygame.K_1
                    responder(alternativas[indice])

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if estado == INICIO or estado == FIM:
                iniciar_jogo()

            elif estado == JOGANDO:
                for i, botao in enumerate(botoes):
                    if botao.collidepoint(evento.pos):
                        responder(alternativas[i])

    tela.fill(FUNDO)

    if estado == INICIO:
        escrever(
            "DESAFIO DE MATEMATICA",
            titulo, AZUL, 400, 170
        )
        escrever(
            "Resolva perguntas faceis!",
            fonte, PRETO, 400, 270
        )
        escrever(
            "Voce tem 10 segundos por pergunta.",
            fonte, PRETO, 400, 320
        )
        escrever(
            "Pressione ENTER para comecar",
            fonte_grande, VERDE, 400, 430
        )

    elif estado == JOGANDO:
        tempo_passado = (
            pygame.time.get_ticks() - inicio_tempo
        ) / 1000
        tempo_restante = max(0, tempo_limite - tempo_passado)

        escrever(
            f"Pontuacao: {pontuacao}",
            fonte, PRETO, 150, 40
        )
        escrever(
            f"Tempo: {tempo_restante:.1f}s",
            fonte, VERMELHO if tempo_restante < 4 else PRETO,
            650, 40
        )

        escrever(
            pergunta, titulo, AZUL, 400, 190
        )

        for i, botao in enumerate(botoes):
            pygame.draw.rect(tela, BRANCO, botao, border_radius=12)
            pygame.draw.rect(tela, AZUL, botao, 3, border_radius=12)
            escrever(
                f"{i + 1}) {alternativas[i]}",
                fonte_grande, PRETO,
                botao.centerx, botao.centery
            )

        escrever(
            "Clique em uma resposta ou aperte 1, 2, 3 ou 4",
            pygame.font.SysFont("arial", 20),
            PRETO, 400, 530
        )

        if tempo_restante <= 0:
            estado = FIM

    elif estado == FIM:
        escrever(
            "FIM DE JOGO!",
            titulo, VERMELHO, 400, 190
        )
        escrever(
            f"Sua pontuacao: {pontuacao}",
            fonte_grande, AZUL, 400, 290
        )
        escrever(
            "Pressione ENTER para jogar novamente",
            fonte, VERDE, 400, 390
        )
        escrever(
            "Pressione ESC para sair",
            fonte, PRETO, 400, 450
        )

    pygame.display.flip()
    relogio.tick(60)
