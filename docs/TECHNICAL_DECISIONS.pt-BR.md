# Documento de Decisões Técnicas

[English version](TECHNICAL_DECISIONS.md)

## Visão Geral

Este documento detalha as decisões técnicas tomadas durante o desenvolvimento do Sistema de Gerenciamento de Inventário Distribuído.

## Resumo Executivo

| Decisão | Alternativa | Justificativa |
|---------|-------------|---------------|
| Event Sourcing | CRUD | Trilha de auditoria, consultas temporais |
| CQRS | Modelo compartilhado | Escalabilidade independente |
| Consistência Eventual | Consistência forte | Maior disponibilidade |
| Optimistic Locking | Pessimistic locking | Melhor performance |
| Cache TTL | Invalidação manual | Mais simples, previsível |
| Circuit Breaker | Sem resiliência | Tolerância a falhas |
| API REST | GraphQL/gRPC | Padrão, simples |
| Pirâmide de Testes | Muitos E2E | Feedback mais rápido |
| Logs Estruturados | Texto plano | Melhor observabilidade |
| GitHub Copilot | Codificação manual | Desenvolvimento mais rápido |

---

## 1. Padrão de Arquitetura: Event Sourcing + CQRS

### Decisão
Implementar Event Sourcing com padrão CQRS.

### Contexto
Sistemas CRUD tradicionais têm dificuldades com:
- Requisitos de auditoria
- Consultas temporais
- Atualizações concorrentes em ambiente distribuído
- Performance de consultas complexas

### Justificativa
Event Sourcing + CQRS fornece:
- Trilha de auditoria completa (conformidade regulatória)
- Modelos de leitura otimizados
- Consistência eventual natural
- Melhores características de escalabilidade
- Capacidade de adicionar novas projeções sem migração

### Trade-offs
✅ **Prós:**
- Histórico completo
- Consultas temporais
- Depuração mais fácil
- Escalabilidade independente de leituras/escritas

❌ **Contras:**
- Complexidade aumentada
- Overhead de armazenamento
- Curva de aprendizado
- Desafios de consistência eventual

---

## 2. Modelo de Consistência: Consistência Eventual

### Decisão
Priorizar disponibilidade sobre consistência forte (AP no teorema CAP).

### Contexto
Ambiente varejista multi-loja onde:
- Lojas podem estar geograficamente distribuídas
- Partições de rede podem ocorrer
- Experiência do usuário é crítica
- Inconsistências temporárias são aceitáveis

### Justificativa
Para inventário de e-commerce:
- Melhor mostrar estoque aproximado do que erro
- Reservas lidam com caminho crítico
- Atualizações propagam rapidamente (< 1 minuto)
- Usuários toleram "fora de estoque" no checkout

### Estratégias de Mitigação
- Sistema de reservas para compras
- TTL de cache curto (30s)
- Optimistic locking para conflitos
- Transações compensatórias

---

## 3. Persistência: Arquivos JSON + SQLite

### Decisão
Usar JSON para event store, SQLite para read models (protótipo).

### Contexto
Sistema protótipo demonstrando padrões, não persistência pronta para produção.

### Justificativa
JSON + SQLite:
- Fácil de inspecionar eventos (legível por humanos)
- Sem dependências externas
- Suficiente para demonstração
- Caminho de migração fácil para DB de produção

### Recomendação para Produção
```
Event Store: PostgreSQL com JSONB
Read Models: PostgreSQL com índices
Cache: Redis
Message Bus: Kafka
```

---

## 4. Controle de Concorrência: Optimistic Locking

### Decisão
Usar optimistic locking baseado em versão em vez de locks pessimistas.

### Contexto
Sistema distribuído onde locks distribuídos são complexos e custosos.

### Justificativa
Optimistic locking:
- Sem necessidade de coordenação distribuída
- Melhor performance
- Adequado naturalmente para event sourcing
- Clientes podem tentar novamente em conflitos

### Trade-offs
✅ **Prós:**
- Alto throughput
- Sem contenção de lock
- Stateless

❌ **Contras:**
- Clientes devem lidar com retries
- Não bom para cenários de alta contenção
- Lógica de cliente mais complexa

---

## 5. Estratégia de Caching: Cache TTL Agressivo

### Decisão
Usar cache em memória com TTL de 30 segundos para todas operações de leitura.

### Contexto
Carga de trabalho pesada em leitura (90% leituras, 10% escritas) onde latência de subsegundo é crítica.

