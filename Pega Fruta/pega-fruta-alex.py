
import tkinter as tk
import random
import time

LARGURA = 500
ALTURA = 600
FPS = 60
TEMPO_FRAME = 1 / FPS

janela = tk.Tk()
janela.title("Pega-Fruta 🍎")
janela.resizable(False, False)

tela = tk.Canvas(
    janela, width=LARGURA, height=ALTURA,
    bg="lightblue", highlightthickness=0
)
tela.pack()

pontos = 0
velocidade = 180  # pixels por segundo
fim_de_jogo = False
teclas = set()
frutas = []
ultimo_tempo = time.perf_counter()
ultimo_spawn = 0

placar = tela.create_text(
    70, 25, text="Pontos: 0",
    font=("Arial", 16, "bold"), fill="black"
)

tela.create_text(
    250, 65,
    text="WASD ou setas para mover",
    font=("Arial", 12), fill="black"
)

cesta = tela.create_rectangle(
    200, 530, 300, 560,
    fill="brown", outline="black"
)


def tecla_pressionada(evento):
    teclas.add(evento.keysym.lower())


def tecla_soltar(evento):
    teclas.discard(evento.keysym.lower())


janela.bind("<KeyPress>", tecla_pressionada)
janela.bind("<KeyRelease>", tecla_soltar)


def criar_fruta():
    x = random.randint(25, LARGURA - 25)
    tipo = random.choice(["🍎", "🍌", "🍓", "🍊", "🍇"])
    fruta = tela.create_text(
        x, -10, text=tipo, font=("Arial", 25)
    )
    frutas.append(fruta)


def atualizar():
    global pontos, velocidade, fim_de_jogo
    global ultimo_tempo, ultimo_spawn

    if fim_de_jogo:
        return

    agora = time.perf_counter()
    dt = min(agora - ultimo_tempo, 0.05)
    ultimo_tempo = agora

    # Movimento da cesta: WASD ou setas
    dx = 0
    dy = 0

    if "a" in teclas or "left" in teclas:
        dx -= 300 * dt
    if "d" in teclas or "right" in teclas:
        dx += 300 * dt
    if "w" in teclas or "up" in teclas:
        dy -= 300 * dt
    if "s" in teclas or "down" in teclas:
        dy += 300 * dt

    x1, y1, x2, y2 = tela.coords(cesta)
    dx = max(-x1, min(dx, LARGURA - x2))
    dy = max(-y1, min(dy, ALTURA - y2))
    tela.move(cesta, dx, dy)

    # Criar uma fruta a cada 0,8 segundo
    if agora - ultimo_spawn >= 0.8:
        criar_fruta()
        ultimo_spawn = agora

    # Atualizar frutas e detectar colisões
    x1, y1, x2, y2 = tela.coords(cesta)

    for fruta in frutas[:]:
        tela.move(fruta, 0, velocidade * dt)
        fx, fy = tela.coords(fruta)

        if x1 <= fx <= x2 and y1 - 15 <= fy <= y2:
            tela.delete(fruta)
            frutas.remove(fruta)
            pontos += 1
            tela.itemconfig(placar, text=f"Pontos: {pontos}")

            if pontos % 5 == 0:
                velocidade += 20

        elif fy > ALTURA:
            tela.delete(fruta)
            frutas.remove(fruta)

    # Limite de 60 atualizações por segundo
    janela.after(max(1, int(TEMPO_FRAME * 1000)), atualizar)


atualizar()
janela.mainloop()
