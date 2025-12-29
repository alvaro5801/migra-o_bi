# Workflow: [VAL-SQL] - Validar Ledger SQL contra VAMAP

## 🛡️ Objetivo

Validar o **Ledger de Dados** (`claim_ledger_sql.json`) contra o log oficial do VAMAP (`vamap_sql.log`), garantindo **Grounding de 100%** e fechando o **Gate G1-SQL** com PASS ou FAIL.

---

## 📋 Pré-requisitos

### Arquivos Obrigatórios

1. ✅ **claim_ledger_sql.json**: Ledger de Dados oficial
   - Path: `run/sql/analysis/claim_ledger_sql.json`
   - Gerado por: `reconciliador-a-sql`

2. ✅ **vamap_sql.log**: Log VAMAP focado em SQL
   - Path: `run/sql/extraction/vamap_sql.log`
   - Gerado por: `ingestor-a-sql`

3. ✅ **{filename}.lined**: Arquivo .lined para validar evidence_pointer
   - Path: `run/extraction/{filename}.lined`
   - Gerado por: `ingestor-a`

### Bloqueio de Gate

Se algum arquivo não existir, **BLOQUEAR** validação:

```
❌ BLOQUEIO: Arquivos de validação incompletos

O Validator-A-SQL requer:
- claim_ledger_sql.json (Ledger de Dados)
- vamap_sql.log (VAMAP oficial)
- {filename}.lined (Evidence pointers)

Status atual:
- Ledger: NÃO ENCONTRADO
- VAMAP: NÃO ENCONTRADO
- Lined: NÃO ENCONTRADO

AÇÃO REQUERIDA:
1. Executar [ING-SQL] para gerar vamap_sql.log
2. Executar [REC-SQL] para gerar claim_ledger_sql.json
3. Retornar para [VAL-SQL]

STATUS: VALIDAÇÃO SQL BLOQUEADA
```

---

## 🔄 Fluxo de Execução

### Step 1: Verificar Gate

**Ação**: Confirmar que Ledger, VAMAP e .lined existem

```python
# Verificar arquivos
ledger_path = "run/sql/analysis/claim_ledger_sql.json"
vamap_path = "run/sql/extraction/vamap_sql.log"
lined_path = "run/extraction/{filename}.lined"

if not os.path.exists(ledger_path):
    print("❌ BLOQUEIO: Ledger não encontrado")
    exit(1)

if not os.path.exists(vamap_path):
    print("❌ BLOQUEIO: VAMAP não encontrado")
    exit(1)

if not os.path.exists(lined_path):
    print("❌ BLOQUEIO: Arquivo .lined não encontrado")
    exit(1)

print("✅ Gate verificado: todos os arquivos existem")
```

---

### Step 2: Carregar Ledger

**Ação**: Ler `claim_ledger_sql.json`

```python
import json

# Carregar Ledger
with open(ledger_path, 'r', encoding='utf-8') as f:
    ledger = json.load(f)

# Validar estrutura
assert 'metadata' in ledger, "❌ Seção 'metadata' não encontrada no Ledger"
assert 'queries' in ledger, "❌ Seção 'queries' não encontrada no Ledger"

total_queries = len(ledger['queries'])
print(f"✅ Ledger carregado: {total_queries} queries")
```

**Validações**:
- ✅ JSON bem formado?
- ✅ Seção `metadata` existe?
- ✅ Seção `queries` existe?
- ✅ Cada query tem `query_id`, `sql_statement`, `affected_tables`, `evidence_pointer`?

---

### Step 3: Parsear VAMAP

**Ação**: Parsear `vamap_sql.log`

```python
# Parsear VAMAP
vamap_data = parse_vamap(vamap_path)

# Estrutura esperada:
# {
#   "tables": [
#     {
#       "table_name": "BANCOS",
#       "columns": [
#         {"name": "COD_BANCO", "type": "PIC 9(4)"},
#         {"name": "NOME_BANCO", "type": "PIC X(50)"}
#       ]
#     }
#   ],
#   "sql_statements": [
#     {
#       "statement": "SELECT COD_BANCO, NOME_BANCO FROM BANCOS...",
#       "type": "SELECT",
#       "tables": ["BANCOS"]
#     }
#   ]
# }

print(f"✅ VAMAP parseado: {len(vamap_data['tables'])} tabelas, {len(vamap_data['sql_statements'])} SQL statements")
```

