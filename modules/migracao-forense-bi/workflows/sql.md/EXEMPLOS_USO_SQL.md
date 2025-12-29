# 📚 Exemplos Práticos - Trilha SQL Especializada

## Guia Prático de Uso dos Comandos SQL

---

## Exemplo 1: Extração SQL Básica

### Cenário
Extrair todas as queries SQL do arquivo `bi14a.esf`, ignorando UI e cores.

### Comando

```bash
[EXT-SQL] Extrair SQL de bi14a.esf
```

### Input (bi14a.esf)

```visual-age
* Linha 500-503: Query de consulta
EXEC SQL
  SELECT COD_BANCO, NOME_BANCO
  FROM BANCOS
  WHERE ATIVO = 'S'
END-EXEC

* Linha 1500-1502: Inserção de banco
EXEC SQL
  INSERT INTO BANCOS (COD_BANCO, NOME_BANCO, ATIVO)
  VALUES (:WS-COD-BANCO, :WS-NOME-BANCO, 'S')
END-EXEC

* Linha 1800-1805: Atualização de status
EXEC SQL
  UPDATE BANCOS
  SET ATIVO = 'N'
  WHERE COD_BANCO = :WS-COD-BANCO
END-EXEC
```

### Output (claims_A_sql.json)

```json
{
  "metadata": {
    "source_file": "bi14a.esf",
    "extraction_timestamp": "2025-12-28T10:30:00Z",
    "extractor_version": "1.0.0-sql",
    "total_queries": 3
  },
  
  "queries": [
    {
      "query_id": "QRY-001",
      "query_type": "SELECT",
      "sql_statement": "SELECT COD_BANCO, NOME_BANCO FROM BANCOS WHERE ATIVO = 'S'",
      "evidence_pointer": "bi14a.esf:L0500-L0503",
      "tables_referenced": ["BANCOS"],
      "parameters": [],
      "affected_tables": ["BANCOS"],
      "operation_type": "READ"
    },
    {
      "query_id": "QRY-015",
      "query_type": "INSERT",
      "sql_statement": "INSERT INTO BANCOS (COD_BANCO, NOME_BANCO, ATIVO) VALUES (:WS-COD-BANCO, :WS-NOME-BANCO, 'S')",
      "evidence_pointer": "bi14a.esf:L1500-L1502",
      "tables_referenced": ["BANCOS"],
      "parameters": [":WS-COD-BANCO", ":WS-NOME-BANCO"],
      "affected_tables": ["BANCOS"],
      "operation_type": "CREATE"
    },
    {
      "query_id": "QRY-018",
      "query_type": "UPDATE",
      "sql_statement": "UPDATE BANCOS SET ATIVO = 'N' WHERE COD_BANCO = :WS-COD-BANCO",
      "evidence_pointer": "bi14a.esf:L1800-L1805",
      "tables_referenced": ["BANCOS"],
      "parameters": [":WS-COD-BANCO"],
      "affected_tables": ["BANCOS"],
      "operation_type": "UPDATE"
    }
  ],
  
  "summary": {
    "total_queries": 3,
    "queries_by_type": {
      "SELECT": 1,
      "INSERT": 1,
      "UPDATE": 1,
      "DELETE": 0
    },
    "tables_affected": ["BANCOS"],
    "operations_by_type": {
      "READ": 1,
      "CREATE": 1,
      "UPDATE": 1,
      "DELETE": 0
    }
  }
}
```

### Logs Gerados

