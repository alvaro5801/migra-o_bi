# 🎯 Especialização SQL - Fase 1 (Soberania SQL)

## ✅ Status: IMPLEMENTADO

**Data**: 2025-12-28  
**Versão**: 1.0  
**Impacto**: 🔴 CRÍTICO - Trilha especializada para validação SQL 100%

---

## 📋 Objetivo

Criar uma **trilha de extração e validação específica para SQL**, garantindo que o **vamap.exe valide cada query encontrada** e que a IA esteja 100% alinhada com as tabelas e colunas reais do banco de dados.

**Princípio**: Separação por Soberanias - SQL como domínio independente de UI/Cores.

---

## 🎯 Estratégia de Separação

### Antes (Extração Genérica)
```
[EXT] → Extrai TUDO (UI + SQL + Lógica) → [VAL] → [ANA]
```

### Depois (Soberania SQL)
```
[EXT-SQL] → Extrai APENAS SQL → [VAL-SQL] → [ANA-SQL]
     ↓                              ↓              ↓
  Ignora UI/Cores         VAMAP SQL Gate    Schema + Linhagem
```

---

## 🔄 Alterações Implementadas

### 1️⃣ Agente Extractor-A

#### Novo Comando: [EXT-SQL]

**Missão Especializada:**
- ✅ **FOCAR**: Blocos EXEC SQL, DECLARE CURSOR, FETCH, INSERT, UPDATE, DELETE
- ❌ **IGNORAR**: Definições de UI, cores, layouts, campos de tela
- ✅ **RASTREAR**: Cada query com evidence_pointer obrigatório

#### Novos Atributos JSON

```json
{
  "queries": [
    {
      "query_id": "QRY-001",
      "query_type": "SELECT",
      "sql_statement": "SELECT COD_BANCO FROM BANCOS WHERE ATIVO='S'",
      "evidence_pointer": "bi14a.esf:L0500-L0502",
      "tables_referenced": ["BANCOS"],
      "parameters": [":WS-COD-BANCO"],
      
      // ✨ NOVOS CAMPOS
      "affected_tables": ["BANCOS"],           // Lista de tabelas citadas
      "operation_type": "READ"                 // CRUD (CREATE/READ/UPDATE/DELETE)
    }
  ]
}
```

#### Mapeamento operation_type

| SQL Statement | operation_type |
|---------------|----------------|
| SELECT | READ |
| INSERT | CREATE |
| UPDATE | UPDATE |
| DELETE | DELETE |
| CALL (stored proc) | EXECUTE |

#### Padrões SQL Visual Age Extraídos

- `EXEC SQL ... END-EXEC`
- `DECLARE cursor_name CURSOR FOR`
- `OPEN cursor_name`
- `FETCH cursor_name INTO`
- `CLOSE cursor_name`
- `INSERT INTO table_name`
- `UPDATE table_name SET`
- `DELETE FROM table_name`
- `SELECT ... INTO :host_vars`
- `COMMIT WORK / ROLLBACK WORK`
- `WHENEVER SQLERROR / WHENEVER NOT FOUND`

#### Outputs Gerados

- `run/extraction/claims_A_sql.json` (apenas queries SQL)
- `run/extraction/sql_extraction_log.txt`
- `run/extraction/sql_tables_summary.csv` (tabelas × operações)

---

### 2️⃣ Agente Validator-A

#### Novo Comando: [VAL-SQL]

**Missão Especializada:**
- ✅ **RULE-VAMAP-SQL**: Confrontar tabelas/colunas extraídas pela IA com DATA DIVISION ou SQLCA do vamap_raw.log
- ✅ **DETECTAR OMISSÕES**: VAMAP detectou tabela que IA não mapeou → FAIL
- ✅ **DETECTAR ALUCINAÇÕES SQL**: IA mapeou tabela que VAMAP não reconhece → FAIL
- ✅ **CONFORMIDADE 100%**: Apenas PASS se IA e VAMAP estão 100% alinhados

#### Regra de Cruzamento

```python
# 1. Carregar tabelas do VAMAP (DATA DIVISION / SQLCA)
vamap_tables = parse_vamap_sql_section("run/ingestion/vamap_raw.log")

# 2. Carregar tabelas da IA (claims_A_sql.json)
ia_tables = extract_affected_tables("run/extraction/claims_A_sql.json")

# 3. Cruzamento
omissoes = vamap_tables - ia_tables  # VAMAP tem, IA não
alucinacoes = ia_tables - vamap_tables  # IA tem, VAMAP não

# 4. Critério de FAIL
if len(omissoes) > 0:
    FAIL("IA não mapeou tabelas que VAMAP detectou")
    
if len(alucinacoes) > 0:
    FAIL("IA mapeou tabelas que VAMAP não reconhece")

# 5. Conformidade
conformidade_sql = (len(ia_tables.intersection(vamap_tables)) / len(vamap_tables)) * 100

if conformidade_sql < 100.0:
    FAIL("Conformidade SQL < 100%")
```

#### Seções do VAMAP Analisadas

```
--- DATA DIVISION ---
01 BANCOS.
   05 COD-BANCO        PIC X(10).
   05 NOME-BANCO       PIC X(100).

--- SQLCA ---
EXEC SQL DECLARE BANCOS TABLE
  (COD_BANCO CHAR(10),
   NOME_BANCO VARCHAR(100))
END-EXEC
```

#### Critério de FAIL

❌ Se VAMAP indicar acesso a uma tabela que a IA não mapeou → **SQL-Gate = FAIL**  
❌ Se IA mapear tabela não presente no VAMAP → **SQL-Gate = FAIL**  
❌ Se conformidade_sql_percentage < 100% → **SQL-Gate = FAIL**

#### Outputs Gerados

- `run/extraction/sql_validation_report.md`
- `run/extraction/sql_gate_status.json`
- `run/extraction/sql_conformance_matrix.csv` (tabela × IA × VAMAP)

#### Exemplo de Output

```json
{
  "sql_gate_status": "PASS",
  "conformidade_sql_percentage": 100.0,
  "tabelas_vamap": ["BANCOS", "AGENCIAS", "TRANSACOES"],
  "tabelas_ia": ["BANCOS", "AGENCIAS", "TRANSACOES"],
  "omissoes": [],
  "alucinacoes": [],
  "queries_validadas": 23,
  "queries_com_tabelas_validas": 23
}
```

---

### 3️⃣ Agente Analyzer-A

#### Novo Comando: [ANA-SQL]

**Missão Especializada:**
- ✅ **GERAR DCL MODERNO**: Converter estruturas legado para SQL moderno (database_schema.sql)
- ✅ **MAPEAR LINHAGEM**: Documentar qual lógica legado afeta qual tabela (data_lineage_report.md)
- ✅ **IDENTIFICAR DEPENDÊNCIAS SQL**: Mapear relacionamentos entre tabelas
- ✅ **DETECTAR RISCOS SQL**: SQL dinâmico, queries complexas, mass updates/deletes

#### Output 1: database_schema.sql

Gerar DDL moderno a partir das estruturas legado:

```sql
-- ============================================
-- DATABASE SCHEMA - Gerado do Legado Visual Age
-- Arquivo Fonte: bi14a.esf
-- Data: 2025-12-28
-- ============================================

-- Tabela: BANCOS
-- Fonte: bi14a.esf:L0500-L0502 (DECLARE TABLE)
CREATE TABLE IF NOT EXISTS bancos (
    cod_banco VARCHAR(10) PRIMARY KEY,
    nome_banco VARCHAR(100) NOT NULL,
    ativo CHAR(1) DEFAULT 'S',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices identificados no legado
    INDEX idx_bancos_nome (nome_banco),
    
    -- Constraints identificadas
    CHECK (ativo IN ('S', 'N'))
);

-- Tabela: AGENCIAS
-- Fonte: bi14a.esf:L0650-L0655
CREATE TABLE IF NOT EXISTS agencias (
    cod_agencia VARCHAR(10) PRIMARY KEY,
    cod_banco VARCHAR(10) NOT NULL,
    nome_agencia VARCHAR(100) NOT NULL,
    
    -- Relacionamentos identificados
    FOREIGN KEY (cod_banco) REFERENCES bancos(cod_banco)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================
-- VIEWS - Queries frequentes do legado
-- ============================================

-- View: Bancos Ativos
-- Fonte: bi14a.esf:L0500-L0502 (SELECT recorrente)
CREATE VIEW vw_bancos_ativos AS
SELECT cod_banco, nome_banco
FROM bancos
WHERE ativo = 'S';
```

