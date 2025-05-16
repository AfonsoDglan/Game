import pgzrun
from pygame import Rect
import math


"""Propriedades da tela do jogo"""
WIDTH = 1440
HEIGHT = 960
TITLE = "Meu Primeiro Jogo Em Pyzero"

"""Constantes do jogo"""
GRAVITY = 0.5
JUMP_FORCE = -11
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 1

"""Constantes para carregamento de mapas,
TILE_SIZE = Tamanho de cada tile (16x16px)
MAP_WIDTH = lagura do mapa ou seja 90 blocos, 
que ao multiplicar por 16 que é o tamanho do 
tile dá o tamanho da lagura da tela do jogo.
MAP_HEIGHT = altura do mapa que mutiplicado por 16
temos a altura da tela do jogo.
"""
TILE_SIZE = 16
MAP_WIDTH = 90
MAP_HEIGHT = 60

"""Aqui temos os id dos tiles do mapa que esão definidos no csv da plataforma
-1 é o id vazio no csv
0 é o id do primeiro bloco da plataforma e 6 é o id da útima plataforma.
29 é o id das armadilhas no mapa
159 é o id da chave que é a recompensa do jogo.
PLATFORM_WIDTH_TILES é o tamanho de tiles que cada plataforma tem."""
TILE_EMPTY = -1
TILE_PLATFORM_START = 0
TILE_PLATFORM_END = 6
TILE_TRAP = 29
TILE_KEY = 159
PLATFORM_WIDTH_TILES = 7


class Player(Actor):  # noqa EF821
    def __init__(self, pos):
        # Imagem padrão (direita)
        super().__init__("personagem/idle/0", pos)
        self.speed = PLAYER_SPEED
        self.jumping = False
        # 1 para direita, -1 para esquerda
        self.direction = 1
        self.lives = 5
        self.invincible = 0
        self.animation_frame = 0
        self.state = "idle"
        # Velocidade vertical inicializada
        self.vy = 0

        """Carrega animações com versões separadas para esquerda/direita"""
        self.animations = {
            "idle": {
                "right": [f"personagem/idle/{i}" for i in range(8)],
                "left": [f"personagem/idle/{i}-l" for i in range(8)]
            },
            "walk": {
                "right": [f"personagem/walk/{i}" for i in range(6)],
                "left": [f"personagem/walk/{i}-l" for i in range(6)]
            },
            "run": {
                "right": [f"personagem/run/{i}" for i in range(6)],
                "left": [f"personagem/run/{i}-l" for i in range(6)]
            },
            "jump": {
                "right": [f"personagem/jump/{i}" for i in range(4)],
                "left": [f"personagem/jump/{i}-l" for i in range(4)]
            }
        }

    def update(self):
        # Movimento horizontal
        move_x = 0
        if keyboard.left: # noqa EF821
            move_x = -self.speed
            self.direction = -1
            self.state = "walk" if abs(move_x) < self.speed else "run"
        elif keyboard.right: # noqa EF821
            move_x = self.speed
            self.direction = 1
            self.state = "walk" if abs(move_x) < self.speed else "run"
        else:
            self.state = "idle"

        if self.jumping:
            self.state = "jump"

        # Aplica movimento horizontal
        self.x += move_x

        # Aplica gravidade
        self.y += self.vy
        self.vy += GRAVITY

        # Verifica colisão com plataformas
        self.handle_collisions()

        # Atualiza animação
        self.animate()

        # Tempo de invencibilidade
        if self.invincible > 0:
            self.invincible -= 1

    def animate(self):
        self.animation_frame += 0.2

        # Determina a direção atual
        direction = "left" if self.direction < 0 else "right"

        # Obtém os frames para o estado e direção atual
        frames = self.animations[self.state][direction]

        if not frames:  # Se não houver frames, não faz nada
            return

        # Atualiza o frame
        if self.animation_frame >= len(frames):
            self.animation_frame = 0
        # Atualiza a imagem do ator
        self.image = frames[int(self.animation_frame)]

    def handle_collisions(self):
        # Verifica colisão com plataformas
        for platform in platforms:
            # Usa platform.rect para as coordenadas e dimensões
            if (self.y + self.height/2 > platform.rect.y and
                    self.y - self.height/2 < platform.rect.y +
                    platform.rect.height and
                    self.x + self.width/2 > platform.rect.x and
                    self.x - self.width/2 < platform.rect.x +
                    platform.rect.width):

                # Colisão por cima
                if (self.vy > 0 and self.y < platform.rect.y +
                        platform.rect.height/2):
                    self.y = platform.rect.y - self.height/2
                    self.vy = 0
                    self.jumping = False
                # Colisão por baixo
                elif (self.vy < 0 and self.y > platform.rect.y +
                        platform.rect.height/2):
                    self.y = (platform.rect.y +
                              platform.rect.height +
                              self.height/2)
                    self.vy = 0

        # Verifica se caiu no vazio
        if self.y > HEIGHT + 100:
            self.respawn()

    def check_key_collision(self):
        # Verifica colisão com chaves
        for key in keys[:]:
            if self.colliderect(key):
                self.keys_collected += 1
                keys.remove(key)
                # Poderia adicionar um som aqui: sounds.key_collect.play()

    def jump(self):
        if not self.jumping:
            self.vy = JUMP_FORCE
            self.jumping = True
            # sounds.jump.play()

    def shoot(self):
        if len(bullets) < 3:  # Limite de tiros na tela
            bullet_x = self.x + self.direction * self.width / 2
            bullet_y = self.y
            bullet_pos = (bullet_x, bullet_y)
            bullets.append(Bullet(bullet_pos, self.direction))
            # sounds.shoot.play()

    def take_damage(self):
        if self.invincible <= 0:
            self.lives -= 1
            self.invincible = 60  # 1 segundo de invencibilidade
            #  sounds.hurt.play()
            if self.lives <= 0:
                self.game_over()

    def respawn(self):
        if platforms:  # Verifica se existe pelo menos uma plataforma
            first_platform = platforms[0]
            self.pos = (first_platform.rect.centerx,
                        first_platform.rect.y - 20)
        else:
            self.pos = (100, 300)  # Fallback
        self.vy = 0
        self.take_damage()

    def game_over(self):
        global game_state
        game_state = "gameover"