**sql_extraction_log.txt:**
```
[2025-12-28 10:30:00] INFO: Iniciando extração SQL de bi14a.esf
[2025-12-28 10:30:01] INFO: Modo: SQL-ONLY (ignorando UI/Cores)
[2025-12-28 10:30:02] INFO: Query detectada: SELECT em L0500-L0503
[2025-12-28 10:30:02] INFO: Tabelas afetadas: BANCOS
[2025-12-28 10:30:02] INFO: Operation type: READ
[2025-12-28 10:30:03] INFO: Query detectada: INSERT em L1500-L1502
[2025-12-28 10:30:03] INFO: Tabelas afetadas: BANCOS
[2025-12-28 10:30:03] INFO: Operation type: CREATE
[2025-12-28 10:30:04] INFO: Query detectada: UPDATE em L1800-L1805
[2025-12-28 10:30:04] INFO: Tabelas afetadas: BANCOS
[2025-12-28 10:30:04] INFO: Operation type: UPDATE
[2025-12-28 10:30:05] INFO: Extração SQL concluída: 3 queries
[2025-12-28 10:30:05] SUCCESS: claims_A_sql.json gerado
```

**sql_tables_summary.csv:**
```csv
table_name,read_count,create_count,update_count,delete_count,total_operations
BANCOS,1,1,1,0,3
```

---

## Exemplo 2: Validação SQL com VAMAP (PASS)

### Cenário
Validar se a IA extraiu todas as tabelas que o VAMAP detectou.

### Comando

```bash
[VAL-SQL] Validar SQL
```

### Input 1: vamap_raw.log (VAMAP)

```
--- DATA DIVISION ---
01 BANCOS.
   05 COD-BANCO        PIC X(10).
   05 NOME-BANCO       PIC X(100).
   05 ATIVO            PIC X(1).

01 AGENCIAS.
   05 COD-AGENCIA      PIC X(10).
   05 COD-BANCO        PIC X(10).
   05 NOME-AGENCIA     PIC X(100).

01 TRANSACOES.
   05 ID-TRANSACAO     PIC 9(10).
   05 COD-BANCO        PIC X(10).
   05 VALOR            PIC 9(15)V99.

--- SQLCA ---
EXEC SQL DECLARE BANCOS TABLE
  (COD_BANCO CHAR(10),
   NOME_BANCO VARCHAR(100),
   ATIVO CHAR(1))
END-EXEC

EXEC SQL DECLARE AGENCIAS TABLE
  (COD_AGENCIA CHAR(10),
   COD_BANCO CHAR(10),
   NOME_AGENCIA VARCHAR(100))
END-EXEC

EXEC SQL DECLARE TRANSACOES TABLE
  (ID_TRANSACAO INTEGER,
   COD_BANCO CHAR(10),
   VALOR DECIMAL(15,2))
END-EXEC

Tabelas Detectadas: BANCOS, AGENCIAS, TRANSACOES
```

### Input 2: claims_A_sql.json (IA)

```json
{
  "queries": [
    {"affected_tables": ["BANCOS"], "operation_type": "READ"},
    {"affected_tables": ["BANCOS"], "operation_type": "CREATE"},
    {"affected_tables": ["AGENCIAS"], "operation_type": "READ"},
    {"affected_tables": ["TRANSACOES"], "operation_type": "READ"}
  ]
}
```

### Processamento

```python
# 1. Extrair tabelas do VAMAP
vamap_tables = {"BANCOS", "AGENCIAS", "TRANSACOES"}

# 2. Extrair tabelas da IA
ia_tables = {"BANCOS", "AGENCIAS", "TRANSACOES"}

# 3. Cruzamento
omissoes = vamap_tables - ia_tables
# Resultado: set() (vazio)

alucinacoes = ia_tables - vamap_tables
# Resultado: set() (vazio)

# 4. Conformidade
intersecao = ia_tables.intersection(vamap_tables)
# Resultado: {"BANCOS", "AGENCIAS", "TRANSACOES"}

conformidade = (len(intersecao) / len(vamap_tables)) * 100
# Resultado: (3 / 3) * 100 = 100.0%

# 5. Decisão
if len(omissoes) == 0 and len(alucinacoes) == 0 and conformidade == 100.0:
    status = "PASS"
```

### Output: sql_gate_status.json

