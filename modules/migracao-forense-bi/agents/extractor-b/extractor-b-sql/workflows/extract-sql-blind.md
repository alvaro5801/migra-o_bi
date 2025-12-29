# Workflow: [EXT-SQL-B] - Extração SQL CEGA (Blind Mode)

## Objetivo
Extrair **todas** as queries SQL, tabelas e cursores do arquivo `.lined` de forma **CEGA** (sem consultar Extractor-A-SQL) para garantir reconciliação anti-alucinação válida.

---

## 🔒 CRÍTICO: Modo Cego

Este workflow opera em **MODO CEGO**:
- ❌ **PROIBIDO** ler `claims_sql_A.json`
- ❌ **PROIBIDO** ler logs do Extractor-A-SQL
- ✅ **OBRIGATÓRIO** extração 100% independente
- ✅ **OBRIGATÓRIO** validar modo cego no início e no fim

---

## Pré-requisitos

### 1. Verificar Arquivo .lined
```
Arquivo: run/extraction/{filename}.lined
Formato: LXXXX|conteúdo
```

### 2. Verificar Knowledge Base
```
- knowledge/sql/sql-patterns-visualage.csv (30 padrões)
- knowledge/sql/sql-mapping-rules.csv (16 regras)
```

### 3. Verificar Modo Cego
```
- claims_sql_A.json NÃO deve ser acessado
- Extração deve ser 100% independente
```

---

## Etapas do Workflow

### Etapa 0: Verificar Modo Cego (CRÍTICO)

```python
print("🔒 Verificando Modo Cego...")

# Lista de arquivos proibidos
forbidden_files = [
    "run/sql/extraction/claims_sql_A.json",
    "run/extraction/claims_A.json",
    "logs/extractor-a-sql.log",
    "logs/extractor-a.log"
]

# Verificar se algum arquivo proibido foi acessado
for forbidden_file in forbidden_files:
    if file_exists(forbidden_file):
        print(f"⚠️ Arquivo proibido existe: {forbidden_file}")
        print(f"   Garantindo que NÃO será acessado...")
        
        # Marcar como proibido
        mark_as_forbidden(forbidden_file)

print("✅ Modo Cego: ATIVO")
print("🔒 Nenhum arquivo proibido será acessado")
print("✅ Extração será 100% independente")
```

---

### Etapa 1: Carregar Arquivo .lined

```python
print("\n🔄 Carregando arquivo .lined...")

# Carregar arquivo
lined_path = f"run/extraction/{filename}.lined"
lined_content = load_file(lined_path)

# Validar formato
if not lined_content:
    print("❌ Arquivo .lined vazio")
    exit(1)

# Converter para dicionário
lined_dict = {}
for line in lined_content.split("\n"):
    if "|" in line:
        line_num_str, content = line.split("|", 1)
        line_num = int(line_num_str[1:])  # Remove 'L'
        lined_dict[line_num] = content

print(f"✅ Arquivo carregado: {len(lined_dict)} linhas")
```

---

### Etapa 2: Carregar Padrões SQL

```python
print("🔄 Carregando padrões SQL...")

# Carregar CSV
sql_patterns = load_csv("knowledge/sql/sql-patterns-visualage.csv")

# Ordenar por prioridade (HIGH → MEDIUM → LOW)
priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
sql_patterns.sort(key=lambda x: priority_order.get(x["PRIORITY"], 0), reverse=True)

# Compilar regex
compiled_patterns = []
for pattern in sql_patterns:
    try:
        regex = re.compile(pattern["REGEX_PATTERN"], re.IGNORECASE | re.DOTALL)
        compiled_patterns.append({
            "id": pattern["PATTERN_ID"],
            "regex": regex,
            "description": pattern["DESCRIPTION"],
            "priority": pattern["PRIORITY"]
        })
    except Exception as e:
        print(f"⚠️ Erro ao compilar padrão {pattern['PATTERN_ID']}: {e}")

print(f"✅ Padrões carregados: {len(compiled_patterns)}")
```

---

### Etapa 3: Identificar Blocos EXEC SQL