class Bullet(Actor): # noqa EF821
    def __init__(self, pos, direction):
        # Usa imagem diferente dependendo da direção
        image = "bullet-l" if direction == -1 else "bullet"
        super().__init__(image, pos)
        self.direction = direction
        self.speed = BULLET_SPEED

    def update(self):
        self.x += self.speed * self.direction

        # Atualiza a imagem se a direção mudar (por precaução)
        if self.direction == -1 and self.image != "bullet-l":
            self.image = "bullet-l"
        elif self.direction == 1 and self.image != "bullet":
            self.image = "bullet"

        # Remove se sair da tela
        if self.x < 0 or self.x > WIDTH:
            bullets.remove(self)

        # Verifica colisão com inimigos
        for enemy in enemies[:]:
            if self.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(self)
                break


class Enemy(Actor): # noqa EF821
    def __init__(self, pos):
        super().__init__("inimigo/0", pos)
        self.speed = ENEMY_SPEED
        self.direction = 1
        self.platform = None
        self.patrol_left = 0
        self.patrol_right = 0
        self.animation_frame = 0
        self.state = "walk"

        self.animations = {
            "walk": {
                "right": [f"inimigo/{i}" for i in range(4)],
                "left": [f"inimigo/{i}-l" for i in range(4)]
            }
        }

    def update(self):
        self.x += self.speed * self.direction
        if self.x <= self.patrol_left or self.x >= self.patrol_right:
            self.direction *= -1
        self.animate()
        if self.colliderect(player) and player.invincible <= 0:
            player.take_damage()
            player.x += 5 * self.direction

    def animate(self):
        self.animation_frame += 0.1
        direction = "left" if self.direction < 0 else "right"
        frames = self.animations[self.state][direction]
        if not frames:
            return

        if self.animation_frame >= len(frames):
            self.animation_frame = 0
        self.image = frames[int(self.animation_frame)]


