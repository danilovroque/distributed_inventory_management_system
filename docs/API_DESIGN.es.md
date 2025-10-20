# 🌐 Diseño de API

Especificación completa de la API REST para el Sistema de Gestión de Inventario.

[🇺🇸 English](API_DESIGN.md) | [🇧🇷 Português](API_DESIGN.pt-BR.md) | [🇪🇸 Español](API_DESIGN.es.md)

## Descripción General

- **Protocolo**: HTTP/1.1, HTTP/2
- **Estilo**: RESTful
- **Formato**: JSON
- **Autenticación**: (Futuro) Bearer Token / API Key
- **Versionamiento**: Basado en ruta (`/api/v1/...`)
- **Documentación**: OpenAPI 3.0 (Swagger)

## URL Base

```
Local: http://localhost:8000/api/v1
Producción: https://api.inventory-system.com/api/v1
```

## Endpoints

### Health Check

#### GET /health

Verificar el estado de salud del servicio.

**Respuesta 200 OK:**
```json
{
  "status": "healthy",
  "service": "inventory-management-system",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Comandos (Operaciones de Escritura)

### 1. Agregar Stock

#### POST /inventory/stock

Agregar stock a una combinación producto-tienda.

**Request Body:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "quantity": 100,
  "reason": "restock"
}
```

**Campos:**
- `product_id` (UUID, obligatorio): ID del producto
- `store_id` (UUID, obligatorio): ID de la tienda
- `quantity` (int, obligatorio): Cantidad a agregar (> 0)
- `reason` (string, obligatorio): Motivo de la adición

**Respuesta 201 Created:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "available": 100,
  "reserved": 0,
  "total": 100,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- `400 Bad Request`: Parámetros inválidos (cantidad negativa)
- `500 Internal Server Error`: Error del servidor

**Ejemplo cURL:**
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

---

### 2. Reservar Stock

#### POST /inventory/reserve

Reservar stock para un cliente (ej. agregar al carrito).

**Request Body:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "quantity": 5,
  "customer_id": "99999999-9999-9999-9999-999999999999"
}
```

**Campos:**
- `product_id` (UUID, obligatorio): ID del producto
- `store_id` (UUID, obligatorio): ID de la tienda
- `quantity` (int, obligatorio): Cantidad a reservar (> 0)
- `customer_id` (UUID, obligatorio): ID del cliente

**Respuesta 201 Created:**
```json
{
  "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "quantity": 5,
  "customer_id": "99999999-9999-9999-9999-999999999999",
  "reserved_at": "2024-01-15T10:31:00Z",
  "expires_at": "2024-01-15T10:46:00Z"
}
```

**Errores:**
- `400 Bad Request`: Parámetros inválidos
- `409 Conflict`: Stock insuficiente
  ```json
  {
    "detail": {
      "message": "Stock insuficiente",
      "required": 5,
      "available": 3
    }
  }
  ```

**Ejemplo cURL:**
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

---

### 3. Confirmar Reserva

#### POST /inventory/commit

Confirmar una reserva (pedido completado).

**Request Body:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
  "order_id": "oooooooo-oooo-oooo-oooo-oooooooooooo"
}
```

**Campos:**
- `product_id` (UUID, obligatorio): ID del producto
- `store_id` (UUID, obligatorio): ID de la tienda
- `reservation_id` (UUID, obligatorio): ID de la reserva a confirmar
- `order_id` (UUID, obligatorio): ID del pedido creado

**Respuesta 200 OK:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
  "order_id": "oooooooo-oooo-oooo-oooo-oooooooooooo",
  "committed_at": "2024-01-15T10:32:00Z",
  "status": "committed"
}
```

**Errores:**
- `404 Not Found`: Reserva no encontrada
  ```json
  {
    "detail": "Reserva no encontrada: rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr"
  }
  ```

**Ejemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/commit" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "11111111-1111-1111-1111-111111111111",
    "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
    "order_id": "oooooooo-oooo-oooo-oooo-oooooooooooo"
  }'
```

---

### 4. Liberar Reserva

#### POST /inventory/release

Liberar una reserva (carrito abandonado, cancelación).

**Request Body:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
  "reason": "cart_abandoned"
}
```

**Campos:**
- `product_id` (UUID, obligatorio): ID del producto
- `store_id` (UUID, obligatorio): ID de la tienda
- `reservation_id` (UUID, obligatorio): ID de la reserva a liberar
- `reason` (string, obligatorio): Motivo de la liberación

**Respuesta 200 OK:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
  "released_at": "2024-01-15T10:33:00Z",
  "reason": "cart_abandoned",
  "status": "released"
}
```

