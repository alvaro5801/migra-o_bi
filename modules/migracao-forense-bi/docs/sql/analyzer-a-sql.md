# 🗄️ Analyzer-A-SQL - Especialista em Migração de Persistência

## Índice Completo

Este documento serve como índice central para toda a documentação do **Analyzer-A-SQL**, o especialista dedicado em migração de persistência SQL.

---

## 📋 Visão Geral

**Nome**: Analyzer-A-SQL  
**Ícone**: 🗄️  
**Papel**: Arquiteto de Dados e Especialista em Migração de Persistência  
**Foco**: SQL Server + Entity Framework Core  
**Versão**: 1.0  
**Status**: ✅ Implementado

---

## 📁 Estrutura de Arquivos

### Configuração Principal
- **[analyzer-a-sql.agent.yaml](../agents/analyzer-a/analyzer-a-sql.agent.yaml)** (~350 linhas)
  - Configuração completa do agente
  - Persona, comandos, tools, gate requirements
  - Especificações de input/output
  - Convenções de nomenclatura
  - Best practices SQL Server

### Instruções Detalhadas
- **[instructions.md](../agents/analyzer-a/analyzer-a-sql/instructions.md)** (~800 linhas)
  - Missão principal
  - Bloqueio de SQL-Gate
  - Comandos disponíveis ([DDL-GEN], [LINEAGE], [ANA-SQL])
  - Mapeamento de tipos COBOL → SQL Server
  - Entity Framework Core mapping
  - Best practices SQL Server
  - Exemplos de DDL gerado
  - Troubleshooting

### Workflows
- **[generate-ddl.md](../agents/analyzer-a/analyzer-a-sql/workflows/generate-ddl.md)**
  - Workflow completo para geração de DDL
  - CREATE TABLE, FOREIGN KEY, INDEX, VIEW, STORED PROCEDURE
  - Funções auxiliares
  - Validação

- **[map-lineage.md](../agents/analyzer-a/analyzer-a-sql/workflows/map-lineage.md)**
  - Workflow completo para mapeamento de linhagem
  - Cálculo de riscos
  - Análise upstream/downstream
  - Identificação de tabelas de alto risco

- **[analyze-sql.md](../agents/analyzer-a/analyzer-a-sql/workflows/analyze-sql.md)**
  - Workflow completo para análise SQL
  - Execução de DDL-GEN + LINEAGE
  - Geração de matriz de complexidade
  - Mapeamento Entity Framework Core
  - Relatório consolidado

### Documentação Complementar
- **[DELEGACAO_SQL.md](../agents/analyzer-a/DELEGACAO_SQL.md)** (~300 linhas)
  - Arquitetura de especialização
  - Divisão de responsabilidades (Analyzer-A vs Analyzer-A-SQL)
  - Fluxo de delegação
  - Protocolo de delegação
  - Exemplos de uso
  - Benefícios da especialização

- **[ANALYZER_A_SQL_IMPLEMENTADO.md](../ANALYZER_A_SQL_IMPLEMENTADO.md)**
  - Status da implementação
  - Estatísticas
  - Checklist de validação
  - Como usar
  - Próximos passos

---

## 🎯 Comandos Disponíveis

### [DDL-GEN] - Gerar DDL Moderno

**Missão**: Gerar `run/sql/analysis/database_schema.sql`

**Funcionalidades**:
- ✅ CREATE TABLE com tipos SQL Server modernos
- ✅ PRIMARY KEY com IDENTITY
- ✅ FOREIGN KEY com ON DELETE/UPDATE
- ✅ Índices para FKs e WHERE columns
- ✅ Constraints (CHECK, DEFAULT, UNIQUE)
- ✅ Colunas de auditoria (CreatedAt, UpdatedAt, IsDeleted)
- ✅ Views para queries recorrentes
- ✅ Stored Procedures para lógica complexa
- ✅ Comentários de documentação

**Workflow**: [generate-ddl.md](../agents/analyzer-a/analyzer-a-sql/workflows/generate-ddl.md)