class Platform:
    def __init__(self, pos, width, height=TILE_SIZE, image="platform"):
        self.width = width
        self.height = height
        self.pos = pos
        self.image = image
        # Cria o retângulo de colisão
        self.rect = Rect(pos[0], pos[1], self.width, self.height)
        self.debug_mode = False
        self.tiles = ["platform" for i in range(7)]

    def draw(self):
        # Desenha os sete tiles da plataforma
        for i in range(PLATFORM_WIDTH_TILES):
            tile_image = self.tiles[i]
            tile_x = self.rect.x + (i * TILE_SIZE)
            screen.blit(tile_image, (tile_x, self.rect.y))  # noqa EF821


class Trap(Actor):  # noqa EF821
    def __init__(self, pos):
        super().__init__("trap", pos)
        self.original_y = pos[1]
        self.speed = 1
        self.direction = 1
        self.platform_below = None

    def update(self):
        self.y += self.speed * self.direction

        # Se estiver descendo, verifica colisão com plataforma
        if self.direction == 1:
            for platform in platforms:
                if (self.colliderect(platform.rect) and
                        platform.rect.top >= self.original_y):
                    self.direction = -1  # Inverte ao atingir a plataforma
                    break
        # Se estiver subindo, verifica se voltou à posição original
        elif self.y <= self.original_y:
            self.direction = 1
            self.y = self.original_y  # Garante posição exata

        # Verifica colisão com o jogador
        if self.colliderect(player) and player.invincible <= 0:
            player.take_damage()
            player.vy = JUMP_FORCE * 0.7


class Key(Actor): # noqa EF821
    def __init__(self, pos):
        super().__init__("key", pos)
        self.animation_frame = 0
        self.animation_speed = 0.1

    def update(self):
        self.y += math.sin(self.animation_frame) * 0.5
        self.animation_frame += self.animation_speed


