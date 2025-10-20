# Architecture Diagrams

This file contains Mermaid diagrams for the system architecture.

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[Web Application]
        Mobile[Mobile App]
        Store[Store System]
    end

    subgraph "API Gateway Layer"
        Gateway[API Gateway / Load Balancer]
    end

    subgraph "Application Layer"
        CommandService[Inventory Command Service<br/>Write Operations]
        QueryService[Inventory Query Service<br/>Read Operations]
    end

    subgraph "Infrastructure Layer"
        EventStore[(Event Store<br/>JSON/SQLite)]
        ReadModel[(Read Model<br/>SQLite Cache)]
        EventBus[Event Bus<br/>In-Memory]
    end

    subgraph "Background Workers"
        SyncWorker1[Store Sync Worker 1]
        SyncWorker2[Store Sync Worker 2]
        AnalyticsWorker[Analytics Worker]
    end

    WebApp --> Gateway
    Mobile --> Gateway
    Store --> Gateway

    Gateway --> CommandService
    Gateway --> QueryService

    CommandService --> EventStore
    EventStore --> EventBus
    
    EventBus --> SyncWorker1
    EventBus --> SyncWorker2
    EventBus --> AnalyticsWorker
    EventBus --> ReadModel

    QueryService --> ReadModel

    style CommandService fill:#ff6b6b
    style QueryService fill:#4ecdc4
    style EventStore fill:#ffe66d
    style EventBus fill:#95e1d3
```

## 2. Clean Architecture Layers

```mermaid
graph TB
    subgraph "Presentation Layer"
        API[FastAPI Endpoints]
        Middleware[Middleware & Error Handlers]
        Schemas[Request/Response Schemas]
    end

    subgraph "Application Layer"
        Commands[Commands<br/>- AddStock<br/>- ReserveStock<br/>- ReleaseStock]
        Queries[Queries<br/>- GetStock<br/>- CheckAvailability]
        AppServices[Application Services<br/>- InventoryService<br/>- SyncService]
    end

    subgraph "Domain Layer"
        Entities[Entities<br/>- Inventory<br/>- Product]
        Events[Domain Events<br/>- StockAdded<br/>- StockReserved]
        ValueObjects[Value Objects<br/>- StockQuantity]
        DomainExceptions[Domain Exceptions]
    end

    subgraph "Infrastructure Layer"
        EventStore[Event Store Repository]
        ReadModelRepo[Read Model Repository]
        EventBusImpl[Event Bus Implementation]
        CircuitBreaker[Circuit Breaker]
        Cache[In-Memory Cache]
    end

    API --> Commands
    API --> Queries
    Commands --> AppServices
    Queries --> AppServices
    AppServices --> Entities
    AppServices --> Events
    Entities --> ValueObjects
    AppServices --> EventStore
    AppServices --> ReadModelRepo
    AppServices --> EventBusImpl
    EventBusImpl --> Cache
    AppServices --> CircuitBreaker

    style Domain Layer fill:#e8f5e9
    style Application Layer fill:#fff3e0
    style Infrastructure Layer fill:#e3f2fd
    style Presentation Layer fill:#f3e5f5
```

## 3. Event Sourcing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant CommandService
    participant EventStore
    participant EventBus
    participant ReadModel
    participant Cache
    participant SyncWorker

    Client->>API: POST /inventory/stock
    API->>CommandService: AddStockCommand
    
    Note over CommandService: Validate business rules
    
    CommandService->>EventStore: Save StockAddedEvent(v)
    
    alt Concurrency Conflict
        EventStore-->>CommandService: ConcurrencyException
        CommandService-->>API: 409 Conflict
        API-->>Client: Retry with new version
    else Success
        EventStore-->>CommandService: Event saved (v+1)
        CommandService->>EventBus: Publish StockAddedEvent
        
        par Parallel Event Processing
            EventBus->>ReadModel: Update projection
            EventBus->>Cache: Invalidate cache
            EventBus->>SyncWorker: Notify sync required
        end
        
        ReadModel-->>EventBus: Updated
        Cache-->>EventBus: Invalidated
        SyncWorker-->>EventBus: Acknowledged
        
        CommandService-->>API: 201 Created
        API-->>Client: Success response
    end

    Note over SyncWorker: Async sync to stores
```

## 4. CQRS Query Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant QueryService
    participant Cache
    participant ReadModel
    participant CircuitBreaker

    Client->>API: GET /inventory/products/{id}
    API->>QueryService: GetStockQuery
    
    QueryService->>Cache: Check cache
    
    alt Cache Hit
        Cache-->>QueryService: Return cached data
        QueryService-->>API: Stock data
    else Cache Miss
        Cache-->>QueryService: Not found
        
        QueryService->>CircuitBreaker: Check state
        
        alt Circuit Open
            CircuitBreaker-->>QueryService: Circuit open
            QueryService-->>API: 503 Service Unavailable
            API-->>Client: Fallback response
        else Circuit Closed
            CircuitBreaker->>ReadModel: Query stock
            ReadModel-->>CircuitBreaker: Stock data
            CircuitBreaker-->>QueryService: Stock data
            
            QueryService->>Cache: Store in cache (TTL: 30s)
            QueryService-->>API: Stock data
        end
    end
    
    API-->>Client: 200 OK + Stock data