```python
print("🔄 Identificando blocos EXEC SQL...")

# Juntar linhas para análise
full_content = "\n".join([f"L{num:04d}|{content}" for num, content in sorted(lined_dict.items())])

# Identificar blocos SQL
sql_blocks = []

for pattern in compiled_patterns:
    matches = pattern["regex"].finditer(full_content)
    
    for match in matches:
        # Extrair bloco SQL
        sql_text = match.group(0)
        
        # Calcular linhas
        text_before = full_content[:match.start()]
        line_start = text_before.count("\n") + 1
        line_end = line_start + sql_text.count("\n")
        
        # Evitar duplicatas
        if not any(b["line_start"] == line_start for b in sql_blocks):
            sql_blocks.append({
                "pattern_id": pattern["id"],
                "sql_text": sql_text,
                "line_start": line_start,
                "line_end": line_end,
                "description": pattern["description"]
            })

print(f"✅ Blocos SQL identificados: {len(sql_blocks)}")
```

---

### Etapa 4: Extrair Queries (com Query IDs B)

```python
print("🔄 Extraindo queries...")

queries = []
query_id_counter = 1

for block in sql_blocks:
    # Limpar SQL (remover LXXXX|)
    sql_lines = []
    for line in block["sql_text"].split("\n"):
        if "|" in line:
            sql_lines.append(line.split("|", 1)[1])
        else:
            sql_lines.append(line)
    
    sql_clean = "\n".join(sql_lines).strip()
    
    # Classificar tipo de query
    sql_upper = sql_clean.upper()
    if "PREPARE" in sql_upper or "EXECUTE" in sql_upper:
        query_type = "DYNAMIC"
    elif "DECLARE" in sql_upper and "CURSOR" in sql_upper:
        query_type = "CURSOR"
    else:
        query_type = "STATIC"
    
    # Classificar operação (CRUD)
    if "SELECT" in sql_upper or "FETCH" in sql_upper:
        operation_type = "READ"
    elif "INSERT" in sql_upper:
        operation_type = "CREATE"
    elif "UPDATE" in sql_upper:
        operation_type = "UPDATE"
    elif "DELETE" in sql_upper:
        operation_type = "DELETE"
    else:
        operation_type = "UNKNOWN"
    
    # Detectar tabelas
    affected_tables = []
    
    # FROM
    from_match = re.search(r'FROM\s+(\w+)', sql_upper)
    if from_match:
        affected_tables.append(from_match.group(1))
    
    # JOIN
    join_matches = re.findall(r'JOIN\s+(\w+)', sql_upper)
    affected_tables.extend(join_matches)
    
    # INTO
    into_match = re.search(r'INTO\s+(\w+)', sql_upper)
    if into_match:
        affected_tables.append(into_match.group(1))
    
    # UPDATE
    update_match = re.search(r'UPDATE\s+(\w+)', sql_upper)
    if update_match:
        affected_tables.append(update_match.group(1))
    
    # DELETE FROM
    delete_match = re.search(r'DELETE\s+FROM\s+(\w+)', sql_upper)
    if delete_match:
        affected_tables.append(delete_match.group(1))
    
    # Remover duplicatas
    affected_tables = list(set(affected_tables))
    
    # Calcular risco
    if "PREPARE" in sql_upper or "EXECUTE" in sql_upper:
        risk_level = "HIGH"
    elif operation_type == "DELETE" and "WHERE" not in sql_upper:
        risk_level = "HIGH"
    elif operation_type == "UPDATE" and "WHERE" not in sql_upper:
        risk_level = "HIGH"
    elif sql_upper.count("JOIN") >= 5:
        risk_level = "HIGH"
    elif "CURSOR" in sql_upper:
        risk_level = "MEDIUM"
    elif sql_upper.count("SELECT") > 1:
        risk_level = "MEDIUM"
    elif sql_upper.count("JOIN") >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Gerar notas
    notes = []
    if "PREPARE" in sql_upper or "EXECUTE" in sql_upper:
        notes.append("SQL dinâmico - difícil rastrear")
    if operation_type == "DELETE" and "WHERE" not in sql_upper:
        notes.append("DELETE sem WHERE - risco mass delete")
    if operation_type == "UPDATE" and "WHERE" not in sql_upper:
        notes.append("UPDATE sem WHERE - risco mass update")
    if sql_upper.count("JOIN") >= 5:
        notes.append(f"Query complexa - {sql_upper.count('JOIN')} JOINs")
    if "CURSOR" in sql_upper:
        notes.append("Cursor - considerar otimização")
    if not notes:
        notes.append("Query simples")
    
    # Gerar evidence_pointer
    evidence_pointer = f"{filename}.esf:L{block['line_start']:04d}-L{block['line_end']:04d}"
    
    # Montar query (com Query ID B!)
    query = {
        "query_id": f"QRY-SQL-B-{query_id_counter:03d}",  # B, não A!
        "query_type": query_type,
        "operation_type": operation_type,
        "sql_statement": sql_clean,
        "affected_tables": affected_tables,
        "evidence_pointer": evidence_pointer,
        "line_start": block["line_start"],
        "line_end": block["line_end"],
        "risk_level": risk_level,
        "notes": "; ".join(notes)
    }
    
    queries.append(query)
    query_id_counter += 1

print(f"✅ Queries extraídas: {len(queries)}")
```

