# 🏗️ Documentación de Arquitectura

Guía de arquitectura completa para el Sistema Distribuido de Gestión de Inventario.

[🇺🇸 English](ARCHITECTURE.md) | [🇧🇷 Português](ARCHITECTURE.pt-BR.md) | [🇪🇸 Español](ARCHITECTURE.es.md)

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Principios de Arquitectura](#principios-de-arquitectura)
3. [Capas de Arquitectura](#capas-de-arquitectura)
4. [Patrones de Diseño](#patrones-de-diseño)
5. [Flujos de Datos](#flujos-de-datos)
6. [Consideraciones de Escalabilidad](#consideraciones-de-escalabilidad)

## Descripción General

El sistema implementa una arquitectura moderna de microservicios utilizando:

- **Clean Architecture** - Separación de responsabilidades en 4 capas
- **Event Sourcing** - Persistencia basada en eventos como fuente de verdad
- **CQRS (Command Query Responsibility Segregation)** - Modelos de lectura y escritura separados
- **DDD (Domain-Driven Design)** - Modelado rico del dominio con agregados y eventos

### Vista de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE PRESENTACIÓN                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   REST API   │  │  Middleware  │  │   Schemas    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   CAPA DE APLICACIÓN                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Comandos   │  │   Consultas  │  │  Servicios   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────┬──────────────────────────────────┬─────────────────┘
         │                                  │
┌────────▼───────────────┐   ┌────────────▼──────────────────┐
│   LADO DE ESCRITURA    │   │      LADO DE LECTURA          │
│  ┌──────────────────┐  │   │  ┌──────────────────────┐    │
│  │  Event Store     │  │   │  │   Read Models        │    │
│  └──────────────────┘  │   │  └──────────────────────┘    │
└────────┬───────────────┘   └──────────────▲────────────────┘
         │                                   │
         │          ┌──────────────┐         │
         └──────────►   Event Bus  ├─────────┘
                    └──────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      CAPA DE DOMINIO                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Entidades   │  │    Eventos   │  │ Objetos Valor│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Principios de Arquitectura

### 1. Clean Architecture (Arquitectura Limpia)

#### Regla de Dependencia
Las dependencias apuntan hacia el interior. Las capas externas dependen de las capas internas, nunca al revés.

```
Presentación → Aplicación → Dominio
Infrastructure → Aplicación/Dominio
```

#### Beneficios
- ✅ Independencia de frameworks
- ✅ Testabilidad
- ✅ Independencia de UI
- ✅ Independencia de base de datos
- ✅ Reglas de negocio agnósticas a factores externos

### 2. SOLID Principles (Principios SOLID)

- **S - Single Responsibility**: Cada clase tiene una única razón para cambiar
- **O - Open/Closed**: Abierto para extensión, cerrado para modificación
- **L - Liskov Substitution**: Los subtipos deben ser sustituibles por sus tipos base
- **I - Interface Segregation**: Muchas interfaces específicas del cliente
- **D - Dependency Inversion**: Depender de abstracciones, no de concreciones

### 3. Domain-Driven Design (Diseño Guiado por el Dominio)

- **Agregados**: Inventory como raíz de agregado
- **Entidades**: Product, Inventory con identidad
- **Objetos de Valor**: StockQuantity como inmutable
- **Eventos de Dominio**: Capturan cambios de estado
- **Repositorios**: Acceso a datos basado en colecciones

## Capas de Arquitectura

### Capa 1: Dominio (Núcleo)

**Ubicación**: `src/domain/`

**Responsabilidades**:
- Lógica de negocio y reglas
- Entidades y objetos de valor
- Eventos de dominio
- Excepciones de dominio

**Componentes Clave**:

#### Entidades
```python
# src/domain/entities/inventory.py
@dataclass
class Inventory:
    """Agregado raíz para inventario"""
    product_id: UUID
    store_id: UUID
    total_quantity: StockQuantity
    reserved_quantity: StockQuantity
    version: int = 0
    pending_events: List[DomainEvent] = field(default_factory=list)
    
    def add_stock(self, quantity: StockQuantity, reason: str) -> None:
        """Agregar stock con validación"""
        self.total_quantity = self.total_quantity.add(quantity)
        event = StockAdded(...)
        self.pending_events.append(event)
        self.version += 1
    
    def reserve_stock(self, quantity: StockQuantity, 
                      customer_id: UUID) -> UUID:
        """Reservar stock si está disponible"""
        available = self.get_available_quantity()
        if available < quantity:
            raise InsufficientStockError(...)
        # ... lógica
```

#### Objetos de Valor
```python
# src/domain/value_objects/stock_quantity.py
@dataclass(frozen=True)
class StockQuantity:
    """Cantidad de stock inmutable con validación"""
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise InvalidQuantityError(...)
    
    def add(self, other: 'StockQuantity') -> 'StockQuantity':
        return StockQuantity(self.value + other.value)
```

#### Eventos de Dominio
```python
# src/domain/events/inventory_events.py
@dataclass
class StockAdded(DomainEvent):
    """Evento cuando se agrega stock"""
    product_id: UUID
    store_id: UUID
    quantity: int
    reason: str
    timestamp: datetime
```

**Principios**:
- Sin dependencias externas
- Lógica de negocio pura
- Inmutabilidad donde sea posible
- Validación rica

### Capa 2: Aplicación

**Ubicación**: `src/application/`

**Responsabilidades**:
- Orquestación de casos de uso
- Handlers de comandos
- Handlers de consultas
- Coordinación de transacciones

**Componentes Clave**:

#### Comandos (Lado de Escritura)
```python
# src/application/commands/add_stock.py
@dataclass
class AddStockCommand:
    """Comando para agregar stock"""
    product_id: UUID
    store_id: UUID
    quantity: int
    reason: str

class AddStockHandler:
    """Handler con reconstrucción de Event Sourcing"""
    
    async def handle(self, command: AddStockCommand) -> None:
        # 1. Cargar eventos del event store
        events = await self.event_store.load_events(
            command.product_id, command.store_id
        )
        
        # 2. Reconstruir agregado desde eventos
        inventory = self._rebuild_from_events(events)
        
        # 3. Ejecutar comando
        inventory.add_stock(
            StockQuantity(command.quantity),
            command.reason
        )
        
        # 4. Guardar nuevos eventos
        await self.event_store.append_events(
            command.product_id,
            command.store_id,
            inventory.pending_events,
            inventory.version - len(inventory.pending_events)
        )
        
        # 5. Publicar eventos
        for event in inventory.pending_events:
            await self.event_bus.publish(event)
```

#### Consultas (Lado de Lectura)
```python
# src/application/queries/get_stock.py
class GetStockQuery:
    """Consulta con caché"""
    
    async def execute(self, product_id: UUID, 
                      store_id: UUID) -> StockResponse:
        # 1. Intentar caché primero
        cache_key = f"stock:{product_id}:{store_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return StockResponse(**cached)
        
        # 2. Consultar modelo de lectura
        stock = await self.read_model.get_stock(
            product_id, store_id
        )
        
        # 3. Almacenar en caché por 30s
        if stock:
            await self.cache.set(
                cache_key, stock.dict(), ttl=30
            )
        
        return stock
```

**Principios**:
- Separación de comandos y consultas (CQRS)
- Sin lógica de negocio (solo orquestación)
- Manejo de transacciones
- Gestión de caché

### Capa 3: Infraestructura

**Ubicación**: `src/infrastructure/`

**Responsabilidades**:
- Persistencia de datos
- Mensajería externa
- Caché
- Resiliencia

**Componentes Clave**:

#### Event Store
```python
# src/infrastructure/persistence/event_store.py
class EventStore:
    """Store de eventos con bloqueo optimista"""
    
    async def append_events(
        self,
        product_id: UUID,
        store_id: UUID,
        events: List[DomainEvent],
        expected_version: int
    ) -> None:
        """Agregar eventos con verificación de versión"""
        
        # 1. Adquirir bloqueo para este agregado
        async with self.locks[aggregate_key]:
            # 2. Cargar versión actual
            current_version = await self._get_current_version(...)
            
            # 3. Verificar conflicto de versión
            if current_version != expected_version:
                raise ConcurrencyError(...)
            
            # 4. Agregar eventos
            await self._append_to_file(...)
```

#### Read Model Repository
```python
# src/infrastructure/persistence/read_model_repository.py
class ReadModelRepository:
    """Proyecciones optimizadas para consultas"""
    
    def update_from_event(self, event: DomainEvent) -> None:
        """Actualizar proyección desde evento"""
        
        if isinstance(event, StockAdded):
            # Actualizar modelo de lectura desnormalizado
            stock = self._get_or_create_stock(...)
            stock.total_quantity += event.quantity
            stock.last_updated = event.timestamp
            self._save(stock)
```

#### Cache
```python
# src/infrastructure/cache/in_memory_cache.py
class InMemoryCache:
    """Cache en memoria con TTL y evicción LRU"""
    
    async def get(self, key: str) -> Optional[Dict]:
        """Obtener de caché con verificación de expiración"""
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired():
                entry.access_time = time.time()
                return entry.value
            del self.cache[key]
        return None
```

#### Circuit Breaker
```python
# src/infrastructure/resilience/circuit_breaker.py
class CircuitBreaker:
    """Circuit breaker con 3 estados"""
    
    async def call(self, func, *args, **kwargs):
        """Ejecutar con protección de circuit breaker"""
        
        if self.state == State.OPEN:
            if self._should_attempt_reset():
                self.state = State.HALF_OPEN
            else:
                raise CircuitBreakerOpenError()
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

**Principios**:
- Implementaciones intercambiables
- Preocupaciones técnicas
- No contiene lógica de negocio
- Dependencias aisladas

### Capa 4: Presentación

**Ubicación**: `src/presentation/`

**Responsabilidades**:
- HTTP API endpoints
- Validación de request/response
- Manejo de errores
- Middleware

**Componentes Clave**:

#### API Endpoints
```python
# src/presentation/api/v1/endpoints/inventory.py
@router.post("/stock", status_code=status.HTTP_201_CREATED)
async def add_stock(
    request: AddStockRequest,
    service: InventoryService = Depends(get_inventory_service)
) -> StockResponse:
    """Endpoint para agregar stock"""
    
    command = AddStockCommand(
        product_id=request.product_id,
        store_id=request.store_id,
        quantity=request.quantity,
        reason=request.reason
    )
    
    await service.add_stock(command)
    
    # Consultar stock actualizado
    query = GetStockQuery(
        product_id=request.product_id,
        store_id=request.store_id
    )
    return await service.get_stock(query)
```

#### Middleware
```python
# src/presentation/middleware/logging_middleware.py
class LoggingMiddleware:
    """Middleware de logging estructurado"""
    
    async def __call__(self, request: Request, 
                       call_next) -> Response:
        request_id = str(uuid4())
        
        logger.bind(request_id=request_id)
        logger.info("request_started", 
                   method=request.method, 
                   path=request.url.path)
        
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        logger.info("request_completed", 
                   status_code=response.status_code,
                   duration=duration)
        
        return response
```

**Principios**:
- Preocupaciones de transporte HTTP
- Conversión de DTOs
- Manejo de errores de usuario
- Documentación (OpenAPI)

## Patrones de Diseño

### 1. Event Sourcing

**Problema**: Necesidad de auditoría completa y reconstrucción de estado

**Solución**: Almacenar eventos como fuente de verdad

```python
# Flujo:
# 1. Usuario ejecuta comando → AddStockCommand
# 2. Cargar todos los eventos → [StockAdded, StockReserved, ...]
# 3. Reconstruir estado → inventory.apply(event) para cada evento
# 4. Ejecutar comando → inventory.add_stock()
# 5. Guardar nuevos eventos → StockAdded guardado
# 6. Estado futuro = eventos pasados + nuevos eventos
```

**Beneficios**:
- Historial completo
- Consultas temporales (time travel)
- Auditoría incorporada
- Depuración facilitada

### 2. CQRS (Command Query Responsibility Segregation)

**Problema**: Los requisitos de lectura y escritura son diferentes

**Solución**: Modelos separados para escrituras y lecturas

```
COMANDOS (Escrituras)          CONSULTAS (Lecturas)
       │                              │
       ▼                              ▼
  Event Store                   Read Models
  (Normalizado)                (Desnormalizado)
       │                              │
       └────────── Events ────────────┘
```

**Beneficios**:
- Modelos de lectura optimizados
- Escalado independiente
- Diferentes requisitos de consistencia
- Mejor rendimiento de caché

### 3. Repository Pattern

**Problema**: Abstracción del acceso a datos

**Solución**: Interfaz basada en colecciones para persistencia

```python
class IEventStore(ABC):
    @abstractmethod
    async def append_events(self, events: List[DomainEvent]): ...
    
    @abstractmethod
    async def load_events(self, aggregate_id: UUID): ...
```

### 4. Unit of Work

**Problema**: Gestionar límites de transacciones

**Solución**: Coordinar múltiples operaciones de repositorio

```python
# Implícito en handlers de comandos:
async def handle(self, command):
    # 1. Cargar
    inventory = await self.load_aggregate(...)
    
    # 2. Ejecutar
    inventory.do_something()
    
    # 3. Guardar (atómico)
    await self.save_aggregate(inventory)
```

### 5. Circuit Breaker

**Problema**: Fallos en cascada en sistemas distribuidos

**Solución**: Rastrear fallos y fallar rápido cuando sea necesario

**Estados**:
- **CLOSED** (Cerrado): Operación normal, rastreando fallos
- **OPEN** (Abierto): Fallo rápido sin intentar
- **HALF_OPEN** (Semi-abierto): Probar si el servicio se ha recuperado

### 6. Observer Pattern (Event Bus)

**Problema**: Comunicación débilmente acoplada entre componentes

**Solución**: Pub/sub para eventos de dominio

```python
# Publishers no saben sobre subscribers
await event_bus.publish(StockAdded(...))

# Subscribers se registran por tipo de evento
event_bus.subscribe(StockAdded, update_read_model)
event_bus.subscribe(StockAdded, invalidate_cache)
```

## Flujos de Datos

### Flujo de Comando (Escritura)

```
1. Cliente → HTTP POST /api/v1/inventory/stock
2. API Layer → Validar con Pydantic
3. API Layer → Crear AddStockCommand
4. Service Layer → Invocar AddStockHandler
5. Command Handler → Cargar eventos desde EventStore
6. Command Handler → Reconstruir Inventory desde eventos
7. Command Handler → inventory.add_stock() (lógica de negocio)
8. Command Handler → Guardar nuevos eventos en EventStore
9. Command Handler → Publicar eventos al EventBus
10. Event Handlers → Actualizar ReadModel, invalidar caché
11. API Layer → Retornar 201 Created
```

### Flujo de Consulta (Lectura)

```
1. Cliente → HTTP GET /api/v1/inventory/products/{id}/stores/{id}
2. API Layer → Validar parámetros
3. API Layer → Crear GetStockQuery
4. Service Layer → Invocar GetStockQueryHandler
5. Query Handler → Verificar cache primero
6. Query Handler → Si falló caché, consultar ReadModel
7. Query Handler → Guardar en caché por 30s
8. API Layer → Retornar 200 OK con datos
```

### Flujo de Evento

```
1. Evento publicado → EventBus.publish(StockAdded)
2. EventBus → Notificar a todos los subscribers
3. ReadModelUpdater → Actualizar proyección
4. CacheInvalidator → Invalidar entradas relevantes
5. (Futuro) ExternalPublisher → Enviar a Kafka
```

## Consideraciones de Escalabilidad

### Escalado Horizontal

**Lado de Escritura**:
```
Load Balancer
     │
     ├─→ API Instance 1 ─→ Event Store (Sharded by aggregate_id)
     ├─→ API Instance 2 ─→ Event Store (Sharded by aggregate_id)
     └─→ API Instance 3 ─→ Event Store (Sharded by aggregate_id)
```

**Lado de Lectura**:
```
Load Balancer
     │
     ├─→ Read API 1 ─→ Redis Cache ─→ Read Replicas
     ├─→ Read API 2 ─→ Redis Cache ─→ Read Replicas
     └─→ Read API 3 ─→ Redis Cache ─→ Read Replicas
```

### Estrategias de Caché

1. **Caché de nivel 1**: En memoria en cada instancia (actual)
2. **Caché de nivel 2**: Redis compartido entre instancias (futuro)
3. **Invalidación**: Basada en patrones o TTL
4. **Calentamiento**: Prellenado de elementos de alta demanda

### Particionamiento

- **Event Store**: Particionar por `(product_id, store_id)`
- **Read Models**: Desnormalizar y replicar según sea necesario
- **Caché**: Claves distribuidas en cluster Redis

### Límites de Escalabilidad

| Componente | Límite Actual | Escalado con |
|------------|---------------|--------------|
| Event Store | ~10K eventos/s | Sharding de DB |
| Read Models | ~50K req/s | Redis + Replicas |
| API Instances | ~1K req/s/instancia | Horizontal |
| Event Bus | En memoria | Kafka/RabbitMQ |

## Mejoras Futuras

### Arquitectura

- [ ] Rastreo distribuido (Jaeger/OpenTelemetry)
- [ ] Event Store basado en PostgreSQL
- [ ] Bus de eventos con Kafka
- [ ] Caché con Redis
- [ ] API Gateway (Kong/Nginx)
- [ ] Service Mesh (Istio)

### Patrones

- [ ] Saga Pattern para transacciones distribuidas
- [ ] CQRS con Event Sourcing completo
- [ ] Materialización de vistas bajo demanda
- [ ] Snapshot de agregados para rendimiento
- [ ] Outbox Pattern para garantías de entrega

### Observabilidad

- [ ] Exportación de métricas (Prometheus)
- [ ] Dashboards (Grafana)
- [ ] Alertas (AlertManager)
- [ ] Log aggregation (ELK Stack)

## Referencias

- **Clean Architecture**: Robert C. Martin
- **Domain-Driven Design**: Eric Evans
- **Event Sourcing**: Greg Young
- **Microservices Patterns**: Chris Richardson