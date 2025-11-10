# 🚦🚗 Traffic Control — Sistema de Gestión de Tráfico con Patrones de Diseño

Un proyecto desarrollado en **Python** utilizando **Pygame**, que implementa los patrones de diseño **Template Method**, **State** y **Chain of Responsibility** para una arquitectura flexible, escalable y fácil de mantener.

---

## 👨‍💻 Autor

* Juan Camilo Mosquera Palomino - 20241020120

* Andres Felipe Lopez Martinez - 20241020052

Proyecto educativo desarrollado para demostrar patrones de diseño en Python con Pygame.

**Tecnologías utilizadas:**
- Python 3.8+
- Pygame 2.5+
- PlantUML para diagramas

---

## 🎯 Objetivo del Proyecto

Este juego tiene como meta recrear un sistema de gestión de tráfico interactivo, donde el jugador debe coordinar semáforos para evitar colisiones y mantener un flujo vehicular eficiente. El proyecto demuestra la aplicación práctica de tres patrones de diseño orientados a objetos en un entorno interactivo usando Pygame.

El proyecto sirve como ejemplo educativo de cómo estructurar código de manera profesional, facilitando la extensibilidad y el mantenimiento mediante:
- **Template Method**: Para definir comportamientos de vehículos con variaciones específicas
- **State**: Para gestionar estados de semáforos con transiciones claras
- **Chain of Responsibility**: Para procesar eventos del juego de manera desacoplada

---

## 🎮 Características del Juego

- ✨ **Interfaz gráfica completa** con sistema de calles e intersección
- 🚗 **5 tipos de vehículos diferentes**: Auto normal, Auto rápido, Autobús, Camión y Vehículo de emergencia
- 🖼️ **Imágenes PNG personalizadas** para cada tipo de vehículo
- 🚦 **Sistema de semáforos inteligente** con estados (verde, amarillo, rojo)
- 🎮 **Control manual de semáforos** mediante clicks del mouse
- 📊 **Sistema de puntuación complejo** con bonificaciones y penalizaciones
- 💥 **Detección de colisiones** en la intersección
- 🚨 **Vehículos de emergencia con prioridad** que pueden saltarse semáforos
- 🎯 **Sistema de niveles progresivo** con dificultad creciente
- 🔔 **Notificaciones visuales** de eventos (colisiones, bonificaciones, infracciones)
- ⏸️ **Sistema de pausa** y reinicio
- 📈 **Estadísticas en tiempo real**: vehículos pasados, colisiones, infracciones
- 🎨 **Efectos visuales**: sirenas parpadeantes, indicadores de prioridad, feedback de color

---

## 🚀 Cómo Ejecutar

### Requisitos Previos

- Python 3.8 o superior
- Pygame 2.5 o superior

### Instalación

1. **Clona el repositorio:**
```bash
git clone https://github.com/NovaChronoBlade/Traffic_Control.git
cd Traffic_Control
```

2. **Crea un entorno virtual (recomendado):**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecuta el juego:**
```bash
python main.py
```

### Controles del Juego

- **Click izquierdo en semáforo**: Cambia el estado del semáforo (rojo → verde → amarillo → rojo)
- **ESPACIO**: Pausar/Reanudar el juego
- **ESC**: Salir del juego
- **F11**: Alternar pantalla completa
- **R** (en Game Over): Reiniciar el juego

---

## 🧩 Patrones de Diseño Implementados

### 🏗️ 1. Template Method (Método Plantilla)

**Propósito:**  
Define el esqueleto de un algoritmo en una operación, delegando algunos pasos a las subclases. Permite que las subclases redefinan ciertos pasos de un algoritmo sin cambiar su estructura.

**Aplicación en el juego:**  
El patrón se utiliza para definir el comportamiento base de todos los vehículos, permitiendo que cada tipo de vehículo (Auto, Autobús, Camión, etc.) personalice aspectos específicos como velocidad, tamaño, aceleración y comportamientos especiales, sin modificar el flujo general de actualización y movimiento.

#### 📋 Estructura del Patrón