---

### [LINEAGE] - Mapear Linhagem

**Missão**: Gerar `run/sql/analysis/data_lineage.csv`

**Funcionalidades**:
- ✅ Agrupar queries por tabela
- ✅ Mapear operações (READ/CREATE/UPDATE/DELETE)
- ✅ Rastrear lógica → query → tabela
- ✅ Calcular riscos (HIGH/MEDIUM/LOW)
- ✅ Identificar dependências upstream/downstream

**Workflow**: [map-lineage.md](../agents/analyzer-a/analyzer-a-sql/workflows/map-lineage.md)

---

### [ANA-SQL] - Análise Completa

**Missão**: Executar análise completa SQL

**Funcionalidades**:
- ✅ Verificar SQL-Gate PASS
- ✅ Executar [DDL-GEN]
- ✅ Executar [LINEAGE]
- ✅ Gerar `complexity_matrix_sql.csv`
- ✅ Gerar `ef_core_mapping.json`
- ✅ Gerar relatório consolidado

**Workflow**: [analyze-sql.md](../agents/analyzer-a/analyzer-a-sql/workflows/analyze-sql.md)

---

## 📊 Outputs Gerados

### 1. database_schema.sql
**Localização**: `run/sql/analysis/database_schema.sql`

**Conteúdo**:
- CREATE TABLE statements
- PRIMARY KEY com IDENTITY
- FOREIGN KEY com ON DELETE/UPDATE
- Índices (PRIMARY, FOREIGN, WHERE columns)
- Constraints (CHECK, DEFAULT, UNIQUE)
- Colunas de auditoria
- Views para queries recorrentes
- Stored Procedures
- Comentários de documentação

**Exemplo**:
```sql
CREATE TABLE Banco (
    Id INT PRIMARY KEY IDENTITY(1,1),
    CodigoBanco NVARCHAR(10) NOT NULL,
    NomeBanco NVARCHAR(100) NOT NULL,
    Ativo BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NULL,
    IsDeleted BIT NOT NULL DEFAULT 0,
    CONSTRAINT UQ_Banco_CodigoBanco UNIQUE (CodigoBanco)
);
```

---

### 2. data_lineage.csv
**Localização**: `run/sql/analysis/data_lineage.csv`

**Colunas**:
- `table_name`: Nome da tabela
- `operation_type`: Tipo de operação (READ/CREATE/UPDATE/DELETE)
- `query_id`: ID da query
- `evidence_pointer`: Ponteiro para o código fonte
- `business_logic_id`: ID da lógica de negócio
- `screen_id`: ID da tela
- `risk_level`: Nível de risco (HIGH/MEDIUM/LOW)
- `notes`: Notas explicativas

**Exemplo**:
```csv
table_name,operation_type,query_id,evidence_pointer,business_logic_id,screen_id,risk_level,notes
Banco,READ,QRY-SQL-001,bi14a.esf:L0500-L0503,LOG-005,SCR-001,LOW,"Query simples"
Banco,DELETE,QRY-SQL-021,bi14a.esf:L2100-L2105,NONE,SCR-005,HIGH,"DELETE sem WHERE - risco mass delete"
```

---

### 3. complexity_matrix_sql.csv
**Localização**: `run/sql/analysis/complexity_matrix_sql.csv`

**Colunas**:
- `query_id`: ID da query
- `query_type`: Tipo de query (STATIC/DYNAMIC/CURSOR)
- `complexity_score`: Score de complexidade
- `risk_level`: Nível de risco
- `tables_count`: Quantidade de tabelas
- `joins_count`: Quantidade de JOINs
- `subqueries_count`: Quantidade de subqueries
- `dynamic_sql`: Se é SQL dinâmico
- `notes`: Notas explicativas

---

### 4. ef_core_mapping.json
**Localização**: `run/sql/analysis/ef_core_mapping.json`