**Extrair**:
- ✅ Tabelas declaradas (seção `DATA DIVISION`)
- ✅ Colunas declaradas (seção `WORKING-STORAGE`)
- ✅ SQL statements (seção `EXEC SQL`)
- ✅ Cursores (seção `DECLARE CURSOR`)

---

### Step 4: Validar VAMAP Grounding

**Ação**: Para cada query no Ledger, buscar prova no VAMAP

```python
queries_with_proof = 0
queries_without_proof = 0
validation_results = []

for query in ledger['queries']:
    query_id = query['query_id']
    sql_statement = query['sql_statement']
    affected_tables = query['affected_tables']
    
    # Validar tabelas no VAMAP
    tables_found = []
    tables_not_found = []
    
    for table in affected_tables:
        if table_exists_in_vamap(table, vamap_data):
            tables_found.append(table)
        else:
            tables_not_found.append(table)
    
    # Validar SQL statement no VAMAP
    sql_found = sql_exists_in_vamap(sql_statement, vamap_data)
    
    # Calcular grounding
    if len(tables_not_found) == 0 and sql_found:
        grounding_status = "GROUNDED"
        queries_with_proof += 1
    else:
        grounding_status = "NOT GROUNDED"
        queries_without_proof += 1
    
    validation_results.append({
        "query_id": query_id,
        "grounding_status": grounding_status,
        "tables_found": tables_found,
        "tables_not_found": tables_not_found,
        "sql_found": sql_found
    })
    
    print(f"{'✅' if grounding_status == 'GROUNDED' else '❌'} Query {query_id}: {grounding_status}")

print(f"\n📊 Grounding Summary:")
print(f"   - Queries com prova: {queries_with_proof}")
print(f"   - Queries sem prova: {queries_without_proof}")
```

**Verificações**:
1. ✅ Tabela existe no VAMAP?
2. ✅ Colunas existem no VAMAP?
3. ✅ SQL statement existe no VAMAP?

---

### Step 5: Validar Evidence Pointer

**Ação**: Verificar que `evidence_pointer` aponta para SQL válido no `.lined`

```python
evidence_pointer_errors = 0

for query in ledger['queries']:
    query_id = query['query_id']
    evidence_pointer = query['evidence_pointer']
    
    # Parsear evidence pointer: "bi14a.esf:L0100-L0104"
    filename, line_range = evidence_pointer.split(':')
    start_line, end_line = parse_line_range(line_range)
    
    # Ler linhas do .lined
    lines = read_lined_file(lined_path, start_line, end_line)
    
    # Validar que contém EXEC SQL
    has_exec_sql = any("EXEC SQL" in line for line in lines)
    has_end_exec = any("END-EXEC" in line for line in lines)
    
    if has_exec_sql and has_end_exec:
        print(f"✅ Query {query_id}: Evidence pointer válido")
    else:
        print(f"❌ Query {query_id}: Evidence pointer inválido (SQL não encontrado)")
        evidence_pointer_errors += 1

print(f"\n📊 Evidence Pointer Summary:")
print(f"   - Evidence pointers válidos: {total_queries - evidence_pointer_errors}")
print(f"   - Evidence pointers inválidos: {evidence_pointer_errors}")
```

**Verificações**:
1. ✅ Linhas existem no .lined?
2. ✅ Linhas contêm EXEC SQL?
3. ✅ SQL é bem formado?

---

### Step 6: Validar Type Mapping

**Ação**: Verificar tipos de dados contra `sql-mapping-rules.csv`