**Errores:**
- `404 Not Found`: Reserva no encontrada

**Ejemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/release" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "11111111-1111-1111-1111-111111111111",
    "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
    "reason": "cart_abandoned"
  }'
```

---

## Consultas (Operaciones de Lectura)

### 5. Obtener Stock

#### GET /inventory/products/{product_id}/stores/{store_id}

Obtener nivel de stock actual para una combinación producto-tienda.

**Parámetros de Ruta:**
- `product_id` (UUID): ID del producto
- `store_id` (UUID): ID de la tienda

**Respuesta 200 OK:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "available": 95,
  "reserved": 5,
  "total": 100,
  "last_updated": "2024-01-15T10:31:00Z"
}
```

**Campos de Respuesta:**
- `available`: Stock disponible para nuevas reservas
- `reserved`: Stock actualmente reservado
- `total`: Stock total (disponible + reservado)
- `last_updated`: Timestamp de la última actualización

**Errores:**
- `404 Not Found`: Combinación producto-tienda no encontrada

**Ejemplo cURL:**
```bash
curl "http://localhost:8000/api/v1/inventory/products/11111111-1111-1111-1111-111111111111/stores/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
```

**Headers de Caché:**
```
Cache-Control: max-age=30
ETag: "abc123..."
```

---

### 6. Verificar Disponibilidad

#### POST /inventory/availability

Verificar si una cantidad requerida está disponible.

**Request Body:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "required_quantity": 10
}
```

**Campos:**
- `product_id` (UUID, obligatorio): ID del producto
- `store_id` (UUID, obligatorio): ID de la tienda
- `required_quantity` (int, obligatorio): Cantidad requerida (> 0)

**Respuesta 200 OK:**
```json
{
  "available": true,
  "current_stock": 95,
  "required_quantity": 10,
  "can_fulfill": true,
  "shortfall": 0
}
```

**Si no está disponible:**
```json
{
  "available": false,
  "current_stock": 3,
  "required_quantity": 10,
  "can_fulfill": false,
  "shortfall": 7
}
```

**Ejemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/availability" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "11111111-1111-1111-1111-111111111111",
    "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "required_quantity": 10
  }'
```

---

### 7. Obtener Inventario del Producto

#### GET /inventory/products/{product_id}

Obtener niveles de stock en todas las tiendas para un producto.

**Parámetros de Ruta:**
- `product_id` (UUID): ID del producto

**Respuesta 200 OK:**
```json
{
  "product_id": "11111111-1111-1111-1111-111111111111",
  "total_available": 285,
  "total_reserved": 15,
  "total_stock": 300,
  "stores": [
    {
      "store_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "available": 95,
      "reserved": 5,
      "total": 100,
      "last_updated": "2024-01-15T10:31:00Z"
    },
    {
      "store_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "available": 190,
      "reserved": 10,
      "total": 200,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Errores:**
- `404 Not Found`: Producto no encontrado o sin stock

**Ejemplo cURL:**
```bash
curl "http://localhost:8000/api/v1/inventory/products/11111111-1111-1111-1111-111111111111"
```

---

## Esquemas de Datos

### AddStockRequest
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": "integer (> 0)",
  "reason": "string (min_length=1, max_length=255)"
}
```

### ReserveStockRequest
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": "integer (> 0)",
  "customer_id": "uuid"
}
```

### CommitReservationRequest
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "reservation_id": "uuid",
  "order_id": "uuid"
}
```

### ReleaseReservationRequest
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "reservation_id": "uuid",
  "reason": "string (min_length=1, max_length=255)"
}
```

### CheckAvailabilityRequest
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "required_quantity": "integer (> 0)"
}
```

