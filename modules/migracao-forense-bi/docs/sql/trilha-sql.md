# 🗄️ Trilha SQL - Soberania de Dados

## Índice Oficial da Soberania SQL - Módulo Migração Forense BI

**Versão**: 1.0  
**Data**: 2025-12-28  
**Status**: ✅ IMPLEMENTADO

---

## 📋 Visão Geral

A **Soberania SQL** é uma arquitetura de isolamento completo do conhecimento e artefatos de banco de dados, separando-os totalmente da lógica de UI. Esta trilha garante que:

- ✅ **Conhecimento SQL** está isolado em `knowledge/sql/`
- ✅ **Outputs SQL** estão isolados em `run/sql/`
- ✅ **Comandos SQL** são especializados e não misturam UI
- ✅ **Validação SQL** é feita contra VAMAP (DATA DIVISION/SQLCA)

---

## 🗂️ Hierarquia de Pastas

### 1. Base de Conhecimento SQL

```
knowledge/sql/
├── sql-mapping-rules.csv       # Regras de tradução COBOL → SQL
└── sql-patterns-visualage.csv  # Padrões regex para detecção SQL
```

#### sql-mapping-rules.csv

**Finalidade**: Mapear tipos COBOL para tipos SQL modernos.

**Estrutura**:
```csv
cobol_type,cobol_pattern,sql_type,sql_length,notes,example_cobol,example_sql
PIC_X,PIC X\((\d+)\),NVARCHAR,{1},Texto variável,PIC X(100),NVARCHAR(100)
PIC_9_INT,PIC 9\((\d+)\),INT,NULL,Inteiro,PIC 9(8),INT
PIC_9V9,PIC 9\((\d+)\)V9\((\d+)\),DECIMAL,"{1},{2}",Decimal,PIC 9(10)V9(2),DECIMAL(10,2)
```

**Uso**:
- Extractor-A/B: Converter definições COBOL em tipos SQL
- Analyzer-A: Gerar DDL moderno com tipos corretos

#### sql-patterns-visualage.csv

**Finalidade**: Padrões regex para identificar construções SQL no código Visual Age.

**Estrutura**:
```csv
pattern_id,pattern_name,regex_pattern,description,capture_groups,example_match,priority
SQL-001,EXEC_SQL_BLOCK,EXEC\s+SQL\s+(.*?)\s+END-EXEC,Bloco SQL embutido,1: SQL statement,EXEC SQL SELECT * FROM BANCOS END-EXEC,HIGH
SQL-002,DECLARE_CURSOR,DECLARE\s+(\w+)\s+CURSOR\s+FOR\s+(.*?),Declaração de cursor,1: cursor_name 2: select,DECLARE C1 CURSOR FOR SELECT * FROM BANCOS,HIGH
```

**Uso**:
- Extractor-A/B: Detectar e extrair queries SQL
- Validator-A: Validar padrões encontrados

---

### 2. Outputs SQL (run/sql/)

```
run/sql/
├── extraction/
│   ├── claims_sql_A.json      # Claims SQL do Extractor-A
│   ├── claims_sql_B.json      # Claims SQL do Extractor-B
│   └── vamap_sql.log          # Log VAMAP filtrado (DATA DIVISION/SQLCA)
│
├── validation/
│   ├── gate_status_sql.json   # Status do Gate SQL (PASS/FAIL)
│   └── validation_report_sql.md  # Relatório de validação SQL
│
└── analysis/
    ├── ddl/
    │   └── database_schema.sql    # DDL SQL moderno gerado
    ├── lineage/
    │   └── data_lineage.csv       # Linhagem de dados (lógica → tabela)
    ├── claim_ledger_sql.json      # Ledger de dados reconciliado
    ├── complexity_matrix_sql.csv  # Matriz de complexidade SQL
    └── ef_core_mapping.json       # Mapeamento Entity Framework Core
```

#### run/sql/extraction/

**Finalidade**: Armazenar claims de SQL extraídos pelos agentes.

**Arquivos**:

