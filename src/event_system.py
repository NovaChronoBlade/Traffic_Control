"""
Patrón Chain of Responsibility
Implementación de cadena de manejadores para procesar eventos del juego
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pygame


class GameEvent:
    """Representa un evento del juego que puede ser procesado"""
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.handled = False
        self.response = {}
    
    def __repr__(self):
        return f"GameEvent(type={self.event_type}, data={self.data})"


class EventHandler(ABC):
    """
    Clase abstracta que representa un manejador en la cadena.
    Cada manejador decide si procesa el evento o lo pasa al siguiente.
    """
    
    def __init__(self):
        self._next_handler: Optional[EventHandler] = None
    
    def set_next(self, handler: 'EventHandler') -> 'EventHandler':
        """Establece el siguiente manejador en la cadena"""
        self._next_handler = handler
        return handler
    
    def handle(self, event: GameEvent) -> GameEvent:
        """
        Procesa el evento y decide si pasarlo al siguiente manejador.
        Template method que define el flujo general.
        """
        if self.can_handle(event):
            self.process(event)
        
        # Si el evento no está completamente manejado, pasa al siguiente
        if self._next_handler and not event.handled:
            return self._next_handler.handle(event)
        
        return event
    
    @abstractmethod
    def can_handle(self, event: GameEvent) -> bool:
        """Determina si este manejador puede procesar el evento"""
        pass
    
    @abstractmethod
    def process(self, event: GameEvent) -> None:
        """Procesa el evento y modifica su estado"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna el nombre del manejador"""
        pass


class CollisionHandler(EventHandler):
    """Manejador de colisiones entre vehículos"""
    
    def __init__(self, game_state: Dict[str, Any]):
        super().__init__()
        self.game_state = game_state
    
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "collision"
    
    def process(self, event: GameEvent) -> None:
        """Procesa una colisión entre vehículos"""
        vehicle1 = event.data.get('vehicle1')
        vehicle2 = event.data.get('vehicle2')
        
        if vehicle1 and vehicle2:
            # Penalización por colisión
            penalty = 100
            
            # Mayor penalización si uno es vehículo de emergencia
            if vehicle1.has_priority or vehicle2.has_priority:
                penalty = 300
            
            self.game_state['score'] = max(0, self.game_state['score'] - penalty)
            self.game_state['lives'] -= 1
            self.game_state['collisions'] += 1
            
            # Marca los vehículos para remover
            event.data['remove_vehicles'] = [vehicle1, vehicle2]
            
            # Información de respuesta
            event.response = {
                'penalty': penalty,
                'message': f"¡Colisión! -{penalty} puntos",
                'severity': 'high' if penalty > 100 else 'medium'
            }
            
            # El evento está parcialmente manejado, pero puede seguir en la cadena
            # para efectos adicionales (sonidos, animaciones, etc.)
    
    def get_name(self) -> str:
        return "CollisionHandler"


class TrafficViolationHandler(EventHandler):
    """Manejador de infracciones de tráfico"""
    
    def __init__(self, game_state: Dict[str, Any]):
        super().__init__()
        self.game_state = game_state
    
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "traffic_violation"
    
    def process(self, event: GameEvent) -> None:
        """Procesa una infracción de tráfico"""
        violation_type = event.data.get('type')
        vehicle = event.data.get('vehicle')
        
        penalties = {
            'red_light': 50,
            'speeding': 30,
            'wrong_lane': 40,
            'emergency_obstruction': 200
        }
        
        penalty = penalties.get(violation_type, 25)
        
        # Reducir puntuación
        self.game_state['score'] = max(0, self.game_state['score'] - penalty)
        self.game_state['violations'] += 1
        
        # Información de respuesta
        messages = {
            'red_light': "¡Semáforo en rojo ignorado!",
            'speeding': "¡Exceso de velocidad!",
            'wrong_lane': "¡Carril incorrecto!",
            'emergency_obstruction': "¡Obstrucción a vehículo de emergencia!"
        }
        
        event.response = {
            'penalty': penalty,
            'message': f"{messages.get(violation_type, 'Infracción')} -{penalty} puntos",
            'severity': 'high' if penalty > 100 else 'low'
        }
    
    def get_name(self) -> str:
        return "TrafficViolationHandler"