```json
{
  "sql_gate_status": "PASS",
  "conformidade_sql_percentage": 100.0,
  "tabelas_vamap": ["BANCOS", "AGENCIAS", "TRANSACOES"],
  "tabelas_ia": ["BANCOS", "AGENCIAS", "TRANSACOES"],
  "omissoes": [],
  "alucinacoes": [],
  "queries_validadas": 23,
  "queries_com_tabelas_validas": 23,
  "timestamp": "2025-12-28T10:35:00Z"
}
```

### Output: sql_validation_report.md

```markdown
# ✅ Relatório de Validação SQL

## Status: PASS

**Conformidade SQL**: 100.0%  
**Queries Validadas**: 23  
**Tabelas Validadas**: 3

---

## Cruzamento IA × VAMAP

### Tabelas VAMAP (Âncora da Verdade)
- BANCOS
- AGENCIAS
- TRANSACOES

### Tabelas IA (Extração)
- BANCOS
- AGENCIAS
- TRANSACOES

---

## Verificações

### ✅ Omissões: 0
Nenhuma tabela detectada pelo VAMAP foi omitida pela IA.

### ✅ Alucinações: 0
Nenhuma tabela extraída pela IA é desconhecida pelo VAMAP.

### ✅ Conformidade: 100.0%
Todas as tabelas do VAMAP foram corretamente mapeadas pela IA.

---

## Conclusão

✅ **SQL-Gate: PASS**

A extração SQL está 100% conforme com o VAMAP.
Analyzer-A está autorizado a prosseguir.
```

---

## Exemplo 3: Validação SQL com VAMAP (FAIL - Omissões)

### Cenário
IA não extraiu uma tabela que o VAMAP detectou.

### Input 1: vamap_raw.log (VAMAP)

```
Tabelas Detectadas: BANCOS, AGENCIAS, TRANSACOES, AUDITORIA
```

### Input 2: claims_A_sql.json (IA)

```json
{
  "queries": [
    {"affected_tables": ["BANCOS"]},
    {"affected_tables": ["AGENCIAS"]},
    {"affected_tables": ["TRANSACOES"]}
    // AUDITORIA não foi extraída!
  ]
}
```

### Processamento

```python
vamap_tables = {"BANCOS", "AGENCIAS", "TRANSACOES", "AUDITORIA"}
ia_tables = {"BANCOS", "AGENCIAS", "TRANSACOES"}

omissoes = vamap_tables - ia_tables
# Resultado: {"AUDITORIA"}

conformidade = (3 / 4) * 100
# Resultado: 75.0%

# Decisão: FAIL
```

### Output: sql_gate_status.json

```json
{
  "sql_gate_status": "FAIL",
  "conformidade_sql_percentage": 75.0,
  "tabelas_vamap": ["BANCOS", "AGENCIAS", "TRANSACOES", "AUDITORIA"],
  "tabelas_ia": ["BANCOS", "AGENCIAS", "TRANSACOES"],
  "omissoes": ["AUDITORIA"],
  "alucinacoes": [],
  "queries_validadas": 23,
  "queries_com_tabelas_validas": 20,
  "timestamp": "2025-12-28T10:40:00Z"
}
```

### Output: sql_validation_report.md

```markdown
# ❌ Relatório de Validação SQL

## Status: FAIL

**Conformidade SQL**: 75.0% (esperado: 100.0%)  
**Queries Validadas**: 23  
**Tabelas Validadas**: 3 de 4

---

## ❌ RULE-VAMAP-SQL FAILED: Omissões Detectadas

### Tabelas que VAMAP detectou mas IA não mapeou:

| Tabela | Fonte VAMAP | Linha |
|--------|-------------|-------|
| AUDITORIA | DATA DIVISION | 680 |

---

## Análise

O VAMAP detectou acesso à tabela **AUDITORIA**, mas a IA não extraiu nenhuma query que a referencie.

**Possíveis Causas:**
1. Query SQL está em bloco não detectado pela IA
2. Tabela é acessada via stored procedure
3. Padrão SQL não reconhecido pela IA

---

## 🚨 AÇÃO REQUERIDA

1. Revisar arquivo fonte em busca de queries para AUDITORIA
2. Verificar se há CALL para stored procedures
3. Re-executar [EXT-SQL] com atenção a padrões SQL não convencionais
4. Re-executar [VAL-SQL] após correção

---

## Status do Gate

❌ **SQL-Gate: FAIL**

Analyzer-A está **BLOQUEADO** até conformidade atingir 100%.
```