```python
# Carregar regras de mapeamento
mapping_rules = load_sql_mapping_rules("knowledge/sql/sql-mapping-rules.csv")

type_mapping_errors = 0

for query in ledger['queries']:
    query_id = query['query_id']
    affected_tables = query['affected_tables']
    
    # Para cada tabela, validar colunas
    for table in affected_tables:
        columns = get_columns_from_vamap(table, vamap_data)
        
        for column in columns:
            cobol_type = column['type']
            expected_sql_type = get_sql_type_from_rules(cobol_type, mapping_rules)
            
            if expected_sql_type:
                print(f"✅ Coluna {column['name']}: {cobol_type} -> {expected_sql_type}")
            else:
                print(f"⚠️ Coluna {column['name']}: {cobol_type} -> Mapeamento não encontrado")
                type_mapping_errors += 1

print(f"\n📊 Type Mapping Summary:")
print(f"   - Type mappings corretos: {total_columns - type_mapping_errors}")
print(f"   - Type mappings incorretos: {type_mapping_errors}")
```

**Verificações**:
1. ✅ Tipo COBOL é válido?
2. ✅ Mapeamento para SQL é correto?
3. ✅ Segue sql-mapping-rules.csv?

---

### Step 7: Calcular Grounding Score

**Ação**: Calcular % de queries com prova no VAMAP

```python
# Calcular Grounding Score
grounding_score = (queries_with_proof / total_queries) * 100

print(f"\n📈 Grounding Score: {grounding_score:.1f}%")

# Determinar threshold
if grounding_score == 100.0:
    threshold = "EXCELLENT"
elif grounding_score >= 95.0:
    threshold = "GOOD"
elif grounding_score >= 90.0:
    threshold = "ACCEPTABLE"
elif grounding_score >= 80.0:
    threshold = "POOR"
else:
    threshold = "FAIL"

print(f"   Threshold: {threshold}")
```

**Fórmula**:

```
Grounding Score = (queries_with_proof / total_queries) * 100
```

**Thresholds**:
- **EXCELLENT**: 100%
- **GOOD**: 95-99%
- **ACCEPTABLE**: 90-94%
- **POOR**: 80-89%
- **FAIL**: < 80%

---

### Step 8: Fechar Gate G1-SQL

**Ação**: Decidir PASS ou FAIL

```python
# Determinar status do Gate
critical_issues = []

# Issue 1: Queries sem prova no VAMAP
if queries_without_proof > 0:
    critical_issues.append(f"{queries_without_proof} queries sem prova no VAMAP")

# Issue 2: Evidence pointers inválidos
if evidence_pointer_errors > 0:
    critical_issues.append(f"{evidence_pointer_errors} evidence pointers inválidos")

# Issue 3: Grounding Score < 100%
if grounding_score < 100.0:
    critical_issues.append(f"Grounding Score {grounding_score:.1f}% (esperado 100%)")

# Decidir PASS ou FAIL
if len(critical_issues) == 0 and grounding_score == 100.0:
    gate_status = "PASS"
    print("\n🎉 GATE G1-SQL: PASS")
else:
    gate_status = "FAIL"
    print("\n❌ GATE G1-SQL: FAIL")
    print("\nIssues Críticos:")
    for i, issue in enumerate(critical_issues, 1):
        print(f"   {i}. {issue}")
```

**Critérios**:

### ✅ PASS
- Grounding Score = 100%
- Zero issues críticos
- Todos os evidence pointers válidos

### ❌ FAIL
- Grounding Score < 100%
- Issues críticos detectados
- Evidence pointers inválidos

---

### Step 9: Gerar Outputs

**Ação**: Gerar `gate_status_sql.json` e `validation_report_sql.md`

#### Output 1: gate_status_sql.json

```python
# Gerar gate_status_sql.json
gate_status_data = {
    "sql_gate_status": gate_status,
    "validation_date": datetime.now().isoformat(),
    "validator_agent": "validator-a-sql",
    "grounding_score": grounding_score,
    "conformidade_sql_percentage": grounding_score,
    "total_queries_validated": total_queries,
    "queries_with_vamap_proof": queries_with_proof,
    "queries_without_vamap_proof": queries_without_proof,
    "type_mapping_errors": type_mapping_errors,
    "evidence_pointer_errors": evidence_pointer_errors,
    "critical_issues": critical_issues,
    "recommendations": generate_recommendations(gate_status, critical_issues)
}

# Salvar
with open("run/sql/validation/gate_status_sql.json", 'w', encoding='utf-8') as f:
    json.dump(gate_status_data, f, indent=2, ensure_ascii=False)

print("✅ Gate status salvo: run/sql/validation/gate_status_sql.json")
```