class ScoreHandler(EventHandler):
    """Manejador de eventos de puntuación positiva"""
    
    def __init__(self, game_state: Dict[str, Any]):
        super().__init__()
        self.game_state = game_state
    
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type in ["vehicle_passed", "smooth_flow", "perfect_timing"]
    
    def process(self, event: GameEvent) -> None:
        """Procesa eventos que otorgan puntos"""
        points = 0
        message = ""
        
        if event.event_type == "vehicle_passed":
            # Puntos por cada vehículo que pasa exitosamente
            vehicle = event.data.get('vehicle')
            base_points = 10
            
            # Bonus por vehículos especiales
            if hasattr(vehicle, 'has_priority') and vehicle.has_priority:
                points = base_points * 3
                message = "¡Vehículo de emergencia! +30 puntos"
            elif vehicle.__class__.__name__ == 'Bus':
                points = base_points * 2
                message = "¡Autobús pasó! +20 puntos"
            else:
                points = base_points
                message = "+10 puntos"
            
            self.game_state['vehicles_passed'] += 1
            
        elif event.event_type == "smooth_flow":
            # Bonus por mantener el flujo sin detenciones
            points = 50
            message = "¡Flujo perfecto! +50 puntos"
            
        elif event.event_type == "perfect_timing":
            # Bonus por cambiar semáforo en el momento perfecto
            points = 25
            message = "¡Timing perfecto! +25 puntos"
        
        self.game_state['score'] += points
        
        event.response = {
            'points': points,
            'message': message,
            'severity': 'positive'
        }
    
    def get_name(self) -> str:
        return "ScoreHandler"


class PowerUpHandler(EventHandler):
    """Manejador de power-ups y bonificaciones especiales"""
    
    def __init__(self, game_state: Dict[str, Any]):
        super().__init__()
        self.game_state = game_state
    
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "power_up"
    
    def process(self, event: GameEvent) -> None:
        """Procesa power-ups recolectados"""
        power_up_type = event.data.get('type')
        
        if power_up_type == "slow_time":
            # Ralentiza el tiempo por un período
            self.game_state['time_scale'] = 0.5
            self.game_state['power_up_duration'] = 5.0
            event.response = {
                'message': "¡Tiempo ralentizado!",
                'duration': 5.0,
                'severity': 'positive'
            }
            
        elif power_up_type == "extra_life":
            # Vida extra
            self.game_state['lives'] += 1
            event.response = {
                'message': "¡Vida extra!",
                'severity': 'positive'
            }
            
        elif power_up_type == "score_multiplier":
            # Multiplicador de puntos
            self.game_state['score_multiplier'] = 2.0
            self.game_state['multiplier_duration'] = 10.0
            event.response = {
                'message': "¡Puntos x2!",
                'duration': 10.0,
                'severity': 'positive'
            }
            
        elif power_up_type == "clear_traffic":
            # Limpia algunos vehículos de la pantalla
            event.data['clear_vehicles'] = True
            event.response = {
                'message': "¡Tráfico despejado!",
                'severity': 'positive'
            }
    
    def get_name(self) -> str:
        return "PowerUpHandler"


class CongestionHandler(EventHandler):
    """Manejador de congestión de tráfico"""
    
    def __init__(self, game_state: Dict[str, Any]):
        super().__init__()
        self.game_state = game_state
    
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "congestion"
    
    def process(self, event: GameEvent) -> None:
        """Procesa eventos de congestión vehicular"""
        congestion_level = event.data.get('level', 'medium')
        waiting_vehicles = event.data.get('waiting_vehicles', 0)
        
        # Penalización basada en el nivel de congestión
        penalties = {
            'low': 5,
            'medium': 15,
            'high': 30,
            'critical': 50
        }
        
        penalty = penalties.get(congestion_level, 10)
        
        self.game_state['score'] = max(0, self.game_state['score'] - penalty)
        
        messages = {
            'low': "Tráfico lento",
            'medium': "Congestión moderada",
            'high': "¡Tráfico pesado!",
            'critical': "¡CONGESTIÓN CRÍTICA!"
        }
        
        event.response = {
            'penalty': penalty,
            'message': f"{messages.get(congestion_level)} -{penalty} puntos",
            'severity': 'medium' if congestion_level in ['low', 'medium'] else 'high',
            'waiting_vehicles': waiting_vehicles
        }
    
    def get_name(self) -> str:
        return "CongestionHandler"