---

## Exemplo 4: Análise SQL e Geração de Schema

### Cenário
Gerar schema SQL moderno e mapeamento de linhagem de dados.

### Comando

```bash
[ANA-SQL] Analisar SQL
```

### Input: claims_A_sql.json (validado)

```json
{
  "queries": [
    {
      "query_id": "QRY-001",
      "sql_statement": "SELECT COD_BANCO, NOME_BANCO FROM BANCOS WHERE ATIVO='S'",
      "affected_tables": ["BANCOS"],
      "operation_type": "READ",
      "evidence_pointer": "bi14a.esf:L0500-L0503"
    },
    {
      "query_id": "QRY-015",
      "sql_statement": "INSERT INTO BANCOS VALUES (:WS-COD, :WS-NOME, 'S')",
      "affected_tables": ["BANCOS"],
      "operation_type": "CREATE",
      "evidence_pointer": "bi14a.esf:L1500-L1502"
    },
    {
      "query_id": "QRY-008",
      "sql_statement": "SELECT * FROM AGENCIAS WHERE COD_BANCO = :WS-COD",
      "affected_tables": ["AGENCIAS"],
      "operation_type": "READ",
      "evidence_pointer": "bi14a.esf:L0700-L0705"
    }
  ]
}
```

### Output 1: database_schema.sql

```sql
-- ============================================
-- DATABASE SCHEMA - Gerado do Legado Visual Age
-- Arquivo Fonte: bi14a.esf
-- Data: 2025-12-28
-- Gerado por: Analyzer-A [ANA-SQL]
-- ============================================

-- ============================================
-- TABELAS
-- ============================================

-- Tabela: BANCOS
-- Fonte: bi14a.esf:L0500-L0503 (DECLARE TABLE via VAMAP)
-- Operações: 2 (1 READ, 1 CREATE)
CREATE TABLE IF NOT EXISTS bancos (
    cod_banco VARCHAR(10) PRIMARY KEY,
    nome_banco VARCHAR(100) NOT NULL,
    ativo CHAR(1) DEFAULT 'S',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints identificadas
    CHECK (ativo IN ('S', 'N')),
    
    -- Comentário: Tabela principal de cadastro de bancos
    COMMENT 'Cadastro de bancos - migrado de bi14a.esf'
);

-- Índices identificados no legado
CREATE INDEX idx_bancos_nome ON bancos(nome_banco);
CREATE INDEX idx_bancos_ativo ON bancos(ativo);

-- Tabela: AGENCIAS
-- Fonte: bi14a.esf:L0700-L0705
-- Operações: 1 (1 READ)
CREATE TABLE IF NOT EXISTS agencias (
    cod_agencia VARCHAR(10) PRIMARY KEY,
    cod_banco VARCHAR(10) NOT NULL,
    nome_agencia VARCHAR(100) NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Relacionamentos identificados via JOIN analysis
    FOREIGN KEY (cod_banco) 
        REFERENCES bancos(cod_banco)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    
    COMMENT 'Cadastro de agências bancárias - migrado de bi14a.esf'
);

-- Índices para performance
CREATE INDEX idx_agencias_banco ON agencias(cod_banco);

-- ============================================
-- VIEWS - Queries frequentes do legado
-- ============================================

-- View: Bancos Ativos
-- Fonte: bi14a.esf:L0500-L0503 (SELECT recorrente)
-- Uso: Dropdown de seleção de bancos
CREATE VIEW vw_bancos_ativos AS
SELECT 
    cod_banco,
    nome_banco,
    data_cadastro
FROM bancos
WHERE ativo = 'S'
ORDER BY nome_banco;

-- ============================================
-- STORED PROCEDURES - Lógica SQL complexa
-- ============================================

-- Procedure: Cadastrar Banco
-- Fonte: bi14a.esf:L1500-L1502 (INSERT recorrente)
CREATE OR REPLACE PROCEDURE sp_cadastrar_banco(
    IN p_cod_banco VARCHAR(10),
    IN p_nome_banco VARCHAR(100),
    OUT p_retorno VARCHAR(10)
)
BEGIN
    -- Verificar duplicidade
    IF EXISTS (SELECT 1 FROM bancos WHERE cod_banco = p_cod_banco) THEN
        SET p_retorno = 'DUPLICADO';
    ELSE
        INSERT INTO bancos (cod_banco, nome_banco, ativo)
        VALUES (p_cod_banco, p_nome_banco, 'S');
        SET p_retorno = 'OK';
    END IF;
END;

-- ============================================
-- TRIGGERS - Auditoria e integridade
-- ============================================

-- Trigger: Auditoria de alterações em BANCOS
CREATE TRIGGER trg_bancos_audit
AFTER UPDATE ON bancos
FOR EACH ROW
BEGIN
    INSERT INTO auditoria (tabela, operacao, usuario, data_hora)
    VALUES ('BANCOS', 'UPDATE', CURRENT_USER(), NOW());
END;

-- ============================================
-- COMENTÁRIOS FINAIS
-- ============================================

-- Total de tabelas: 2
-- Total de views: 1
-- Total de stored procedures: 1
-- Total de triggers: 1
-- Queries analisadas: 3
-- Conformidade VAMAP: 100%

-- Próximos passos:
-- 1. Revisar constraints e ajustar conforme necessário
-- 2. Adicionar índices adicionais baseados em performance
-- 3. Implementar stored procedures para lógica complexa
-- 4. Configurar backup e recovery
```