def load_map_from_csv(filename):
    """Função para carregar um mapa a partir de um arquivo CSV"""
    map_data = []
    try:
        with open(filename, 'r') as file:
            linhas = file.read().strip().splitlines()
            for linha in linhas:
                # Divide os valores da linha e converte para inteiros
                map_data.append(
                    [int(cell) for cell in linha.strip().split(",")]
                    )
        return map_data
    except Exception as e:
        print(f"Erro ao carregar o mapa {filename}: {e}")
        return [[-1 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]


def is_valid_platform(row, start_idx):
    """Função auxiliar para verificar se uma sequência de tiles
    forma uma plataforma válida,
    primeiro Verifica se há espaço suficiente para uma plataforma de 7 tiles
    depois Verifica se os tiles formam uma sequência de 0 a 6"""
    if start_idx + PLATFORM_WIDTH_TILES > len(row):
        return False

    for i in range(PLATFORM_WIDTH_TILES):
        if row[start_idx + i] != i:
            return False
    return True


def init():
    """Inicialização do jogo"""
    global player, platforms, enemies, bullets, traps, keys, debug_mode
    debug_mode = False
    # Carrega o mapa
    platform_map = load_map_from_csv("csv_plataform.csv")
    platforms = []
    traps = []
    keys = []

    """Aqui é a parte da criação de todas as plataformas"""
    for y in range(len(platform_map)):
        x = 0
        while x < len(platform_map[y]):
            tile_id = platform_map[y][x]
            if tile_id == TILE_PLATFORM_START:
                if is_valid_platform(platform_map[y], x):
                    platform_width = TILE_SIZE * PLATFORM_WIDTH_TILES
                    platform_pos = (x * TILE_SIZE, y * TILE_SIZE)
                    platform = Platform(platform_pos, platform_width)
                    platforms.append(platform)
                    x += PLATFORM_WIDTH_TILES
                else:
                    x += 1
            elif tile_id == TILE_TRAP:
                trap_x = x * TILE_SIZE + TILE_SIZE // 2
                trap_y = y * TILE_SIZE + TILE_SIZE // 2
                traps.append(Trap((trap_x, trap_y)))
                x += 1
            elif tile_id == TILE_KEY:
                key_x = x * TILE_SIZE + TILE_SIZE // 2
                key_y = y * TILE_SIZE + TILE_SIZE // 2
                keys.append(Key((key_x, key_y)))
                x += 1
            else:
                x += 1

    spawn_platform = None
    if platforms:
        # Ordena as plataformas: mais abaixo primeiro, depois mais à esquerda
        platforms.sort(
            key=lambda p: (p.rect.bottom, p.rect.left), reverse=True)
        spawn_platform = platforms[0]  # A primeira após ordenar

    """aqui é criado o jogador, 20px acima da plataforma
    e localizado no canto inferior esquerdo da tela"""
    if spawn_platform:
        spawn_x = spawn_platform.rect.centerx
        spawn_y = spawn_platform.rect.top - 20
        player = Player((spawn_x, spawn_y))
    else:
        player = Player((100, HEIGHT - 100))

    player.vy = 0

    """Aqui é a parte da criação dos inimigos nas plataformas."""
    enemies = []
    for i, platform in enumerate(platforms):
        if i > 0 and i < len(platforms) - 1 and i % 2 == 0:
            enemy_x = platform.rect.x + platform.rect.width // 2
            enemy_y = platform.rect.y - 20
            enemy = Enemy((enemy_x, enemy_y))
            enemy.patrol_left = platform.rect.x + 10
            enemy.patrol_right = platform.rect.x + platform.rect.width - 10
            enemies.append(enemy)
    bullets = []


"""init() é chamado quando o jogo é inicializado
já o game_state armazena em qual tela estamos no jogo"""
init()
game_state = "intro"


def draw():
    """Nessa função temos a implementação das 3 telas do jogo o menu,
    a tela de game over e a tela de vitoria"""
    screen.clear()

    if game_state == "intro":
        screen.fill((0, 0, 0))
        screen.draw.text("Bem-vindo ao Jogo de Plataforma!",
                         center=(WIDTH//2, HEIGHT//2 - 100),
                         fontsize=60, color="white")
        screen.draw.text("Instruções:\n- Use as setas para se mover\n\
                        - Espaço para atirar\n- Colete a chave para vencer\n\
                        - Evite armadilhas e inimigos!",
                         center=(WIDTH//2, HEIGHT//2),
                         fontsize=36, color="white",
                         align="center")
        screen.draw.text("Pressione ENTER para começar",
                         center=(WIDTH//2, HEIGHT//2 + 200),
                         fontsize=40, color="yellow")

    elif game_state == "gameover":
        screen.fill((0, 0, 0))
        screen.draw.text("Game Over",
                         center=(WIDTH//2, HEIGHT//2),
                         fontsize=100, color="red")
        screen.draw.text("Pressione R para reiniciar",
                         center=(WIDTH//2, HEIGHT//2 + 100),
                         fontsize=40, color="white")

    elif game_state == "win":
        screen.fill((0, 100, 0))
        screen.draw.text("Parabéns! Você venceu!",
                         center=(WIDTH//2, HEIGHT//2),
                         fontsize=80, color="white")
        screen.draw.text("Pressione R para jogar novamente",
                         center=(WIDTH//2, HEIGHT//2 + 100),
                         fontsize=40, color="yellow")

    elif game_state == "playing":
        screen.fill((135, 206, 235))

        for platform in platforms:
            platform.draw()
        for trap in traps:
            trap.draw()
        for key in keys:
            key.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        if player.invincible % 10 < 5:
            player.draw()
        for i in range(player.lives):
            screen.blit("heart", (20 + i * 30, 20))


def on_key_down(key):
    """Pode haver erro aqui, estou comparando as teclas com o numero intero
    que ele representa para o pyzero ao serem clicadas."""
    global game_state
    if game_state == "intro" and key == 13:
        game_state = "playing"
        init()

    elif game_state in ["gameover", "win"] and key == 114:
        game_state = "playing"
        init()

    elif game_state == "playing":
        if key == 1073741906:
            player.jump()
        elif key == 32:
            player.shoot()


def update():
    if game_state != "playing":
        return

    player.update()
    for enemy in enemies:
        enemy.update()
    for bullet in bullets[:]:
        bullet.update()
    for trap in traps:
        trap.update()
    for key in keys[:]:
        key.update()
        if player.colliderect(key):
            keys.remove(key)
            end_game(win=True)


def end_game(win=False):
    global game_state
    game_state = "win" if win else "gameover"


def game_over(self):
    end_game(win=False)


pgzrun.go()
