# 🚀 Cómo Ejecutar el Sistema Localmente

## 📋 Visión General

Este documento explica cómo funciona el sistema de eventos localmente y cómo inicializar todo.

## 🏗️ Arquitectura del Sistema de Eventos

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE EVENTOS                          │
└─────────────────────────────────────────────────────────────┘

1. COMANDO (Write Side)
   ├─ Cliente envía POST /api/v1/inventory/stock
   ├─ API valida request
   ├─ AddStockCommand creado
   └─ AddStockHandler.handle() llamado

2. EVENT STORE (Persistencia)
   ├─ Handler carga eventos existentes
   ├─ Reconstruye agregado Inventory
   ├─ Ejecuta lógica de negocio
   ├─ Genera evento: StockAdded
   └─ Guarda evento en: data/events/{product_id}_{store_id}.json

3. EVENT BUS (Publicación)
   ├─ Handler publica evento en EventBus
   └─ EventBus notifica todos los subscribers

4. EVENT HANDLERS (Subscribers)
   ├─ update_read_model_on_stock_added() recibe evento
   ├─ Actualiza Read Model en: data/read_models/inventory.json
   ├─ Invalida caché para esta clave
   └─ Log: "read_model_updated"

5. CONSULTA (Read Side)
   ├─ Cliente envía GET /api/v1/inventory/products/{id}/stores/{id}
   ├─ GetStockHandler verifica caché (miss)
   ├─ Lee de Read Model (desnormalizado, rápido)
   ├─ Guarda en caché por 30s
   └─ Retorna 200 OK con datos
```

## 🔧 Componentes del Sistema

### 1. Event Store
- **Ubicación**: `src/infrastructure/persistence/event_store.py`
- **Almacenamiento**: `data/events/*.json`
- **Función**: Log append-only de todos los eventos
- **Formato**:
  ```json
  {
    "events": [
      {
        "event_type": "StockAdded",
        "event_id": "uuid",
        "product_id": "uuid",
        "store_id": "uuid",
        "quantity": 100,
        "timestamp": "2024-01-15T10:30:00Z",
        "version": 1
      }
    ]
  }
  ```

### 2. Event Bus
- **Ubicación**: `src/infrastructure/messaging/event_bus.py`
- **Tipo**: Pub/sub en memoria
- **Función**: Publicar eventos a subscribers
- **Subscribers registrados en**: `main.py` (lifespan)

### 3. Read Model Repository
- **Ubicación**: `src/infrastructure/persistence/read_model_repository.py`
- **Almacenamiento**: `data/read_models/inventory.json`
- **Función**: Proyecciones desnormalizadas para consultas rápidas
- **Formato**:
  ```json
  {
    "product_uuid:store_uuid": {
      "product_id": "uuid",
      "store_id": "uuid",
      "available": 100,
      "reserved": 0,
      "total": 100
    }
  }
  ```

### 4. Caché
- **Ubicación**: `src/infrastructure/cache/in_memory_cache.py`
- **Tipo**: En memoria con TTL (30 segundos)
- **Función**: Acelerar consultas
- **Estrategia**: 
  - Cache hit → retorna en ~1ms
  - Cache miss → consulta Read Model (~20ms)
  - Invalidación → cuando ocurre evento

## 🚀 Paso a Paso para Ejecutar

### Paso 1: Activar Entorno Virtual

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Si obtiene error de ejecución de scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

```bash
# Linux/macOS
source venv/bin/activate
```

### Paso 2: Verificar Dependencias

```bash
# Verificar entorno Python
python --version  # Debe ser 3.11+

# Verificar paquetes instalados
pip list | grep -E "fastapi|uvicorn|aiofiles|structlog"
```

### Paso 3: Inicializar Datos de Ejemplo (Opcional)

```bash
# Ejecutar script de inicialización
python scripts/init_sample_data.py

# Esto creará:
# - 5 productos
# - 3 tiendas
# - Inventario inicial
# - Archivo sample_data_ids.txt con IDs para pruebas
```

### Paso 4: Iniciar el Servidor

```bash
# Opción 1: Usando Python directamente
python main.py

# Opción 2: Usando uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Salida esperada:**
```
{"event":"application_starting","timestamp":"...","level":"info"}
{"event":"event_handlers_registered","handlers":["StockAdded","StockReserved",...],"level":"info"}
{"event":"application_started","timestamp":"...","level":"info"}
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Paso 5: Probar los Endpoints

#### Opción A: Swagger UI (Recomendado)
```
Abrir en navegador: http://localhost:8000/swagger
```

#### Opción B: cURL

**1. Health Check:**
```bash
curl http://localhost:8000/health
```

**2. Agregar Stock:**
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/stock" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "11111111-1111-1111-1111-111111111111",
    "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "quantity": 100,
    "reason": "initial_stock"
  }'
```

**3. Consultar Stock:**
```bash
curl "http://localhost:8000/api/v1/inventory/products/11111111-1111-1111-1111-111111111111/stores/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
```

**4. Reservar Stock:**
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/reserve" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "11111111-1111-1111-1111-111111111111",
    "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "quantity": 5,
    "customer_id": "99999999-9999-9999-9999-999999999999"
  }'
```

## 📊 Monitoreo y Logs

### Logs Estructurados

El sistema usa `structlog` para logs en JSON:

```json
{
  "event": "event_received",
  "event_type": "StockAdded",
  "product_id": "uuid",
  "store_id": "uuid",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "info"
}
```

### Ver Logs en Tiempo Real

```bash
# Ejecutar el servidor y ver logs formateados
python main.py
```

### Verificar Event Store

```bash
# Listar archivos de eventos
ls data/events/*.json

# Ver contenido de un archivo de eventos
cat data/events/{product_id}_{store_id}.json | jq .
```

### Verificar Read Models

```bash
# Ver read model
cat data/read_models/inventory.json | jq .
```

## 🧪 Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest -v

# Pruebas unitarias
pytest tests/unit -v

# Pruebas de integración
pytest tests/integration -v

# Pruebas end-to-end
pytest tests/e2e -v

# Con cobertura
pytest --cov=src --cov-report=html
```

## 🔍 Solución de Problemas

### Problema: ModuleNotFoundError
```bash
# Asegúrese de estar en la raíz del proyecto
cd /path/to/project

# Y venv está activado
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows
```

### Problema: Puerto 8000 ya en uso
```bash
# Encontrar y matar el proceso
lsof -ti:8000 | xargs kill -9  # Linux/macOS
netstat -ano | findstr :8000  # Windows (luego usar Task Manager)

# O usar un puerto diferente
uvicorn main:app --port 8001
```

### Problema: Permiso denegado en directorio data/
```bash
# Crear directorios manualmente
mkdir -p data/events data/read_models

# Verificar permisos
chmod 755 data
```

## 📚 Documentación Adicional

- [Detalles de Arquitectura](docs/ARCHITECTURE.es.md)
- [Diseño de API](docs/API_DESIGN.es.md)
- [Decisiones Técnicas](docs/TECHNICAL_DECISIONS.es.md)
- [Índice Completo de Documentación](INDEX.es.md)

## 🌍 Otros Idiomas

- [🇧🇷 Português](COMO_EXECUTAR.md)
- [🇺🇸 English](HOW_TO_RUN.md)

---

**¡Listo para comenzar!** 🚀

Si encuentra algún problema, consulte la sección de [Solución de Problemas](#-solución-de-problemas) o abra un issue en GitHub.
