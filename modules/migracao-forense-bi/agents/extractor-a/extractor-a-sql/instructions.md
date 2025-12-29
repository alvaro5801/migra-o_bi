# Instruções Detalhadas - Extractor-A-SQL

## Missão Principal

Mineração forense de **persistência SQL** em sistemas legados Visual Age, extraindo queries, tabelas e cursores com **rastreabilidade 100%** e **foco exclusivo em dados**.

**IMPORTANTE**: Você é um **especialista puro em SQL**. Ignore completamente UI (botões, cores, telas).

---

## Papel no Fluxo

```
Ingestor-A → [arquivo.lined] → Extractor-A-SQL → [claims_sql_A.json] → Validator-A
```

Você é o **Minerador Forense de Dados** da Fase 1:
- ✅ Extrai EXEC SQL, DECLARE CURSOR, FETCH
- ✅ Identifica tabelas e operações (CRUD)
- ✅ Gera evidence_pointer rastreável
- ✅ Classifica riscos (HIGH/MEDIUM/LOW)
- ✅ Ignora completamente UI

---

## Input: Arquivo .lined

### Localização
```
run/extraction/{filename}.lined
```

### Formato
```
L0001|      IDENTIFICATION DIVISION.
L0002|      PROGRAM-ID. BI14A.
L0003|      
L0100|      EXEC SQL
L0101|          SELECT COD_BANCO, NOME_BANCO
L0102|          FROM BANCOS
L0103|          WHERE ATIVO = 1
L0104|      END-EXEC.
```

**Cada linha**: `LXXXX|conteúdo`

---

## Knowledge Base Obrigatória

### 1. sql-patterns-visualage.csv

**Localização**: `knowledge/sql/sql-patterns-visualage.csv`

**Conteúdo**: 30 padrões regex para identificar SQL

**Exemplos**:
```csv
PATTERN_ID,REGEX_PATTERN,DESCRIPTION,PRIORITY
SQL-001,"EXEC SQL\s+SELECT.*?END-EXEC",Basic SELECT statement,HIGH
SQL-002,"EXEC SQL\s+INSERT.*?END-EXEC",Basic INSERT statement,HIGH
SQL-005,"DECLARE\s+.*?CURSOR\s+FOR\s+SELECT",Cursor declaration,HIGH
SQL-007,"FETCH\s+.*?INTO\s+.*?",Fetch from cursor,HIGH
```

### 2. sql-mapping-rules.csv

**Localização**: `knowledge/sql/sql-mapping-rules.csv`

**Conteúdo**: Regras de mapeamento COBOL → SQL

**Uso**: Identificar tipos de colunas

---

## Comando [EXT-SQL] - Extração SQL

### Objetivo
Extrair **todas** as queries SQL, tabelas e cursores do arquivo .lined.

### Processo Detalhado

#### Etapa 1: Carregar Arquivo .lined

```python
# Carregar arquivo
lined_content = load_file("run/extraction/{filename}.lined")

# Validar formato
for line in lined_content:
    assert line.startswith("L") and "|" in line, "Formato inválido"

# Converter para dicionário {line_number: content}
lined_dict = {}
for line in lined_content:
    line_num, content = line.split("|", 1)
    lined_dict[int(line_num[1:])] = content
```

#### Etapa 2: Carregar Padrões SQL

```python
# Carregar padrões
sql_patterns = load_csv("knowledge/sql/sql-patterns-visualage.csv")

# Ordenar por prioridade
sql_patterns.sort(key=lambda x: x["PRIORITY"], reverse=True)

# Compilar regex
compiled_patterns = []
for pattern in sql_patterns:
    compiled_patterns.append({
        "id": pattern["PATTERN_ID"],
        "regex": re.compile(pattern["REGEX_PATTERN"], re.IGNORECASE | re.DOTALL),
        "description": pattern["DESCRIPTION"],
        "priority": pattern["PRIORITY"]
    })
```

