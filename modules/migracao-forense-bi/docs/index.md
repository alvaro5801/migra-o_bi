# Documentação - Migração Forense BI

## Visão Geral

O módulo **Migração Forense BI** implementa uma metodologia rigorosa e rastreável para migração de sistemas legados Visual Age para arquiteturas modernas, seguindo o princípio Zero-Trust: **nada é PROVEN sem evidência**.

## Arquitetura do Módulo

### Estrutura de 3 Fases

```
Fase 1: As-Is Forense
├── Extractor-A    → Extração forense de .esf
├── Analyzer-A     → Análise estrutural
└── Validator-A    → Validação de completude

Fase 2: To-Be Arquitetura
├── Architect-B    → Design de arquitetura moderna
├── Mapper-B       → Mapeamento legado → moderno
└── Validator-B    → Validação de viabilidade

Fase 3: Implementação Controlada
├── Generator-C    → Geração de código moderno
├── Tester-C       → Testes e validação
└── Auditor-C      → Auditoria de conformidade
```

## Princípios Fundamentais

### 1. Zero-Trust
**Nada é PROVEN sem evidência rastreável**

Cada afirmação sobre o sistema legado deve ser respaldada por um `EvidencePointer` no formato:
```
arquivo.esf:Lxxxx-Lyyyy
```

### 2. Rastreabilidade Completa
**Do código legado ao código moderno**

Toda transformação deve ser rastreável:
- Código legado → Claims (Fase 1)
- Claims → Design (Fase 2)
- Design → Código moderno (Fase 3)

### 3. Validação Contínua
**Validar em cada etapa**

Cada fase tem validações rigorosas:
- Completude de extração
- Consistência de mapeamento
- Conformidade de implementação

### 4. Output Estruturado
**JSON padronizado e versionado**

Todos os outputs seguem schemas JSON rigorosos:
- `claims_A.json` - Extração (Fase 1)
- `design_B.json` - Arquitetura (Fase 2)
- `implementation_C.json` - Código (Fase 3)

## Fase 1: As-Is Forense

### Objetivo
Extrair e documentar o estado atual do sistema legado com evidências completas.

### Agentes

#### Extractor-A 🔍
**Missão**: Extração Forense Zero-Trust de arquivos Visual Age (.esf)

**Identifica**:
- ✅ Telas (screens)
- ✅ Campos (fields)
- ✅ Queries SQL
- ✅ Lógica de Negócio

**Output**: `run/extraction/claims_A.json`

**Documentação**: [Extractor-A Guide](./agents/extractor-a.md)

#### Analyzer-A 📊
**Missão**: Análise estrutural e de dependências

**Analisa**:
- Dependências entre componentes
- Fluxos de dados
- Complexidade ciclomática
- Pontos de integração

**Output**: `run/analysis/analysis_A.json`

**Documentação**: [Analyzer-A Guide](./agents/analyzer-a.md)

#### Validator-A ✅
**Missão**: Validação de completude e consistência

**Valida**:
- Coverage >= 95%
- Referências válidas
- Evidence pointers corretos
- Consistência de dados

**Output**: `run/validation/validation_A.json`

**Documentação**: [Validator-A Guide](./agents/validator-a.md)

## Fase 2: To-Be Arquitetura

### Objetivo
Projetar arquitetura moderna baseada nas evidências coletadas.

### Agentes

#### Architect-B 🏗️
**Missão**: Design de arquitetura moderna

**Projeta**:
- Arquitetura de microsserviços
- APIs RESTful
- Banco de dados relacional
- Camadas de aplicação

**Output**: `run/architecture/design_B.json`

#### Mapper-B 🗺️
**Missão**: Mapeamento legado → moderno

**Mapeia**:
- Telas → Endpoints API
- Campos → DTOs/Models
- Queries → Repositories
- Lógica → Services

**Output**: `run/mapping/mapping_B.json`

#### Validator-B ✅
**Missão**: Validação de viabilidade técnica

**Valida**:
- Viabilidade de implementação
- Performance esperada
- Segurança
- Escalabilidade

**Output**: `run/validation/validation_B.json`

## Fase 3: Implementação Controlada

### Objetivo
Implementar código moderno com testes e validação contínua.

### Agentes

#### Generator-C 💻
**Missão**: Geração de código moderno

**Gera**:
- Controllers (ASP.NET Core)
- Services (lógica de negócio)
- Repositories (acesso a dados)
- DTOs e Models

**Output**: Código-fonte em `src/`

#### Tester-C 🧪
**Missão**: Testes automatizados e validação

**Testa**:
- Testes unitários
- Testes de integração
- Testes de regressão
- Validação funcional

**Output**: `tests/` + relatórios