**Clase Abstracta - Vehicle** (`src/vehicles.py`):
```python
class Vehicle(ABC):
    """
    Clase abstracta que implementa el patrón Template Method.
    Define el esqueleto del algoritmo de movimiento y comportamiento de vehículos.
    """
    
    def __init__(self, x: float, y: float, direction: str, lane: int):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = self.get_base_speed()
        self.max_speed = self.get_max_speed()
        self.acceleration = self.get_acceleration()
        self.size = self.get_size()
        self.color = self.get_color()
        # ...
    
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
        else:
            self.decelerate(dt)
        
        # 3. Mover el vehículo
        self.move(dt)
        
        # 4. Aplicar comportamiento post-movimiento
        self.post_move_behavior()
    
    # Métodos abstractos que DEBEN ser implementados
    @abstractmethod
    def get_base_speed(self) -> float:
        pass
    
    @abstractmethod
    def get_max_speed(self) -> float:
        pass
    
    # Hooks opcionales que PUEDEN ser sobrescritos
    def special_behavior(self, dt: float) -> None:
        pass
```

#### 🎯 Vehículos Concretos Implementados

**1. Car** - Vehículo estándar con velocidad media
```python
class Car(Vehicle):
    def get_base_speed(self) -> float:
        return 100
    
    def get_max_speed(self) -> float:
        return 150
    
    def get_size(self) -> Tuple[int, int]:
        return (50, 30)
```

**2. FastCar** - Vehículo rápido con comportamiento especial
```python
class FastCar(Vehicle):
    def get_max_speed(self) -> float:
        return 250
    
    def special_behavior(self, dt: float) -> None:
        """Los autos rápidos zigzaguean ligeramente"""
        if not self.stopped and random.random() < 0.01:
            if self.direction in ['left', 'right']:
                self.y += random.randint(-2, 2)
```

**3. Bus** - Autobús lento que hace paradas
```python
class Bus(Vehicle):
    def get_max_speed(self) -> float:
        return 100
    
    def special_behavior(self, dt: float) -> None:
        """Los autobuses se detienen ocasionalmente (paradas)"""
        if not self.stopped and random.random() < 0.002:
            self.speed = 0
```

**4. EmergencyVehicle** - Vehículo de emergencia con prioridad
```python
class EmergencyVehicle(Vehicle):
    def check_priority(self) -> bool:
        """Vehículos de emergencia siempre tienen prioridad"""
        return True
    
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja con efecto de luz de emergencia parpadeante"""
        super().draw(screen)
        # Efecto de sirena...
```

**5. Truck** - Camión muy grande y lento
```python
class Truck(Vehicle):
    def get_max_speed(self) -> float:
        return 80
    
    def decelerate(self, dt: float) -> None:
        """Los camiones frenan más lentamente"""
        if self.speed > 0:
            self.speed = max(self.speed - self.acceleration * 1.5 * dt, 0)
```

#### 📍 Factory Pattern Adicional

```python
class VehicleFactory:
    """Factory para crear diferentes tipos de vehículos"""
    
    @staticmethod
    def create_random_vehicle(x: float, y: float, 
                            direction: str, lane: int) -> Vehicle:
        """Crea un vehículo aleatorio con probabilidades ponderadas"""
        rand = random.random()
        
        if rand < 0.5:      # 50% auto normal
            return Car(x, y, direction, lane)
        elif rand < 0.7:    # 20% auto rápido
            return FastCar(x, y, direction, lane)
        elif rand < 0.85:   # 15% autobús
            return Bus(x, y, direction, lane)
        elif rand < 0.95:   # 10% camión
            return Truck(x, y, direction, lane)
        else:               # 5% emergencia
            return EmergencyVehicle(x, y, direction, lane)
```

#### 🎓 Beneficios del Template Method

| Beneficio | Descripción |
|-----------|-------------|
| **Reutilización de código** | El algoritmo común está en un solo lugar (clase base) |
| **Extensibilidad** | Fácil agregar nuevos tipos de vehículos sin modificar el flujo base |
| **Mantenibilidad** | Cambios en el algoritmo base se propagan automáticamente |
| **Flexibilidad** | Cada subclase personaliza solo lo que necesita |
| **Polimorfismo** | Todos los vehículos pueden ser tratados uniformemente |
| **Hooks opcionales** | `special_behavior()` y `post_move_behavior()` permiten extensiones opcionales |

