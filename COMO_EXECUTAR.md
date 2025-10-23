# 🚀 Como Executar o Sistema Localmente

**🌍 Outros idiomas:** [🇺🇸 English](HOW_TO_RUN.md) | [🇪🇸 Español](COMO_EJECUTAR.md)

## 📋 Visão Geral

Este documento explica como o sistema de eventos funciona localmente e como inicializar tudo.

## 🏗️ Arquitetura do Sistema de Eventos

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DE EVENTOS                          │
└─────────────────────────────────────────────────────────────┘

1. COMANDO (Write Side)
   ├─ Cliente envia POST /api/v1/inventory/stock
   ├─ API valida request
   ├─ AddStockCommand criado
   └─ AddStockHandler.handle() chamado

2. EVENT STORE (Persistência)
   ├─ Handler carrega eventos existentes
   ├─ Reconstrói agregado Inventory
   ├─ Executa lógica de negócio
   ├─ Gera evento: StockAdded
   └─ Salva evento em: data/events/{product_id}_{store_id}.json

3. EVENT BUS (Publicação)
   ├─ Handler publica evento no EventBus
   └─ EventBus notifica todos os subscribers

4. EVENT HANDLERS (Subscribers)
   ├─ update_read_model_on_stock_added() recebe evento
   ├─ Atualiza Read Model em: data/read_models/inventory.json
   ├─ Invalida cache para essa chave
   └─ Log: "read_model_updated"

5. CONSULTA (Read Side)
   ├─ Cliente envia GET /api/v1/inventory/products/{id}/stores/{id}
   ├─ GetStockHandler verifica cache (miss)
   ├─ Lê de Read Model (desnormalizado, rápido)
   ├─ Guarda em cache por 30s
   └─ Retorna 200 OK com dados