#### Auditor-C 📋
**Missão**: Auditoria de conformidade e rastreabilidade

**Audita**:
- Rastreabilidade completa
- Conformidade com design
- Cobertura de testes
- Qualidade de código

**Output**: `run/audit/audit_C.json`

## Formato de Evidence Pointer

### Estrutura
```
arquivo.esf:Lxxxx-Lyyyy
```

### Componentes
- `arquivo.esf` - Nome do arquivo fonte (com extensão)
- `L` - Prefixo literal (uppercase)
- `xxxx` - Linha inicial (4 dígitos com zeros à esquerda)
- `-` - Separador
- `L` - Prefixo literal (uppercase)
- `yyyy` - Linha final (4 dígitos com zeros à esquerda)

### Exemplos Válidos
```
bi14a.esf:L0001-L0001    (linha única)
bi14a.esf:L0123-L0145    (range de linhas)
cb2qa.esf:L1500-L1502    (query SQL)
relatorio.esf:L0500-L0750 (bloco grande)
```

### Validação
```regex
^[a-z0-9_-]+\.esf:L\d{4}-L\d{4}$
```

## Estrutura de Outputs

### run/extraction/
```
run/extraction/
├── claims_A.json           # Claims extraídos (principal)
├── extraction_log.txt      # Log detalhado
├── validation_report.md    # Relatório de validação
└── manifest.json           # Manifest com hashes
```

### run/analysis/
```
run/analysis/
├── analysis_A.json         # Análise estrutural
├── dependencies.json       # Grafo de dependências
├── complexity_report.md    # Relatório de complexidade
└── integration_points.json # Pontos de integração
```

### run/architecture/
```
run/architecture/
├── design_B.json           # Design de arquitetura
├── api_specification.yaml  # OpenAPI spec
├── database_schema.sql     # Schema SQL
└── architecture_diagram.md # Diagrama de arquitetura
```

### run/mapping/
```
run/mapping/
├── mapping_B.json          # Mapeamento completo
├── traceability_matrix.csv # Matriz de rastreabilidade
└── transformation_rules.md # Regras de transformação
```

### run/implementation/
```
run/implementation/
├── implementation_C.json   # Metadados de implementação
├── code_generation_log.txt # Log de geração
└── test_results.xml        # Resultados de testes
```

### run/audit/
```
run/audit/
├── audit_C.json            # Auditoria completa
├── traceability_report.md  # Relatório de rastreabilidade
├── compliance_report.md    # Relatório de conformidade
└── quality_metrics.json    # Métricas de qualidade
```

## Fluxo de Trabalho Completo

### 1. Extração (Fase 1)
```bash
# Extrair arquivo Visual Age
[EXT] Extrair bi14a.esf

# Validar extração
[VAL] Validar extração

# Gerar relatório
[RPT] Relatório de extração
```

### 2. Análise (Fase 1)
```bash
# Analisar estrutura
[ANA] Analisar claims_A.json

# Gerar grafo de dependências
[DEP] Gerar dependências

# Calcular complexidade
[CPX] Calcular complexidade
```

### 3. Arquitetura (Fase 2)
```bash
# Projetar arquitetura
[ARC] Projetar arquitetura moderna

# Mapear componentes
[MAP] Mapear legado → moderno

# Validar viabilidade
[VAL] Validar design
```

### 4. Implementação (Fase 3)
```bash
# Gerar código
[GEN] Gerar código moderno

# Executar testes
[TST] Executar testes

# Auditar conformidade
[AUD] Auditar implementação
```

## Métricas de Qualidade

### Fase 1: Extração
- **Coverage**: >= 98%
- **Evidence Validity**: 100%
- **Referências Válidas**: 100%

### Fase 2: Arquitetura
- **Mapeamento Completo**: >= 95%
- **Viabilidade Técnica**: >= 90%
- **Conformidade com Padrões**: 100%

### Fase 3: Implementação
- **Cobertura de Testes**: >= 80%
- **Rastreabilidade**: 100%
- **Qualidade de Código**: >= 85%

## Guias Rápidos

- [Quick Start](./quick-start.md) - Começar rapidamente
- [Guia de Agentes](./agents/index.md) - Detalhes de cada agente
- [Guia de Workflows](./workflows/index.md) - Fluxos de trabalho
- [Troubleshooting](./troubleshooting.md) - Solução de problemas
- [FAQ](./faq.md) - Perguntas frequentes

## Referências

- [Visual Age Patterns](../knowledge/visual-age-patterns.csv) - Padrões Visual Age
- [Extraction Rules](../knowledge/extraction-rules.csv) - Regras de extração
- [Exemplos](../reference/) - Exemplos práticos

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi

