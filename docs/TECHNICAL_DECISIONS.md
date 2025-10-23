# Technical Decisions Document

## Overview

This document details the technical decisions made during the development of the Distributed Inventory Management System.

## 1. Architecture Pattern: Event Sourcing + CQRS

### Decision
Implement Event Sourcing with CQRS pattern.

### Context
Traditional CRUD systems struggle with:
- Audit requirements
- Temporal queries
- Concurrent updates in distributed environment
- Performance of complex queries

### Alternatives Considered
1. **Traditional CRUD with optimistic locking**
   - Simpler implementation
   - Lost events history
   - Harder to debug

2. **Event Sourcing only (no CQRS)**
   - Still complex queries on event streams
   - Slower read performance

3. **CQRS only (no Event Sourcing)**
   - Lost audit trail
   - Harder to implement eventual consistency

### Rationale
Event Sourcing + CQRS provides:
- Complete audit trail (regulatory compliance)
- Optimized read models
- Natural eventual consistency
- Better scaling characteristics
- Ability to add new projections without migration

### Trade-offs
✅ **Pros:**
- Complete history
- Temporal queries
- Easier debugging
- Scalable reads/writes independently

❌ **Cons:**
- Increased complexity
- Storage overhead
- Learning curve
- Eventual consistency challenges

---

## 2. Consistency Model: Eventual Consistency

### Decision
Prioritize availability over strong consistency (AP in CAP theorem).

### Context
Multi-store retail environment where:
- Stores may be geographically distributed
- Network partitions can occur
- User experience is critical
- Temporary inconsistencies are acceptable

### Alternatives Considered
1. **Strong consistency with distributed transactions**
   - Lower availability
   - Higher latency
   - More complex

2. **Strong consistency per store**
   - Doesn't solve multi-store queries
   - Still needs sync mechanism

### Rationale
For e-commerce inventory:
- Better to show approximate stock than error
- Reservations handle critical path
- Updates propagate quickly (< 1 minute)
- Users tolerate "out of stock" at checkout

### Mitigation Strategies
- Reservation system for purchases
- Short cache TTL (30s)
- Optimistic locking for conflicts
- Compensating transactions

---

## 3. Persistence: JSON Files + SQLite

### Decision
Use JSON for event store, SQLite for read models (prototype).

### Context
Prototype system demonstrating patterns, not production-ready persistence.

### Alternatives Considered
1. **PostgreSQL for everything**
   - Overkill for prototype
   - More setup required
   - But better for production

2. **In-memory only**
   - Lost on restart
   - Can't demonstrate persistence patterns

3. **MongoDB**
   - Better for event store
   - Adds dependency
   - Not SQL-standard

### Rationale
JSON + SQLite:
- Easy to inspect events (human-readable)
- No external dependencies
- Sufficient for demonstration
- Easy migration path to production DB

### Production Recommendation
```
Event Store: PostgreSQL with JSONB
Read Models: PostgreSQL with indexes
Cache: Redis
Message Bus: Kafka
```

---

## 4. Concurrency Control: Optimistic Locking

### Decision
Use version-based optimistic locking instead of pessimistic locks.

### Context
Distributed system where distributed locks are complex and costly.

### Alternatives Considered
1. **Pessimistic locking**
   - Requires distributed lock manager (Redis, ZooKeeper)
   - Lower throughput
   - Deadlock risks

2. **No concurrency control**
   - Data corruption
   - Lost updates
   - Unacceptable

3. **Last-write-wins**
   - Simple but loses data
   - Not suitable for inventory

### Rationale
Optimistic locking:
- No distributed coordination needed
- Better performance
- Natural fit with event sourcing
- Clients can retry conflicts

### Trade-offs
✅ **Pros:**
- High throughput
- No lock contention
- Stateless

❌ **Cons:**
- Clients must handle retries
- Not good for high-contention scenarios
- More complex client logic

---

## 5. Caching Strategy: Aggressive TTL-based Cache

### Decision
Use in-memory cache with 30-second TTL for all read operations.

### Context
Read-heavy workload (90% reads, 10% writes) where sub-second latency is critical.

### Alternatives Considered
1. **No caching**
   - Simpler
   - Higher latency
   - More DB load

2. **Cache-aside with manual invalidation**
   - More control
   - More complex
   - Easy to get wrong

3. **Read-through cache**
   - Even more complex
   - Overkill for this use case

### Rationale
TTL-based cache:
- Simple to implement
- Predictable staleness
- Automatic cleanup
- Good enough for inventory use case

### Cache Invalidation
Events trigger explicit invalidation:
```python
on StockUpdated → invalidate(product:store)
```

---

## 6. Error Handling: Circuit Breaker + Retry

### Decision
Implement Circuit Breaker pattern with exponential backoff retry.

