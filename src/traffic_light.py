"""
Patrón State
Implementación de semáforos con diferentes estados y transiciones
"""

import pygame
from abc import ABC, abstractmethod
from typing import Tuple


class TrafficLightState(ABC):
    """
    Clase abstracta que representa un estado del semáforo.
    Cada estado concreto implementa su comportamiento específico.
    """
    
    def __init__(self, traffic_light: 'TrafficLight'):
        self.traffic_light = traffic_light
        self.time_in_state = 0
    
    @abstractmethod
    def get_color(self) -> Tuple[int, int, int]:
        """Retorna el color RGB del estado"""
        pass
    
    @abstractmethod
    def can_pass(self) -> bool:
        """Indica si los vehículos pueden pasar"""
        pass
    
    @abstractmethod
    def get_duration(self) -> float:
        """Duración del estado en segundos"""
        pass
    
    @abstractmethod
    def next_state(self) -> 'TrafficLightState':
        """Retorna el siguiente estado en la secuencia"""
        pass
    
    def update(self, dt: float) -> None:
        """Actualiza el tiempo en el estado y transiciona si es necesario"""
        self.time_in_state += dt
        
        if self.time_in_state >= self.get_duration():
            self.traffic_light.change_state(self.next_state())
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna el nombre del estado"""
        pass
    
    def on_enter(self) -> None:
        """Hook ejecutado al entrar al estado"""
        self.time_in_state = 0
    
    def on_exit(self) -> None:
        """Hook ejecutado al salir del estado"""
        pass


class GreenState(TrafficLightState):
    """Estado Verde - Los vehículos pueden pasar"""
    
    def get_color(self) -> Tuple[int, int, int]:
        return (0, 255, 0)  # Verde
    
    def can_pass(self) -> bool:
        return True
    
    def get_duration(self) -> float:
        # Duración base del semáforo, puede ser ajustada dinámicamente
        return self.traffic_light.green_duration
    
    def next_state(self) -> TrafficLightState:
        return YellowState(self.traffic_light)
    
    def get_name(self) -> str:
        return "GREEN"
    
    def on_enter(self) -> None:
        super().on_enter()
        # Aquí podrías agregar efectos de sonido o animaciones


class YellowState(TrafficLightState):
    """Estado Amarillo - Advertencia, los vehículos deben prepararse para detenerse"""
    
    def get_color(self) -> Tuple[int, int, int]:
        return (255, 255, 0)  # Amarillo
    
    def can_pass(self) -> bool:
        # Los vehículos pueden pasar en amarillo si están muy cerca
        return False
    
    def get_duration(self) -> float:
        return self.traffic_light.yellow_duration
    
    def next_state(self) -> TrafficLightState:
        return RedState(self.traffic_light)
    
    def get_name(self) -> str:
        return "YELLOW"


class RedState(TrafficLightState):
    """Estado Rojo - Los vehículos deben detenerse"""
    
    def get_color(self) -> Tuple[int, int, int]:
        return (255, 0, 0)  # Rojo
    
    def can_pass(self) -> bool:
        return False
    
    def get_duration(self) -> float:
        return self.traffic_light.red_duration
    
    def next_state(self) -> TrafficLightState:
        return GreenState(self.traffic_light)
    
    def get_name(self) -> str:
        return "RED"


class TrafficLight:
    """
    Contexto que mantiene el estado actual del semáforo.
    Permite cambiar entre estados y delega el comportamiento al estado actual.
    """
    
    def __init__(self, x: int, y: int, direction: str, 
                 green_duration: float = 5.0,
                 yellow_duration: float = 2.0,
                 red_duration: float = 5.0):
        self.x = x
        self.y = y
        self.direction = direction  # 'horizontal' o 'vertical'
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.red_duration = red_duration
        
        # Estado inicial
        self._state = RedState(self)
        self._state.on_enter()
        
        self.manual_override = False  # Para control manual del jugador
        self.size = 20
    
    def change_state(self, new_state: TrafficLightState) -> None:
        """Cambia el estado del semáforo"""
        self._state.on_exit()
        self._state = new_state
        self._state.on_enter()
    
    def update(self, dt: float) -> None:
        """Actualiza el semáforo (automático si no hay override manual)"""
        if not self.manual_override:
            self._state.update(dt)
    
    def can_pass(self) -> bool:
        """Delega al estado actual si los vehículos pueden pasar"""
        return self._state.can_pass()
    
    def get_color(self) -> Tuple[int, int, int]:
        """Delega al estado actual el color"""
        return self._state.get_color()
    
    def get_state_name(self) -> str:
        """Retorna el nombre del estado actual"""
        return self._state.get_name()
    
    def get_time_remaining(self) -> float:
        """Retorna el tiempo restante en el estado actual"""
        return max(0, self._state.get_duration() - self._state.time_in_state)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el semáforo en pantalla"""
        # Fondo del semáforo
        background_rect = pygame.Rect(self.x - 15, self.y - 45, 30, 90)
        pygame.draw.rect(screen, (50, 50, 50), background_rect, border_radius=5)
        
        # Las tres luces
        red_pos = (self.x, self.y - 25)
        yellow_pos = (self.x, self.y)
        green_pos = (self.x, self.y + 25)
        
        # Dibuja todas las luces apagadas primero
        for pos in [red_pos, yellow_pos, green_pos]:
            pygame.draw.circle(screen, (30, 30, 30), pos, 10)
        
        # Dibuja la luz activa
        state_name = self.get_state_name()
        if state_name == "RED":
            pygame.draw.circle(screen, (255, 0, 0), red_pos, 10)
            pygame.draw.circle(screen, (255, 100, 100), red_pos, 12, 2)
        elif state_name == "YELLOW":
            pygame.draw.circle(screen, (255, 255, 0), yellow_pos, 10)
            pygame.draw.circle(screen, (255, 255, 100), yellow_pos, 12, 2)
        elif state_name == "GREEN":
            pygame.draw.circle(screen, (0, 255, 0), green_pos, 10)
            pygame.draw.circle(screen, (100, 255, 100), green_pos, 12, 2)
    
    # Métodos para control manual del jugador
    def toggle_manual_override(self) -> None:
        """Activa/desactiva el control manual"""
        self.manual_override = not self.manual_override
    
    def force_green(self) -> None:
        """Fuerza el estado verde (control manual)"""
        if self.manual_override:
            self.change_state(GreenState(self))
    
    def force_red(self) -> None:
        """Fuerza el estado rojo (control manual)"""
        if self.manual_override:
            self.change_state(RedState(self))
    
    def force_yellow(self) -> None:
        """Fuerza el estado amarillo (control manual)"""
        if self.manual_override:
            self.change_state(YellowState(self))
    
    def cycle_state(self) -> None:
        """Cicla manualmente al siguiente estado"""
        if self.manual_override:
            self.change_state(self._state.next_state())
    
    def adjust_timing(self, green_modifier: float = 1.0, 
                     red_modifier: float = 1.0) -> None:
        """Ajusta dinámicamente la duración de los estados"""
        self.green_duration *= green_modifier
        self.red_duration *= red_modifier
        
        # Límites razonables
        self.green_duration = max(2.0, min(15.0, self.green_duration))
        self.red_duration = max(2.0, min(15.0, self.red_duration))