1. **claims_sql_A.json**
   - Gerado por: Extractor-A `[EXT-SQL]`
   - Conteúdo: Queries SQL, tabelas, colunas, cursores
   - Estrutura:
   ```json
   {
     "metadata": {
       "source_file": "bi14a.esf",
       "extraction_mode": "SQL_ONLY",
       "timestamp": "2025-12-28T10:30:00Z"
     },
     "queries": [
       {
         "query_id": "QRY-SQL-001",
         "query_type": "SELECT",
         "sql_statement": "SELECT COD_BANCO FROM BANCOS WHERE ATIVO='S'",
         "evidence_pointer": "bi14a.esf:L0500-L0503",
         "affected_tables": ["BANCOS"],
         "operation_type": "READ",
         "columns_used": ["COD_BANCO", "ATIVO"]
       }
     ],
     "tables": [
       {
         "table_name": "BANCOS",
         "columns": [
           {"name": "COD_BANCO", "cobol_type": "PIC X(10)", "sql_type": "NVARCHAR(10)"},
           {"name": "NOME_BANCO", "cobol_type": "PIC X(100)", "sql_type": "NVARCHAR(100)"},
           {"name": "ATIVO", "cobol_type": "PIC X(1)", "sql_type": "CHAR(1)"}
         ],
         "evidence_pointer": "bi14a.esf:L0100-L0120"
       }
     ]
   }
   ```

2. **claims_sql_B.json**
   - Gerado por: Extractor-B `[EXT-SQL]`
   - Conteúdo: Mesma estrutura de claims_sql_A.json
   - Uso: Reconciliação (comparar A vs B)

3. **vamap_sql.log**
   - Gerado por: Ingestor-A (filtro do vamap_raw.log)
   - Conteúdo: Apenas seções DATA DIVISION e SQLCA
   - Uso: Âncora da verdade para validação SQL

#### run/sql/validation/

**Finalidade**: Armazenar resultados da validação SQL.

**Arquivos**:

1. **gate_status_sql.json**
   - Gerado por: Validator-A `[VAL-SQL]`
   - Conteúdo: Status binário PASS/FAIL
   - Estrutura:
   ```json
   {
     "sql_gate_status": "PASS",
     "conformidade_sql_percentage": 100.0,
     "timestamp": "2025-12-28T10:35:00Z",
     "tabelas_vamap": ["BANCOS", "AGENCIAS", "TRANSACOES"],
     "tabelas_ia": ["BANCOS", "AGENCIAS", "TRANSACOES"],
     "omissoes": [],
     "alucinacoes": [],
     "queries_validadas": 23,
     "queries_com_tabelas_validas": 23,
     "next_agent_allowed": true
   }
   ```

2. **validation_report_sql.md**
   - Gerado por: Validator-A `[VAL-SQL]`
   - Conteúdo: Relatório humano detalhado
   - Seções:
     - Sumário Executivo (PASS/FAIL)
     - Conformidade SQL (IA vs VAMAP)
     - Omissões detectadas
     - Alucinações detectadas
     - Recomendações de correção

#### run/sql/analysis/

**Finalidade**: Armazenar análises e artefatos SQL gerados.

**Estrutura Organizada**:
```
analysis/
├── ddl/                       # Artefatos de DDL
│   └── database_schema.sql
├── lineage/                   # Artefatos de Linhagem
│   └── data_lineage.csv
├── claim_ledger_sql.json      # Ledger reconciliado
├── complexity_matrix_sql.csv  # Matriz de complexidade
└── ef_core_mapping.json       # Mapeamento EF Core
```

**Arquivos**:

1. **ddl/database_schema.sql**
   - **Pasta**: `run/sql/analysis/ddl/`
   - Gerado por: Analyzer-A-SQL `[DDL-GEN]`
   - Conteúdo: DDL SQL Server moderno (CREATE TABLE, VIEWS, STORED PROCEDURES)
   - Exemplo:
   ```sql
   -- Gerado por Analyzer-A-SQL [DDL-GEN]
   -- Fonte: bi14a.esf
   -- Data: 2025-12-28
   
   CREATE TABLE Banco (
       Id INT PRIMARY KEY IDENTITY(1,1),
       CodigoBanco NVARCHAR(10) NOT NULL,
       NomeBanco NVARCHAR(100) NOT NULL,
       Ativo BIT NOT NULL DEFAULT 1,
       
       -- Auditoria
       CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
       UpdatedAt DATETIME2 NULL,
       IsDeleted BIT NOT NULL DEFAULT 0,
       
       -- Constraints
       CONSTRAINT CHK_Banco_Ativo CHECK (Ativo IN (0, 1)),
       CONSTRAINT UQ_Banco_CodigoBanco UNIQUE (CodigoBanco)
   );
   GO
   
   CREATE INDEX IX_Banco_CodigoBanco ON Banco(CodigoBanco);
   GO
   
   CREATE VIEW vw_BancosAtivos AS
   SELECT Id, CodigoBanco, NomeBanco
   FROM Banco
   WHERE Ativo = 1 AND IsDeleted = 0;
   GO
   ```

