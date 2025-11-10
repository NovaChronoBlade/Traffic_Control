"""
Patrón Template Method
Implementación de vehículos con comportamiento base y variaciones específicas
"""

import pygame
import random
import os
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class Vehicle(ABC):
    """
    Clase abstracta que implementa el patrón Template Method.
    Define el esqueleto del algoritmo de movimiento y comportamiento de vehículos.
    """
    
    def __init__(self, x: float, y: float, direction: str, lane: int):
        self.x = x
        self.y = y
        self.direction = direction  # 'up', 'down', 'left', 'right'
        self.lane = lane
        self.speed = self.get_base_speed()
        self.max_speed = self.get_max_speed()
        self.acceleration = self.get_acceleration()
        self.size = self.get_size()
        self.color = self.get_color()
        self.stopped = False
        self.waiting_time = 0
        self.has_priority = self.check_priority()
        
        # Cargar imagen si existe
        self.image = self.load_image()
        self.original_image = self.image  # Guardar original para rotaciones
        
    # Template Method - Define el esqueleto del algoritmo
    def update(self, dt: float, can_move: bool) -> None:
        """
        Método template que define el flujo de actualización del vehículo.
        Las subclases no pueden modificar este flujo, solo los pasos individuales.
        """
        # 1. Verificar comportamiento especial
        self.special_behavior(dt)
        
        # 2. Ajustar velocidad según condiciones
        if can_move:
            self.accelerate(dt)
            self.stopped = False
            self.waiting_time = 0
        else:
            self.decelerate(dt)
            self.stopped = True
            self.waiting_time += dt
        
        # 3. Mover el vehículo
        self.move(dt)
        
        # 4. Aplicar comportamiento post-movimiento
        self.post_move_behavior()
    
    def move(self, dt: float) -> None:
        """Mueve el vehículo según su dirección y velocidad"""
        if self.direction == 'right':
            self.x += self.speed * dt
        elif self.direction == 'left':
            self.x -= self.speed * dt
        elif self.direction == 'down':
            self.y += self.speed * dt
        elif self.direction == 'up':
            self.y -= self.speed * dt
    
    def accelerate(self, dt: float) -> None:
        """Acelera el vehículo hasta su velocidad máxima"""
        if self.speed < self.max_speed:
            self.speed = min(self.speed + self.acceleration * dt, self.max_speed)
    
    def decelerate(self, dt: float) -> None:
        """Desacelera el vehículo hasta detenerse"""
        if self.speed > 0:
            self.speed = max(self.speed - self.acceleration * 2 * dt, 0)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el vehículo en pantalla (con imagen o rectángulo de respaldo)"""
        if self.image:
            # Usar imagen PNG
            # Rotar imagen según dirección
            if self.direction == 'right':
                rotated_image = self.original_image
            elif self.direction == 'left':
                rotated_image = pygame.transform.rotate(self.original_image, 180)
            elif self.direction == 'down':
                rotated_image = pygame.transform.rotate(self.original_image, 270)
            else:  # up
                rotated_image = pygame.transform.rotate(self.original_image, 90)
            
            # Centrar la imagen en la posición del vehículo
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
            
            # Indicador de prioridad
            if self.has_priority:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)
        else:
            # Dibujar rectángulo de respaldo (código original)
            if self.direction in ['left', 'right']:
                width, height = self.size[0], self.size[1]
            else:
                width, height = self.size[1], self.size[0]
            
            rect = pygame.Rect(self.x - width // 2, self.y - height // 2, width, height)
            pygame.draw.rect(screen, self.color, rect)
            
            # Indicador de prioridad
            if self.has_priority:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)
    
    def is_off_screen(self, screen_width: int, screen_height: int) -> bool:
        """Verifica si el vehículo salió de la pantalla"""
        margin = 100
        return (self.x < -margin or self.x > screen_width + margin or
                self.y < -margin or self.y > screen_height + margin)
    
    def get_rect(self) -> pygame.Rect:
        """Retorna el rectángulo de colisión del vehículo"""
        if self.direction in ['left', 'right']:
            width, height = self.size[0], self.size[1]
        else:
            width, height = self.size[1], self.size[0]
        return pygame.Rect(self.x - width // 2, self.y - height // 2, width, height)
    
    # Métodos abstractos que deben ser implementados por las subclases
    @abstractmethod
    def get_base_speed(self) -> float:
        """Define la velocidad base del vehículo"""
        pass
    
    @abstractmethod
    def get_max_speed(self) -> float:
        """Define la velocidad máxima del vehículo"""
        pass
    
    @abstractmethod
    def get_acceleration(self) -> float:
        """Define la aceleración del vehículo"""
        pass
    
    @abstractmethod
    def get_size(self) -> Tuple[int, int]:
        """Define el tamaño del vehículo (ancho, alto)"""
        pass
    
    @abstractmethod
    def get_color(self) -> Tuple[int, int, int]:
        """Define el color del vehículo"""
        pass
    
    def get_image_name(self) -> Optional[str]:
        """Hook para el nombre del archivo de imagen. Retorna None si no hay imagen."""
        return None
    
    def load_image(self) -> Optional[pygame.Surface]:
        """Carga la imagen del vehículo si existe"""
        image_name = self.get_image_name()
        if not image_name:
            return None
        
        # Buscar en la carpeta assets/vehicles
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_path, 'assets', 'vehicles', image_name)
        
        if os.path.exists(image_path):
            try:
                image = pygame.image.load(image_path).convert_alpha()
                # Escalar imagen al tamaño definido
                width, height = self.size
                image = pygame.transform.scale(image, (width, height))
                return image
            except Exception as e:
                print(f"Error cargando imagen {image_name}: {e}")
                return None
        return None
    
    # Hooks - Métodos opcionales que las subclases pueden sobrescribir
    def special_behavior(self, dt: float) -> None:
        """Hook para comportamiento especial antes del movimiento"""
        pass
    
    def post_move_behavior(self) -> None:
        """Hook para comportamiento especial después del movimiento"""
        pass
    
    def check_priority(self) -> bool:
        """Hook para determinar si el vehículo tiene prioridad"""
        return False


class Car(Vehicle):
    """Vehículo estándar - Velocidad media"""
    
    def get_base_speed(self) -> float:
        return 100
    
    def get_max_speed(self) -> float:
        return 150
    
    def get_acceleration(self) -> float:
        return 80
    
    def get_size(self) -> Tuple[int, int]:
        return (50, 30)  # Reducido para que quepan 2 por carril
    
    def get_color(self) -> Tuple[int, int, int]:
        # Colores variados para los autos
        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 255)]
        return random.choice(colors)
    
    def get_image_name(self) -> Optional[str]:
        """Retorna el nombre del archivo de imagen"""
        return "car.png"


class FastCar(Vehicle):
    """Vehículo rápido - Alta velocidad y aceleración"""
    
    def get_base_speed(self) -> float:
        return 150
    
    def get_max_speed(self) -> float:
        return 250
    
    def get_acceleration(self) -> float:
        return 150
    
    def get_size(self) -> Tuple[int, int]:
        return (55, 32)  # Reducido
    
    def get_color(self) -> Tuple[int, int, int]:
        return (255, 165, 0)  # Naranja
    
    def get_image_name(self) -> Optional[str]:
        return "fast_car.png"
    
    def special_behavior(self, dt: float) -> None:
        """Los autos rápidos pueden zigzaguear ligeramente"""
        if not self.stopped and random.random() < 0.01:
            if self.direction in ['left', 'right']:
                self.y += random.randint(-2, 2)
            else:
                self.x += random.randint(-2, 2)


class Bus(Vehicle):
    """Autobús - Lento pero grande"""
    
    def get_base_speed(self) -> float:
        return 60
    
    def get_max_speed(self) -> float:
        return 100
    
    def get_acceleration(self) -> float:
        return 40
    
    def get_size(self) -> Tuple[int, int]:
        return (85, 38)  # Reducido, más grande que autos
    
    def get_color(self) -> Tuple[int, int, int]:
        return (0, 128, 255)  # Azul claro
    
    def get_image_name(self) -> Optional[str]:
        return "bus.png"
    
    def special_behavior(self, dt: float) -> None:
        """Los autobuses se detienen ocasionalmente (paradas)"""
        if not self.stopped and random.random() < 0.002:
            self.speed = 0
            self.waiting_time = 0
        
        # Reanudar después de "parada"
        if self.speed == 0 and self.waiting_time > 1.0 and random.random() < 0.1:
            self.speed = self.get_base_speed()


class EmergencyVehicle(Vehicle):
    """Vehículo de emergencia - Prioridad absoluta"""
    
    def get_base_speed(self) -> float:
        return 180
    
    def get_max_speed(self) -> float:
        return 200
    
    def get_acceleration(self) -> float:
        return 200
    
    def get_size(self) -> Tuple[int, int]:
        return (60, 35)  # Reducido
    
    def get_color(self) -> Tuple[int, int, int]:
        return (255, 0, 0)  # Rojo
    
    def get_image_name(self) -> Optional[str]:
        return "emergency.png"
    
    def check_priority(self) -> bool:
        """Vehículos de emergencia siempre tienen prioridad"""
        return True
    
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja con efecto de luz de emergencia"""
        super().draw(screen)
        
        # Efecto de sirena parpadeante
        if pygame.time.get_ticks() % 500 < 250:
            if self.direction in ['left', 'right']:
                width, height = self.size[0], self.size[1]
            else:
                width, height = self.size[1], self.size[0]
            
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x - width // 4), int(self.y)), 5)
            pygame.draw.circle(screen, (0, 0, 255), 
                             (int(self.x + width // 4), int(self.y)), 5)


class Truck(Vehicle):
    """Camión - Muy lento y muy grande"""
    
    def get_base_speed(self) -> float:
        return 50
    
    def get_max_speed(self) -> float:
        return 80
    
    def get_acceleration(self) -> float:
        return 30
    
    def get_size(self) -> Tuple[int, int]:
        return (110, 40)  # Reducido, el más grande
    
    def get_color(self) -> Tuple[int, int, int]:
        return (139, 69, 19)  # Café
    
    def get_image_name(self) -> Optional[str]:
        return "truck.png"
    
    def decelerate(self, dt: float) -> None:
        """Los camiones frenan más lentamente"""
        if self.speed > 0:
            self.speed = max(self.speed - self.acceleration * 1.5 * dt, 0)


# Factory para crear vehículos
class VehicleFactory:
    """Factory para crear diferentes tipos de vehículos"""
    
    @staticmethod
    def create_vehicle(vehicle_type: str, x: float, y: float, 
                      direction: str, lane: int) -> Vehicle:
        """Crea un vehículo según el tipo especificado"""
        vehicles = {
            'car': Car,
            'fast_car': FastCar,
            'bus': Bus,
            'emergency': EmergencyVehicle,
            'truck': Truck
        }
        
        vehicle_class = vehicles.get(vehicle_type, Car)
        return vehicle_class(x, y, direction, lane)
    
    @staticmethod
    def create_random_vehicle(x: float, y: float, 
                            direction: str, lane: int) -> Vehicle:
        """Crea un vehículo aleatorio con probabilidades ponderadas"""
        rand = random.random()
        
        if rand < 0.5:  # 50% auto normal
            return Car(x, y, direction, lane)
        elif rand < 0.7:  # 20% auto rápido
            return FastCar(x, y, direction, lane)
        elif rand < 0.85:  # 15% autobús
            return Bus(x, y, direction, lane)
        elif rand < 0.95:  # 10% camión
            return Truck(x, y, direction, lane)
        else:  # 5% emergencia
            return EmergencyVehicle(x, y, direction, lane)