### Output 2: data_lineage_report.md

```markdown
# 📊 Relatório de Linhagem de Dados

**Arquivo Analisado**: bi14a.esf  
**Data**: 2025-12-28  
**Gerado por**: Analyzer-A [ANA-SQL]

---

## Sumário Executivo

| Métrica | Valor |
|---------|-------|
| Total de Tabelas | 2 |
| Total de Queries | 3 |
| Operações de Leitura | 2 |
| Operações de Escrita | 1 |
| Conformidade VAMAP | 100% |

---

## 🗂️ Tabelas e Suas Dependências

### BANCOS

**Operações Identificadas**: 2 queries

| Operação | Tipo | Localização | Lógica de Negócio |
|----------|------|-------------|-------------------|
| SELECT | READ | bi14a.esf:L0500-L0503 | Carregar dropdown de bancos ativos |
| INSERT | CREATE | bi14a.esf:L1500-L1502 | Cadastro de novo banco (tela CADASTRO_BANCO) |

**Lógica de Negócio que Afeta BANCOS**:
- `LOG-005`: Validação de código de banco (bi14a.esf:L1200-L1215)
- `LOG-012`: Verificação de duplicidade (bi14a.esf:L1600-L1620)

**Campos Afetados**:
- `cod_banco`: Chave primária, usado em 2 queries
- `nome_banco`: Exibido em dropdown, atualizado em cadastro
- `ativo`: Flag de status, crítico para filtro de bancos ativos

**Dependências Downstream**:
- Tabela `AGENCIAS` (FK cod_banco)
- View `VW_BANCOS_ATIVOS`

**Riscos Identificados**:
- 🟢 LOW: Queries simples, sem complexidade

---

### AGENCIAS

**Operações Identificadas**: 1 query

| Operação | Tipo | Localização | Lógica de Negócio |
|----------|------|-------------|-------------------|
| SELECT | READ | bi14a.esf:L0700-L0705 | Listar agências por banco |

**Lógica de Negócio que Afeta AGENCIAS**:
- `LOG-008`: Filtro de agências por banco (bi14a.esf:L1300-L1320)

**Campos Afetados**:
- `cod_agencia`: Chave primária
- `cod_banco`: FK para BANCOS
- `nome_agencia`: Exibido em lista

**Dependências Upstream**:
- Tabela `BANCOS` (referenciada via FK)

**Riscos Identificados**:
- 🟢 LOW: Query simples com FK

---

## 🔄 Fluxo de Dados

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

---

## ⚠️ Zonas de Risco SQL

### Nenhum risco crítico identificado

✅ Todas as queries são simples e bem estruturadas.

---

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| Tabelas com operações READ | 2 |
| Tabelas com operações WRITE | 1 |
| Queries com >= 3 JOINs | 0 |
| SQL dinâmico detectado | 0 |
| Cursores declarados | 0 |

---

## ✅ Recomendações

1. **Criar View**: Query QRY-001 é recorrente, criar `vw_bancos_ativos`
2. **Stored Procedure**: Query QRY-015 deve virar `sp_cadastrar_banco`
3. **Adicionar Índice**: Criar índice em `bancos(ativo)` para performance
4. **Implementar Auditoria**: Adicionar trigger para rastrear alterações

---

**Fim do Relatório**
```