### Context
Distributed system where components can fail temporarily.

### Alternatives Considered
1. **No resilience patterns**
   - Cascading failures
   - Poor user experience

2. **Simple retry**
   - Can overwhelm failing service
   - No backoff

3. **Timeout only**
   - Still sends traffic to failing service
   - Wastes resources

### Rationale
Circuit Breaker + Retry:
- Protects against cascading failures
- Gives failing services time to recover
- Better user experience (fast-fail when open)
- Industry-standard pattern

### Configuration
```python
failure_threshold: 5 errors
timeout: 30 seconds
retry_attempts: 3
backoff: exponential (1s, 2s, 4s)
```

---

## 7. API Design: REST with OpenAPI

### Decision
RESTful API with FastAPI and auto-generated OpenAPI documentation.

### Context
Need standard, well-documented API for multiple client types.

### Alternatives Considered
1. **GraphQL**
   - More flexible
   - More complex
   - Overkill for CRUD-like operations

2. **gRPC**
   - Better performance
   - Harder to debug
   - Less standard

3. **REST**
   - Industry standard
   - Easy to understand
   - Good tooling

### Rationale
REST + OpenAPI:
- Well understood
- Excellent tooling
- Auto-generated documentation
- Easy to test
- FastAPI is modern and fast

---

## 8. Testing Strategy: Pyramid with Integration Focus

### Decision
Test pyramid: many unit tests, some integration tests, few E2E tests.

### Context
Clean Architecture makes testing at different levels natural.

### Test Distribution
```
E2E Tests (5%)        ▲
Integration (25%)     ██
Unit Tests (70%)   ████████
```

### Rationale
- Unit tests: Fast, test business logic
- Integration: Test component interaction
- E2E: Test critical user flows

### Coverage Target
- Overall: > 80%
- Domain layer: > 90%
- Application layer: > 80%
- Infrastructure: > 70%

---

## 9. Logging: Structured JSON Logging

### Decision
Use structured logging (structlog) with JSON output.

### Context
Need to analyze logs programmatically for debugging and monitoring.

### Alternatives Considered
1. **Plain text logs**
   - Human-readable
   - Hard to parse
   - Can't query efficiently

2. **Structured logging**
   - Machine-readable
   - Queryable
   - Standardized

### Rationale
Structured logging enables:
- Log aggregation (ELK, Splunk)
- Query by fields
- Correlation IDs
- Better observability

### Example
```json
{
  "timestamp": "2025-10-19T10:00:00Z",
  "level": "INFO",
  "event": "stock_reserved",
  "product_id": "uuid",
  "quantity": 5,
  "trace_id": "abc-123"
}
```

---

## 10. GenAI Integration: GitHub Copilot

### Decision
Use GitHub Copilot throughout development for code generation and suggestions.

### Context
Demonstrate modern development practices with AI assistance.

### Usage Patterns
1. **Boilerplate reduction**
   - Entity creation
   - Test scaffolding
   - API endpoints

2. **Pattern application**
   - Repository implementations
   - Event handlers
   - Error handling

3. **Documentation**
   - Docstrings
   - README sections
   - Comments

### Impact
- ~40% faster development
- More consistent code style
- Better test coverage
- Comprehensive documentation

### Human Oversight
- All generated code reviewed
- Business logic hand-crafted
- Architecture decisions made by human
- Tests verify correctness

---

## Summary Table

| Decision | Alternative | Rationale |
|----------|-------------|-----------|
| Event Sourcing | CRUD | Audit trail, temporal queries |
| CQRS | Shared model | Independent scaling |
| Eventual Consistency | Strong consistency | Higher availability |
| Optimistic Locking | Pessimistic locking | Better performance |
| TTL Cache | Manual invalidation | Simpler, predictable |
| Circuit Breaker | No resilience | Fault tolerance |
| REST API | GraphQL/gRPC | Standard, simple |
| Test Pyramid | E2E heavy | Faster feedback |
| Structured Logs | Plain text | Better observability |
| GitHub Copilot | Manual coding | Faster development |

---

## Lessons Learned

### What Worked Well
1. **Clean Architecture** - Easy to test, maintain, and extend
2. **Event Sourcing** - Debugging was much easier with complete history
3. **CQRS** - Read optimizations didn't affect write path
4. **Type hints + Pydantic** - Caught many bugs at development time

### What Could Be Improved
1. **Event replay** - Should implement snapshotting for large streams
2. **Testing** - Need more load tests for concurrency scenarios
3. **Documentation** - Could benefit from sequence diagrams
4. **Monitoring** - Need real metrics and alerts

### Future Considerations
1. Implement event versioning strategy
2. Add distributed tracing
3. Consider polyglot persistence
4. Implement SAGA pattern for complex transactions
5. Add GraphQL layer for flexible queries