**Estrutura**:
```json
{
  "entities": [
    {
      "entity_name": "Banco",
      "table_name": "Banco",
      "properties": [...],
      "navigation_properties": [...],
      "indexes": [...],
      "constraints": [...]
    }
  ],
  "dbcontext": {
    "name": "ApplicationDbContext",
    "dbsets": [...]
  },
  "configurations": [...]
}
```

---

### 5. sql_analysis_report.md
**Localização**: `run/sql/analysis/sql_analysis_report.md`

**Seções**:
- Sumário Executivo
- DDL Gerado
- Linhagem de Dados
- Riscos Identificados
- Complexidade SQL
- Entity Framework Core
- Próximos Passos
- Arquivos Gerados

---

## 🔐 Bloqueio de SQL-Gate

O Analyzer-A-SQL **só executa** se o SQL-Gate estiver **PASS**.

### Verificação

**Arquivo**: `run/sql/validation/gate_status_sql.json`

**Conteúdo Obrigatório**:
```json
{
  "sql_gate_status": "PASS"
}
```

### Comportamento de Bloqueio

Se `sql_gate_status != "PASS"`:
- ❌ Análise é **bloqueada**
- ❌ Nenhum output é gerado
- ❌ Mensagem de bloqueio é exibida

**Mensagem de Bloqueio**:
```
❌ BLOQUEIO: SQL-Gate não está PASS

O Analyzer-A-SQL só pode executar após validação SQL bem-sucedida.

Status atual: FAIL ou não encontrado
Conformidade SQL: XX.X%

AÇÃO REQUERIDA:
1. Executar [EXT-SQL] para extrair SQL
2. Executar [VAL-SQL] para validar
3. Corrigir erros até SQL-Gate = PASS
4. Retornar para [DDL-GEN] ou [LINEAGE]

STATUS: ANÁLISE SQL BLOQUEADA
```

---

## 🔄 Delegação SQL

O **Analyzer-A** (geral) delega tarefas SQL para o **Analyzer-A-SQL** (especialista).

### Divisão de Responsabilidades

| Aspecto | Analyzer-A (Geral) | Analyzer-A-SQL (Especialista) |
|---------|-------------------|-------------------------------|
| **Foco** | Estrutura geral | Persistência |
| **Análise** | Lógica, UI, dependências | SQL, DDL, linhagem |
| **Outputs** | taint_report.md, dependency_graph.json | database_schema.sql, data_lineage.csv |
| **Comandos** | [ANA], [MAP], [RISK], [CERT] | [DDL-GEN], [LINEAGE], [ANA-SQL] |

### Fluxo de Delegação

```
Analyzer-A (Geral)
    ↓
Verificar existência de SQL
    ↓
Verificar SQL-Gate PASS
    ↓
Delegar para Analyzer-A-SQL
    ↓
Aguardar conclusão
    ↓
Integrar resultados
```

**Documentação**: [DELEGACAO_SQL.md](../agents/analyzer-a/DELEGACAO_SQL.md)

---

## 🎓 Como Usar

### Passo 1: Verificar SQL-Gate

```bash
# Verificar se SQL-Gate está PASS
cat run/sql/validation/gate_status_sql.json
```

### Passo 2: Executar Comandos

```bash
# Gerar DDL
[DDL-GEN] Gerar DDL

# Mapear linhagem
[LINEAGE] Mapear linhagem

# Análise completa
[ANA-SQL] Analisar SQL
```

### Passo 3: Verificar Outputs

```bash
# Ver DDL gerado
cat run/sql/analysis/database_schema.sql

# Ver linhagem
cat run/sql/analysis/data_lineage.csv

# Ver relatório
cat run/sql/analysis/sql_analysis_report.md
```

---

## 🛠️ Mapeamento de Tipos

### COBOL → SQL Server

| COBOL Type | SQL Server Type | Exemplo |
|------------|-----------------|---------|
| PIC X(n) | NVARCHAR(n) | PIC X(100) → NVARCHAR(100) |
| PIC 9(n) | INT | PIC 9(8) → INT |
| PIC 9(n)V9(m) | DECIMAL(n,m) | PIC 9(10)V9(2) → DECIMAL(10,2) |
| COMP | INT | COMP → INT |
| COMP-3 | DECIMAL | COMP-3 → DECIMAL |