2. **lineage/data_lineage.csv**
   - **Pasta**: `run/sql/analysis/lineage/`
   - Gerado por: Analyzer-A-SQL `[LINEAGE]`
   - Conteúdo: Linhagem de dados (qual lógica afeta qual tabela)
   - Estrutura:
   ```csv
   table_name,operation_type,query_id,evidence_pointer,business_logic_id,screen_id,risk_level,notes
   V0BILHETE,READ,QRY-SQL-LEDGER-006,bi14a.esf:L1194-L1210,NONE,NONE,LOW,"Query simples; Leitura completa de bilhete"
   V0BILHETE,UPDATE,QRY-SQL-LEDGER-005,bi14a.esf:L1160-L1175,NONE,NONE,MEDIUM,"UPDATE com WHERE; Atualização de dados bancários"
   V0RELATORIOS,READ,QRY-SQL-LEDGER-009,bi14a.esf:L1299-L1310,NONE,NONE,LOW,"Query simples; Leitura de relatório"
   V0RELATORIOS,CREATE,QRY-SQL-LEDGER-010,bi14a.esf:L1333-L1355,NONE,NONE,MEDIUM,"INSERT com múltiplas colunas; Inclusão de relatório"
   ```

3. **claim_ledger_sql.json**
   - **Pasta**: `run/sql/analysis/`
   - Gerado por: Reconciliador-A-SQL `[REC-SQL]`
   - Conteúdo: Ledger de dados reconciliado (verdade única)
   - Estrutura:
   ```json
   {
     "metadata": {
       "reconciliation_date": "2025-12-28T13:30:00Z",
       "total_queries": 18,
       "match_count": 17,
       "conflict_count": 0,
       "hallucination_count": 1,
       "confidence_score": 94.44
     },
     "queries": [...]
   }
   ```

4. **complexity_matrix_sql.csv**
   - **Pasta**: `run/sql/analysis/`
   - Gerado por: Analyzer-A-SQL `[ANA-SQL]`
   - Conteúdo: Matriz de complexidade SQL
   - Estrutura:
   ```csv
   query_id,query_type,complexity_score,risk_level,tables_count,joins_count,subqueries_count,dynamic_sql,notes
   QRY-SQL-LEDGER-001,STATIC,2,LOW,1,0,0,FALSE,Query simples
   QRY-SQL-LEDGER-005,STATIC,5,MEDIUM,1,0,0,FALSE,UPDATE com WHERE
   QRY-SQL-LEDGER-010,STATIC,7,MEDIUM,1,0,0,FALSE,INSERT com 22 colunas
   ```

5. **ef_core_mapping.json**
   - **Pasta**: `run/sql/analysis/`
   - Gerado por: Analyzer-A-SQL `[ANA-SQL]`
   - Conteúdo: Mapeamento para Entity Framework Core
   - Estrutura:
   ```json
   {
     "entities": [
       {
         "entity_name": "Bilhete",
         "table_name": "V0BILHETE",
         "properties": [...],
         "navigation_properties": [...],
         "indexes": [...],
         "constraints": [...]
       }
     ]
   }
   ```

---

## 🎯 Comandos Especializados SQL

### 1. [EXT-SQL] - Extração SQL

**Agentes**: Extractor-A, Extractor-B

**Comando**: `[EXT-SQL] Extrair SQL de <arquivo.esf>`