---

### Etapa 5: Identificar Tabelas

```python
print("🔄 Identificando tabelas...")

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

tables_list = list(tables.values())

print(f"✅ Tabelas identificadas: {len(tables_list)}")
```

---

### Etapa 6: Analisar Cursores

```python
print("🔄 Analisando cursores...")

cursors = []

for block in sql_blocks:
    sql_upper = block["sql_text"].upper()
    
    if "DECLARE" in sql_upper and "CURSOR" in sql_upper:
        # Extrair nome do cursor
        cursor_match = re.search(r'DECLARE\s+(\w+)\s+CURSOR', sql_upper)
        if cursor_match:
            cursor_name = cursor_match.group(1)
            
            # Extrair query do cursor
            query_match = re.search(r'FOR\s+(SELECT.*?)(?:END-EXEC|$)', sql_upper, re.DOTALL)
            cursor_query = query_match.group(1).strip() if query_match else ""
            
            # Detectar tabelas
            affected_tables = []
            from_match = re.search(r'FROM\s+(\w+)', cursor_query)
            if from_match:
                affected_tables.append(from_match.group(1))
            
            # Contar FETCHs
            fetch_count = full_content.upper().count(f"FETCH {cursor_name}")
            
            # Evidence pointer
            evidence_pointer = f"{filename}.esf:L{block['line_start']:04d}-L{block['line_end']:04d}"
            
            cursor = {
                "cursor_name": cursor_name,
                "cursor_query": cursor_query,
                "affected_tables": affected_tables,
                "evidence_pointer": evidence_pointer,
                "fetch_count": fetch_count
            }
            
            cursors.append(cursor)

print(f"✅ Cursores analisados: {len(cursors)}")
```

---

### Etapa 7: Gerar JSON (com Metadata BLIND)

```python
print("🔄 Gerando JSON...")

claims_sql_b = {
    "metadata": {
        "source_file": f"{filename}.esf",
        "extraction_date": datetime.now().isoformat(),
        "extractor_agent": "extractor-b-sql",
        "extraction_mode": "BLIND",  # CRÍTICO!
        "total_queries": len(queries),
        "total_tables": len(tables_list),
        "total_cursors": len(cursors)
    },
    "queries": queries,
    "tables": tables_list,
    "cursors": cursors
}

print("✅ JSON gerado")
```

---

### Etapa 8: Validar Qualidade

```python
print("🔄 Validando qualidade...")

errors = []

for query in queries:
    # Evidence pointer
    if not query.get("evidence_pointer"):
        errors.append(f"Query {query['query_id']} sem evidence_pointer")
    
    # Operation type
    if query.get("operation_type") not in ["READ", "CREATE", "UPDATE", "DELETE", "UNKNOWN"]:
        errors.append(f"Query {query['query_id']} com operation_type inválido")
    
    # Affected tables (exceto SQL dinâmico)
    if not query.get("affected_tables") and query.get("query_type") != "DYNAMIC":
        errors.append(f"Query {query['query_id']} sem affected_tables")
    
    # Risk level
    if query.get("risk_level") not in ["HIGH", "MEDIUM", "LOW"]:
        errors.append(f"Query {query['query_id']} com risk_level inválido")
    
    # Query ID deve ser B, não A
    if not query.get("query_id", "").startswith("QRY-SQL-B-"):
        errors.append(f"Query {query['query_id']} deve começar com QRY-SQL-B-")

if errors:
    print("❌ Erros de validação:")
    for error in errors:
        print(f"   - {error}")
    exit(1)

print("✅ Validação OK")
```

