"""
Utilidades para manejo de colisiones y geometría
"""

import pygame
from typing import List, Optional
from src.vehicles import Vehicle
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INTERSECTION_SIZE,
    SAFE_DISTANCE_BETWEEN_VEHICLES, STOP_LINE_DISTANCE,
    DETECTION_MARGIN, LANE_WIDTH
)


class CollisionDetector:
    """Maneja la detección de colisiones entre vehículos"""
    
    @staticmethod
    def are_in_intersection(v1: Vehicle, v2: Vehicle) -> bool:
        """Verifica si ambos vehículos están en la intersección"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        intersection_zone = pygame.Rect(
            center_x - INTERSECTION_SIZE // 2,
            center_y - INTERSECTION_SIZE // 2,
            INTERSECTION_SIZE,
            INTERSECTION_SIZE
        )
        
        return (intersection_zone.collidepoint(v1.x, v1.y) and 
                intersection_zone.collidepoint(v2.x, v2.y))
    
    @staticmethod
    def are_in_different_directions(v1: Vehicle, v2: Vehicle) -> bool:
        """Verifica si dos vehículos van en direcciones diferentes"""
        return v1.direction != v2.direction
    
    @staticmethod
    def check_collision(v1: Vehicle, v2: Vehicle) -> bool:
        """Verifica si dos vehículos colisionan"""
        # Solo colisionan si están en la intersección
        if not CollisionDetector.are_in_intersection(v1, v2):
            return False
        
        # Solo colisionan si van en direcciones diferentes
        if not CollisionDetector.are_in_different_directions(v1, v2):
            return False
        
        # Verificar colisión de rectángulos
        return v1.get_rect().colliderect(v2.get_rect())


class VehicleSpacingChecker:
    """Verifica el espacio entre vehículos para evitar amontonamiento"""
    
    @staticmethod
    def get_vehicle_ahead(vehicle: Vehicle, all_vehicles: List[Vehicle]) -> Optional[Vehicle]:
        """Encuentra el vehículo más cercano adelante en la misma dirección y carril"""
        closest_vehicle = None
        min_distance = float('inf')
        
        for other in all_vehicles:
            if other == vehicle or other.direction != vehicle.direction:
                continue
            
            # Verificar si están en el mismo carril (aproximadamente)
            if not VehicleSpacingChecker._are_in_same_lane(vehicle, other):
                continue
            
            # Calcular si está adelante
            distance = VehicleSpacingChecker._get_distance_ahead(vehicle, other)
            
            if distance is not None and 0 < distance < min_distance:
                min_distance = distance
                closest_vehicle = other
        
        return closest_vehicle
    
    @staticmethod
    def _are_in_same_lane(v1: Vehicle, v2: Vehicle) -> bool:
        """Verifica si dos vehículos están en el mismo carril"""
        tolerance = 30  # Píxeles de tolerancia
        
        if v1.direction in ['left', 'right']:
            # Para movimiento horizontal, comparar Y
            return abs(v1.y - v2.y) < tolerance
        else:
            # Para movimiento vertical, comparar X
            return abs(v1.x - v2.x) < tolerance
    
    @staticmethod
    def _get_distance_ahead(vehicle: Vehicle, other: Vehicle) -> Optional[float]:
        """Calcula la distancia al vehículo adelante, retorna None si está atrás"""
        if vehicle.direction == 'right':
            if other.x > vehicle.x:
                return other.x - vehicle.x
        elif vehicle.direction == 'left':
            if other.x < vehicle.x:
                return vehicle.x - other.x
        elif vehicle.direction == 'down':
            if other.y > vehicle.y:
                return other.y - vehicle.y
        elif vehicle.direction == 'up':
            if other.y < vehicle.y:
                return vehicle.y - other.y
        
        return None
    
    @staticmethod
    def can_move_forward(vehicle: Vehicle, all_vehicles: List[Vehicle]) -> bool:
        """Verifica si el vehículo puede moverse sin chocar con el de adelante"""
        vehicle_ahead = VehicleSpacingChecker.get_vehicle_ahead(vehicle, all_vehicles)
        
        if vehicle_ahead is None:
            return True
        
        distance = VehicleSpacingChecker._get_distance_ahead(vehicle, vehicle_ahead)
        
        if distance is None:
            return True
        
        # Calcular distancia de seguridad según tamaño de vehículos
        safe_distance = SAFE_DISTANCE_BETWEEN_VEHICLES + (vehicle.size[0] + vehicle_ahead.size[0]) // 2
        
        return distance >= safe_distance


class TrafficLightChecker:
    """Verifica si un vehículo puede pasar según los semáforos"""
    
    @staticmethod
    def can_pass_traffic_light(vehicle: Vehicle, lights: dict) -> bool:
        """Verifica si el vehículo puede pasar el semáforo"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Vehículos de emergencia que se saltan semáforos cambian de carril
        if vehicle.has_priority and not TrafficLightChecker._is_near_stop_line(vehicle):
            TrafficLightChecker._change_lane_if_needed(vehicle)
            return True
        
        # Calcular posición de parada según tamaño del vehículo
        # El vehículo debe parar ANTES de la línea, considerando su tamaño
        vehicle_half_length = vehicle.size[0] // 2
        
        if vehicle.direction == 'right':
            # La línea está en center_x - STOP_LINE_DISTANCE
            # El vehículo para cuando su frente (x + mitad) llega a la línea
            stop_point = center_x - STOP_LINE_DISTANCE - vehicle_half_length - DETECTION_MARGIN
            if vehicle.x >= stop_point and vehicle.x < center_x - 50:
                return lights['horizontal'][0].can_pass()
                
        elif vehicle.direction == 'left':
            # La línea está en center_x + STOP_LINE_DISTANCE
            # El vehículo para cuando su frente (x - mitad) llega a la línea
            stop_point = center_x + STOP_LINE_DISTANCE + vehicle_half_length + DETECTION_MARGIN
            if vehicle.x <= stop_point and vehicle.x > center_x + 50:
                return lights['horizontal'][1].can_pass()
                
        elif vehicle.direction == 'down':
            # La línea está en center_y - STOP_LINE_DISTANCE
            stop_point = center_y - STOP_LINE_DISTANCE - vehicle_half_length - DETECTION_MARGIN
            if vehicle.y >= stop_point and vehicle.y < center_y - 50:
                return lights['vertical'][0].can_pass()
                
        elif vehicle.direction == 'up':
            # La línea está en center_y + STOP_LINE_DISTANCE
            stop_point = center_y + STOP_LINE_DISTANCE + vehicle_half_length + DETECTION_MARGIN
            if vehicle.y <= stop_point and vehicle.y > center_y + 50:
                return lights['vertical'][1].can_pass()
        
        return True
    
    @staticmethod
    def _is_near_stop_line(vehicle: Vehicle) -> bool:
        """Verifica si el vehículo está cerca de la línea de parada"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        threshold = 150
        
        if vehicle.direction in ['left', 'right']:
            return abs(vehicle.x - center_x) < threshold
        else:
            return abs(vehicle.y - center_y) < threshold
    
    @staticmethod
    def _change_lane_if_needed(vehicle: Vehicle):
        """Cambia de carril al vehículo de emergencia para pasar semáforo en rojo"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        lane_offset = LANE_WIDTH // 2
        
        # Solo cambiar si está cerca de la intersección
        if vehicle.direction == 'right':
            if center_x - 200 < vehicle.x < center_x - 100:
                vehicle.y += lane_offset if vehicle.y < center_y else -lane_offset
        elif vehicle.direction == 'left':
            if center_x + 100 < vehicle.x < center_x + 200:
                vehicle.y += lane_offset if vehicle.y < center_y else -lane_offset
        elif vehicle.direction == 'down':
            if center_y - 200 < vehicle.y < center_y - 100:
                vehicle.x += lane_offset if vehicle.x < center_x else -lane_offset
        elif vehicle.direction == 'up':
            if center_y + 100 < vehicle.y < center_y + 200:
                vehicle.x += lane_offset if vehicle.x < center_x else -lane_offset
