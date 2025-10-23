# Sistema de Gestión de Inventario Distribuido

Un sistema de gestión de inventario distribuido de alto rendimiento, construido con Event Sourcing, CQRS y siguiendo los principios de Clean Architecture.

## 🏗️ Visión General de la Arquitectura

Este sistema implementa una arquitectura distribuida moderna para resolver problemas de consistencia y latencia de inventario en un entorno minorista multi-tienda.

### Funcionalidades Principales

- ✅ **Event Sourcing** - Registro de auditoría completo y consultas temporales
- ✅ **Patrón CQRS** - Operaciones de lectura y escritura optimizadas
- ✅ **Clean Architecture** - Separación de responsabilidades y mantenibilidad
- ✅ **Circuit Breaker** - Tolerancia a fallos y degradación elegante
- ✅ **Caché en Memoria** - Rendimiento de consulta en subsegundos

## 📊 Diagrama de Arquitectura

```
┌─────────────┐
│   Clientes  │
└──────┬──────┘
       │
┌──────▼──────────────┐
│   API Gateway       │
└──────┬──────────────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────┐
│Write│  │Read  │  (CQRS)
│Layer│  │Layer │
└──┬──┘  └─▲────┘
   │       │
┌──▼───────┴──┐
│ Event Store │
└─────────────┘
```

## 🚀 Comenzando

### Prerequisitos

- Python 3.11+
- pip

### Instalación

1. Instale las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecute la aplicación:
```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

## 🧪 Pruebas

Ejecute todas las pruebas:
```bash
pytest
```

Ejecute tipos específicos de pruebas:
```bash
# Pruebas unitarias
pytest tests/unit -v

# Pruebas de integración
pytest tests/integration -v

# Pruebas E2E
pytest tests/e2e -v
```

Ejecute con cobertura:
```bash
pytest --cov=src --cov-report=html
```

## 📚 Documentación de la API

La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/swagger`
- ReDoc: `http://localhost:8000/redoc`

## 🏛️ Detalles de la Arquitectura

### Capa de Dominio
- **Entidades**: `Inventory`, `Product`
- **Objetos de Valor**: `StockQuantity`
- **Eventos**: Eventos de dominio para todos los cambios de estado
- **Excepciones**: Excepciones específicas del dominio

### Capa de Aplicación
- **Comandos**: Operaciones de escritura (AddStock, ReserveStock, etc.)
- **Consultas**: Operaciones de lectura (GetStock, CheckAvailability, etc.)
- **Servicios**: Orquestación de casos de uso

### Capa de Infraestructura
- **Event Store**: Persistencia de eventos basada en JSON
- **Read Model**: Proyecciones optimizadas para consultas
- **Event Bus**: Pub/sub en memoria
- **Caché**: Caché en memoria basada en TTL
- **Circuit Breaker**: Mecanismo de tolerancia a fallos

### Capa de Presentación
- **API**: Endpoints REST con FastAPI
- **Middleware**: Logging, manejo de errores
- **Schemas**: Validación de solicitud/respuesta

## 🔧 Decisiones de Diseño

### ¿Por qué Event Sourcing?
- Registro de auditoría completo para cumplimiento regulatorio
- Capacidad de reconstruir estado a partir de eventos
- Consultas temporales (estado en cualquier punto en el tiempo)
- Se ajusta naturalmente a sistemas distribuidos

### ¿Por qué CQRS?
- Modelos de lectura optimizados con desnormalización
- Escalabilidad independiente de lecturas y escrituras
- Diferentes requisitos de consistencia por lado
- Mejor utilización de caché

### ¿Por qué Consistencia Eventual?
- Mayor disponibilidad (teorema CAP)
- Mejor rendimiento para tiendas distribuidas
- Aceptable para casos de uso de inventario
- Puede mostrar stock "aproximado" sin caída del sistema

### Compromisos

| Decisión | Beneficio | Costo |
|---------|-----------|-------|
| Event Sourcing | Registro de auditoría, consultas temporales | Sobrecarga de almacenamiento, complejidad |
| Consistencia Eventual | Alta disponibilidad | Posibles inconsistencias temporales |
| Caché en memoria | Lecturas muy rápidas | Uso de memoria, invalidación de caché |
| Optimistic locking | Sin bloqueos distribuidos | Sobrecarga de reintento en conflictos |

## 🔐 Consideraciones de Seguridad

- Validación de entrada con Pydantic
- Identificadores basados en UUID (sin IDs secuenciales)
- Configuración CORS
- Logging estructurado (sin datos sensibles)

## 🚧 Mejoras Futuras

- [ ] Rastreo distribuido (OpenTelemetry)
- [ ] Exportación de métricas (Prometheus)
- [ ] Base de datos real (MySQL)
- [ ] Redis para caché distribuida
- [ ] Kafka para event bus
- [ ] API GraphQL
- [ ] Webhooks para notificaciones de eventos

## 📝 Herramientas de Desarrollo Utilizadas

- **IDE**: Visual Studio Code con extensiones Python
- **Pruebas**: pytest
- **Documentación**: OpenAPI/Swagger
- **GenAI**: GitHub Copilot para generación de código y sugerencias

## 📖 Documentación Adicional

- [🇧🇷 Português](README.pt-BR.md)
- [🇺🇸 English](README.md)
- [📚 Índice Completo de Documentación](INDEX.es.md)
