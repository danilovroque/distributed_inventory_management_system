# Arquitetura do Sistema

[English version](ARCHITECTURE.md)

## Visão Geral

Este documento descreve as decisões arquiteturais e padrões usados no Sistema de Gerenciamento de Inventário Distribuído.

## Padrões Arquiteturais

### 1. Clean Architecture

O sistema segue os princípios da Clean Architecture com clara separação de responsabilidades:

```
┌─────────────────────────────────────────┐
│     Camada de Apresentação (API)        │
├─────────────────────────────────────────┤
│   Camada de Aplicação (Casos de Uso)   │
├─────────────────────────────────────────┤
│   Camada de Domínio (Lógica de Negócio)│
├─────────────────────────────────────────┤
│ Camada de Infraestrutura (Deps Externas)│
└─────────────────────────────────────────┘
```

**Benefícios:**
- Independência de frameworks
- Testabilidade
- Independência de UI
- Independência de banco de dados
- Independência de agências externas

### 2. Event Sourcing

Todas as mudanças de estado são armazenadas como eventos imutáveis em um log append-only.

**Estrutura do Event Store:**
```
data/events/
  inventory-{product_id}-{store_id}.jsonl
    {"event_id": "...", "event_type": "StockAddedEvent", ...}
    {"event_id": "...", "event_type": "StockReservedEvent", ...}
```

**Benefícios:**
- Trilha de auditoria completa
- Consultas temporais
- Replay de eventos
- Capacidades de depuração

**Desafios:**
- Crescimento de armazenamento
- Complexidade de consultas
- Consistência eventual

### 3. CQRS (Command Query Responsibility Segregation)

Modelos separados para operações de escrita (comandos) e leitura (consultas).

**Camada de Escrita (Comandos):**
- Valida regras de negócio
- Gera eventos de domínio
- Adiciona ao event store
- Publica eventos no bus

**Camada de Leitura (Consultas):**
- Lê de projeções otimizadas
- Usa cache agressivo
- Eventualmente consistente
- Tempos de resposta rápidos

### 4. Domain-Driven Design

**Agregados:**
- `Inventory` - Raiz agregada para gerenciamento de estoque
  - Protege invariantes (quantity >= reserved)
  - Gera eventos de domínio
  - Encapsula lógica de negócio

**Objetos de Valor:**
- `StockQuantity` - Imutável, auto-validável

**Eventos de Domínio:**
- `StockAddedEvent`
- `StockReservedEvent`
- `StockReleasedEvent`
- `StockCommittedEvent`

## Fluxo de Dados

### Caminho de Escrita

```
1. Requisição do Cliente
   ↓
2. Validação da API (Pydantic)
   ↓
3. Command Handler
   ↓
4. Carregar Agregado (a partir de eventos)
   ↓
5. Executar Lógica de Domínio
   ↓
6. Gerar Eventos
   ↓
7. Adicionar ao Event Store (com optimistic locking)
   ↓
8. Publicar no Event Bus
   ↓
9. Projeções Assíncronas (atualizar read models)
   ↓
10. Resposta ao Cliente
```

### Caminho de Leitura

```
1. Requisição do Cliente
   ↓
2. Verificar Cache
   ├─ Hit → Retornar dados em cache
   └─ Miss ↓
3. Consultar Read Model
   ↓
4. Atualizar Cache
   ↓
5. Resposta ao Cliente
```

## Modelo de Consistência

### Consistência Eventual

O sistema prioriza **disponibilidade** sobre **consistência forte** (AP no teorema CAP).

**Por quê?**
- E-commerce pode tolerar inconsistências temporárias
- Melhor experiência do usuário (respostas rápidas)
- Maior disponibilidade do sistema
- Escala melhor horizontalmente

**Estratégias de Mitigação:**
- TTL de cache curto (30s)
- Sistema de reservas para operações críticas
- Optimistic locking baseado em versão
- Transações compensatórias

## Controle de Concorrência

### Optimistic Locking

Usa números de versão para detectar conflitos:

```python
# Incompatibilidade de versão = conflito
current_version = 5
expected_version = 4  # Outro processo já atualizou!
→ ConcurrencyError → Cliente tenta novamente
```

**Benefícios:**
- Sem locks distribuídos
- Melhor performance
- Adequado naturalmente para event sourcing

**Trade-off:**
- Clientes devem lidar com retries
- Não adequado para cenários de alta contenção

## Tolerância a Falhas

### Padrão Circuit Breaker

Protege contra falhas em cascata:

```
FECHADO → falhas < threshold
   ↓
ABERTO → rejeitar todas requisições
   ↓
MEIO-ABERTO → tentar uma requisição
   ↓
FECHADO (sucesso) ou ABERTO (falha)
```

### Retry com Backoff Exponencial

Falhas transitórias são retentadas com atrasos crescentes:
- Tentativa 1: imediato
- Tentativa 2: atraso de 1s
- Tentativa 3: atraso de 2s
- Tentativas máximas: 3

## Estratégia de Caching

### Cache Multi-Nível

1. **Cache em Memória** (InMemoryCache)
   - TTL: 30 segundos
   - Tamanho máximo: 1000 entradas
   - Eviction LRU

2. **Read Model** (Projeções)
   - Views desnormalizadas persistentes
   - Atualizadas assincronamente via eventos

### Invalidação de Cache

Invalidado em eventos de escrita:
```python
# Estoque atualizado
await cache.invalidate(f"stock:{product_id}:{store_id}")
await cache.invalidate(f"product_inventory:{product_id}")
```

## Considerações de Escalabilidade

### Escalabilidade Horizontal

**Camada de API:**
- Stateless
- Pode escalar independentemente
- Balanceamento de carga

**Event Store:**
- Particionado por stream ID
- Append-only (otimizado para escrita)

**Read Models:**
- Pode ter múltiplas projeções
- Cada uma otimizada para consultas específicas

### Escalabilidade Vertical

- I/O assíncrono para alta concorrência
- Connection pooling
- Processamento em lote de eventos

## Observabilidade

### Logging Estruturado

Todos os logs são JSON estruturado:
```json
{
  "timestamp": "2025-10-19T10:00:00Z",
  "level": "INFO",
  "event": "stock_added",
  "product_id": "...",
  "quantity": 100
}
```

### Métricas (Futuro)

- Latência de requisição (p50, p95, p99)
- Taxas de erro
- Taxa de acerto de cache
- Lag de processamento de eventos

### Rastreamento (Futuro)

- Rastreamento distribuído com OpenTelemetry
- IDs de correlação de requisição

## Segurança

### Validação de Entrada

- Modelos Pydantic para todas as entradas
- Validação de UUID
- Verificações de faixa de quantidade

### Tratamento de Erros

- Sem dados sensíveis em erros
- Mensagens de erro genéricas para clientes
- Logs detalhados para depuração

## Justificativa da Stack Tecnológica

| Tecnologia | Justificativa |
|------------|---------------|
| **FastAPI** | Moderno, assíncrono, docs auto-geradas |
| **Pydantic** | Validação em runtime, type safety |
| **SQLite** | Simples, embarcado, bom para protótipo |
| **JSON** | Eventos legíveis por humanos, fácil depuração |
| **structlog** | Logging estruturado, pronto para produção |
| **pytest** | Padrão da indústria, suporte async |

## Melhorias Futuras de Arquitetura

### Melhorias para Produção

1. **Substituir SQLite por PostgreSQL**
   - Melhor concorrência
   - Transações ACID
   - Replicação

2. **Substituir Event Store JSON por PostgreSQL**
   - Appends atômicos
   - Melhor performance de consulta
   - Suporte nativo a UUID

3. **Adicionar Redis para Caching**
   - Cache distribuído
   - Pub/sub para eventos
   - Melhor escalabilidade

4. **Adicionar Kafka para Event Bus**
   - Entrega garantida
   - Capacidade de replay
   - Melhor ordenação

5. **Adicionar Fila de Mensagens (RabbitMQ/SQS)**
   - Processamento assíncrono
   - Melhor resiliência
   - Filas de dead letter

6. **Implementar API Gateway**
   - Rate limiting
   - Autenticação/Autorização
   - Roteamento de requisições

---

Esta arquitetura equilibra simplicidade para demonstração com padrões que escalam para cargas de trabalho de produção.