#### Output 2: validation_report_sql.md

```python
# Gerar validation_report_sql.md
report = generate_validation_report(
    gate_status=gate_status,
    grounding_score=grounding_score,
    total_queries=total_queries,
    queries_with_proof=queries_with_proof,
    queries_without_proof=queries_without_proof,
    validation_results=validation_results,
    type_mapping_errors=type_mapping_errors,
    evidence_pointer_errors=evidence_pointer_errors,
    critical_issues=critical_issues
)

# Salvar
with open("run/sql/validation/validation_report_sql.md", 'w', encoding='utf-8') as f:
    f.write(report)

print("✅ Validation report salvo: run/sql/validation/validation_report_sql.md")
```

---

## 📊 Exemplo de Execução

### Entrada

```bash
[VAL-SQL] bi14a.esf
```

### Processamento

```
🛡️ Validator-A-SQL - Auditor de Integridade de Dados

📋 Step 1: Verificar Gate
✅ Ledger encontrado: run/sql/analysis/claim_ledger_sql.json
✅ VAMAP encontrado: run/sql/extraction/vamap_sql.log
✅ Arquivo .lined encontrado: run/extraction/bi14a.lined

📋 Step 2: Carregar Ledger
✅ Ledger carregado: 12 queries

📋 Step 3: Parsear VAMAP
✅ VAMAP parseado: 3 tabelas, 12 SQL statements

📋 Step 4: Validar VAMAP Grounding
✅ Query QRY-SQL-001: GROUNDED
✅ Query QRY-SQL-002: GROUNDED
✅ Query QRY-SQL-003: GROUNDED
✅ Query QRY-SQL-004: GROUNDED
✅ Query QRY-SQL-005: GROUNDED
✅ Query QRY-SQL-006: GROUNDED
✅ Query QRY-SQL-007: GROUNDED
✅ Query QRY-SQL-008: GROUNDED
✅ Query QRY-SQL-009: GROUNDED
✅ Query QRY-SQL-010: GROUNDED
✅ Query QRY-SQL-011: GROUNDED
✅ Query QRY-SQL-012: GROUNDED

📊 Grounding Summary:
   - Queries com prova: 12
   - Queries sem prova: 0

📋 Step 5: Validar Evidence Pointer
✅ Query QRY-SQL-001: Evidence pointer válido
✅ Query QRY-SQL-002: Evidence pointer válido
✅ Query QRY-SQL-003: Evidence pointer válido
✅ Query QRY-SQL-004: Evidence pointer válido
✅ Query QRY-SQL-005: Evidence pointer válido
✅ Query QRY-SQL-006: Evidence pointer válido
✅ Query QRY-SQL-007: Evidence pointer válido
✅ Query QRY-SQL-008: Evidence pointer válido
✅ Query QRY-SQL-009: Evidence pointer válido
✅ Query QRY-SQL-010: Evidence pointer válido
✅ Query QRY-SQL-011: Evidence pointer válido
✅ Query QRY-SQL-012: Evidence pointer válido

📊 Evidence Pointer Summary:
   - Evidence pointers válidos: 12
   - Evidence pointers inválidos: 0

📋 Step 6: Validar Type Mapping
✅ Coluna COD_BANCO: PIC 9(4) -> INT
✅ Coluna NOME_BANCO: PIC X(50) -> NVARCHAR(50)
✅ Coluna ATIVO: PIC 9(1) -> INT
...

📊 Type Mapping Summary:
   - Type mappings corretos: 15
   - Type mappings incorretos: 0

📋 Step 7: Calcular Grounding Score
📈 Grounding Score: 100.0%
   Threshold: EXCELLENT

📋 Step 8: Fechar Gate G1-SQL
🎉 GATE G1-SQL: PASS

📋 Step 9: Gerar Outputs
✅ Gate status salvo: run/sql/validation/gate_status_sql.json
✅ Validation report salvo: run/sql/validation/validation_report_sql.md
```