**Missão**:
- ✅ Focar 100% em SQL (EXEC SQL, CURSOR, INSERT, UPDATE, DELETE)
- ❌ Ignorar UI (telas, botões, cores, layouts)
- ✅ Usar `knowledge/sql/sql-patterns-visualage.csv` para detecção
- ✅ Usar `knowledge/sql/sql-mapping-rules.csv` para conversão de tipos
- ✅ Gerar `run/sql/extraction/claims_sql_A.json` (ou _B.json)

**Regras**:
1. Nunca misturar claims de UI com claims de SQL
2. Cada query deve ter `affected_tables` e `operation_type`
3. Cada tabela deve ter mapeamento COBOL → SQL
4. Evidence pointer obrigatório para rastreabilidade

**Output**:
```
run/sql/extraction/
├── claims_sql_A.json  ← Extractor-A
└── claims_sql_B.json  ← Extractor-B
```

---

### 2. [VAL-SQL] - Validação SQL

**Agente**: Validator-A

**Comando**: `[VAL-SQL] Validar SQL`

**Missão**:
- ✅ Confrontar claims SQL (IA) vs vamap_sql.log (VAMAP)
- ✅ Detectar omissões (VAMAP tem, IA não)
- ✅ Detectar alucinações (IA tem, VAMAP não)
- ✅ Calcular conformidade SQL = 100%
- ✅ Gerar `run/sql/validation/gate_status_sql.json`

**Regras**:
1. Carregar `run/sql/extraction/vamap_sql.log` (DATA DIVISION/SQLCA)
2. Carregar `run/sql/extraction/claims_sql_A.json` (IA)
3. Cruzar tabelas: `omissoes = vamap_tables - ia_tables`
4. Cruzar tabelas: `alucinacoes = ia_tables - vamap_tables`
5. Calcular: `conformidade = (intersecção / total_vamap) * 100`
6. FAIL se: `len(omissoes) > 0 OR len(alucinacoes) > 0 OR conformidade < 100%`

**Output**:
```
run/sql/validation/
├── gate_status_sql.json       ← Status PASS/FAIL
└── validation_report_sql.md   ← Relatório detalhado
```

---

### 3. [ANA-SQL] - Análise SQL

**Agente**: Analyzer-A

**Comando**: `[ANA-SQL] Analisar SQL`

**Missão**:
- ✅ Gerar DDL SQL moderno (`database_schema.sql`)
- ✅ Mapear linhagem de dados (`data_lineage.csv`)
- ✅ Calcular complexidade SQL (`complexity_matrix_sql.csv`)
- ✅ Identificar riscos SQL (dinâmico, mass ops, queries complexas)

**Regras**:
1. Carregar `run/sql/extraction/claims_sql_A.json` (validado)
2. Agrupar queries por tabela
3. Identificar relacionamentos (FKs via JOINs)
4. Mapear lógica → query → tabela
5. Detectar padrões de risco (SQL dinâmico, mass delete, queries >= 5 JOINs)
6. Gerar DDL com CREATE TABLE, VIEWS, STORED PROCEDURES

**Output**:
```
run/sql/analysis/
├── ddl/
│   └── database_schema.sql         ← DDL moderno
├── lineage/
│   └── data_lineage.csv            ← Linhagem de dados
├── claim_ledger_sql.json           ← Ledger reconciliado
├── complexity_matrix_sql.csv       ← Complexidade SQL
└── ef_core_mapping.json            ← Mapeamento EF Core
```

---

## 🔒 Regras de Isolamento

### Regra 1: Separação de Conhecimento

**Proibido**:
- ❌ Misturar padrões SQL com padrões UI em um mesmo arquivo
- ❌ Usar `knowledge/visual-age-patterns.csv` para SQL

**Permitido**:
- ✅ `knowledge/sql/` exclusivo para SQL
- ✅ `knowledge/ui/` exclusivo para UI (se existir)

### Regra 2: Separação de Outputs

**Proibido**:
- ❌ Salvar claims SQL em `run/extraction/claims_A.json` (genérico)
- ❌ Misturar validação SQL com validação UI

**Permitido**:
- ✅ `run/sql/` exclusivo para artefatos SQL
- ✅ `run/ui/` exclusivo para artefatos UI (se existir)

### Regra 3: Comandos Especializados

**Proibido**:
- ❌ `[EXT]` extrair SQL e UI juntos
- ❌ `[VAL]` validar SQL e UI juntos

