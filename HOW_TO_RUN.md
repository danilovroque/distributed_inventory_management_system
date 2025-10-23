# 🚀 How to Run the System Locally

## 📋 Overview

This document explains how the event system works locally and how to initialize everything.

## 🏗️ Event System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EVENT FLOW                                │
└─────────────────────────────────────────────────────────────┘

1. COMMAND (Write Side)
   ├─ Client sends POST /api/v1/inventory/stock
   ├─ API validates request
   ├─ AddStockCommand created
   └─ AddStockHandler.handle() called

2. EVENT STORE (Persistence)
   ├─ Handler loads existing events
   ├─ Rebuilds Inventory aggregate
   ├─ Executes business logic
   ├─ Generates event: StockAdded
   └─ Saves event to: data/events/{product_id}_{store_id}.json

3. EVENT BUS (Publishing)
   ├─ Handler publishes event to EventBus
   └─ EventBus notifies all subscribers

4. EVENT HANDLERS (Subscribers)
   ├─ update_read_model_on_stock_added() receives event
   ├─ Updates Read Model in: data/read_models/inventory.json
   ├─ Invalidates cache for this key
   └─ Log: "read_model_updated"

5. QUERY (Read Side)
   ├─ Client sends GET /api/v1/inventory/products/{id}/stores/{id}
   ├─ GetStockHandler checks cache (miss)
   ├─ Reads from Read Model (denormalized, fast)
   ├─ Stores in cache for 30s
   └─ Returns 200 OK with data
```

## 🔧 System Components

### 1. Event Store
- **Location**: `src/infrastructure/persistence/event_store.py`
- **Storage**: `data/events/*.json`
- **Function**: Append-only log of all events
- **Format**:
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
- **Location**: `src/infrastructure/messaging/event_bus.py`
- **Type**: In-memory pub/sub
- **Function**: Publish events to subscribers
- **Subscribers registered in**: `main.py` (lifespan)

### 3. Read Model Repository
- **Location**: `src/infrastructure/persistence/read_model_repository.py`
- **Storage**: `data/read_models/inventory.json`
- **Function**: Denormalized projections for fast queries
- **Format**:
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

### 4. Cache
- **Location**: `src/infrastructure/cache/in_memory_cache.py`
- **Type**: In-memory with TTL (30 seconds)
- **Function**: Accelerate queries
- **Strategy**: 
  - Cache hit → returns in ~1ms
  - Cache miss → query Read Model (~20ms)
  - Invalidation → when event occurs

## 🚀 Step by Step to Execute

### Step 1: Activate Virtual Environment

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# If you get script execution error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

```bash
# Linux/macOS
source venv/bin/activate
```

### Step 2: Verify Dependencies

```bash
# Check Python environment
python --version  # Should be 3.11+

# Check installed packages
pip list | grep -E "fastapi|uvicorn|aiofiles|structlog"
```

### Step 3: Initialize Sample Data (Optional)

```bash
# Run initialization script
python scripts/init_sample_data.py

# This will create:
# - 5 products
# - 3 stores
# - Initial inventory
# - sample_data_ids.txt file with IDs for testing
```

### Step 4: Start the Server

```bash
# Option 1: Using Python directly
python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
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

### Step 5: Test the Endpoints

#### Option A: Swagger UI (Recommended)
```
Open in browser: http://localhost:8000/swagger
```

#### Option B: cURL

**1. Health Check:**
```bash
curl http://localhost:8000/health
```

**2. Add Stock:**
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

**3. Query Stock:**
```bash
curl "http://localhost:8000/api/v1/inventory/products/11111111-1111-1111-1111-111111111111/stores/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
```

**4. Reserve Stock:**
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

## 📊 Monitoring and Logs

### Structured Logs

The system uses `structlog` for JSON logs:

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

### View Real-time Logs

```bash
# Run the server and view formatted logs
python main.py
```

### Check Event Store

```bash
# List event files
ls data/events/*.json

# View content of an event file
cat data/events/{product_id}_{store_id}.json | jq .
```

### Check Read Models

```bash
# View read model
cat data/read_models/inventory.json | jq .
```

## 🧪 Running Tests

```bash
# Run all tests
pytest -v

# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# End-to-end tests
pytest tests/e2e -v

# With coverage
pytest --cov=src --cov-report=html
```

## 🔍 Troubleshooting

### Issue: ModuleNotFoundError
```bash
# Make sure you're in the project root
cd /path/to/project

# And venv is activated
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows
```

### Issue: Port 8000 already in use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9  # Linux/macOS
netstat -ano | findstr :8000  # Windows (then use Task Manager)

# Or use a different port
uvicorn main:app --port 8001
```

### Issue: Permission denied on data/ directory
```bash
# Create directories manually
mkdir -p data/events data/read_models

# Check permissions
chmod 755 data
```

## 📚 Additional Documentation

- [Architecture Details](docs/ARCHITECTURE.md)
- [API Design](docs/API_DESIGN.md)
- [Technical Decisions](docs/TECHNICAL_DECISIONS.md)
- [Complete Documentation Index](INDEX.md)

## 🌍 Other Languages

- [🇧🇷 Português](COMO_EXECUTAR.md)
- [🇪🇸 Español](COMO_EJECUTAR.md)

---

**Ready to start!** 🚀

If you encounter any issues, check the [Troubleshooting](#-troubleshooting) section or open an issue on GitHub.