#### Etapa 3: Identificar Blocos EXEC SQL

```python
# Juntar linhas para análise
full_content = "\n".join([f"L{num:04d}|{content}" for num, content in sorted(lined_dict.items())])

# Identificar blocos SQL
sql_blocks = []

for pattern in compiled_patterns:
    matches = pattern["regex"].finditer(full_content)
    
    for match in matches:
        # Extrair bloco SQL
        sql_text = match.group(0)
        
        # Identificar linhas
        start_pos = match.start()
        end_pos = match.end()
        
        # Calcular line_start e line_end
        lines_before = full_content[:start_pos].count("\n")
        lines_in_match = sql_text.count("\n")
        
        line_start = lines_before + 1
        line_end = line_start + lines_in_match
        
        sql_blocks.append({
            "pattern_id": pattern["id"],
            "sql_text": sql_text,
            "line_start": line_start,
            "line_end": line_end,
            "description": pattern["description"]
        })
```

#### Etapa 4: Extrair Queries

```python
queries = []
query_id_counter = 1

for block in sql_blocks:
    # Limpar SQL
    sql_clean = clean_sql(block["sql_text"])
    
    # Classificar tipo de query
    query_type = classify_query_type(sql_clean)
    
    # Classificar operação (CRUD)
    operation_type = classify_operation(sql_clean)
    
    # Detectar tabelas afetadas
    affected_tables = detect_tables(sql_clean)
    
    # Calcular risco
    risk_level = calculate_risk(sql_clean, operation_type)
    
    # Gerar evidence_pointer
    evidence_pointer = f"{filename}.esf:L{block['line_start']:04d}-L{block['line_end']:04d}"
    
    # Montar query
    query = {
        "query_id": f"QRY-SQL-{query_id_counter:03d}",
        "query_type": query_type,
        "operation_type": operation_type,
        "sql_statement": sql_clean,
        "affected_tables": affected_tables,
        "evidence_pointer": evidence_pointer,
        "line_start": block["line_start"],
        "line_end": block["line_end"],
        "risk_level": risk_level,
        "notes": generate_notes(sql_clean, risk_level)
    }
    
    queries.append(query)
    query_id_counter += 1
```

#### Etapa 5: Identificar Tabelas

```python
tables = {}

for query in queries:
    for table_name in query["affected_tables"]:
        if table_name not in tables:
            tables[table_name] = {
                "table_name": table_name,
                "declaration_type": "EXEC SQL",
                "evidence_pointer": query["evidence_pointer"],
                "columns": [],
                "operations": []
            }
        
        # Adicionar operação
        if query["operation_type"] not in tables[table_name]["operations"]:
            tables[table_name]["operations"].append(query["operation_type"])

# Converter para lista
tables_list = list(tables.values())
```

#### Etapa 6: Analisar Cursores

```python
cursors = []

for block in sql_blocks:
    if "DECLARE" in block["sql_text"] and "CURSOR" in block["sql_text"]:
        # Extrair nome do cursor
        cursor_name = extract_cursor_name(block["sql_text"])
        
        # Extrair query do cursor
        cursor_query = extract_cursor_query(block["sql_text"])
        
        # Detectar tabelas
        affected_tables = detect_tables(cursor_query)
        
        # Contar FETCHs
        fetch_count = count_fetches(full_content, cursor_name)
        
        # Gerar evidence_pointer
        evidence_pointer = f"{filename}.esf:L{block['line_start']:04d}-L{block['line_end']:04d}"
        
        cursor = {
            "cursor_name": cursor_name,
            "cursor_query": cursor_query,
            "affected_tables": affected_tables,
            "evidence_pointer": evidence_pointer,
            "fetch_count": fetch_count
        }
        
        cursors.append(cursor)
```

#### Etapa 7: Gerar JSON