#### 📊 Diagrama UML - Template Method Pattern

**Ver diagrama completo:** [template_method_pattern.puml](template_method_pattern.puml)

El diagrama muestra:
- La clase abstracta `Vehicle` con el Template Method `update()`
- Los 5 tipos de vehículos concretos (Car, FastCar, Bus, EmergencyVehicle, Truck)
- El patrón Factory para creación de vehículos
- Las operaciones primitivas (abstractas) y los hooks (opcionales)
- Las relaciones de herencia y dependencias

---

### 🔄 2. State (Estado)

**Propósito:**  
Permite que un objeto altere su comportamiento cuando su estado interno cambia. El objeto parecerá cambiar de clase.

**Aplicación en el juego:**  
El patrón State se utiliza para gestionar los semáforos, donde cada estado (Verde, Amarillo, Rojo) tiene su propio comportamiento y reglas de transición. Esto permite que el semáforo cambie dinámicamente su comportamiento según su estado actual sin usar condicionales complejos.

#### 📋 Estructura del Patrón

**Clase Abstracta - TrafficLightState** (`src/traffic_light.py`):
```python
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
    def next_state(self) -> 'TrafficLightState':
        """Retorna el siguiente estado en la secuencia"""
        pass
    
    def update(self, dt: float) -> None:
        """Actualiza el tiempo en el estado y transiciona si es necesario"""
        self.time_in_state += dt
        
        if self.time_in_state >= self.get_duration():
            self.traffic_light.change_state(self.next_state())
```

#### 🎯 Estados Concretos

**1. GreenState** - Los vehículos pueden pasar
```python
class GreenState(TrafficLightState):
    def get_color(self) -> Tuple[int, int, int]:
        return (0, 255, 0)  # Verde
    
    def can_pass(self) -> bool:
        return True
    
    def next_state(self) -> TrafficLightState:
        return YellowState(self.traffic_light)
    
    def get_name(self) -> str:
        return "GREEN"
```

**2. YellowState** - Advertencia de cambio
```python
class YellowState(TrafficLightState):
    def get_color(self) -> Tuple[int, int, int]:
        return (255, 255, 0)  # Amarillo
    
    def can_pass(self) -> bool:
        return False  # Los vehículos deben prepararse para detenerse
    
    def next_state(self) -> TrafficLightState:
        return RedState(self.traffic_light)
```

**3. RedState** - Los vehículos deben detenerse
```python
class RedState(TrafficLightState):
    def get_color(self) -> Tuple[int, int, int]:
        return (255, 0, 0)  # Rojo
    
    def can_pass(self) -> bool:
        return False
    
    def next_state(self) -> TrafficLightState:
        return GreenState(self.traffic_light)
```

#### 🎮 Contexto - TrafficLight

```python
class TrafficLight:
    """
    Contexto que mantiene el estado actual del semáforo.
    Delega el comportamiento al estado actual.
    """
    
    def __init__(self, x: int, y: int, direction: str, 
                 green_duration: float = 5.0,
                 yellow_duration: float = 2.0,
                 red_duration: float = 5.0):
        self.x = x
        self.y = y
        self.direction = direction
        
        # Estado inicial
        self._state = RedState(self)
        self._state.on_enter()
        
        self.manual_override = False
    
    def change_state(self, new_state: TrafficLightState) -> None:
        """Cambia el estado del semáforo"""
        self._state.on_exit()
        self._state = new_state
        self._state.on_enter()
    
    def can_pass(self) -> bool:
        """Delega al estado actual"""
        return self._state.can_pass()
    
    def cycle_state(self) -> None:
        """Cicla manualmente al siguiente estado (para control del jugador)"""
        if self.manual_override:
            self.change_state(self._state.next_state())
```

#### 🎛️ Controlador Coordinado

