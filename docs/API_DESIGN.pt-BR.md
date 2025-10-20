# Documento de Design da API

[English version](API_DESIGN.md)

## Princípios de Design

### Design RESTful

A API segue os princípios REST:
- URLs baseadas em recursos
- Verbos HTTP para operações
- Códigos de status padrão
- Comunicação stateless

### Consistência

- Nomenclatura consistente (snake_case para JSON)
- Respostas de erro consistentes
- API versionada (v1)
- Paginação consistente (futuro)

### Performance

- Cache agressivo para leituras
- Operações assíncronas
- Serialização eficiente (Pydantic)
- Connection pooling

## Categorias de Endpoints

### Comandos (Operações de Escrita)

Comandos modificam o estado do sistema e **NÃO** são idempotentes por design (exceto com chaves de idempotência).

#### POST /api/v1/inventory/stock

Adicionar estoque ao inventário.

**Requisição:**
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": 100,
  "reason": "reabastecimento"
}
```

**Resposta (201 Created):**
```json
{
  "inventory_id": "uuid",
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": 100,
  "reserved": 0,
  "available": 100,
  "version": 1
}
```

**Erros:**
- 400: Entrada inválida
- 409: Conflito de concorrência

---

#### POST /api/v1/inventory/reserve

Reservar estoque (soft lock).

**Requisição:**
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": 5,
  "customer_id": "uuid"
}
```

**Resposta (201 Created):**
```json
{
  "reservation_id": "uuid",
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": 5,
  "reserved_total": 5,
  "available": 95,
  "version": 2
}
```

**Erros:**
- 400: Entrada inválida
- 409: Estoque insuficiente ou conflito de concorrência

---

#### POST /api/v1/inventory/commit

Confirmar reserva (finalizar venda).

**Requisição:**
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "reservation_id": "uuid",
  "order_id": "uuid"
}
```

**Resposta (200 OK):**
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": 95,
  "reserved": 0,
  "available": 95,
  "version": 3
}
```

**Erros:**
- 404: Reserva não encontrada
- 409: Conflito de concorrência

---

#### POST /api/v1/inventory/release

Liberar reserva (cancelar).

**Requisição:**
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "reservation_id": "uuid",
  "reason": "cliente_cancelou"
}
```

**Resposta (200 OK):**
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "reserved_total": 0,
  "available": 100,
  "version": 3
}
```

---

### Consultas (Operações de Leitura)

Consultas são **idempotentes** e **cacheáveis**.

#### GET /api/v1/inventory/products/{product_id}/stores/{store_id}

Obter estoque para produto e loja específicos.

**Resposta (200 OK):**
```json
{
  "inventory_id": "uuid",
  "product_id": "uuid",
  "store_id": "uuid",
  "quantity": 100,
  "reserved": 5,
  "available": 95,
  "version": 5
}
```

**Cache:** TTL de 30 segundos

---

#### POST /api/v1/inventory/availability

Verificar se há estoque suficiente disponível.

**Requisição:**
```json
{
  "product_id": "uuid",
  "store_id": "uuid",
  "required_quantity": 10
}
```

**Resposta (200 OK):**
```json
{
  "available": true,
  "sufficient": true,
  "current_stock": 95,
  "required_quantity": 10,
  "product_id": "uuid",
  "store_id": "uuid"
}
```

**Cache:** TTL de 30 segundos

---

#### GET /api/v1/inventory/products/{product_id}

Obter inventário em todas as lojas para um produto.

**Resposta (200 OK):**
```json
[
  {
    "inventory_id": "uuid",
    "product_id": "uuid",
    "store_id": "uuid-1",
    "quantity": 100,
    "reserved": 5,
    "available": 95
  },
  {
    "inventory_id": "uuid",
    "product_id": "uuid",
    "store_id": "uuid-2",
    "quantity": 50,
    "reserved": 0,
    "available": 50
  }
]
```

---

### Saúde e Observabilidade

#### GET /api/v1/health

Verificação básica de saúde.

**Resposta (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

---

#### GET /api/v1/health/detailed

Verificação detalhada de saúde com componentes.

**Resposta (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "components": {
    "cache": {
      "status": "healthy",
      "stats": {
        "size": 42,
        "max_size": 1000
      }
    },
    "event_bus": {
      "status": "healthy",
      "handlers_count": 4
    }
  }
}
```

## Respostas de Erro

Todos os erros seguem formato consistente:

```json
{
  "code": "CODIGO_ERRO",
  "message": "Mensagem legível por humanos",
  "details": {
    "field": "contexto adicional"
  }
}
```

### Códigos de Erro

| Código | Status HTTP | Descrição |
|--------|-------------|-----------|
| INVALID_STOCK_QUANTITY | 400 | Validação de quantidade falhou |
| INSUFFICIENT_STOCK | 409 | Estoque insuficiente para operação |
| CONCURRENCY_CONFLICT | 409 | Incompatibilidade de versão (tentar novamente) |
| RESERVATION_NOT_FOUND | 404 | Reserva não existe |
| PRODUCT_NOT_FOUND | 404 | Produto não existe |
| INTERNAL_ERROR | 500 | Erro inesperado do servidor |

## Paginação (Futuro)

Para endpoints de lista:

**Requisição:**
```
GET /api/v1/inventory?limit=20&offset=0
```

**Resposta:**
```json
{
  "items": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

## Rate Limiting (Futuro)

Headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1634567890
```

## Versionamento

- Atual: v1
- Baseado em URL: `/api/v1/...`
- Mudanças breaking requerem nova versão
- Política de depreciação: aviso de 6 meses

## Negociação de Conteúdo

Suporta:
- `application/json` (padrão)
- Futuro: `application/xml`, `application/msgpack`

## CORS

Configurado para:
- Desenvolvimento: Permitir todas origens
- Produção: Whitelist de origens específicas

## Autenticação (Futuro)

```
Authorization: Bearer <jwt_token>
```

## Boas Práticas Implementadas

1. ✅ Convenções de nomenclatura consistentes
2. ✅ Códigos de status HTTP apropriados
3. ✅ Tratamento abrangente de erros
4. ✅ Validação de requisição (Pydantic)
5. ✅ Schemas de resposta
6. ✅ Documentação da API (OpenAPI)
7. ✅ Endpoints de health check
8. ✅ Logging estruturado
9. ✅ Headers de cache
10. ✅ Operações assíncronas

---

Este design de API equilibra princípios REST com considerações práticas de performance para um sistema de inventário distribuído.
