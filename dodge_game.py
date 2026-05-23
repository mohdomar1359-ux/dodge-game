from ursina import *
import random

app = Ursina()

window.title        = 'Dodge!'
window.borderless   = False
window.fullscreen   = False
window.size         = (800, 600)
camera.orthographic = True
camera.fov          = 10

# ── Game state ────────────────────────────────────────────────────────────────
score       = 0
lives       = 3
speed       = 3.0
spawn_rate  = 0.8
game_over   = False
paused      = False

# ── Player ────────────────────────────────────────────────────────────────────
player = Entity(
    model   = 'cube',
    texture = 'white_cube',
    color   = color.cyan,
    scale   = (0.8, 0.8, 0.8),
    position= (0, -4, 0),
    collider= 'box',
)

# ── HUD ───────────────────────────────────────────────────────────────────────
score_text = Text(
    text     = 'Score: 0',
    position = (-0.85, 0.45),
    scale    = 1.6,
    color    = color.white,
)

lives_text = Text(
    text     = '❤ ❤ ❤',
    position = (0.4, 0.45),
    scale    = 1.6,
    color    = color.red,
)

hint_text = Text(
    text     = 'A / D or ← / → to move',
    position = (-0.3, -0.47),
    scale    = 1.2,
    color    = color.gray,
)

# ── Falling objects ───────────────────────────────────────────────────────────
falling = []

COLORS = [color.red, color.orange, color.yellow, color.magenta, color.lime]

def spawn_object():
    x = random.uniform(-4.5, 4.5)
    e = Entity(
        model   = 'cube',
        texture = 'white_cube',
        color   = random.choice(COLORS),
        scale   = (random.uniform(0.4, 0.9),) * 3,
        position= (x, 6, 0),
        collider= 'box',
    )
    falling.append(e)

spawn_timer = 0

# ── Game over overlay ─────────────────────────────────────────────────────────
go_bg = Entity(
    parent  = camera.ui,
    model   = 'quad',
    color   = color.rgba(0, 0, 0, 180),
    scale   = (2, 2),
    enabled = False,
    z       = -1,
)

go_text = Text(
    text     = '',
    origin   = (0, 0),
    scale    = 3,
    color    = color.white,
    enabled  = False,
)

go_sub = Text(
    text     = '',
    origin   = (0, 0),
    position = (0, -0.08),
    scale    = 1.4,
    color    = color.yellow,
    enabled  = False,
)

def show_game_over():
    go_bg.enabled  = True
    go_text.enabled = True
    go_sub.enabled  = True
    go_text.text   = 'GAME OVER'
    go_sub.text    = f'Score: {score}   |   Press R to restart'
    hint_text.enabled = False

def restart():
    global score, lives, speed, spawn_rate, game_over, spawn_timer
    score      = 0
    lives      = 3
    speed      = 3.0
    spawn_rate = 0.8
    game_over  = False
    spawn_timer= 0
    player.position = (0, -4, 0)
    player.color    = color.cyan
    for e in falling:
        destroy(e)
    falling.clear()
    score_text.text   = 'Score: 0'
    lives_text.text   = '❤ ❤ ❤'
    go_bg.enabled     = False
    go_text.enabled   = False
    go_sub.enabled    = False
    hint_text.enabled = True

def update_lives_display():
    hearts = ['❤'] * lives + ['♡'] * (3 - lives)
    lives_text.text = ' '.join(hearts)

# ── Main update ───────────────────────────────────────────────────────────────
def update():
    global score, lives, speed, spawn_rate, spawn_timer, game_over

    if game_over:
        return

    # ── Player movement ──
    move = 0
    if held_keys['a'] or held_keys['left arrow']:  move = -1
    if held_keys['d'] or held_keys['right arrow']: move =  1
    player.x += move * 7 * time.dt
    player.x   = clamp(player.x, -4.8, 4.8)

    # ── Spawn timer ──
    spawn_timer += time.dt
    if spawn_timer >= spawn_rate:
        spawn_timer = 0
        spawn_object()
        # Gradually get harder
        speed      = min(speed + 0.05, 12)
        spawn_rate = max(spawn_rate - 0.01, 0.25)

    # ── Move falling objects ──
    for e in falling[:]:
        e.y -= speed * time.dt

        # Hit player?
        if e.intersects(player).hit:
            falling.remove(e)
            destroy(e)
            lives -= 1
            update_lives_display()
            player.color = color.red
            invoke(setattr, player, 'color', color.cyan, delay=0.3)
            if lives <= 0:
                game_over = True
                show_game_over()
            continue

        # Off screen — give a point
        if e.y < -6:
            falling.remove(e)
            destroy(e)
            score += 1
            score_text.text = f'Score: {score}'

def input(key):
    if key == 'r' and game_over:
        restart()
    if key == 'escape':
        application.quit()

app.run()
