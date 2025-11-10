"""
Traffic Control - Juego de gestión de tráfico
Integración de los tres patrones de diseño:
1. Template Method - Vehículos con comportamientos variados
2. State - Semáforos con estados y transiciones
3. Chain of Responsibility - Sistema de eventos
"""

import pygame
import sys
import random
from typing import List

# Importar módulos del juego
from src.vehicles import Vehicle, VehicleFactory
from src.traffic_light import TrafficLight, TrafficLightController
from src.event_system import EventSystem
from src.config import *
from src.collision_utils import CollisionDetector, VehicleSpacingChecker, TrafficLightChecker
from src.renderer import RoadRenderer, UIRenderer


class Game:
    """Clase principal del juego"""
    
    def __init__(self):
        pygame.init()
        
        # Configuración de pantalla (pantalla completa)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Traffic Control")
        
        # Reloj y tiempo
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        # Estado del juego
        self.game_state = {
            'score': 0,
            'lives': INITIAL_LIVES,
            'level': 1,
            'vehicles_passed': 0,
            'collisions': 0,
            'violations': 0,
            'time_scale': 1.0,
            'power_up_duration': 0,
            'score_multiplier': 1.0,
            'multiplier_duration': 0
        }
        
        # Sistema de eventos (Chain of Responsibility)
        self.event_system = EventSystem(self.game_state)
        
        # Listas de entidades
        self.vehicles: List[Vehicle] = []
        self.spawn_timer = 0
        self.spawn_interval = INITIAL_SPAWN_INTERVAL
        
        # Controlador de semáforos (State Pattern)
        self.traffic_controller = TrafficLightController()
        self.setup_intersection()
        
        # Renderizadores
        self.road_renderer = RoadRenderer()
        self.ui_renderer = UIRenderer()
        
        # Game over
        self.game_over = False
    
    def setup_intersection(self):
        """Configura la intersección con semáforos"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Semáforos horizontales (este-oeste) - a los lados de la calle horizontal
        light_h1 = TrafficLight(center_x - 200, center_y - 100, 'horizontal', 
                               green_duration=DEFAULT_GREEN_DURATION, 
                               red_duration=DEFAULT_RED_DURATION)
        light_h2 = TrafficLight(center_x + 200, center_y + 100, 'horizontal',
                               green_duration=DEFAULT_GREEN_DURATION, 
                               red_duration=DEFAULT_RED_DURATION)
        
        # Semáforos verticales (norte-sur) - a los lados de la calle vertical
        light_v1 = TrafficLight(center_x - 100, center_y - 200, 'vertical',
                               green_duration=DEFAULT_GREEN_DURATION, 
                               red_duration=DEFAULT_RED_DURATION)
        light_v2 = TrafficLight(center_x + 100, center_y + 200, 'vertical',
                               green_duration=DEFAULT_GREEN_DURATION, 
                               red_duration=DEFAULT_RED_DURATION)
        
        # TODOS los semáforos empiezan en rojo y en modo MANUAL
        for light in [light_h1, light_h2, light_v1, light_v2]:
            light.force_red()
            light.manual_override = True
            self.traffic_controller.add_traffic_light(light)
        
        # Referencias para fácil acceso
        self.lights = {
            'horizontal': [light_h1, light_h2],
            'vertical': [light_v1, light_v2]
        }
    
    def spawn_vehicle(self):
        """Genera un nuevo vehículo en una posición aleatoria"""
        directions = ['left', 'right', 'up', 'down']
        direction = random.choice(directions)
        
        center_y = SCREEN_HEIGHT // 2
        center_x = SCREEN_WIDTH // 2
        
        # Posiciones de spawn según dirección
        spawn_positions = {
            'right': (-50, center_y - 30, 0),
            'left': (SCREEN_WIDTH + 50, center_y + 30, 1),
            'down': (center_x - 30, -50, 2),
            'up': (center_x + 30, SCREEN_HEIGHT + 50, 3)
        }
        
        x, y, lane = spawn_positions[direction]
        
        # Crear vehículo aleatorio usando el Factory (Template Method)
        vehicle = VehicleFactory.create_random_vehicle(x, y, direction, lane)
        self.vehicles.append(vehicle)
    
    def check_collisions(self):
        """Detecta colisiones entre vehículos usando CollisionDetector"""
        for i, v1 in enumerate(self.vehicles):
            for v2 in self.vehicles[i+1:]:
                if CollisionDetector.check_collision(v1, v2):
                    # Emitir evento de colisión (Chain of Responsibility)
                    event = self.event_system.emit_event('collision', {
                        'vehicle1': v1,
                        'vehicle2': v2
                    })
                    
                    # Remover vehículos colisionados
                    if 'remove_vehicles' in event.data:
                        for v in event.data['remove_vehicles']:
                            if v in self.vehicles:
                                self.vehicles.remove(v)
    
    def check_congestion(self):
        """Detecta congestión de tráfico"""
        stopped_vehicles = sum(1 for v in self.vehicles if v.stopped)
        
        if stopped_vehicles > 15:
            level = 'critical'
        elif stopped_vehicles > 10:
            level = 'high'
        elif stopped_vehicles > 5:
            level = 'medium'
        elif stopped_vehicles > 3:
            level = 'low'
        else:
            return
        
        # Emitir evento de congestión periódicamente
        if random.random() < 0.01:  # 1% de probabilidad por frame
            self.event_system.emit_event('congestion', {
                'level': level,
                'waiting_vehicles': stopped_vehicles
            })
    
    def update(self, dt: float):
        """Actualiza el estado del juego"""
        if self.paused or self.game_over:
            return
        
        # Aplicar escala de tiempo (power-ups)
        dt *= self.game_state['time_scale']
        
        # Actualizar duración de power-ups
        if self.game_state['power_up_duration'] > 0:
            self.game_state['power_up_duration'] -= dt
            if self.game_state['power_up_duration'] <= 0:
                self.game_state['time_scale'] = 1.0
        
        if self.game_state['multiplier_duration'] > 0:
            self.game_state['multiplier_duration'] -= dt
            if self.game_state['multiplier_duration'] <= 0:
                self.game_state['score_multiplier'] = 1.0
        
        # Actualizar semáforos (State Pattern)
        self.traffic_controller.update(dt)
        
        # Spawn de vehículos
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_vehicle()
            self.spawn_timer = 0
            
            # Aumentar dificultad gradualmente
            self.spawn_interval = max(MIN_SPAWN_INTERVAL, 
                                     INITIAL_SPAWN_INTERVAL - (self.game_state['level'] * SPAWN_DIFFICULTY_INCREASE))
        
        # Actualizar vehículos (Template Method)
        for vehicle in self.vehicles[:]:
            # Verificar si puede moverse usando las utilidades
            can_move_light = TrafficLightChecker.can_pass_traffic_light(vehicle, self.lights)
            can_move_spacing = VehicleSpacingChecker.can_move_forward(vehicle, self.vehicles)
            can_move = can_move_light and can_move_spacing
            
            vehicle.update(dt, can_move)
            
            # Remover vehículos fuera de pantalla
            if vehicle.is_off_screen(SCREEN_WIDTH, SCREEN_HEIGHT):
                self.vehicles.remove(vehicle)
                
                # Dar puntos por vehículo que pasó exitosamente
                self.event_system.emit_event('vehicle_passed', {
                    'vehicle': vehicle
                })
        
        # Detectar colisiones (Chain of Responsibility)
        self.check_collisions()
        
        # Detectar congestión
        self.check_congestion()
        
        # Actualizar notificaciones
        self.event_system.update_notifications()
        
        # Aumentar nivel
        if self.game_state['vehicles_passed'] > 0 and \
           self.game_state['vehicles_passed'] % VEHICLES_PER_LEVEL == 0:
            self.game_state['level'] += 1
        
        # Game Over
        if self.game_state['lives'] <= 0:
            self.game_over = True
    
    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Fondo y calles
        self.road_renderer.draw(self.screen)
        
        # Semáforos
        self.traffic_controller.draw_all(self.screen)
        
        # Vehículos
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        
        # UI
        self.ui_renderer.draw_hud(self.screen, self.game_state)
        
        # Notificaciones de eventos
        self.event_system.draw_notifications(self.screen)
        
        # Pausa
        if self.paused:
            self.ui_renderer.draw_pause_screen(self.screen)
        
        # Game Over
        if self.game_over:
            self.ui_renderer.draw_game_over(self.screen, self.game_state)
        
        pygame.display.flip()
    
    def handle_events(self):
        """Maneja los eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Reiniciar juego
                elif event.key == pygame.K_F11:
                    # Alternar pantalla completa
                    pygame.display.toggle_fullscreen()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    x, y = event.pos
                    
                    # Verificar click en semáforo y cambiar directamente su estado
                    light = self.traffic_controller.get_light_at_position(x, y)
                    if light:
                        light.cycle_state()
    
    def run(self):
        """Loop principal del juego"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