class LoggingHandler(EventHandler):
    """Manejador final que registra todos los eventos (para debug)"""
    
    def __init__(self):
        super().__init__()
        self.event_log = []
    
    def can_handle(self, event: GameEvent) -> bool:
        return True  # Maneja todos los eventos
    
    def process(self, event: GameEvent) -> None:
        """Registra el evento en el log"""
        self.event_log.append({
            'type': event.event_type,
            'data': event.data,
            'response': event.response,
            'timestamp': pygame.time.get_ticks()
        })
        
        # Mantener solo los últimos 100 eventos
        if len(self.event_log) > 100:
            self.event_log.pop(0)
        
        # Marca el evento como completamente manejado
        event.handled = True
    
    def get_name(self) -> str:
        return "LoggingHandler"
    
    def get_recent_events(self, count: int = 5):
        """Retorna los eventos más recientes"""
        return self.event_log[-count:]


class EventSystem:
    """
    Sistema que gestiona la cadena de responsabilidad.
    Facilita la creación y manejo de eventos.
    """
    
    def __init__(self, game_state: Dict[str, Any]):
        self.game_state = game_state
        self.notifications = []  # Notificaciones para mostrar en pantalla
        
        # Construir la cadena de manejadores
        self.collision_handler = CollisionHandler(game_state)
        self.violation_handler = TrafficViolationHandler(game_state)
        self.score_handler = ScoreHandler(game_state)
        self.power_up_handler = PowerUpHandler(game_state)
        self.congestion_handler = CongestionHandler(game_state)
        self.logging_handler = LoggingHandler()
        
        # Encadenar los manejadores
        self.collision_handler.set_next(self.violation_handler) \
                              .set_next(self.score_handler) \
                              .set_next(self.power_up_handler) \
                              .set_next(self.congestion_handler) \
                              .set_next(self.logging_handler)
        
        # El primer manejador en la cadena
        self.first_handler = self.collision_handler
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> GameEvent:
        """Emite un evento y lo procesa a través de la cadena"""
        event = GameEvent(event_type, data)
        processed_event = self.first_handler.handle(event)
        
        # Si hay mensaje de respuesta, agregarlo a las notificaciones
        if processed_event.response.get('message'):
            self.notifications.append({
                'message': processed_event.response['message'],
                'severity': processed_event.response.get('severity', 'info'),
                'time': pygame.time.get_ticks(),
                'duration': 2000  # 2 segundos
            })
        
        return processed_event
    
    def update_notifications(self) -> None:
        """Limpia notificaciones expiradas"""
        current_time = pygame.time.get_ticks()
        self.notifications = [
            n for n in self.notifications 
            if current_time - n['time'] < n['duration']
        ]
    
    def draw_notifications(self, screen: pygame.Surface) -> None:
        """Dibuja las notificaciones en pantalla"""
        font = pygame.font.Font(None, 28)
        y_offset = 100
        
        for notification in self.notifications:
            # Color según severidad
            colors = {
                'positive': (0, 255, 0),
                'low': (255, 255, 0),
                'medium': (255, 165, 0),
                'high': (255, 0, 0),
                'info': (255, 255, 255)
            }
            color = colors.get(notification['severity'], (255, 255, 255))
            
            # Efecto de fade out
            elapsed = pygame.time.get_ticks() - notification['time']
            alpha = 255 if elapsed < 1500 else int(255 * (1 - (elapsed - 1500) / 500))
            
            text = font.render(notification['message'], True, color)
            
            # Fondo semitransparente
            text_rect = text.get_rect(center=(screen.get_width() // 2, y_offset))
            background = pygame.Surface((text_rect.width + 20, text_rect.height + 10))
            background.fill((0, 0, 0))
            background.set_alpha(min(180, alpha))
            
            screen.blit(background, (text_rect.x - 10, text_rect.y - 5))
            
            # Aplicar alpha al texto (limitado en pygame básico, pero simula el efecto)
            text.set_alpha(alpha)
            screen.blit(text, text_rect)
            
            y_offset += 40
    
    def get_event_log(self, count: int = 5):
        """Retorna los eventos recientes del log"""
        return self.logging_handler.get_recent_events(count)