class TrafficLightController:
    """
    Controlador que gestiona múltiples semáforos coordinados.
    Asegura que semáforos perpendiculares no estén verdes al mismo tiempo.
    """
    
    def __init__(self):
        self.traffic_lights = []
        self.horizontal_lights = []
        self.vertical_lights = []
    
    def add_traffic_light(self, traffic_light: TrafficLight) -> None:
        """Agrega un semáforo al controlador"""
        self.traffic_lights.append(traffic_light)
        
        if traffic_light.direction == 'horizontal':
            self.horizontal_lights.append(traffic_light)
        else:
            self.vertical_lights.append(traffic_light)
    
    def update(self, dt: float) -> None:
        """Actualiza todos los semáforos"""
        for light in self.traffic_lights:
            light.update(dt)
        
        # Coordina los semáforos si no están en modo manual
        self.coordinate_lights()
    
    def coordinate_lights(self) -> None:
        """
        Asegura que los semáforos perpendiculares estén coordinados.
        Si los horizontales están en verde, los verticales deben estar en rojo.
        """
        for h_light in self.horizontal_lights:
            if not h_light.manual_override and h_light.can_pass():
                for v_light in self.vertical_lights:
                    if not v_light.manual_override and v_light.can_pass():
                        # Conflicto: forzar uno a rojo
                        v_light.change_state(RedState(v_light))
    
    def draw_all(self, screen: pygame.Surface) -> None:
        """Dibuja todos los semáforos"""
        for light in self.traffic_lights:
            light.draw(screen)
    
    def get_light_at_position(self, x: int, y: int, tolerance: int = 30) -> TrafficLight:
        """Encuentra el semáforo más cercano a una posición (para clicks)"""
        for light in self.traffic_lights:
            distance = ((light.x - x) ** 2 + (light.y - y) ** 2) ** 0.5
            if distance <= tolerance:
                return light
        return None