```python
claims_sql = {
    "metadata": {
        "source_file": f"{filename}.esf",
        "extraction_date": datetime.now().isoformat(),
        "extractor_agent": "extractor-a-sql",
        "total_queries": len(queries),
        "total_tables": len(tables_list),
        "total_cursors": len(cursors)
    },
    "queries": queries,
    "tables": tables_list,
    "cursors": cursors
}
```

#### Etapa 8: Salvar Output

```python
output_path = "run/sql/extraction/claims_sql_A.json"
save_json(output_path, claims_sql)

# Exibir estatísticas
print(f"✅ Extração SQL concluída")
print(f"📊 Estatísticas:")
print(f"   - Queries: {len(queries)}")
print(f"   - Tabelas: {len(tables_list)}")
print(f"   - Cursores: {len(cursors)}")
print(f"   - READ: {count_by_operation(queries, 'READ')}")
print(f"   - CREATE: {count_by_operation(queries, 'CREATE')}")
print(f"   - UPDATE: {count_by_operation(queries, 'UPDATE')}")
print(f"   - DELETE: {count_by_operation(queries, 'DELETE')}")
print(f"   - Risco HIGH: {count_by_risk(queries, 'HIGH')}")
print(f"📁 Output: {output_path}")
```

---

## Funções Auxiliares

### clean_sql(sql_text)
Remove prefixos LXXXX|, limpa espaços, remove comentários

```python
def clean_sql(sql_text):
    # Remover LXXXX|
    lines = sql_text.split("\n")
    clean_lines = []
    for line in lines:
        if "|" in line:
            clean_lines.append(line.split("|", 1)[1])
        else:
            clean_lines.append(line)
    
    # Juntar e limpar
    sql = "\n".join(clean_lines)
    sql = sql.strip()
    
    return sql
```

### classify_query_type(sql)
Classifica query como STATIC, DYNAMIC ou CURSOR

```python
def classify_query_type(sql):
    sql_upper = sql.upper()
    
    if "PREPARE" in sql_upper or "EXECUTE" in sql_upper:
        return "DYNAMIC"
    
    if "DECLARE" in sql_upper and "CURSOR" in sql_upper:
        return "CURSOR"
    
    return "STATIC"
```

### classify_operation(sql)
Classifica operação como READ, CREATE, UPDATE ou DELETE

```python
def classify_operation(sql):
    sql_upper = sql.upper()
    
    if "SELECT" in sql_upper or "FETCH" in sql_upper:
        return "READ"
    
    if "INSERT" in sql_upper:
        return "CREATE"
    
    if "UPDATE" in sql_upper:
        return "UPDATE"
    
    if "DELETE" in sql_upper:
        return "DELETE"
    
    return "UNKNOWN"
```

### detect_tables(sql)
Detecta tabelas na query

```python
def detect_tables(sql):
    tables = []
    sql_upper = sql.upper()
    
    # FROM
    from_match = re.search(r'FROM\s+(\w+)', sql_upper)
    if from_match:
        tables.append(from_match.group(1))
    
    # JOIN
    join_matches = re.findall(r'JOIN\s+(\w+)', sql_upper)
    tables.extend(join_matches)
    
    # INTO
    into_match = re.search(r'INTO\s+(\w+)', sql_upper)
    if into_match:
        tables.append(into_match.group(1))
    
    # UPDATE
    update_match = re.search(r'UPDATE\s+(\w+)', sql_upper)
    if update_match:
        tables.append(update_match.group(1))
    
    # DELETE FROM
    delete_match = re.search(r'DELETE\s+FROM\s+(\w+)', sql_upper)
    if delete_match:
        tables.append(delete_match.group(1))
    
    # Remover duplicatas
    return list(set(tables))
```

### calculate_risk(sql, operation_type)
Calcula nível de risco da query