```

## 5. Domain Model

```mermaid
classDiagram
    class Product {
        +UUID id
        +str sku
        +str name
        +Decimal price
        +validate()
    }

    class Inventory {
        +UUID id
        +UUID product_id
        +UUID store_id
        +StockQuantity quantity
        +StockQuantity reserved
        +int version
        +add_stock(quantity)
        +reserve_stock(quantity)
        +release_stock(quantity)
        +commit_reservation(quantity)
        +get_available()
    }

    class StockQuantity {
        <<ValueObject>>
        +int value
        +validate()
        +add(other)
        +subtract(other)
    }

    class DomainEvent {
        <<Abstract>>
        +UUID event_id
        +datetime timestamp
        +int version
        +dict metadata
    }

    class StockAddedEvent {
        +UUID product_id
        +UUID store_id
        +int quantity
    }

    class StockReservedEvent {
        +UUID product_id
        +UUID store_id
        +int quantity
        +UUID reservation_id
    }

    class StockReleasedEvent {
        +UUID product_id
        +UUID store_id
        +int quantity
        +UUID reservation_id
    }

    Inventory --> Product
    Inventory --> StockQuantity
    DomainEvent <|-- StockAddedEvent
    DomainEvent <|-- StockReservedEvent
    DomainEvent <|-- StockReleasedEvent
    Inventory ..> DomainEvent : emits
```

## 6. Circuit Breaker State Machine

```mermaid
stateDiagram-v2
    [*] --> Closed: Initial State
    
    Closed --> Open: Failure threshold reached<br/>(e.g., 5 failures in 10s)
    
    Open --> HalfOpen: Timeout elapsed<br/>(e.g., after 30s)
    
    HalfOpen --> Closed: Success
    HalfOpen --> Open: Failure
    
    Closed --> Closed: Success
    
    note right of Open
        All requests immediately fail
        Return cached data or fallback
    end note
    
    note right of HalfOpen
        Allow limited requests
        to test if service recovered
    end note
    
    note right of Closed
        Normal operation
        Monitor failure rate
    end note
```

## 7. Multi-Store Synchronization

```mermaid
graph LR
    subgraph "Central System"
        Central[(Central<br/>Event Store)]
        EventBus[Event Bus]
    end

    subgraph "Store 1"
        Local1[(Local<br/>Cache)]
        Worker1[Sync Worker]
    end

    subgraph "Store 2"
        Local2[(Local<br/>Cache)]
        Worker2[Sync Worker]
    end

    subgraph "Store N"
        LocalN[(Local<br/>Cache)]
        WorkerN[Sync Worker]
    end

    Central --> EventBus
    EventBus -->|Push events| Worker1
    EventBus -->|Push events| Worker2
    EventBus -->|Push events| WorkerN

    Worker1 -->|Update| Local1
    Worker2 -->|Update| Local2
    WorkerN -->|Update| LocalN

    Local1 -.->|Pull updates<br/>if offline| Central
    Local2 -.->|Pull updates<br/>if offline| Central
    LocalN -.->|Pull updates<br/>if offline| Central

    style Central fill:#ff6b6b
    style EventBus fill:#95e1d3
```

## 8. Event Processing Pipeline

```mermaid
flowchart TD
    Start([Event Created]) --> Validate{Validate Event}
    
    Validate -->|Invalid| Error[Log Error & Alert]
    Validate -->|Valid| Store[Store in Event Store]
    
    Store --> Publish[Publish to Event Bus]
    
    Publish --> Parallel{Parallel Processing}
    
    Parallel -->|Path 1| UpdateRead[Update Read Model]
    Parallel -->|Path 2| InvalidateCache[Invalidate Cache]
    Parallel -->|Path 3| NotifyStores[Notify Store Workers]
    Parallel -->|Path 4| Analytics[Send to Analytics]
    
    UpdateRead --> CheckRead{Success?}
    InvalidateCache --> CheckCache{Success?}
    NotifyStores --> CheckNotify{Success?}
    Analytics --> CheckAnalytics{Success?}
    
    CheckRead -->|No| RetryRead[Retry with Backoff]
    CheckCache -->|No| RetryCache[Retry with Backoff]
    CheckNotify -->|No| RetryNotify[Retry with Backoff]
    CheckAnalytics -->|No| RetryAnalytics[Retry with Backoff]
    
    RetryRead --> UpdateRead
    RetryCache --> InvalidateCache
    RetryNotify --> NotifyStores
    RetryAnalytics --> Analytics
    
    CheckRead -->|Yes| Merge[Merge Results]
    CheckCache -->|Yes| Merge
    CheckNotify -->|Yes| Merge
    CheckAnalytics -->|Yes| Merge
    
    Merge --> End([Event Processed])
    Error --> End
    
    style Start fill:#95e1d3
    style End fill:#4ecdc4
    style Error fill:#ff6b6b
```

## How to View These Diagrams

1. **GitHub/GitLab**: These platforms render Mermaid automatically
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **Online**: Copy to https://mermaid.live/
4. **Export**: Use mermaid-cli to generate PNG/SVG files

## Generate Images

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate images
mmdc -i docs/DIAGRAMS.md -o docs/diagrams/
```
