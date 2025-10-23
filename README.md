# Distributed Inventory Management System

A high-performance distributed inventory management system built with Event Sourcing, CQRS, and following Clean Architecture principles.

## 🏗️ Architecture Overview

This system implements a modern distributed architecture to solve consistency and latency problems for inventory in a multi-store retail environment.

### Key Features

- ✅ **Event Sourcing** - Complete audit trail and temporal queries
- ✅ **CQRS Pattern** - Optimized read and write operations
- ✅ **Clean Architecture** - Separation of concerns and maintainability
- ✅ **Circuit Breaker** - Fault tolerance and graceful degradation
- ✅ **In-Memory Cache** - Sub-second query performance

## 📊 Architecture Diagram

```
┌─────────────┐
│   Clients   │
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

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run specific test types:
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# E2E tests
pytest tests/e2e -v
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/swagger`
- ReDoc: `http://localhost:8000/redoc`

## 🏛️ Architecture Details

### Domain Layer
- **Entities**: `Inventory`, `Product`
- **Value Objects**: `StockQuantity`
- **Events**: Domain events for all state changes
- **Exceptions**: Domain-specific exceptions

### Application Layer
- **Commands**: Write operations (AddStock, ReserveStock, etc.)
- **Queries**: Read operations (GetStock, CheckAvailability, etc.)
- **Services**: Use case orchestration

### Infrastructure Layer
- **Event Store**: JSON-based event persistence
- **Read Model**: Query-optimized projections
- **Event Bus**: In-memory pub/sub
- **Cache**: TTL-based in-memory cache
- **Circuit Breaker**: Fault tolerance mechanism

### Presentation Layer
- **API**: REST endpoints with FastAPI
- **Middleware**: Logging, error handling
- **Schemas**: Request/response validation

## 🔧 Design Decisions

### Why Event Sourcing?
- Complete audit trail for regulatory compliance
- Ability to rebuild state from events
- Temporal queries (state at any point in time)
- Naturally fits distributed systems

### Why CQRS?
- Optimized read models with denormalization
- Independent scaling of reads and writes
- Different consistency requirements per side
- Better cache utilization

### Why Eventual Consistency?
- Higher availability (CAP theorem)
- Better performance for distributed stores
- Acceptable for inventory use cases
- Can show "approximate" stock without system downtime

### Trade-offs

| Decision | Benefit | Cost |
|---------|-----------|-------|
| Event Sourcing | Audit trail, temporal queries | Storage overhead, complexity |
| Eventual Consistency | High availability | Possible temporary inconsistencies |
| In-memory cache | Very fast reads | Memory usage, cache invalidation |
| Optimistic locking | No distributed locks | Retry overhead on conflicts |

## 🔐 Security Considerations

- Input validation with Pydantic
- UUID-based identifiers (no sequential IDs)
- CORS configuration
- Structured logging (no sensitive data)

## 🚧 Future Improvements

- [ ] Distributed tracing (OpenTelemetry)
- [ ] Metrics export (Prometheus)
- [ ] Real database (MySQL)
- [ ] Redis for distributed cache
- [ ] Kafka for event bus
- [ ] GraphQL API
- [ ] Webhooks for event notifications

## 📝 Development Tools Used

- **IDE**: Visual Studio Code with Python extensions
- **Testing**: pytest
- **Documentation**: OpenAPI/Swagger
- **GenAI**: GitHub Copilot for code generation and suggestions

## 📖 Additional Documentation

- [🇧🇷 Português](README.pt-BR.md)
- [🇪🇸 Español](README.es.md)
- [📚 Complete Documentation Index](INDEX.md)