**Permitido**:
- ✅ `[EXT-SQL]` extrai apenas SQL
- ✅ `[EXT-UI]` extrai apenas UI (se existir)
- ✅ `[VAL-SQL]` valida apenas SQL
- ✅ `[VAL-UI]` valida apenas UI (se existir)

---

## ✅ Validação de Integridade da Migração de Dados

### Checklist de Validação

Use este checklist para validar a integridade da migração SQL:

#### 1. Estrutura de Pastas

- [ ] `knowledge/sql/` existe
- [ ] `knowledge/sql/sql-mapping-rules.csv` existe
- [ ] `knowledge/sql/sql-patterns-visualage.csv` existe
- [ ] `run/sql/extraction/` existe
- [ ] `run/sql/validation/` existe
- [ ] `run/sql/analysis/` existe

#### 2. Base de Conhecimento

- [ ] `sql-mapping-rules.csv` tem >= 15 regras de mapeamento
- [ ] `sql-patterns-visualage.csv` tem >= 30 padrões regex
- [ ] Padrões HIGH priority estão presentes (EXEC SQL, DECLARE CURSOR, INSERT, UPDATE, DELETE)

#### 3. Extração SQL

- [ ] `claims_sql_A.json` foi gerado
- [ ] Todas as queries têm `affected_tables`
- [ ] Todas as queries têm `operation_type`
- [ ] Todas as queries têm `evidence_pointer`
- [ ] Nenhum claim de UI está presente
- [ ] Tipos COBOL foram convertidos para SQL

#### 4. Validação SQL

- [ ] `gate_status_sql.json` foi gerado
- [ ] `conformidade_sql_percentage` está calculado
- [ ] `omissoes` está vazio (ou documentado)
- [ ] `alucinacoes` está vazio (ou documentado)
- [ ] `sql_gate_status` é "PASS" ou "FAIL"
- [ ] `validation_report_sql.md` foi gerado

#### 5. Análise SQL

- [ ] `ddl/database_schema.sql` foi gerado
- [ ] DDL contém CREATE TABLE para todas as tabelas
- [ ] Tipos SQL estão corretos (baseados em sql-mapping-rules.csv)
- [ ] `lineage/data_lineage.csv` foi gerado
- [ ] Linhagem mapeia lógica → query → tabela
- [ ] `complexity_matrix_sql.csv` foi gerado
- [ ] `ef_core_mapping.json` foi gerado
- [ ] Riscos SQL estão identificados

#### 6. Integridade dos Dados

- [ ] Todas as tabelas do VAMAP foram mapeadas
- [ ] Todas as queries têm tabelas válidas
- [ ] Relacionamentos (FKs) foram identificados
- [ ] Constraints foram documentadas
- [ ] Índices foram identificados

---

## 📊 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ TRILHA SQL - SOBERANIA DE DADOS                                 │
└─────────────────────────────────────────────────────────────────┘

1. INGESTOR-A
   ├─ Criar estrutura: run/sql/extraction/, validation/, analysis/
   ├─ Executar vamap.exe → vamap_raw.log
   └─ Filtrar SQL: vamap_sql.log (DATA DIVISION + SQLCA)

2. EXTRACTOR-A [EXT-SQL]
   ├─ Carregar: knowledge/sql/sql-patterns-visualage.csv
   ├─ Detectar: EXEC SQL, CURSOR, INSERT, UPDATE, DELETE
   ├─ Ignorar: UI, Cores, Layouts
   ├─ Mapear tipos: knowledge/sql/sql-mapping-rules.csv
   └─ Gerar: run/sql/extraction/claims_sql_A.json

3. EXTRACTOR-B [EXT-SQL]
   └─ Gerar: run/sql/extraction/claims_sql_B.json

4. VALIDATOR-A [VAL-SQL]
   ├─ Carregar: vamap_sql.log (VAMAP)
   ├─ Carregar: claims_sql_A.json (IA)
   ├─ Cruzar: IA × VAMAP
   ├─ Detectar: Omissões e Alucinações
   ├─ Calcular: Conformidade SQL
   └─ Gerar: run/sql/validation/gate_status_sql.json