### StockResponse
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "available": "integer",
  "reserved": "integer",
  "total": "integer",
  "last_updated": "datetime (ISO 8601)"
}
```

### AvailabilityResponse
```json
{
  "available": "boolean",
  "current_stock": "integer",
  "required_quantity": "integer",
  "can_fulfill": "boolean",
  "shortfall": "integer"
}
```

---

## Códigos de Estado HTTP

| Código | Significado | Cuándo se Usa |
|--------|-------------|---------------|
| 200 | OK | Consulta exitosa |
| 201 | Created | Recurso creado exitosamente |
| 400 | Bad Request | Parámetros inválidos |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Conflicto de negocio (ej. stock insuficiente) |
| 500 | Internal Server Error | Error del servidor |
| 503 | Service Unavailable | Circuit breaker abierto |

---

## Manejo de Errores

### Formato de Error Estándar

```json
{
  "detail": {
    "message": "Descripción del error",
    "error_code": "ERROR_CODE",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123..."
  }
}
```

### Ejemplos de Errores

#### Stock Insuficiente (409 Conflict)
```json
{
  "detail": {
    "message": "Stock insuficiente para completar la reserva",
    "error_code": "INSUFFICIENT_STOCK",
    "required": 10,
    "available": 3,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Reserva No Encontrada (404 Not Found)
```json
{
  "detail": {
    "message": "Reserva no encontrada",
    "error_code": "RESERVATION_NOT_FOUND",
    "reservation_id": "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Error de Validación (400 Bad Request)
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

#### Error de Concurrencia (409 Conflict)
```json
{
  "detail": {
    "message": "Conflicto de versión detectado",
    "error_code": "CONCURRENCY_ERROR",
    "expected_version": 5,
    "current_version": 7,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

## Rate Limiting (Futuro)

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1610715000

{
  "detail": "Se excedió el límite de rate. Reintentar después de 2024-01-15T10:30:00Z"
}
```

---

## Versionamiento de API

**Estrategia**: Versionamiento basado en ruta

```
/api/v1/inventory/stock    ← Versión actual
/api/v2/inventory/stock    ← Futura versión
```

**Política de Deprecación**:
- Se admiten 2 versiones simultáneas
- Aviso de deprecación 6 meses antes
- Soporte de versión antigua por 12 meses

---

## Autenticación (Futuro)

### Bearer Token
```http
GET /api/v1/inventory/products/xxx
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key
```http
GET /api/v1/inventory/products/xxx
X-API-Key: your-api-key-here
```

---

## CORS

**Headers Actuales:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 3600
```

**Producción**: Restringir a orígenes específicos

---

## Documentación Interactiva

### Swagger UI
```
http://localhost:8000/swagger
```

### ReDoc
```
http://localhost:8000/redoc
```

### Especificación OpenAPI
```
http://localhost:8000/openapi.json
```

---

## Ejemplos de Integración

### JavaScript/TypeScript
```typescript
// Agregar stock
const response = await fetch('http://localhost:8000/api/v1/inventory/stock', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product_id: '11111111-1111-1111-1111-111111111111',
    store_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    quantity: 100,
    reason: 'restock'
  })
});

const data = await response.json();
console.log(data);
```

### Python
```python
import requests

# Reservar stock
response = requests.post(
    'http://localhost:8000/api/v1/inventory/reserve',
    json={
        'product_id': '11111111-1111-1111-1111-111111111111',
        'store_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'quantity': 5,
        'customer_id': '99999999-9999-9999-9999-999999999999'
    }
)

data = response.json()
print(f"Reservation ID: {data['reservation_id']}")
```

### cURL
```bash
# Obtener stock
curl -X GET \
  "http://localhost:8000/api/v1/inventory/products/11111111-1111-1111-1111-111111111111/stores/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" \
  -H "Accept: application/json"
```

---

## Mejores Prácticas

### Para Clientes

1. **Siempre manejar errores 409**: El stock insuficiente es una condición normal
2. **Implementar reintentos con backoff exponencial**: Para errores 5xx
3. **Respetar caché**: Usar ETags y Cache-Control
4. **Enviar request_id**: Para rastreo en logs
5. **Manejar idempotencia**: Los comandos deberían ser idempotentes

### Para el Servidor

1. **Validar entrada**: Usar Pydantic para validación estricta
2. **Logging estructurado**: Registrar cada request con request_id
3. **Monitoreo**: Rastrear latencia, tasa de error, throughput
4. **Graceful degradation**: Circuit breaker para dependencias

---

## Monitoreo y Métricas

### Métricas Clave (Futuro)

```
# Latencia por endpoint
api_request_duration_seconds{endpoint="/inventory/stock",method="POST"}

# Tasa de solicitudes
api_requests_total{endpoint="/inventory/stock",method="POST",status="201"}

# Tasa de errores
api_errors_total{endpoint="/inventory/reserve",error_type="insufficient_stock"}

# Estado de Circuit Breaker
circuit_breaker_state{service="event_store"}
```

---

Para más detalles, consulta:
- [Documentación de Arquitectura](ARCHITECTURE.es.md)
- [Decisiones Técnicas](TECHNICAL_DECISIONS.es.md)
- [Guía de Inicio Rápido](../QUICKSTART.es.md)