```python
class TrafficLightController:
    """
    Controlador que gestiona múltiples semáforos coordinados.
    Asegura que semáforos perpendiculares no estén verdes simultáneamente.
    """
    
    def coordinate_lights(self) -> None:
        """
        Coordina semáforos para evitar colisiones.
        Si horizontales están verdes, verticales deben estar rojos.
        """
        for h_light in self.horizontal_lights:
            if h_light.can_pass():
                for v_light in self.vertical_lights:
                    if v_light.can_pass():
                        v_light.change_state(RedState(v_light))
```

#### 📍 Uso en el Juego

**En `main.py` líneas 71-102:**
```python
def setup_intersection(self):
    """Configura la intersección con semáforos"""
    # Semáforos horizontales (este-oeste)
    light_h1 = TrafficLight(center_x - 200, center_y - 100, 'horizontal')
    light_h2 = TrafficLight(center_x + 200, center_y + 100, 'horizontal')
    
    # Semáforos verticales (norte-sur)
    light_v1 = TrafficLight(center_x - 100, center_y - 200, 'vertical')
    light_v2 = TrafficLight(center_x + 100, center_y + 200, 'vertical')
```

**Control del jugador en `main.py` líneas 283-285:**
```python
light = self.traffic_controller.get_light_at_position(x, y)
if light:
    light.cycle_state()  # Cambia al siguiente estado
```

#### 🎓 Beneficios del State Pattern

| Beneficio | Descripción |
|-----------|-------------|
| **Elimina condicionales** | No hay if/else complejos para cada estado |
| **Encapsulación** | Cada estado encapsula su comportamiento |
| **Fácil extensión** | Agregar nuevos estados (ej: parpadeante) es trivial |
| **Transiciones claras** | Las transiciones están bien definidas |
| **Mantenibilidad** | Cambios en un estado no afectan a otros |
| **Single Responsibility** | Cada clase de estado tiene una única responsabilidad |

#### 📊 Diagrama UML - State Pattern

**Ver diagrama completo:** [state_pattern.puml](state_pattern.puml)

El diagrama muestra:
- La clase abstracta `TrafficLightState` con la interfaz de estados
- Los 3 estados concretos (GreenState, YellowState, RedState)
- La clase contexto `TrafficLight` que mantiene el estado actual
- El controlador `TrafficLightController` que coordina múltiples semáforos
- Las transiciones entre estados (Verde → Amarillo → Rojo → Verde)
- Las capacidades de control manual del jugador

---

### 🔗 3. Chain of Responsibility (Cadena de Responsabilidad)

**Propósito:**  
Evita acoplar el emisor de una petición a su receptor, dando a más de un objeto la posibilidad de responder a la petición. Encadena los objetos receptores y pasa la petición a lo largo de la cadena hasta que un objeto la maneja.

**Aplicación en el juego:**  
El patrón se utiliza para procesar eventos del juego (colisiones, infracciones, puntuaciones, congestión, power-ups). Cada manejador en la cadena decide si puede procesar el evento y, si no, lo pasa al siguiente. Esto permite agregar, remover o reordenar manejadores sin afectar el resto del sistema.

#### 📋 Estructura del Patrón

**Clase Base - EventHandler** (`src/event_system.py`):
```python
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
```

**Evento del Juego:**
```python
class GameEvent:
    """Representa un evento del juego que puede ser procesado"""
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.handled = False
        self.response = {}
```

#### 🎯 Manejadores Implementados

**1. CollisionHandler** - Maneja colisiones entre vehículos
```python
class CollisionHandler(EventHandler):
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "collision"
    
    def process(self, event: GameEvent) -> None:
        vehicle1 = event.data.get('vehicle1')
        vehicle2 = event.data.get('vehicle2')
        
        # Penalización mayor si involucra vehículo de emergencia
        penalty = PENALTY_COLLISION_EMERGENCY if (
            vehicle1.has_priority or vehicle2.has_priority
        ) else PENALTY_COLLISION
        
        self.game_state['score'] = max(0, self.game_state['score'] - penalty)
        self.game_state['lives'] -= 1
        self.game_state['collisions'] += 1
        
        event.data['remove_vehicles'] = [vehicle1, vehicle2]
        event.response = {
            'penalty': penalty,
            'message': f"¡Colisión! -{penalty} puntos",
            'severity': 'high'
        }
```