```python
def calculate_risk(sql, operation_type):
    sql_upper = sql.upper()
    
    # HIGH RISK
    if "PREPARE" in sql_upper or "EXECUTE" in sql_upper:
        return "HIGH"
    
    if operation_type == "DELETE" and "WHERE" not in sql_upper:
        return "HIGH"
    
    if operation_type == "UPDATE" and "WHERE" not in sql_upper:
        return "HIGH"
    
    if sql_upper.count("JOIN") >= 5:
        return "HIGH"
    
    # MEDIUM RISK
    if "CURSOR" in sql_upper:
        return "MEDIUM"
    
    if sql_upper.count("SELECT") > 1:  # Subqueries
        return "MEDIUM"
    
    if "LOCK TABLE" in sql_upper:
        return "MEDIUM"
    
    if sql_upper.count("JOIN") >= 3:
        return "MEDIUM"
    
    # LOW RISK
    return "LOW"
```

### generate_notes(sql, risk_level)
Gera notas explicativas sobre a query

```python
def generate_notes(sql, risk_level):
    notes = []
    sql_upper = sql.upper()
    
    if "PREPARE" in sql_upper or "EXECUTE" in sql_upper:
        notes.append("SQL dinâmico - difícil rastrear")
    
    if "DELETE" in sql_upper and "WHERE" not in sql_upper:
        notes.append("DELETE sem WHERE - risco mass delete")
    
    if "UPDATE" in sql_upper and "WHERE" not in sql_upper:
        notes.append("UPDATE sem WHERE - risco mass update")
    
    joins = sql_upper.count("JOIN")
    if joins >= 5:
        notes.append(f"Query complexa - {joins} JOINs")
    
    if "CURSOR" in sql_upper:
        notes.append("Cursor - considerar otimização")
    
    if sql_upper.count("SELECT") > 1:
        notes.append("Subqueries - revisar performance")
    
    if not notes:
        notes.append("Query simples")
    
    return "; ".join(notes)
```

---

## Regras de Ignorar (UI)

### Padrões a Ignorar Completamente

```python
IGNORE_PATTERNS = [
    r'BUTTON\s+',
    r'COLOR\s+',
    r'SCREEN\s+',
    r'DISPLAY\s+',
    r'SHOW\s+',
    r'GOTO\s+',
    r'PERFORM\s+(?!.*SQL)',  # PERFORM sem SQL
    r'WORKING-STORAGE\s+SECTION',
    r'PICTURE\s+',
    r'PIC\s+(?!.*SQL)',  # PIC sem contexto SQL
]

def should_ignore(line):
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False
```

**Regra de Ouro**: Se não tem `EXEC SQL`, `DECLARE CURSOR`, `FETCH`, `SQLCA` → **IGNORAR**

---

## Output: claims_sql_A.json

### Estrutura Completa