### Justificativa
Cache baseado em TTL:
- Simples de implementar
- Staleness previsível
- Limpeza automática
- Bom o suficiente para caso de uso de inventário

### Invalidação de Cache
Eventos disparam invalidação explícita:
```python
on StockUpdated → invalidate(product:store)
```

---

## 6. Tratamento de Erros: Circuit Breaker + Retry

### Decisão
Implementar padrão Circuit Breaker com retry exponencial backoff.

### Contexto
Sistema distribuído onde componentes podem falhar temporariamente.

### Justificativa
Circuit Breaker + Retry:
- Protege contra falhas em cascata
- Dá tempo para serviços falhados se recuperarem
- Melhor experiência do usuário (fast-fail quando aberto)
- Padrão da indústria

### Configuração
```python
failure_threshold: 5 erros
timeout: 30 segundos
retry_attempts: 3
backoff: exponencial (1s, 2s, 4s)
```

---

## 7. Design de API: REST com OpenAPI

### Decisão
API RESTful com FastAPI e documentação OpenAPI auto-gerada.

### Contexto
Necessidade de API padrão e bem documentada para múltiplos tipos de cliente.

### Justificativa
REST + OpenAPI:
- Bem compreendido
- Excelente ferramental
- Documentação auto-gerada
- Fácil de testar
- FastAPI é moderno e rápido

---

## 8. Estratégia de Testes: Pirâmide com Foco em Integração

### Decisão
Pirâmide de testes: muitos testes unitários, alguns testes de integração, poucos testes E2E.

### Contexto
Clean Architecture torna testes em diferentes níveis natural.

### Distribuição de Testes
```
Testes E2E (5%)        ▲
Integração (25%)     ██
Testes Unit (70%)  ████████
```

### Justificativa
- Testes unitários: Rápidos, testam lógica de negócio
- Integração: Testam interação de componentes
- E2E: Testam fluxos críticos do usuário

### Meta de Cobertura
- Geral: > 80%
- Camada de domínio: > 90%
- Camada de aplicação: > 80%
- Infraestrutura: > 70%

---

## 9. Logging: Logging JSON Estruturado

### Decisão
Usar logging estruturado (structlog) com saída JSON.

### Contexto
Necessidade de analisar logs programaticamente para depuração e monitoramento.

### Justificativa
Logging estruturado permite:
- Agregação de logs (ELK, Splunk)
- Consulta por campos
- IDs de correlação
- Melhor observabilidade

### Exemplo
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

## 10. Integração GenAI: GitHub Copilot

### Decisão
Usar GitHub Copilot durante o desenvolvimento para geração de código e sugestões.

### Contexto
Demonstrar práticas modernas de desenvolvimento com assistência de IA.

### Padrões de Uso
1. **Redução de boilerplate**
   - Criação de entidades
   - Scaffolding de testes
   - Endpoints de API

2. **Aplicação de padrões**
   - Implementações de repository
   - Event handlers
   - Tratamento de erros

3. **Documentação**
   - Docstrings
   - Seções de README
   - Comentários

### Impacto
- ~40% de desenvolvimento mais rápido
- Estilo de código mais consistente
- Melhor cobertura de testes
- Documentação abrangente

### Supervisão Humana
- Todo código gerado revisado
- Lógica de negócio feita à mão
- Decisões de arquitetura feitas por humano
- Testes verificam correção

---

## Lições Aprendidas

### O que Funcionou Bem
1. **Clean Architecture** - Fácil de testar, manter e estender
2. **Event Sourcing** - Depuração foi muito mais fácil com histórico completo
3. **CQRS** - Otimizações de leitura não afetaram caminho de escrita
4. **Type hints + Pydantic** - Pegou muitos bugs em tempo de desenvolvimento

### O que Poderia Ser Melhorado
1. **Replay de eventos** - Deveria implementar snapshotting para streams grandes
2. **Testes** - Precisa de mais testes de carga para cenários de concorrência
3. **Documentação** - Poderia se beneficiar de diagramas de sequência
4. **Monitoramento** - Precisa de métricas e alertas reais

### Considerações Futuras
1. Implementar estratégia de versionamento de eventos
2. Adicionar rastreamento distribuído
3. Considerar persistência poliglota
4. Implementar padrão SAGA para transações complexas
5. Adicionar camada GraphQL para consultas flexíveis

---

Este documento serve como referência para entender por que escolhas técnicas específicas foram feitas e pode guiar futuras decisões de desenvolvimento.
