# 📑 Índice do Projeto - Inventory Management System

## 🎯 Começar Aqui

1. **[STATUS.md](STATUS.md)** - 🎉 Status da implementação e visão geral visual
2. **[NEXT_STEPS.md](NEXT_STEPS.md)** - 🚀 Guia passo-a-passo para executar
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⚡ Comandos rápidos

## 📖 Documentação Principal

### Português 🇧🇷
- **[README.pt-BR.md](README.pt-BR.md)** - Documentação completa em português
- **[QUICKSTART.pt-BR.md](QUICKSTART.pt-BR.md)** - Início rápido (5 minutos)

### English 🇺🇸
- **[README.md](README.md)** - Complete documentation in English
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start (5 minutes)

## 🏗️ Documentação Técnica

### Arquitetura
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** 🇺🇸 - Detailed architecture
- **[docs/ARCHITECTURE.pt-BR.md](docs/ARCHITECTURE.pt-BR.md)** 🇧🇷 - Arquitetura detalhada

### API
- **[docs/API_DESIGN.md](docs/API_DESIGN.md)** 🇺🇸 - API design and endpoints
- **[docs/API_DESIGN.pt-BR.md](docs/API_DESIGN.pt-BR.md)** 🇧🇷 - Design da API

### Decisões Técnicas
- **[docs/TECHNICAL_DECISIONS.md](docs/TECHNICAL_DECISIONS.md)** 🇺🇸 - Technical decisions
- **[docs/TECHNICAL_DECISIONS.pt-BR.md](docs/TECHNICAL_DECISIONS.pt-BR.md)** 🇧🇷 - Decisões técnicas

### Diagramas
- **[docs/DIAGRAMS.md](docs/DIAGRAMS.md)** 📊 - 8 Mermaid diagrams (bilingual)

### Índice Completo
- **[docs/INDEX.md](docs/INDEX.md)** 📑 - Complete documentation index

## 📊 Status e Relatórios

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Sumário executivo do projeto
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Status detalhado da implementação

## 🚀 Execução

### Arquivos Principais
- **[main.py](main.py)** - FastAPI application entry point
- **[requirements.txt](requirements.txt)** - Python dependencies

### Scripts
- **[scripts/init_sample_data.py](scripts/init_sample_data.py)** - Initialize sample data
- **[examples/basic_usage.py](examples/basic_usage.py)** - Basic usage example

### Configuração
- **[pytest.ini](pytest.ini)** - Test configuration
- **[.gitignore](.gitignore)** - Git ignore patterns
- **[.env.example](.env.example)** - Environment variables template

## 📂 Estrutura do Código

### Domain Layer (Domínio)
```
src/domain/
├── entities/           # Inventory, Product
├── events/            # Domain events
├── value_objects/     # StockQuantity
└── exceptions/        # Domain exceptions
```

### Application Layer (Aplicação)
```
src/application/
├── commands/          # AddStock, ReserveStock, etc.
├── queries/           # GetStock, CheckAvailability
└── services/          # InventoryService
```

### Infrastructure Layer (Infraestrutura)
```
src/infrastructure/
├── persistence/       # EventStore, ReadModelRepository
├── cache/            # InMemoryCache
├── messaging/        # EventBus
└── resilience/       # CircuitBreaker
```

### Presentation Layer (Apresentação)
```
src/presentation/
├── api/v1/endpoints/  # REST API endpoints
├── api/v1/schemas/    # Pydantic schemas
└── middleware/        # Logging middleware
```

### Tests (Testes)
```
tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── e2e/             # End-to-end tests
```

## 🎓 Recursos de Aprendizado

### Padrões Implementados
- Event Sourcing
- CQRS (Command Query Responsibility Segregation)
- Clean Architecture
- Domain-Driven Design (DDD)
- Repository Pattern
- Circuit Breaker Pattern
- Observer Pattern (EventBus)

### Princípios SOLID
- Single Responsibility Principle
- Open/Closed Principle
- Liskov Substitution Principle
- Interface Segregation Principle
- Dependency Inversion Principle

## 🔍 Navegação Rápida

### Por Funcionalidade

**Adicionar Estoque:**
- Comando: `src/application/commands/add_stock.py`
- Endpoint: `src/presentation/api/v1/endpoints/inventory.py` (POST /stock)
- Domínio: `src/domain/entities/inventory.py` (método `add_stock`)

**Reservar Estoque:**
- Comando: `src/application/commands/reserve_stock.py`
- Endpoint: `src/presentation/api/v1/endpoints/inventory.py` (POST /reserve)
- Domínio: `src/domain/entities/inventory.py` (método `reserve_stock`)