#### Output 2: data_lineage_report.md

Mapear linhagem de dados com seções:

1. **Sumário Executivo**
   - Total de tabelas
   - Total de queries
   - Operações de escrita vs leitura

2. **Tabelas e Suas Dependências**
   - Operações por tabela (READ/CREATE/UPDATE/DELETE)
   - Lógica de negócio que afeta cada tabela
   - Campos afetados
   - Dependências downstream (FKs)
   - Riscos identificados

3. **Fluxo de Dados**
   ```
   TELA_CONSULTA (SCR-001)
       ↓
     SELECT BANCOS (QRY-001)
       ↓
     VALIDAR_BANCO (LOG-005)
       ↓
     SELECT AGENCIAS (QRY-008)
       ↓
     EXIBIR_RESULTADO (SCR-002)
   ```

4. **Zonas de Risco SQL**
   - SQL dinâmico
   - Mass updates/deletes
   - Queries complexas (>= 5 JOINs)

5. **Estatísticas e Recomendações**

#### Outputs Gerados

- `run/analysis/database_schema.sql`
- `run/analysis/data_lineage_report.md`
- `run/analysis/sql_risk_matrix.csv`
- `run/analysis/table_dependencies_graph.json`

---

## 📁 Base de Conhecimento SQL

### Novo Arquivo: sql-patterns-visualage.csv

**Localização**: `knowledge/sql-patterns-visualage.csv`

**Conteúdo**: 30 padrões SQL comuns em Visual Age

| Pattern ID | Pattern Type | Description | Operation Type | Risk Level |
|------------|--------------|-------------|----------------|------------|
| SQL-001 | EXEC_SQL_BLOCK | Bloco SQL embutido padrão | VARIES | LOW |
| SQL-002 | DECLARE_CURSOR | Declaração de cursor | SELECT | MEDIUM |
| SQL-006 | INSERT_STATEMENT | Inserção de dados | INSERT | MEDIUM |
| SQL-007 | UPDATE_STATEMENT | Atualização de dados | UPDATE | MEDIUM |
| SQL-008 | DELETE_STATEMENT | Deleção de dados | DELETE | HIGH |
| SQL-011 | DYNAMIC_SQL | SQL construído em runtime | VARIES | HIGH |
| ... | ... | ... | ... | ... |

**Uso**: Referência para identificação de padrões SQL no legado.

---

## 🔄 Fluxo Completo - Trilha SQL

```
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: AS-IS FORENSE - TRILHA SQL                             │
└─────────────────────────────────────────────────────────────────┘

1. INGESTOR-A
   ├─ Passo 0: Invocar vamap.exe
   │  └─ Output: run/ingestion/vamap_raw.log (com DATA DIVISION/SQLCA)
   └─ Passo 1-5: Processar arquivo normalmente

2. EXTRACTOR-A
   ├─ [EXT-SQL] Extração Especializada SQL
   │  ├─ Ignorar UI/Cores/Layouts
   │  ├─ Focar em EXEC SQL, CURSOR, INSERT, UPDATE, DELETE
   │  ├─ Adicionar affected_tables e operation_type
   │  └─ Output: claims_A_sql.json
   └─ Rastreabilidade: evidence_pointer obrigatório

3. VALIDATOR-A
   ├─ [VAL-SQL] Validação Especializada SQL
   │  ├─ RULE-VAMAP-SQL (CRÍTICA)
   │  │  ├─ Carregar tabelas do VAMAP (DATA DIVISION/SQLCA)
   │  │  ├─ Carregar tabelas da IA (claims_A_sql.json)
   │  │  ├─ Detectar omissões (VAMAP tem, IA não)
   │  │  ├─ Detectar alucinações (IA tem, VAMAP não)
   │  │  └─ Conformidade SQL = 100%
   │  └─ Output: sql_gate_status.json
   └─ Gate SQL-G1: PASS/FAIL

4. ANALYZER-A
   ├─ [ANA-SQL] Análise Especializada SQL
   │  ├─ Gerar database_schema.sql (DCL moderno)
   │  ├─ Gerar data_lineage_report.md (linhagem de dados)
   │  ├─ Mapear relacionamentos (FKs via JOINs)
   │  ├─ Identificar riscos SQL
   │  └─ Outputs: schema + linhagem + riscos
   └─ Certificação SQL: COMPLETA
```