**2. TrafficViolationHandler** - Maneja infracciones de tráfico
```python
class TrafficViolationHandler(EventHandler):
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "traffic_violation"
    
    def process(self, event: GameEvent) -> None:
        violation_type = event.data.get('type')
        
        penalties = {
            'red_light': 50,
            'speeding': 30,
            'emergency_obstruction': 200
        }
        
        penalty = penalties.get(violation_type, 25)
        self.game_state['score'] = max(0, self.game_state['score'] - penalty)
```

**3. ScoreHandler** - Maneja eventos de puntuación positiva
```python
class ScoreHandler(EventHandler):
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type in ["vehicle_passed", "smooth_flow", "perfect_timing"]
    
    def process(self, event: GameEvent) -> None:
        if event.event_type == "vehicle_passed":
            vehicle = event.data.get('vehicle')
            
            # Bonus por vehículos especiales
            if vehicle.has_priority:
                points = 30  # Vehículo de emergencia
            elif vehicle.__class__.__name__ == 'Bus':
                points = 20  # Autobús
            else:
                points = 10  # Auto normal
            
            self.game_state['score'] += points
            self.game_state['vehicles_passed'] += 1
```

**4. PowerUpHandler** - Maneja power-ups especiales
```python
class PowerUpHandler(EventHandler):
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "power_up"
    
    def process(self, event: GameEvent) -> None:
        power_up_type = event.data.get('type')
        
        if power_up_type == "slow_time":
            self.game_state['time_scale'] = 0.5
            self.game_state['power_up_duration'] = 5.0
        elif power_up_type == "score_multiplier":
            self.game_state['score_multiplier'] = 2.0
```

**5. CongestionHandler** - Maneja congestión de tráfico
```python
class CongestionHandler(EventHandler):
    def can_handle(self, event: GameEvent) -> bool:
        return event.event_type == "congestion"
    
    def process(self, event: GameEvent) -> None:
        congestion_level = event.data.get('level', 'medium')
        
        penalties = {
            'low': 5,
            'medium': 15,
            'high': 30,
            'critical': 50
        }
        
        penalty = penalties.get(congestion_level, 10)
        self.game_state['score'] = max(0, self.game_state['score'] - penalty)
```

**6. LoggingHandler** - Manejador final que registra todos los eventos
```python
class LoggingHandler(EventHandler):
    def can_handle(self, event: GameEvent) -> bool:
        return True  # Maneja todos los eventos
    
    def process(self, event: GameEvent) -> None:
        self.event_log.append({
            'type': event.event_type,
            'data': event.data,
            'response': event.response,
            'timestamp': pygame.time.get_ticks()
        })
        
        event.handled = True  # Marca como completamente manejado
```

#### 🔧 Sistema de Eventos

```python
class EventSystem:
    """
    Sistema que gestiona la cadena de responsabilidad.
    Facilita la creación y manejo de eventos.
    """
    
    def __init__(self, game_state: Dict[str, Any]):
        # Crear manejadores
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
        
        self.first_handler = self.collision_handler
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> GameEvent:
        """Emite un evento y lo procesa a través de la cadena"""
        event = GameEvent(event_type, data)
        processed_event = self.first_handler.handle(event)
        
        # Agregar notificación visual si hay mensaje
        if processed_event.response.get('message'):
            self.notifications.append({
                'message': processed_event.response['message'],
                'severity': processed_event.response.get('severity', 'info'),
                'time': pygame.time.get_ticks(),
                'duration': 2000
            })
        
        return processed_event
```

#### 📍 Uso en el Juego

**Detección de colisiones en `main.py` líneas 126-141:**
```python
def check_collisions(self):
    """Detecta colisiones entre vehículos"""
    for i, v1 in enumerate(self.vehicles):
        for v2 in self.vehicles[i+1:]:
            if CollisionDetector.check_collision(v1, v2):
                # Emitir evento de colisión (Chain of Responsibility)
                event = self.event_system.emit_event('collision', {
                    'vehicle1': v1,
                    'vehicle2': v2
                })
                
                # Procesar respuesta
                if 'remove_vehicles' in event.data:
                    for v in event.data['remove_vehicles']:
                        if v in self.vehicles:
                            self.vehicles.remove(v)
```