### Saída

```
✅ Validação SQL concluída

🛡️ Status do Gate G1-SQL: PASS

📊 Estatísticas:
   - Queries validadas: 12
   - Com prova VAMAP: 12
   - Sem prova VAMAP: 0
   - Grounding Score: 100%
   - Conformidade SQL: 100%
   - Issues críticos: 0

📄 Outputs:
   - Gate Status: run/sql/validation/gate_status_sql.json
   - Validation Report: run/sql/validation/validation_report_sql.md

🚦 Gate G1-SQL: PASS
```

---

## 🔒 Regras de Validação

### 1. VAMAP Grounding (CRITICAL)

**Regra**: Para cada query no Ledger, buscar no VAMAP:
- ✅ Tabela existe no VAMAP?
- ✅ Colunas existem no VAMAP?
- ✅ SQL statement existe no VAMAP?

**Severidade**: CRITICAL  
**Ação em caso de falha**: Gate = FAIL

---

### 2. Evidence Pointer (CRITICAL)

**Regra**: Para cada evidence_pointer:
- ✅ Linhas existem no .lined?
- ✅ Linhas contêm EXEC SQL?
- ✅ SQL é bem formado?

**Severidade**: CRITICAL  
**Ação em caso de falha**: Gate = FAIL

---

### 3. Type Mapping (HIGH)

**Regra**: Para cada coluna:
- ✅ Tipo COBOL é válido?
- ✅ Mapeamento para SQL é correto?
- ✅ Segue sql-mapping-rules.csv?

**Severidade**: HIGH  
**Ação em caso de falha**: Adicionar a issues (não bloqueia Gate)

---

### 4. Reconciliation Status (HIGH)

**Regra**: Queries com status CONFLICT ou HALLUCINATION:
- ⚠️ CONFLICT: Revisar manualmente
- ❌ HALLUCINATION: Falha crítica
- ⚠️ OMISSION: Adicionar ao Ledger

**Severidade**: HIGH  
**Ação em caso de falha**: Adicionar a issues

---

## 🎯 Outputs

### 1. gate_status_sql.json

**Path**: `run/sql/validation/gate_status_sql.json`

**Estrutura**:

```json
{
  "sql_gate_status": "PASS",
  "validation_date": "2025-12-28T10:30:00Z",
  "validator_agent": "validator-a-sql",
  "grounding_score": 100.0,
  "conformidade_sql_percentage": 100.0,
  "total_queries_validated": 12,
  "queries_with_vamap_proof": 12,
  "queries_without_vamap_proof": 0,
  "type_mapping_errors": 0,
  "evidence_pointer_errors": 0,
  "critical_issues": [],
  "recommendations": [
    "Todas as queries têm prova no VAMAP",
    "Todos os evidence pointers são válidos",
    "Type mapping está correto"
  ]
}
```

---

### 2. validation_report_sql.md

**Path**: `run/sql/validation/validation_report_sql.md`

**Seções**:
1. Sumário Executivo
2. Status do Gate G1-SQL
3. Grounding Score
4. Validação VAMAP
5. Validação Evidence Pointer
6. Validação Type Mapping
7. Issues Críticos
8. Recomendações

---

## ✅ Checklist de Qualidade

### Validações Obrigatórias

- [ ] Ledger existe?
- [ ] VAMAP existe?
- [ ] Arquivo .lined existe?
- [ ] JSON bem formado?
- [ ] Grounding Score calculado?
- [ ] Gate status gerado?
- [ ] Validation report gerado?
- [ ] Gate fechado (PASS ou FAIL)?

### Verificações de Integridade

- [ ] Todas as queries têm prova no VAMAP?
- [ ] Todos os evidence pointers são válidos?
- [ ] Todos os types estão corretos?
- [ ] Zero issues críticos?

---

**Validator-A-SQL**: Guardião do Gate G1-SQL, garantindo 100% de grounding e integridade! 🛡️