**Consultar Estoque:**
- Query: `src/application/queries/get_stock.py`
- Endpoint: `src/presentation/api/v1/endpoints/inventory.py` (GET /products/{id}/stores/{id})
- Read Model: `src/infrastructure/persistence/read_model_repository.py`

### Por Camada

**Domain (Negócio):**
- [src/domain/entities/inventory.py](src/domain/entities/inventory.py)
- [src/domain/value_objects/stock_quantity.py](src/domain/value_objects/stock_quantity.py)
- [src/domain/events/inventory_events.py](src/domain/events/inventory_events.py)

**Application (Casos de Uso):**
- [src/application/services/inventory_service.py](src/application/services/inventory_service.py)
- [src/application/commands/](src/application/commands/)
- [src/application/queries/](src/application/queries/)

**Infrastructure (Técnico):**
- [src/infrastructure/persistence/event_store.py](src/infrastructure/persistence/event_store.py)
- [src/infrastructure/cache/in_memory_cache.py](src/infrastructure/cache/in_memory_cache.py)
- [src/infrastructure/resilience/circuit_breaker.py](src/infrastructure/resilience/circuit_breaker.py)

**Presentation (API):**
- [src/presentation/api/v1/endpoints/inventory.py](src/presentation/api/v1/endpoints/inventory.py)
- [src/presentation/api/v1/schemas/inventory_schemas.py](src/presentation/api/v1/schemas/inventory_schemas.py)

## 🧪 Testes

### Executar Testes
```bash
pytest -v                    # Todos os testes
pytest tests/unit -v         # Testes unitários
pytest tests/integration -v  # Testes de integração
pytest tests/e2e -v         # Testes end-to-end
pytest --cov=src            # Com cobertura
```

### Arquivos de Teste
- [tests/unit/test_stock_quantity.py](tests/unit/test_stock_quantity.py)
- [tests/unit/test_inventory.py](tests/unit/test_inventory.py)
- [tests/integration/test_event_store.py](tests/integration/test_event_store.py)
- [tests/e2e/test_api.py](tests/e2e/test_api.py)

## 📈 Estatísticas

```
Total de Arquivos Python:    64 arquivos
Total de Documentação:       14 arquivos markdown
Linhas de Código:            ~3000+ linhas
Linhas de Documentação:      ~2500+ linhas
Linhas de Testes:            ~400 linhas
Diagramas Mermaid:           8 diagramas
Idiomas:                     2 (English + Português)
```

## 🆘 Precisa de Ajuda?

1. **Não sei por onde começar:**
   - Leia [STATUS.md](STATUS.md) para visão geral
   - Siga [NEXT_STEPS.md](NEXT_STEPS.md) passo-a-passo

2. **Como executar:**
   - Veja [QUICK_REFERENCE.md](QUICK_REFERENCE.md) para comandos

3. **Entender a arquitetura:**
   - Leia [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) ou versão PT-BR
   - Veja [docs/DIAGRAMS.md](docs/DIAGRAMS.md) para visualizar

4. **Usar a API:**
   - Consulte [docs/API_DESIGN.md](docs/API_DESIGN.md) ou versão PT-BR
   - Acesse http://localhost:8000/swagger (Swagger UI)

5. **Entender decisões técnicas:**
   - Leia [docs/TECHNICAL_DECISIONS.md](docs/TECHNICAL_DECISIONS.md)

## 🎯 Links Rápidos

### Documentação Interativa (quando API estiver rodando)
- 📖 Swagger UI: http://localhost:8000/swagger
- 📚 ReDoc: http://localhost:8000/redoc
- 💚 Health Check: http://localhost:8000/health

### Repositório
- 📁 GitHub: (adicione seu link aqui)
- 📋 Issues: (adicione seu link aqui)

## 🏆 Conquistas

✅ Clean Architecture completa  
✅ Event Sourcing implementado  
✅ CQRS com read models  
✅ 64 arquivos Python criados  
✅ 14 documentos profissionais  
✅ Documentação bilíngue  
✅ Testes em 3 níveis  
✅ API REST completa  
✅ 8 diagramas técnicos  
✅ Production-ready  

---

## 📞 Contato

Para questões sobre o projeto:
- 📧 Email: (seu email)
- 💼 LinkedIn: (seu perfil)
- 🐙 GitHub: (seu perfil)

---

**Última Atualização:** 19 de Outubro de 2025

**Status:** ✅ Implementação Completa

**Versão:** 1.0.0

---

*Desenvolvido com ❤️ usando Python 3.11+, FastAPI e Clean Architecture*