**Vehículo que pasa exitosamente en `main.py` líneas 210-213:**
```python
if vehicle.is_off_screen(SCREEN_WIDTH, SCREEN_HEIGHT):
    self.vehicles.remove(vehicle)
    
    self.event_system.emit_event('vehicle_passed', {
        'vehicle': vehicle
    })
```

#### 🎓 Beneficios de Chain of Responsibility

| Beneficio | Descripción |
|-----------|-------------|
| **Desacoplamiento** | El emisor no necesita conocer quién manejará el evento |
| **Flexibilidad** | Fácil agregar, remover o reordenar manejadores |
| **Single Responsibility** | Cada manejador tiene una única responsabilidad |
| **Extensibilidad** | Nuevos tipos de eventos se agregan sin modificar código existente |
| **Registro centralizado** | LoggingHandler captura todos los eventos al final |
| **Notificaciones automáticas** | EventSystem genera notificaciones visuales automáticamente |

#### 📊 Diagrama UML - Chain of Responsibility Pattern

**Ver diagrama completo:** [chain_of_responsibility_pattern.puml](chain_of_responsibility_pattern.puml)

El diagrama muestra:
- La clase base `EventHandler` con el patrón template para procesar eventos
- Los 6 manejadores concretos en la cadena (Collision, Violation, Score, PowerUp, Congestion, Logging)
- La clase `GameEvent` que encapsula los datos del evento
- El `EventSystem` que construye y gestiona la cadena
- La clase `Game` como cliente que emite eventos
- El flujo de procesamiento a través de la cadena de responsabilidad

---

## 📊 Arquitectura del Proyecto

```
Traffic_Control/
├── main.py                 # Punto de entrada, clase Game principal
├── requirements.txt        # Dependencias del proyecto
├── assets/                 # Recursos multimedia
│   ├── vehicles/          # Imágenes PNG de vehículos
│   │   ├── car.png
│   │   ├── fast_car.png
│   │   ├── bus.png
│   │   ├── truck.png
│   │   └── emergency.png
│   └── sounds/            # Efectos de sonido (futuro)
└── src/                   # Código fuente
    ├── __init__.py
    ├── config.py          # Constantes y configuración
    ├── vehicles.py        # Template Method: Jerarquía de vehículos
    ├── traffic_light.py   # State: Estados de semáforos
    ├── event_system.py    # Chain of Responsibility: Sistema de eventos
    ├── collision_utils.py # Utilidades de detección de colisiones
    └── renderer.py        # Renderizado de UI y elementos visuales
```

---

## 🎮 Mecánicas del Juego

### Sistema de Puntuación

**Puntos Positivos:**
- Vehículo normal pasa: **+10 puntos**
- Autobús pasa: **+20 puntos**
- Vehículo de emergencia pasa: **+30 puntos**
- Flujo perfecto: **+50 puntos**
- Timing perfecto: **+25 puntos**

**Penalizaciones:**
- Colisión normal: **-100 puntos** y **-1 vida**
- Colisión con emergencia: **-300 puntos** y **-1 vida**
- Infracción de tráfico: **-50 puntos**
- Congestión baja: **-5 puntos**
- Congestión media: **-15 puntos**
- Congestión alta: **-30 puntos**
- Congestión crítica: **-50 puntos**

### Sistema de Vidas

- Comienzas con **5 vidas**
- Pierdes una vida por cada colisión
- Game Over cuando las vidas llegan a 0

### Sistema de Niveles

- Subes de nivel cada **20 vehículos** que pasan exitosamente
- La dificultad aumenta con cada nivel:
  - Menor intervalo entre spawns de vehículos
  - Más vehículos en pantalla simultáneamente

### Tipos de Vehículos