```

## 🔧 Componentes do Sistema

### 1. Event Store
- **Localização**: `src/infrastructure/persistence/event_store.py`
- **Armazenamento**: `data/events/*.json`
- **Função**: Append-only log de todos os eventos
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
- **Localização**: `src/infrastructure/messaging/event_bus.py`
- **Tipo**: In-memory pub/sub
- **Função**: Publicar eventos para subscribers
- **Subscribers registrados em**: `main.py` (lifespan)

### 3. Read Model Repository
- **Localização**: `src/infrastructure/persistence/read_model_repository.py`
- **Armazenamento**: `data/read_models/inventory.json`
- **Função**: Projeções desnormalizadas para queries rápidas
- **Formato**:
  ```json
  {
    "product_uuid:store_uuid": {
      "product_id": "uuid",
      "store_id": "uuid",
      "total_quantity": 100,
      "reserved_quantity": 0,
      "available_quantity": 100,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  }
  ```

### 4. Cache
- **Localização**: `src/infrastructure/cache/in_memory_cache.py`
- **Tipo**: In-memory com TTL (30 segundos)
- **Função**: Acelerar queries
- **Estratégia**: 
  - Cache hit → retorna em ~1ms
  - Cache miss → query Read Model (~20ms)
  - Invalidação → quando evento ocorre

## 🚀 Passo a Passo para Executar

### Passo 1: Ativar Ambiente Virtual

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Se der erro de execução de scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 2: Verificar Dependências

```powershell
# Verificar ambiente Python
python --version  # Deve ser 3.11+

# Verificar pacotes instalados
pip list | Select-String "fastapi|uvicorn|aiofiles|structlog"
```

### Passo 3: Inicializar Dados de Exemplo (Opcional)

```powershell
# Executar script de inicialização
python scripts\init_sample_data.py

# Isso vai criar:
# - 5 produtos
# - 3 lojas
# - Inventário inicial
# - Arquivo sample_data_ids.txt com IDs para testes
```

### Passo 4: Iniciar o Servidor

```powershell
# Opção 1: Usando Python diretamente
python main.py

# Opção 2: Usando uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opção 3: Usando o Python do venv explicitamente
"C:/Users/danil/OneDrive/Documents/Danilo/Teste MELI/venv/Scripts/python.exe" main.py
```

**Saída esperada:**
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

### Passo 5: Testar os Endpoints

#### Opção A: Swagger UI (Recomendado)
```
Abrir no navegador: http://localhost:8000/swagger
```

#### Opção B: cURL (PowerShell)

**1. Health Check:**
```powershell
curl http://localhost:8000/health
```

**2. Adicionar Stock:**
```powershell
$body = @{
    product_id = "11111111-1111-1111-1111-111111111111"
    store_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    quantity = 100
    reason = "initial_stock"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/inventory/stock" `
  -ContentType "application/json" -Body $body
```

**3. Consultar Stock:**
```powershell
curl "http://localhost:8000/api/v1/inventory/products/11111111-1111-1111-1111-111111111111/stores/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
```

**4. Reservar Stock:**
```powershell
$body = @{
    product_id = "11111111-1111-1111-1111-111111111111"
    store_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    quantity = 5
    customer_id = "99999999-9999-9999-9999-999999999999"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/inventory/reserve" `
  -ContentType "application/json" -Body $body
```

## 📊 Monitoramento e Logs

### Logs Estruturados

O sistema usa `structlog` para logs em JSON:

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

### Ver Logs em Tempo Real

```powershell
# Executar o servidor e ver logs formatados
python main.py
```

### Verificar Event Store

```powershell
# Listar arquivos de eventos
Get-ChildItem -Path data\events -Filter *.json

# Ver conteúdo de um arquivo de eventos
Get-Content data\events\{product_id}_{store_id}.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Verificar Read Models

```powershell
# Ver read model
Get-Content data\read_models\inventory.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## 🔄 Fluxo Completo de um Comando

### Exemplo: Adicionar Stock

1. **Request recebido**
   ```
   POST /api/v1/inventory/stock
   ```

2. **Log: request_started**
   ```json
   {"event":"request_started","method":"POST","path":"/api/v1/inventory/stock"}
   ```

3. **Comando criado**
   ```python
   AddStockCommand(product_id=..., store_id=..., quantity=100)
   ```

4. **Handler processa**
   - Carrega eventos existentes do Event Store
   - Reconstrói agregado Inventory
   - Executa `inventory.add_stock()`
   - Gera evento `StockAdded`

5. **Evento salvo**
   ```
   data/events/{product_id}_{store_id}.json
   ```

6. **Log: event_saved**
   ```json
   {"event":"event_saved","event_type":"StockAdded","version":1}
   ```

7. **Evento publicado**
   ```python
   event_bus.publish("StockAdded", event)
   ```

8. **Log: event_received**
   ```json
   {"event":"event_received","event_type":"StockAdded"}
   ```

9. **Read Model atualizado**
   ```
   data/read_models/inventory.json
   ```

10. **Log: read_model_updated**
    ```json
    {"event":"read_model_updated","event_type":"StockAdded"}
    ```

11. **Cache invalidado**
    ```python
    cache.delete("stock:{product_id}:{store_id}")
    ```

12. **Resposta enviada**
    ```
    HTTP 201 Created
    ```

## 🐛 Troubleshooting

### Problema: Eventos não atualizam Read Model

**Sintoma**: POST funciona mas GET retorna 404

**Causa**: Event handlers não registrados

**Solução**: Verificar que `main.py` tem as subscrições:
```python
event_bus.subscribe("StockAdded", update_read_model_on_stock_added)
```

### Problema: Dados inconsistentes

**Sintoma**: Read Model desatualizado em relação ao Event Store

**Solução**: Reprocessar eventos
```powershell
# Deletar read models
Remove-Item data\read_models\* -Force

# Reiniciar servidor (vai reprocessar eventos)
python main.py
```

### Problema: Erro de concorrência

**Sintoma**: `ConcurrencyError: Expected version X but got Y`

**Causa**: Múltiplas escritas simultâneas no mesmo agregado

**Solução**: Normal! O sistema usa bloqueo optimista. Clientes devem fazer retry.

## 📁 Estrutura de Arquivos Gerada

Após executar o sistema, você verá:

```
Teste MELI/
├── data/
│   ├── events/                    ← Event Store (append-only)
│   │   ├── {product_uuid}_{store_uuid}.json
│   │   └── ...
│   └── read_models/               ← Read Models (CQRS)
│       └── inventory.json
├── sample_data_ids.txt            ← IDs de teste (se executou init_sample_data.py)
└── ...
```

## 🎯 Próximos Passos

1. ✅ **Iniciar servidor**: `python main.py`
2. ✅ **Abrir Swagger**: http://localhost:8000/swagger
3. ✅ **Criar dados de teste**: `python scripts/init_sample_data.py`
4. ✅ **Testar endpoints**: Usar IDs do `sample_data_ids.txt`
5. ✅ **Ver logs**: Observar eventos sendo processados
6. ✅ **Verificar arquivos**: Olhar `data/events/` e `data/read_models/`

## 📚 Documentação Adicional

- [README.md](README.md) - Visão geral completa
- [QUICKSTART.md](QUICKSTART.md) - Início rápido em 5 minutos
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura detalhada
- [docs/API_DESIGN.md](docs/API_DESIGN.md) - Especificação da API
- [docs/TECHNICAL_DECISIONS.md](docs/TECHNICAL_DECISIONS.md) - Decisões técnicas

---

**Pronto para começar!** 🚀

Execute: `python main.py` e acesse http://localhost:8000/swagger
