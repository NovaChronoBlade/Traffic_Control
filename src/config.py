"""
Constantes y configuración del juego Traffic Control
"""

# Dimensiones de la pantalla
SCREEN_WIDTH = 1200 
SCREEN_HEIGHT = 800
FPS = 60

# Colores
ROAD_COLOR = (60, 60, 60)
LINE_COLOR = (255, 255, 255)
GRASS_COLOR = (34, 139, 34)
BG_COLOR = (50, 150, 50)
STOP_LINE_COLOR = (255, 255, 255)

# Configuración de calles
STREET_WIDTH = 160  # Ancho de cada calle
LANE_WIDTH = 80  # Ancho de cada carril

# Configuración de intersección
INTERSECTION_SIZE = 200  # Tamaño del área de intersección

# Distancias y posiciones
STOP_LINE_DISTANCE = 110  # Distancia de línea de paso desde el centro (más cerca de la intersección)
SAFE_DISTANCE_BETWEEN_VEHICLES = 90  # Distancia mínima entre vehículos
DETECTION_MARGIN = 10  # Margen de seguridad

# Configuración de spawn
INITIAL_SPAWN_INTERVAL = 2.0  # Segundos entre spawns
MIN_SPAWN_INTERVAL = 0.8
SPAWN_DIFFICULTY_INCREASE = 0.1  # Por nivel

# Configuración del juego
INITIAL_LIVES = 5
VEHICLES_PER_LEVEL = 20  # Vehículos necesarios para subir de nivel

# Puntuación
POINTS_NORMAL_CAR = 10
POINTS_BUS = 20
POINTS_EMERGENCY = 30
POINTS_SMOOTH_FLOW = 50
POINTS_PERFECT_TIMING = 25

# Penalizaciones
PENALTY_COLLISION = 100
PENALTY_COLLISION_EMERGENCY = 300
PENALTY_VIOLATION = 50
PENALTY_CONGESTION_LOW = 5
PENALTY_CONGESTION_MEDIUM = 15
PENALTY_CONGESTION_HIGH = 30
PENALTY_CONGESTION_CRITICAL = 50

# Configuración de semáforos
DEFAULT_GREEN_DURATION = 6.0
DEFAULT_YELLOW_DURATION = 2.0
DEFAULT_RED_DURATION = 6.0