| Vehículo | Velocidad | Tamaño | Probabilidad | Características |
|----------|-----------|--------|--------------|-----------------|
| **Auto Normal** | Media (150) | Pequeño | 50% | Vehículo estándar |
| **Auto Rápido** | Alta (250) | Pequeño | 20% | Zigzaguea ligeramente |
| **Autobús** | Baja (100) | Grande | 15% | Hace paradas ocasionales |
| **Camión** | Muy Baja (80) | Muy Grande | 10% | Frena lentamente |
| **Emergencia** | Alta (200) | Mediano | 5% | Prioridad, puede saltarse semáforos |

---

## 🔍 Características Técnicas Avanzadas

### Detección de Colisiones

El sistema utiliza tres verificadores especializados:

1. **CollisionDetector**: Detecta colisiones en la intersección
   - Verifica si ambos vehículos están en la zona de intersección
   - Confirma que van en direcciones diferentes
   - Usa rectángulos de colisión para detección precisa

2. **VehicleSpacingChecker**: Mantiene distancia segura entre vehículos
   - Encuentra el vehículo más cercano adelante
   - Calcula distancia según tamaño de vehículos
   - Previene amontonamientos en carriles

3. **TrafficLightChecker**: Verifica respeto a semáforos
   - Calcula posición de parada precisa según tamaño del vehículo
   - Maneja vehículos de emergencia con prioridad
   - Coordina con sistema de cambio de carril

### Sistema de Notificaciones

- Notificaciones visuales en tiempo real
- Colores según severidad:
  - 🟢 Verde: Eventos positivos
  - 🟡 Amarillo: Advertencias leves
  - 🟠 Naranja: Advertencias medias
  - 🔴 Rojo: Eventos críticos
- Efecto de fade out automático después de 2 segundos

### Renderizado Eficiente

- **RoadRenderer**: Dibuja calles, líneas y zona de intersección
- **UIRenderer**: Gestiona HUD, pantallas de pausa y game over
- Uso de superficies con alpha para efectos de transparencia
- Imágenes rotadas según dirección del vehículo

---

## 🚀 Posibles Extensiones

El diseño con patrones facilita agregar nuevas características:

### Nuevos Vehículos (Template Method)
- Motocicletas (más rápidas, más ágiles)
- Vehículos de carga pesada
- Transporte público especializado

### Nuevos Estados de Semáforo (State)
- Estado parpadeante (para mantenimiento)
- Estado de flecha verde (giro permitido)
- Estado de cuenta regresiva

### Nuevos Eventos (Chain of Responsibility)
- Sistema de achievements
- Power-ups visuales en el mapa
- Eventos climáticos (lluvia ralentiza tráfico)
- Sistema de multas y recompensas

### Otras Mejoras
- Múltiples intersecciones
- Mapa más grande con scroll
- Modo multijugador
- Guardado de puntuaciones altas
- Efectos de sonido
- Música de fondo
- Tutorial interactivo

---

## 📚 Conceptos de Programación Aplicados

- **Programación Orientada a Objetos (OOP)**
- **Clases Abstractas y Métodos Abstractos**
- **Herencia y Polimorfismo**
- **Encapsulación**
- **Composición sobre Herencia**
- **SOLID Principles**:
  - Single Responsibility Principle
  - Open/Closed Principle
  - Liskov Substitution Principle
  - Interface Segregation Principle
  - Dependency Inversion Principle
- **Type Hints** para mejor documentación
- **Documentación con docstrings**

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible para fines educativos.

---

## 🎯 Aprendizajes Clave

1. **Template Method** es ideal para definir algoritmos con pasos variables
2. **State** elimina condicionales complejos y hace el código más mantenible
3. **Chain of Responsibility** desacopla emisores y receptores de eventos
4. Los patrones de diseño no son sobrecarga, son inversión en mantenibilidad
5. Pygame permite crear juegos educativos visualmente atractivos
6. La documentación clara es tan importante como el código

---

## 📞 Contacto

NovaChronoBlade - [GitHub](https://github.com/NovaChronoBlade)

Link del Proyecto: [https://github.com/NovaChronoBlade/Traffic_Control](https://github.com/NovaChronoBlade/Traffic_Control)

---

**¡Gracias por explorar este proyecto educativo!** 🚦🚗

Si te resultó útil, considera darle una ⭐ al repositorio.
