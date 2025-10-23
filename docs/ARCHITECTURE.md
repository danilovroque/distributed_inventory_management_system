# System Architecture

[🇺🇸 English](ARCHITECTURE.md) | [🇧🇷 Português](ARCHITECTURE.pt-BR.md) | [🇪🇸 Español](ARCHITECTURE.es.md)

## Overview

This document describes the architectural decisions and patterns used in the Distributed Inventory Management System.

## Architectural Patterns

### 1. Clean Architecture

The system follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│     Presentation Layer (API)            │
├─────────────────────────────────────────┤
│   Application Layer (Use Cases)        │
├─────────────────────────────────────────┤
│   Domain Layer (Business Logic)        │
├─────────────────────────────────────────┤
│ Infrastructure Layer (External Deps)   │
└─────────────────────────────────────────┘
```

**Benefits:**
- Framework independence
- Testability
- UI independence
- Database independence
- External agency independence

### 2. Event Sourcing

All state changes are stored as immutable events in an append-only log.

**Event Store Structure:**
```
data/events/
  inventory-{product_id}-{store_id}.jsonl
    {"event_id": "...", "event_type": "StockAddedEvent", ...}
    {"event_id": "...", "event_type": "StockReservedEvent", ...}
```

**Benefits:**
- Complete audit trail
- Temporal queries
- Event replay
- Debugging capabilities

**Challenges:**
- Storage growth
- Query complexity
- Eventual consistency

### 3. CQRS (Command Query Responsibility Segregation)

Separate models for write operations (commands) and read operations (queries).

**Write Side (Commands):**
- Validates business rules
- Generates domain events
- Appends to event store
- Publishes events to bus

**Read Side (Queries):**
- Reads from optimized projections
- Uses aggressive caching
- Eventually consistent
- Fast response times

### 4. Domain-Driven Design

**Aggregates:**
- `Inventory` - Aggregate root for stock management
  - Protects invariants (quantity >= reserved)
  - Generates domain events
  - Encapsulates business logic

**Value Objects:**
- `StockQuantity` - Immutable, self-validating

**Domain Events:**
- `StockAddedEvent`
- `StockReservedEvent`
- `StockReleasedEvent`
- `StockCommittedEvent`

## Data Flow

### Write Path

```
1. Client Request
   ↓
2. API Validation (Pydantic)
   ↓
3. Command Handler
   ↓
4. Load Aggregate (from events)
   ↓
5. Execute Domain Logic
   ↓
6. Generate Events
   ↓
7. Append to Event Store (with optimistic locking)
   ↓
8. Publish to Event Bus
   ↓
9. Async Projections (update read models)
   ↓
10. Response to Client
```

### Read Path

```
1. Client Request
   ↓
2. Check Cache
   ├─ Hit → Return cached data
   └─ Miss ↓
3. Query Read Model
   ↓
4. Update Cache
   ↓
5. Response to Client
```

## Consistency Model

### Eventual Consistency

The system prioritizes **availability** over **strong consistency** (AP in CAP theorem).

**Why?**
- E-commerce can tolerate temporary inconsistencies
- Better user experience (fast responses)
- Higher system availability
- Scales better horizontally

**Mitigation Strategies:**
- Short cache TTL (30s)
- Reservation system for critical operations
- Version-based optimistic locking
- Compensating transactions

## Concurrency Control

### Optimistic Locking

Uses version numbers to detect conflicts:

```python
# Version mismatch = conflict
current_version = 5
expected_version = 4  # Another process already updated!
→ ConcurrencyError → Client retries
```

**Benefits:**
- No distributed locks
- Better performance
- Naturally fits event sourcing

**Trade-off:**
- Clients must handle retries
- Not suitable for high-contention scenarios

## Fault Tolerance

### Circuit Breaker Pattern

Protects against cascading failures:

```
CLOSED → failures < threshold
   ↓
OPEN → reject all requests
   ↓
HALF-OPEN → try one request
   ↓
CLOSED (success) or OPEN (failure)
```

### Retry with Exponential Backoff

Transient failures are retried with increasing delays:
- Attempt 1: immediate
- Attempt 2: 1s delay
- Attempt 3: 2s delay
- Max attempts: 3

## Caching Strategy

### Multi-Level Cache

1. **In-Memory Cache** (InMemoryCache)
   - TTL: 30 seconds
   - Max size: 1000 entries
   - LRU eviction

2. **Read Model** (Projections)
   - Persistent denormalized views
   - Updated asynchronously via events

### Cache Invalidation

Invalidated on write events:
```python
# Stock updated
await cache.invalidate(f"stock:{product_id}:{store_id}")
await cache.invalidate(f"product_inventory:{product_id}")
```

## Scalability Considerations

### Horizontal Scalability

**API Layer:**
- Stateless
- Can scale independently
- Load balancing

**Event Store:**
- Partitioned by stream ID
- Append-only (write-optimized)

**Read Models:**
- Can have multiple projections
- Each optimized for specific queries

### Vertical Scalability

- Async I/O for high concurrency
- Connection pooling
- Batch event processing

## Observability

### Structured Logging

All logs are structured JSON:
```json
{
  "timestamp": "2025-10-19T10:00:00Z",
  "level": "INFO",
  "event": "stock_added",
  "product_id": "...",
  "quantity": 100
}
```

### Metrics (Future)

- Request latency (p50, p95, p99)
- Error rates
- Cache hit rate
- Event processing lag

### Tracing (Future)

- Distributed tracing with OpenTelemetry
- Request correlation IDs

## Security

### Input Validation

- Pydantic models for all inputs
- UUID validation
- Quantity range checks

### Error Handling

- No sensitive data in errors
- Generic error messages for clients
- Detailed logs for debugging

## Technology Stack Rationale

| Technology | Rationale |
|------------|-----------|
| **FastAPI** | Modern, async, auto-generated docs |
| **Pydantic** | Runtime validation, type safety |
| **JSON** | Human-readable events, easy debugging |
| **structlog** | Structured logging, production-ready |
| **pytest** | Industry standard, async support |

## Future Architecture Improvements

### Production Enhancements

1. **Replace SQLite with PostgreSQL**
   - Better concurrency
   - ACID transactions
   - Replication

2. **Replace JSON Event Store with PostgreSQL**
   - Atomic appends
   - Better query performance
   - Native UUID support

3. **Add Redis for Caching**
   - Distributed cache
   - Pub/sub for events
   - Better scalability

4. **Add Kafka for Event Bus**
   - Guaranteed delivery
   - Replay capability
   - Better ordering

5. **Add Message Queue (RabbitMQ/SQS)**
   - Async processing
   - Better resilience
   - Dead letter queues

6. **Implement API Gateway**
   - Rate limiting
   - Authentication/Authorization
   - Request routing