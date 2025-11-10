"""
Renderizado de elementos visuales del juego
"""

import pygame
from typing import List
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROAD_COLOR, LINE_COLOR,
    GRASS_COLOR, STOP_LINE_COLOR, STREET_WIDTH, STOP_LINE_DISTANCE
)


class RoadRenderer:
    """Dibuja las calles e intersección"""
    
    @staticmethod
    def draw(screen: pygame.Surface):
        """Dibuja el fondo, calles y líneas"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Fondo de césped
        screen.fill(GRASS_COLOR)
        
        # Calle horizontal
        pygame.draw.rect(screen, ROAD_COLOR, 
                        (0, center_y - STREET_WIDTH // 2, SCREEN_WIDTH, STREET_WIDTH))
        
        # Calle vertical
        pygame.draw.rect(screen, ROAD_COLOR,
                        (center_x - STREET_WIDTH // 2, 0, STREET_WIDTH, SCREEN_HEIGHT))
        
        # Líneas divisorias centrales
        RoadRenderer._draw_center_lines(screen, center_x, center_y)
        
        # Líneas de paso (stop lines)
        RoadRenderer._draw_stop_lines(screen, center_x, center_y)
    
    @staticmethod
    def _draw_center_lines(screen: pygame.Surface, center_x: int, center_y: int):
        """Dibuja las líneas divisorias del centro"""
        dash_length = 30
        gap_length = 20
        
        # Línea horizontal
        x = 0
        while x < SCREEN_WIDTH:
            pygame.draw.rect(screen, LINE_COLOR,
                           (x, center_y - 2, dash_length, 4))
            x += dash_length + gap_length
        
        # Línea vertical
        y = 0
        while y < SCREEN_HEIGHT:
            pygame.draw.rect(screen, LINE_COLOR,
                           (center_x - 2, y, 4, dash_length))
            y += dash_length + gap_length
    
    @staticmethod
    def _draw_stop_lines(screen: pygame.Surface, center_x: int, center_y: int):
        """Dibuja las líneas de paso donde los vehículos deben detenerse"""
        stop_line_width = 12
        stop_line_gap = 16
        
        # Línea horizontal izquierda (para vehículos hacia la derecha)
        for i in range(10):
            pygame.draw.rect(screen, STOP_LINE_COLOR,
                           (center_x - STOP_LINE_DISTANCE , 
                            center_y - STREET_WIDTH // 2 + i * stop_line_gap, 
                            10, stop_line_width))
        
        # Línea horizontal derecha (para vehículos hacia la izquierda)
        for i in range(10):
            pygame.draw.rect(screen, STOP_LINE_COLOR,
                           (center_x + STOP_LINE_DISTANCE - 10, 
                            center_y - STREET_WIDTH // 2 + i * stop_line_gap, 
                            10, stop_line_width))
        
        # Línea vertical superior (para vehículos hacia abajo)
        for i in range(10):
            pygame.draw.rect(screen, STOP_LINE_COLOR,
                           (center_x - STREET_WIDTH // 2 + i * stop_line_gap, 
                            center_y - STOP_LINE_DISTANCE, 
                            stop_line_width, 10))
        
        # Línea vertical inferior (para vehículos hacia arriba)
        for i in range(10):
            pygame.draw.rect(screen, STOP_LINE_COLOR,
                           (center_x - STREET_WIDTH // 2 + i * stop_line_gap, 
                            center_y + STOP_LINE_DISTANCE - 10, 
                            stop_line_width, 10))


class UIRenderer:
    """Dibuja la interfaz de usuario"""
    
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw_hud(self, screen: pygame.Surface, game_state: dict):
        """Dibuja el HUD (puntos, vidas, nivel)"""
        # Panel superior
        panel_height = 80
        panel = pygame.Surface((SCREEN_WIDTH, panel_height))
        panel.fill((30, 30, 30))
        panel.set_alpha(200)
        screen.blit(panel, (0, 0))
        
        # Puntuación
        score_text = self.font_medium.render(f"Puntos: {game_state['score']}", 
                                            True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
        # Vidas
        lives_color = (255, 0, 0) if game_state['lives'] <= 2 else (255, 255, 0)
        lives_text = self.font_medium.render(f"Vidas: {game_state['lives']}", 
                                            True, lives_color)
        screen.blit(lives_text, (250, 20))
        
        # Nivel
        level_text = self.font_medium.render(f"Nivel: {game_state['level']}", 
                                            True, (255, 255, 0))
        screen.blit(level_text, (450, 20))
        
        # Estadísticas
        stats_text = self.font_small.render(
            f"Pasados: {game_state['vehicles_passed']} | "
            f"Colisiones: {game_state['collisions']} | "
            f"Infracciones: {game_state['violations']}", 
            True, (200, 200, 200))
        screen.blit(stats_text, (650, 30))
        
        # Power-ups activos
        self._draw_active_powerups(screen, game_state)
        
        # Instrucciones
        help_text = self.font_small.render(
            "Click en semáforos para cambiar luces | ESPACIO: Pausar | ESC: Salir",
            True, (150, 150, 150))
        screen.blit(help_text, (20, SCREEN_HEIGHT - 30))
    
    def _draw_active_powerups(self, screen: pygame.Surface, game_state: dict):
        """Dibuja indicadores de power-ups activos"""
        y_pos = 25
        
        if game_state.get('time_scale', 1.0) < 1.0:
            powerup_text = self.font_small.render("⏱ TIEMPO LENTO", True, (0, 255, 255))
            screen.blit(powerup_text, (SCREEN_WIDTH - 200, y_pos))
            y_pos += 25
        
        if game_state.get('score_multiplier', 1.0) > 1.0:
            mult_text = self.font_small.render(
                f"✨ PUNTOS x{game_state['score_multiplier']:.1f}", 
                True, (255, 215, 0))
            screen.blit(mult_text, (SCREEN_WIDTH - 200, y_pos))
    
    def draw_pause_screen(self, screen: pygame.Surface):
        """Dibuja la pantalla de pausa"""
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pause_overlay.fill((0, 0, 0))
        pause_overlay.set_alpha(100)
        screen.blit(pause_overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSA", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)
    
    def draw_game_over(self, screen: pygame.Surface, game_state: dict):
        """Dibuja la pantalla de Game Over"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Texto principal
        game_over_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, text_rect)
        
        # Puntuación final
        score_text = self.font_medium.render(
            f"Puntuación Final: {game_state['score']}", 
            True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        # Estadísticas
        stats_lines = [
            f"Nivel alcanzado: {game_state['level']}",
            f"Vehículos pasados: {game_state['vehicles_passed']}",
            f"Colisiones: {game_state['collisions']}",
            f"Infracciones: {game_state['violations']}"
        ]
        
        y_offset = SCREEN_HEIGHT // 2 + 60
        for line in stats_lines:
            text = self.font_small.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 35
        
        # Instrucciones
        restart_text = self.font_small.render(
            "Presiona R para reiniciar o ESC para salir", 
            True, (255, 255, 0))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(restart_text, restart_rect)
