# Sistema de Gerenciamento de Inventário Distribuído

Um sistema de gerenciamento de inventário distribuído de alta performance, construído com Event Sourcing, CQRS e seguindo os princípios de Clean Architecture.

## 🏗️ Visão Geral da Arquitetura

Este sistema implementa uma arquitetura distribuída moderna para resolver problemas de consistência e latência de inventário em um ambiente varejista multi-loja.

### Funcionalidades Principais

- ✅ **Event Sourcing** - Trilha de auditoria completa e consultas temporais
- ✅ **Padrão CQRS** - Operações de leitura e escrita otimizadas
- ✅ **Clean Architecture** - Separação de responsabilidades e manutenibilidade
- ✅ **Circuit Breaker** - Tolerância a falhas e degradação graciosa
- ✅ **Cache em Memória** - Performance de consulta em subsegundos

## 📊 Diagrama de Arquitetura

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

## 🚀 Começando

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a aplicação:
```bash
python main.py
```

A API estará disponível em `http://localhost:8000`

## 🧪 Testes

Execute todos os testes:
```bash
pytest
```

Execute tipos específicos de teste:
```bash
# Testes unitários
pytest tests/unit -v

# Testes de integração
pytest tests/integration -v

# Testes E2E
pytest tests/e2e -v
```

Execute com cobertura:
```bash
pytest --cov=src --cov-report=html
```

## 📚 Documentação da API

A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/swagger`
- ReDoc: `http://localhost:8000/redoc`

## 🏛️ Detalhes da Arquitetura

### Camada de Domínio
- **Entidades**: `Inventory`, `Product`
- **Objetos de Valor**: `StockQuantity`
- **Eventos**: Eventos de domínio para todas as mudanças de estado
- **Exceções**: Exceções específicas do domínio

### Camada de Aplicação
- **Comandos**: Operações de escrita (AddStock, ReserveStock, etc.)
- **Consultas**: Operações de leitura (GetStock, CheckAvailability, etc.)
- **Serviços**: Orquestração de casos de uso

### Camada de Infraestrutura
- **Event Store**: Persistência de eventos baseada em JSON
- **Read Model**: Projeções otimizadas para consultas
- **Event Bus**: Pub/sub em memória
- **Cache**: Cache em memória baseado em TTL
- **Circuit Breaker**: Mecanismo de tolerância a falhas

### Camada de Apresentação
- **API**: Endpoints REST com FastAPI
- **Middleware**: Logging, tratamento de erros
- **Schemas**: Validação de requisição/resposta

## 🔧 Decisões de Design

### Por que Event Sourcing?
- Trilha de auditoria completa para conformidade regulatória
- Capacidade de reconstruir estado a partir de eventos
- Consultas temporais (estado em qualquer ponto no tempo)
- Adequado naturalmente para sistemas distribuídos

### Por que CQRS?
- Modelos de leitura otimizados com desnormalização
- Escalabilidade independente de leituras e escritas
- Diferentes requisitos de consistência por lado
- Melhor utilização de cache

### Por que Consistência Eventual?
- Maior disponibilidade (teorema CAP)
- Melhor performance para lojas distribuídas
- Aceitável para casos de uso de inventário
- Pode mostrar estoque "aproximado" sem downtime do sistema

### Trade-offs

| Decisão | Benefício | Custo |
|---------|-----------|-------|
| Event Sourcing | Trilha de auditoria, consultas temporais | Overhead de armazenamento, complexidade |
| Consistência Eventual | Alta disponibilidade | Inconsistências temporárias possíveis |
| Cache em memória | Leituras muito rápidas | Uso de memória, invalidação de cache |
| Optimistic locking | Sem locks distribuídos | Overhead de retry em conflitos |

## 🔐 Considerações de Segurança

- Validação de entrada com Pydantic
- Identificadores baseados em UUID (sem IDs sequenciais)
- Configuração CORS
- Logging estruturado (sem dados sensíveis)

## 🚧 Melhorias Futuras

- [ ] Rastreamento distribuído (OpenTelemetry)
- [ ] Exportação de métricas (Prometheus)
- [ ] Banco de dados real (Mysql)
- [ ] Redis para cache distribuído
- [ ] Kafka para event bus
- [ ] API GraphQL
- [ ] Webhooks para notificações de eventos

## 📝 Ferramentas de Desenvolvimento Utilizadas

- **IDE**: Visual Studio Code com extensões Python
- **Testes**: pytest
- **Documentação**: OpenAPI/Swagger
- **GenAI**: GitHub Copilot para geração de código e sugestões