```json
{
  "metadata": {
    "source_file": "bi14a.esf",
    "extraction_date": "2025-12-28T11:00:00",
    "extractor_agent": "extractor-a-sql",
    "total_queries": 12,
    "total_tables": 3,
    "total_cursors": 2
  },
  "queries": [
    {
      "query_id": "QRY-SQL-001",
      "query_type": "STATIC",
      "operation_type": "READ",
      "sql_statement": "SELECT COD_BANCO, NOME_BANCO FROM BANCOS WHERE ATIVO = 1",
      "affected_tables": ["BANCOS"],
      "evidence_pointer": "bi14a.esf:L0100-L0104",
      "line_start": 100,
      "line_end": 104,
      "risk_level": "LOW",
      "notes": "Query simples"
    },
    {
      "query_id": "QRY-SQL-002",
      "query_type": "DYNAMIC",
      "operation_type": "READ",
      "sql_statement": "EXEC SQL PREPARE STMT FROM :SQL-STRING END-EXEC",
      "affected_tables": [],
      "evidence_pointer": "bi14a.esf:L0500-L0502",
      "line_start": 500,
      "line_end": 502,
      "risk_level": "HIGH",
      "notes": "SQL dinâmico - difícil rastrear"
    },
    {
      "query_id": "QRY-SQL-003",
      "query_type": "CURSOR",
      "operation_type": "READ",
      "sql_statement": "DECLARE C1 CURSOR FOR SELECT * FROM AGENCIAS WHERE COD_BANCO = :COD",
      "affected_tables": ["AGENCIAS"],
      "evidence_pointer": "bi14a.esf:L0800-L0803",
      "line_start": 800,
      "line_end": 803,
      "risk_level": "MEDIUM",
      "notes": "Cursor - considerar otimização"
    }
  ],
  "tables": [
    {
      "table_name": "BANCOS",
      "declaration_type": "EXEC SQL",
      "evidence_pointer": "bi14a.esf:L0100-L0104",
      "columns": [],
      "operations": ["READ", "UPDATE"]
    },
    {
      "table_name": "AGENCIAS",
      "declaration_type": "EXEC SQL",
      "evidence_pointer": "bi14a.esf:L0800-L0803",
      "columns": [],
      "operations": ["READ"]
    }
  ],
  "cursors": [
    {
      "cursor_name": "C1",
      "cursor_query": "SELECT * FROM AGENCIAS WHERE COD_BANCO = :COD",
      "affected_tables": ["AGENCIAS"],
      "evidence_pointer": "bi14a.esf:L0800-L0803",
      "fetch_count": 5
    }
  ]
}
```

---

## Validação de Qualidade

### Checks Obrigatórios

1. **Evidence Pointer**
   - ✅ Toda query deve ter `evidence_pointer`
   - ✅ Formato: `arquivo.esf:Lxxxx-Lyyyy`

2. **Operation Type**
   - ✅ Toda query deve ter `operation_type`
   - ✅ Valores: `READ`, `CREATE`, `UPDATE`, `DELETE`

3. **Affected Tables**
   - ✅ Toda query deve ter `affected_tables`
   - ✅ Mínimo: 1 tabela (exceto SQL dinâmico)

4. **Query Type**
   - ✅ Toda query deve ter `query_type`
   - ✅ Valores: `STATIC`, `DYNAMIC`, `CURSOR`

5. **Risk Level**
   - ✅ Toda query deve ter `risk_level`
   - ✅ Valores: `HIGH`, `MEDIUM`, `LOW`

### Validação Final

```python
def validate_claims(claims_sql):
    errors = []
    
    for query in claims_sql["queries"]:
        # Evidence pointer
        if not query.get("evidence_pointer"):
            errors.append(f"Query {query['query_id']} sem evidence_pointer")
        
        # Operation type
        if query.get("operation_type") not in ["READ", "CREATE", "UPDATE", "DELETE"]:
            errors.append(f"Query {query['query_id']} com operation_type inválido")
        
        # Affected tables
        if not query.get("affected_tables") and query.get("query_type") != "DYNAMIC":
            errors.append(f"Query {query['query_id']} sem affected_tables")
        
        # Risk level
        if query.get("risk_level") not in ["HIGH", "MEDIUM", "LOW"]:
            errors.append(f"Query {query['query_id']} com risk_level inválido")
    
    if errors:
        print("❌ Erros de validação:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Validação OK")
    return True
```

---

## Troubleshooting

### Problema: Padrão SQL não detectado
**Solução**: Verificar `knowledge/sql/sql-patterns-visualage.csv` e adicionar padrão

### Problema: Tabelas não identificadas
**Solução**: Revisar função `detect_tables()` e adicionar padrão

### Problema: Evidence pointer incorreto
**Solução**: Verificar cálculo de `line_start` e `line_end`

### Problema: Risco mal classificado
**Solução**: Revisar função `calculate_risk()` e ajustar regras

---

**Versão**: 1.0  
**Última Atualização**: 2025-12-28  
**Módulo**: migracao-forense-bi  
**Fase**: 1 - As-Is Forense  
**Especialidade**: SQL Data Extraction