---

## 📊 Benefícios da Especialização SQL

### 1. ✅ Foco Cirúrgico
**Antes**: Extração genérica mistura UI + SQL + Lógica  
**Depois**: Trilha dedicada 100% SQL, sem ruído de UI

### 2. ✅ Validação Autoritativa
**Antes**: Validação heurística de SQL  
**Depois**: Cruzamento IA vs VAMAP (DATA DIVISION/SQLCA)

### 3. ✅ Linhagem de Dados
**Antes**: Difícil rastrear qual lógica afeta qual tabela  
**Depois**: Mapeamento completo lógica → query → tabela

### 4. ✅ Schema Moderno
**Antes**: Estruturas legado não documentadas  
**Depois**: DDL SQL moderno gerado automaticamente

### 5. ✅ Detecção de Riscos SQL
**Antes**: Riscos SQL não identificados  
**Depois**: SQL dinâmico, mass ops, queries complexas mapeados

---

## 📈 Métricas de Sucesso

| Métrica | Alvo | Status |
|---------|------|--------|
| **Conformidade SQL (IA vs VAMAP)** | 100% | ✅ Implementado |
| **Queries com affected_tables** | 100% | ✅ Implementado |
| **Queries com operation_type** | 100% | ✅ Implementado |
| **Taxa de Omissão SQL** | 0% | ✅ Detectado |
| **Taxa de Alucinação SQL** | 0% | ✅ Detectado |
| **Schema SQL Gerado** | 100% tabelas | ✅ Implementado |
| **Linhagem Documentada** | 100% queries | ✅ Implementado |

---

## 🚨 Tratamento de Erros

### Erro 1: SQL-Gate FAIL - Omissões

```
❌ RULE-VAMAP-SQL FAILED: Omissões Detectadas

Tabelas que VAMAP detectou mas IA não mapeou:
- TRANSACOES (DATA DIVISION linha 450)
- AUDITORIA (SQLCA linha 680)

Conformidade SQL: 85.7% (esperado: 100%)

🚨 AÇÃO REQUERIDA:
1. Revisar extração SQL
2. Verificar se queries dessas tabelas estão no código
3. Re-executar [EXT-SQL]
```

### Erro 2: SQL-Gate FAIL - Alucinações

```
❌ RULE-VAMAP-SQL FAILED: Alucinações Detectadas

Tabelas que IA mapeou mas VAMAP não reconhece:
- CLIENTES_TEMP (claims_A_sql.json QRY-015)

Conformidade SQL: 95.0% (esperado: 100%)

🚨 AÇÃO REQUERIDA:
1. Verificar se tabela realmente existe no código
2. Verificar se VAMAP processou arquivo completo
3. Corrigir extração ou VAMAP
```

### Erro 3: Tabelas sem operation_type

```
❌ VALIDATION FAILED: Queries sem operation_type

Queries sem classificação CRUD:
- QRY-008: sql_statement presente, operation_type ausente
- QRY-012: sql_statement presente, operation_type ausente

🚨 AÇÃO REQUERIDA:
1. Revisar Extractor-A
2. Garantir mapeamento SELECT→READ, INSERT→CREATE, etc.
3. Re-executar [EXT-SQL]
```

---

## 📚 Arquivos Modificados/Criados

### Agentes Atualizados

