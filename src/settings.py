from pygame.math import Vector2

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 16

# Map dimensions in tiles
MAP_WIDTH = 80
MAP_HEIGHT = 60

# Overlay offsets
PLAYER_TOOL_OFFSET = {
    'left': Vector2(-12, 8),
    'right': Vector2(12, 8),
    'up': Vector2(0, 2),
    'down': Vector2(0, 12)
}

OVERLAY_POS = {
    'tools' : (40, SCREEN_HEIGHT - 5),
    'seeds' : (90, SCREEN_HEIGHT - 15),
}

# Drawing layers
LAYERS = {
    'water' : 0,
    'ground' : 1,
    'soil' : 2,
    'soil_water' : 3,
    'rain_floor' : 4,
    'house_bottom' : 5,
    'ground_plants' : 6,
    'main' : 7,
    'house_top' : 8,
    'fruits' : 9,
    'rain_drops' : 10
    }

# Small = 16x32
# Large = 32x32
APPLE_POS = {
    'Tree' : [(4, -5), (-2, 1), (3, 5), (4, -5), (-2, 1), (3, 5)],
    'Tree Large' : [(6, -5), (11, 1), (6, 5), (6, -5), (11, 1), (6, 5)]
}

GROWTH_SPEED = {
    'corn' : 1,
    'tomato' : 0.7,
}