---

## Exemplo 5: Detecção de Riscos SQL

### Cenário
Identificar SQL dinâmico e mass delete.

### Input: claims_A_sql.json

```json
{
  "queries": [
    {
      "query_id": "QRY-050",
      "query_type": "DYNAMIC",
      "sql_statement": "PREPARE S1 FROM :WS-SQL-STRING",
      "affected_tables": ["UNKNOWN"],
      "operation_type": "EXECUTE",
      "evidence_pointer": "bi14a.esf:L2500-L2550"
    },
    {
      "query_id": "QRY-055",
      "query_type": "DELETE",
      "sql_statement": "DELETE FROM BANCOS",
      "affected_tables": ["BANCOS"],
      "operation_type": "DELETE",
      "evidence_pointer": "bi14a.esf:L3000-L3005"
    }
  ]
}
```

### Output: sql_risk_matrix.csv

```csv
query_id,risk_level,risk_type,description,evidence_pointer,recommendation
QRY-050,HIGH,DYNAMIC_SQL,SQL construído em runtime - difícil rastrear tabelas,bi14a.esf:L2500-L2550,Converter para stored procedure ou queries estáticas
QRY-055,HIGH,MASS_DELETE,DELETE sem WHERE clause - risco de deleção em massa,bi14a.esf:L3000-L3005,Adicionar WHERE clause ou implementar soft delete
```

### Output: data_lineage_report.md (seção riscos)

```markdown
## ⚠️ Zonas de Risco SQL

### 1. SQL Dinâmico
- **bi14a.esf:L2500-L2550**: Query construída em runtime
- **Risco**: Difícil rastrear tabelas afetadas, vulnerável a SQL injection
- **Recomendação**: Converter para stored procedures com parâmetros tipados

### 2. Mass Delete
- **bi14a.esf:L3000-L3005**: DELETE sem WHERE clause
- **Risco**: Pode deletar todas as linhas da tabela BANCOS
- **Recomendação**: Adicionar WHERE clause obrigatório ou implementar soft delete (flag ativo='N')
```

---

## Resumo de Comandos

| Comando | Função | Output Principal |
|---------|--------|------------------|
| `[EXT-SQL]` | Extração SQL especializada | claims_A_sql.json |
| `[VAL-SQL]` | Validação IA × VAMAP | sql_gate_status.json |
| `[ANA-SQL]` | Análise + Linhagem | database_schema.sql, data_lineage_report.md |

---

**Versão**: 1.0  
**Data**: 2025-12-28  
**Autor**: BMad Method v6.0