---

### Etapa 9: Salvar Output

```python
print("🔄 Salvando output...")

output_path = "run/sql/extraction/claims_sql_B.json"
save_json(output_path, claims_sql_b)

print(f"✅ Output salvo: {output_path}")
```

---

### Etapa 10: Validar Modo Cego (CRÍTICO)

```python
print("\n🔒 Validando Modo Cego...")

# Verificar se algum arquivo proibido foi acessado
violations = []

for forbidden_file in forbidden_files:
    if file_was_accessed(forbidden_file):
        violations.append(forbidden_file)

if violations:
    print("❌ VIOLAÇÃO DE MODO CEGO!")
    print("   Arquivos proibidos foram acessados:")
    for violation in violations:
        print(f"   - {violation}")
    print("\n   Consequências:")
    print("   - Extração NÃO é independente")
    print("   - Reconciliação será INVÁLIDA")
    print("   - Anti-alucinação comprometida")
    print("\n   AÇÃO REQUERIDA:")
    print("   - Refazer extração sem acessar arquivos proibidos")
    exit(1)

print("✅ Modo Cego: MANTIDO")
print("✅ Nenhum arquivo proibido foi acessado")
print("✅ Extração 100% independente")
print("✅ Reconciliação será válida")
```

---

### Etapa 11: Exibir Estatísticas

```python
print("\n" + "="*60)
print("✅ EXTRAÇÃO SQL CEGA CONCLUÍDA")
print("="*60)

print(f"\n🔒 Modo Cego: ATIVO")
print(f"   - Nenhum arquivo proibido foi acessado")
print(f"   - Extração 100% independente")
print(f"   - Reconciliação será válida")

print(f"\n📊 Estatísticas:")
print(f"   - Queries: {len(queries)}")
print(f"   - Tabelas: {len(tables_list)}")
print(f"   - Cursores: {len(cursors)}")

# Contar por operação
read_count = sum(1 for q in queries if q["operation_type"] == "READ")
create_count = sum(1 for q in queries if q["operation_type"] == "CREATE")
update_count = sum(1 for q in queries if q["operation_type"] == "UPDATE")
delete_count = sum(1 for q in queries if q["operation_type"] == "DELETE")

print(f"\n📈 Operações:")
print(f"   - READ: {read_count}")
print(f"   - CREATE: {create_count}")
print(f"   - UPDATE: {update_count}")
print(f"   - DELETE: {delete_count}")

# Contar por risco
high_risk = sum(1 for q in queries if q["risk_level"] == "HIGH")
medium_risk = sum(1 for q in queries if q["risk_level"] == "MEDIUM")
low_risk = sum(1 for q in queries if q["risk_level"] == "LOW")

print(f"\n⚠️ Riscos:")
print(f"   - HIGH: {high_risk}")
print(f"   - MEDIUM: {medium_risk}")
print(f"   - LOW: {low_risk}")

print(f"\n📁 Output: {output_path}")
print("\n✅ Extração SQL CEGA concluída com sucesso!")
print("✅ Pronto para reconciliação com claims_sql_A.json")
```

---

## Output

**Arquivo**: `run/sql/extraction/claims_sql_B.json`

**Estrutura**:
```json
{
  "metadata": {
    "extraction_mode": "BLIND",
    ...
  },
  "queries": [...],
  "tables": [...],
  "cursors": [...]
}
```

---

## Validação

Verificar:
- ✅ Todas as queries têm `evidence_pointer`
- ✅ Todas as queries têm `operation_type` válido
- ✅ Todas as queries têm `affected_tables` (exceto DYNAMIC)
- ✅ Todas as queries têm `risk_level` válido
- ✅ Query IDs são `QRY-SQL-B-XXX` (não `QRY-SQL-A-XXX`)
- ✅ Metadata indica `extraction_mode: "BLIND"`
- ✅ **Modo Cego foi mantido**
- ✅ **Nenhum arquivo proibido foi acessado**
- ✅ **Extração 100% independente**

---

**Status**: ✅ Workflow Completo  
**Versão**: 1.0  
**Data**: 2025-12-28  
**Modo**: BLIND (Extração Cega)