**Fonte**: `knowledge/sql/sql-mapping-rules.csv`

### COBOL → C# (Entity Framework)

| COBOL Type | C# Type |
|------------|---------|
| PIC X(n) | string |
| PIC 9(n) | int |
| PIC 9(n)V9(m) | decimal |
| DATE | DateTime |
| BOOLEAN | bool |

---

## ✅ Best Practices SQL Server

### 1. Tipos de Dados
✅ Usar `NVARCHAR` ao invés de `VARCHAR` (Unicode)  
✅ Usar `DATETIME2` ao invés de `DATETIME` (precisão)  
✅ Usar `BIT` ao invés de `CHAR(1)` para booleanos  
✅ Usar `DECIMAL(18,2)` para valores monetários

### 2. Índices
✅ Criar índices para Primary Keys (automático)  
✅ Criar índices para Foreign Keys (sempre!)  
✅ Criar índices para colunas em WHERE frequentes

### 3. Auditoria
✅ Adicionar `CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE()`  
✅ Adicionar `UpdatedAt DATETIME2 NULL`  
✅ Adicionar `IsDeleted BIT NOT NULL DEFAULT 0`

### 4. Soft Delete
✅ Implementar coluna `IsDeleted`  
✅ Usar Query Filter no EF Core  
✅ Nunca fazer DELETE físico em produção

---

## 📈 Métricas

O Analyzer-A-SQL rastreia as seguintes métricas:

- `total_tables_analyzed`: Total de tabelas analisadas
- `total_relationships_identified`: Total de relacionamentos (FKs)
- `total_indexes_suggested`: Total de índices sugeridos
- `ddl_lines_generated`: Linhas de DDL geradas
- `lineage_entries_mapped`: Entradas de linhagem mapeadas
- `ef_entities_generated`: Entidades EF Core geradas
- `sql_complexity_average`: Complexidade SQL média
- `high_risk_queries_count`: Queries de alto risco

---

## 🔍 Troubleshooting

### Problema: SQL-Gate não está PASS
**Solução**: Executar [VAL-SQL] e corrigir erros antes de analisar

### Problema: claims_sql_A.json não encontrado
**Solução**: Executar [EXT-SQL] para extrair SQL

### Problema: Tipos COBOL não mapeados
**Solução**: Adicionar regra em sql-mapping-rules.csv

### Problema: Relacionamentos não detectados
**Solução**: Verificar se JOINs estão nas queries

---

## 🎉 Status da Implementação

✅ **100% IMPLEMENTADO**

- [x] Estrutura de pastas criada
- [x] analyzer-a-sql.agent.yaml (~350 linhas)
- [x] instructions.md (~800 linhas)
- [x] Workflows (DDL-GEN, LINEAGE, ANA-SQL)
- [x] Delegação SQL (DELEGACAO_SQL.md)
- [x] Documentação completa
- [x] Best practices SQL Server
- [x] Entity Framework Core mapping
- [x] Bloqueio de SQL-Gate
- [x] Zero linter errors

---

## 📚 Referências

- **[analyzer-a-sql.agent.yaml](../agents/analyzer-a/analyzer-a-sql.agent.yaml)** - Configuração
- **[instructions.md](../agents/analyzer-a/analyzer-a-sql/instructions.md)** - Instruções
- **[DELEGACAO_SQL.md](../agents/analyzer-a/DELEGACAO_SQL.md)** - Delegação
- **[ANALYZER_A_SQL_IMPLEMENTADO.md](../ANALYZER_A_SQL_IMPLEMENTADO.md)** - Status
- **[trilha-sql.md](trilha-sql.md)** - Soberania SQL

---

**Versão**: 1.0  
**Data**: 2025-12-28  
**Autor**: BMad Method v6.0  
**Status**: ✅ PRONTO PARA USO