5. RECONCILIADOR-A-SQL [REC-SQL]
   ├─ Carregar: claims_sql_A.json e claims_sql_B.json
   ├─ Comparar: A vs B (MATCH, CONFLICT, HALLUCINATION, OMISSION)
   ├─ Gerar: run/sql/validation/diff_report_sql.md
   └─ Gerar: run/sql/analysis/claim_ledger_sql.json

6. VALIDATOR-A-SQL [VAL-SQL]
   ├─ Carregar: claim_ledger_sql.json (Ledger)
   ├─ Carregar: vamap_sql.log (VAMAP)
   ├─ Cruzar: Ledger × VAMAP
   ├─ Validar: Evidence pointers, type mapping, SQLCA
   ├─ Calcular: Grounding Score (100%)
   └─ Gerar: run/sql/validation/gate_status_sql.json

7. ANALYZER-A-SQL [ANA-SQL]
   ├─ Carregar: claim_ledger_sql.json (validado)
   ├─ Agrupar: Queries por tabela
   ├─ Mapear: Linhagem de dados
   ├─ Detectar: Riscos SQL
   ├─ Gerar: run/sql/analysis/ddl/database_schema.sql
   ├─ Gerar: run/sql/analysis/lineage/data_lineage.csv
   ├─ Gerar: run/sql/analysis/complexity_matrix_sql.csv
   └─ Gerar: run/sql/analysis/ef_core_mapping.json
```

---

## 🎓 Exemplos de Uso

### Exemplo 1: Extração SQL

```bash
[EXT-SQL] Extrair SQL de bi14a.esf
```

**Resultado**:
- ✅ `run/sql/extraction/claims_sql_A.json` criado
- ✅ 23 queries SQL extraídas
- ✅ 3 tabelas mapeadas (BANCOS, AGENCIAS, TRANSACOES)
- ✅ Tipos COBOL → SQL convertidos

### Exemplo 2: Validação SQL

```bash
[VAL-SQL] Validar SQL
```

**Resultado**:
- ✅ Conformidade SQL: 100%
- ✅ Omissões: 0
- ✅ Alucinações: 0
- ✅ SQL-Gate: PASS

### Exemplo 3: Análise SQL

```bash
[ANA-SQL] Analisar SQL
```

**Resultado**:
- ✅ `ddl/database_schema.sql` gerado (150 linhas DDL)
- ✅ `lineage/data_lineage.csv` gerado (47 linhas de linhagem)
- ✅ `complexity_matrix_sql.csv` gerado (23 queries analisadas)
- ✅ `ef_core_mapping.json` gerado (7 entidades mapeadas)
- ✅ 2 riscos HIGH detectados (SQL dinâmico, mass delete)

---

## 📞 Suporte

### Dúvidas Frequentes

**P: Por que separar SQL de UI?**
R: Para garantir que a migração de dados seja independente da migração de interface, permitindo validação especializada e evitando mistura de conceitos.

**P: O que é vamap_sql.log?**
R: É um filtro do vamap_raw.log contendo apenas as seções DATA DIVISION e SQLCA, que são as partes relevantes para validação SQL.

**P: Como funciona a validação SQL?**
R: Confrontamos as tabelas extraídas pela IA (claims_sql_A.json) com as tabelas detectadas pelo VAMAP (vamap_sql.log). Se houver omissões ou alucinações, o gate SQL falha.

**P: O que são omissões e alucinações?**
R: Omissões são tabelas que o VAMAP detectou mas a IA não extraiu. Alucinações são tabelas que a IA extraiu mas o VAMAP não reconhece.

**P: Posso usar [EXT] para extrair SQL?**
R: Não. Use [EXT-SQL] para garantir isolamento. O comando [EXT] é genérico e pode misturar UI com SQL.

---

## 📚 Documentação Relacionada

- [Integração VAMAP](../INTEGRACAO_VAMAP.md) - Âncora da Verdade
- [Resumo Integração VAMAP](../RESUMO_INTEGRACAO_VAMAP.md) - Resumo VAMAP
- [Especialização SQL Fase 1](../ESPECIALIZACAO_SQL_FASE1.md) - Documentação completa
- [README Principal](../README.md) - Visão geral do módulo

---

**Versão**: 1.0  
**Data**: 2025-12-28  
**Autor**: BMad Method v6.0  
**Módulo**: migracao-forense-bi


