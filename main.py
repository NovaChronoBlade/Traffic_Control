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
from typing import List, Tuple
from src.vehicles import Vehicle, VehicleFactory
from src.traffic_light import TrafficLight, TrafficLightController
from src.event_system import EventSystem


class Game:
    """Clase principal del juego"""
    
    def __init__(self):
        pygame.init()
        
        # Configuración de pantalla
        # self.WIDTH = 1200
        # self.HEIGHT = 800
        self.WIDTH = 1000
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Traffic Control")
        
        # Reloj y tiempo
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True
        self.paused = False
        
        # Estado del juego
        self.game_state = {
            'score': 0,
            'lives': 5,
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
        self.spawn_interval = 2.0  # segundos
        
        # Controlador de semáforos (State Pattern)
        self.traffic_controller = TrafficLightController()
        self.setup_intersection()
        
        # Fuentes
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colores
        self.ROAD_COLOR = (60, 60, 60)
        self.LINE_COLOR = (255, 255, 255)
        self.GRASS_COLOR = (34, 139, 34)
        self.BG_COLOR = (50, 150, 50)
        
        # Game over
        self.game_over = False
    
    def setup_intersection(self):
        """Configura la intersección con semáforos"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2
        
        # Semáforos horizontales (este-oeste) - a los lados de la calle horizontal
        light_h1 = TrafficLight(center_x - 200, center_y - 100, 'horizontal', 
                               green_duration=6.0, red_duration=6.0)
        light_h2 = TrafficLight(center_x + 200, center_y + 100, 'horizontal',
                               green_duration=6.0, red_duration=6.0)
        
        # Semáforos verticales (norte-sur) - a los lados de la calle vertical
        light_v1 = TrafficLight(center_x - 100, center_y - 200, 'vertical',
                               green_duration=6.0, red_duration=6.0)
        light_v2 = TrafficLight(center_x + 100, center_y + 200, 'vertical',
                               green_duration=6.0, red_duration=6.0)
        
        # TODOS los semáforos empiezan en rojo y en modo MANUAL
        light_h1.force_red()
        light_h2.force_red()
        light_v1.force_red()
        light_v2.force_red()
        
        # Activar control manual permanente
        light_h1.manual_override = True
        light_h2.manual_override = True
        light_v1.manual_override = True
        light_v2.manual_override = True
        
        self.traffic_controller.add_traffic_light(light_h1)
        self.traffic_controller.add_traffic_light(light_h2)
        self.traffic_controller.add_traffic_light(light_v1)
        self.traffic_controller.add_traffic_light(light_v2)
        
        # Referencias para fácil acceso
        self.lights = {
            'horizontal': [light_h1, light_h2],
            'vertical': [light_v1, light_v2]
        }
    
    def spawn_vehicle(self):
        """Genera un nuevo vehículo en una posición aleatoria"""
        # Direcciones posibles
        directions = ['left', 'right', 'up', 'down']
        direction = random.choice(directions)
        
        # Posiciones de spawn según dirección
        if direction == 'right':
            x, y = -50, self.HEIGHT // 2 - 30
            lane = 0
        elif direction == 'left':
            x, y = self.WIDTH + 50, self.HEIGHT // 2 + 30
            lane = 1
        elif direction == 'down':
            x, y = self.WIDTH // 2 - 30, -50
            lane = 2
        else:  # up
            x, y = self.WIDTH // 2 + 30, self.HEIGHT + 50
            lane = 3
        
        # Crear vehículo aleatorio usando el Factory (Template Method)
        vehicle = VehicleFactory.create_random_vehicle(x, y, direction, lane)
        self.vehicles.append(vehicle)
    
    def check_collisions(self):
        """Detecta colisiones entre vehículos SOLO en la intersección"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2
        
        # Definir zona de intersección donde pueden ocurrir colisiones
        intersection_zone = pygame.Rect(center_x - 100, center_y - 100, 200, 200)
        
        for i, v1 in enumerate(self.vehicles):
            for v2 in self.vehicles[i+1:]:
                # Verificar si ambos vehículos están en la intersección
                v1_in_intersection = intersection_zone.collidepoint(v1.x, v1.y)
                v2_in_intersection = intersection_zone.collidepoint(v2.x, v2.y)
                
                # Solo detectar colisión si ambos están en la intersección
                # Y van en direcciones diferentes (no en fila)
                if v1_in_intersection and v2_in_intersection:
                    if v1.direction != v2.direction:  # Diferentes direcciones
                        if v1.get_rect().colliderect(v2.get_rect()):
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
    
    def check_traffic_lights(self, vehicle: Vehicle) -> bool:
        """Verifica si un vehículo puede pasar según los semáforos"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2
        
        # Posición de las líneas de paso (stop line)
        stop_line_position = 120
        
        # Distancia de detección (debe detenerse ANTES de la línea)
        # Ajustamos según el tamaño del vehículo
        vehicle_half_length = vehicle.size[0] // 2 + 10  # Margen de seguridad
        
        # Verificar según dirección del vehículo
        if vehicle.direction == 'right':
            # Debe detenerse antes de la línea de paso izquierda
            stop_point = center_x - stop_line_position - vehicle_half_length
            if vehicle.x >= stop_point and vehicle.x < center_x - 50:
                if not self.lights['horizontal'][0].can_pass():
                    return False
                    
        elif vehicle.direction == 'left':
            # Debe detenerse antes de la línea de paso derecha
            stop_point = center_x + stop_line_position + vehicle_half_length
            if vehicle.x <= stop_point and vehicle.x > center_x + 50:
                if not self.lights['horizontal'][1].can_pass():
                    return False
                    
        elif vehicle.direction == 'down':
            # Debe detenerse antes de la línea de paso superior
            stop_point = center_y - stop_line_position - vehicle_half_length
            if vehicle.y >= stop_point and vehicle.y < center_y - 50:
                if not self.lights['vertical'][0].can_pass():
                    return False
                    
        elif vehicle.direction == 'up':
            # Debe detenerse antes de la línea de paso inferior
            stop_point = center_y + stop_line_position + vehicle_half_length
            if vehicle.y <= stop_point and vehicle.y > center_y + 50:
                if not self.lights['vertical'][1].can_pass():
                    return False
        
        # Vehículos de emergencia tienen prioridad
        if vehicle.has_priority:
            return True
        
        return True
    
    def check_vehicle_ahead(self, vehicle: Vehicle) -> bool:
        """Verifica si hay otro vehículo muy cerca adelante en la misma dirección"""
        safe_distance = 80  # Distancia de seguridad entre vehículos
        
        for other in self.vehicles:
            if other == vehicle:
                continue
            
            # Solo verificar vehículos en la misma dirección
            if other.direction != vehicle.direction:
                continue
            
            # Calcular distancia según dirección
            if vehicle.direction == 'right':
                # El otro está adelante si su x es mayor
                if other.x > vehicle.x:
                    distance = other.x - vehicle.x
                    if distance < safe_distance:
                        return False  # Hay un vehículo muy cerca adelante
                        
            elif vehicle.direction == 'left':
                # El otro está adelante si su x es menor
                if other.x < vehicle.x:
                    distance = vehicle.x - other.x
                    if distance < safe_distance:
                        return False
                        
            elif vehicle.direction == 'down':
                # El otro está adelante si su y es mayor
                if other.y > vehicle.y:
                    distance = other.y - vehicle.y
                    if distance < safe_distance:
                        return False
                        
            elif vehicle.direction == 'up':
                # El otro está adelante si su y es menor
                if other.y < vehicle.y:
                    distance = vehicle.y - other.y
                    if distance < safe_distance:
                        return False
        
        return True
    
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
            self.spawn_interval = max(0.8, 2.0 - (self.game_state['level'] * 0.1))
        
        # Actualizar vehículos (Template Method)
        for vehicle in self.vehicles[:]:
            # Verificar si puede moverse (semáforo Y vehículo adelante)
            can_move_traffic_light = self.check_traffic_lights(vehicle)
            can_move_no_vehicle_ahead = self.check_vehicle_ahead(vehicle)
            can_move = can_move_traffic_light and can_move_no_vehicle_ahead
            
            vehicle.update(dt, can_move)
            
            # Remover vehículos fuera de pantalla
            if vehicle.is_off_screen(self.WIDTH, self.HEIGHT):
                self.vehicles.remove(vehicle)
                
                # Dar puntos por vehículo que pasó exitosamente
                points = int(10 * self.game_state['score_multiplier'])
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
           self.game_state['vehicles_passed'] % 20 == 0:
            self.game_state['level'] += 1
        
        # Game Over
        if self.game_state['lives'] <= 0:
            self.game_over = True
    
    def draw_road(self):
        """Dibuja las calles de la intersección"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2
        
        # Fondo de césped
        self.screen.fill(self.GRASS_COLOR)
        
        # Calle horizontal
        pygame.draw.rect(self.screen, self.ROAD_COLOR, 
                        (0, center_y - 80, self.WIDTH, 160))
        
        # Calle vertical
        pygame.draw.rect(self.screen, self.ROAD_COLOR,
                        (center_x - 80, 0, 160, self.HEIGHT))
        
        # Líneas divisorias
        dash_length = 30
        gap_length = 20
        
        # Línea horizontal
        x = 0
        while x < self.WIDTH:
            pygame.draw.rect(self.screen, self.LINE_COLOR,
                           (x, center_y - 2, dash_length, 4))
            x += dash_length + gap_length
        
        # Línea vertical
        y = 0
        while y < self.HEIGHT:
            pygame.draw.rect(self.screen, self.LINE_COLOR,
                           (center_x - 2, y, 4, dash_length))
            y += dash_length + gap_length
        
        # Líneas de paso (stop lines) donde los vehículos deben detenerse
        stop_line_color = (255, 255, 255)
        stop_line_width = 4
        
        # Línea de paso horizontal izquierda (para vehículos yendo a la derecha)
        for i in range(10):
            pygame.draw.rect(self.screen, stop_line_color,
                           (center_x - 120, center_y - 80 + i * 16, 10, 12))
        
        # Línea de paso horizontal derecha (para vehículos yendo a la izquierda)
        for i in range(10):
            pygame.draw.rect(self.screen, stop_line_color,
                           (center_x + 110, center_y - 80 + i * 16, 10, 12))
        
        # Línea de paso vertical superior (para vehículos yendo hacia abajo)
        for i in range(10):
            pygame.draw.rect(self.screen, stop_line_color,
                           (center_x - 80 + i * 16, center_y - 120, 12, 10))
        
        # Línea de paso vertical inferior (para vehículos yendo hacia arriba)
        for i in range(10):
            pygame.draw.rect(self.screen, stop_line_color,
                           (center_x - 80 + i * 16, center_y + 110, 12, 10))
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Panel superior
        panel_height = 80
        panel = pygame.Surface((self.WIDTH, panel_height))
        panel.fill((30, 30, 30))
        panel.set_alpha(200)
        self.screen.blit(panel, (0, 0))
        
        # Puntuación
        score_text = self.font_medium.render(f"Puntos: {self.game_state['score']}", 
                                            True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        
        # Vidas
        lives_text = self.font_medium.render(f"Vidas: {self.game_state['lives']}", 
                                            True, (255, 0, 0))
        self.screen.blit(lives_text, (250, 20))
        
        # Nivel
        level_text = self.font_medium.render(f"Nivel: {self.game_state['level']}", 
                                            True, (255, 255, 0))
        self.screen.blit(level_text, (450, 20))
        
        # Estadísticas
        stats_text = self.font_small.render(
            f"Pasados: {self.game_state['vehicles_passed']} | "
            f"Colisiones: {self.game_state['collisions']} | "
            f"Infracciones: {self.game_state['violations']}", 
            True, (200, 200, 200))
        self.screen.blit(stats_text, (650, 30))
        
        # Indicadores de power-ups activos
        if self.game_state['time_scale'] < 1.0:
            powerup_text = self.font_small.render("TIEMPO LENTO", True, (0, 255, 255))
            self.screen.blit(powerup_text, (self.WIDTH - 200, 25))
        
        if self.game_state['score_multiplier'] > 1.0:
            mult_text = self.font_small.render(
                f"PUNTOS x{self.game_state['score_multiplier']:.1f}", 
                True, (255, 215, 0))
            self.screen.blit(mult_text, (self.WIDTH - 200, 50))
        
        # Instrucciones
        help_text = self.font_small.render(
            "Click en semáforos para cambiar luces | ESPACIO: Pausar | ESC: Salir",
            True, (150, 150, 150))
        self.screen.blit(help_text, (20, self.HEIGHT - 30))
    
    def draw_game_over(self):
        """Dibuja la pantalla de Game Over"""
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Texto principal
        game_over_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, text_rect)
        
        # Puntuación final
        score_text = self.font_medium.render(
            f"Puntuación Final: {self.game_state['score']}", 
            True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # Estadísticas
        stats_lines = [
            f"Nivel alcanzado: {self.game_state['level']}",
            f"Vehículos pasados: {self.game_state['vehicles_passed']}",
            f"Colisiones: {self.game_state['collisions']}",
            f"Infracciones: {self.game_state['violations']}"
        ]
        
        y_offset = self.HEIGHT // 2 + 60
        for line in stats_lines:
            text = self.font_small.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35
        
        # Instrucciones
        restart_text = self.font_small.render(
            "Presiona R para reiniciar o ESC para salir", 
            True, (255, 255, 0))
        restart_rect = restart_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT - 100))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Fondo y calles
        self.draw_road()
        
        # Semáforos
        self.traffic_controller.draw_all(self.screen)
        
        # Vehículos
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        # Notificaciones de eventos
        self.event_system.draw_notifications(self.screen)
        
        # Pausa
        if self.paused:
            pause_overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
            pause_overlay.fill((0, 0, 0))
            pause_overlay.set_alpha(100)
            self.screen.blit(pause_overlay, (0, 0))
            
            pause_text = self.font_large.render("PAUSA", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)
        
        # Game Over
        if self.game_over:
            self.draw_game_over()
        
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
            dt = self.clock.tick(self.FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