| Agente | Arquivo | Mudanças |
|--------|---------|----------|
| **Extractor-A** | `agents/extractor-a.agent.yaml` | ✅ Novo comando: [EXT-SQL] |
| | `agents/extractor-a/instructions.md` | ✅ Seção: Extração Especializada SQL |
| **Validator-A** | `agents/validator-a.agent.yaml` | ✅ Novo comando: [VAL-SQL] |
| | `agents/validator-a/instructions.md` | ✅ Seção: RULE-VAMAP-SQL |
| **Analyzer-A** | `agents/analyzer-a.agent.yaml` | ✅ Novo comando: [ANA-SQL] |
| | `agents/analyzer-a/instructions.md` | ✅ Seção: Análise SQL + Linhagem |

### Novos Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `knowledge/sql-patterns-visualage.csv` | 30 padrões SQL Visual Age |
| `ESPECIALIZACAO_SQL_FASE1.md` | Este documento |

### Outputs Novos

| Arquivo | Gerado Por | Descrição |
|---------|------------|-----------|
| `run/extraction/claims_A_sql.json` | Extractor-A | Claims apenas SQL |
| `run/extraction/sql_extraction_log.txt` | Extractor-A | Log extração SQL |
| `run/extraction/sql_tables_summary.csv` | Extractor-A | Tabelas × Operações |
| `run/extraction/sql_validation_report.md` | Validator-A | Relatório validação SQL |
| `run/extraction/sql_gate_status.json` | Validator-A | Gate SQL PASS/FAIL |
| `run/extraction/sql_conformance_matrix.csv` | Validator-A | IA × VAMAP × Tabelas |
| `run/analysis/database_schema.sql` | Analyzer-A | DDL SQL moderno |
| `run/analysis/data_lineage_report.md` | Analyzer-A | Linhagem de dados |
| `run/analysis/sql_risk_matrix.csv` | Analyzer-A | Riscos SQL |
| `run/analysis/table_dependencies_graph.json` | Analyzer-A | Grafo dependências |

---

## ✨ Exemplo de Uso

### Passo 1: Extração SQL

```bash
[EXT-SQL] Extrair SQL de bi14a.esf

# Extractor-A executa:
# 1. Ignora UI/Cores/Layouts
# 2. Foca em EXEC SQL, CURSOR, INSERT, UPDATE, DELETE
# 3. Adiciona affected_tables e operation_type
# 4. Gera claims_A_sql.json
```

### Passo 2: Validação SQL

```bash
[VAL-SQL] Validar SQL

# Validator-A executa:
# 1. Carrega vamap_raw.log (DATA DIVISION/SQLCA)
# 2. Carrega claims_A_sql.json
# 3. Confronta tabelas: IA vs VAMAP
# 4. Detecta omissões e alucinações
# 5. Calcula conformidade SQL
# 6. PASS apenas se 100%
```

### Passo 3: Análise SQL

```bash
[ANA-SQL] Analisar SQL

# Analyzer-A executa:
# 1. Gera database_schema.sql (DDL moderno)
# 2. Gera data_lineage_report.md (linhagem)
# 3. Mapeia relacionamentos (FKs)
# 4. Identifica riscos SQL
# 5. Certifica trilha SQL completa
```

---

## 🎉 Conclusão

A **Especialização SQL da Fase 1** transforma a extração genérica em uma **trilha cirúrgica focada 100% em Banco de Dados**, com:

✅ **Separação por Soberania**: SQL independente de UI/Cores  
✅ **Validação Autoritativa**: IA vs VAMAP (DATA DIVISION/SQLCA)  
✅ **Linhagem de Dados**: Rastreamento completo lógica → tabela  
✅ **Schema Moderno**: DDL SQL gerado automaticamente  
✅ **Detecção de Riscos**: SQL dinâmico, mass ops, queries complexas

**Resultado**: Migração forense SQL com **tripla garantia** (IA + VAMAP + Linhagem) e **zero tolerância** para omissões ou alucinações.

---

**Documento gerado em**: 2025-12-28  
**Versão**: 1.0  
**Status**: ✅ IMPLEMENTADO E DOCUMENTADO

**Autor**: BMad Method v6.0  
**Módulo**: migracao-forense-bi  
**Fase**: 1 - As-Is Forense - Trilha SQL


