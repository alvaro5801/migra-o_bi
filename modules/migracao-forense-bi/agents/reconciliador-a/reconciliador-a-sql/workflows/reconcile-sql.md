# Workflow: [REC-SQL] - Reconciliação SQL

## Objetivo
Comparar extrações SQL A e B, detectar divergências e gerar o Ledger de Dados oficial (versão única da verdade).

---

## Pré-requisitos

### 1. Verificar Extrações SQL
```
Arquivos obrigatórios:
- run/sql/extraction/claims_sql_A.json (Extractor-A-SQL)
- run/sql/extraction/claims_sql_B.json (Extractor-B-SQL)
```

### 2. Verificar Knowledge Base
```
- knowledge/sql/sql-patterns-visualage.csv
- knowledge/sql/sql-mapping-rules.csv
- knowledge/reconciliation-rules.csv
```

---

## Etapas do Workflow

### Etapa 1: Verificar Gate

```python
print("🔒 Verificando Gate...")

# Arquivos obrigatórios
required_files = {
    "claims_sql_A.json": "run/sql/extraction/claims_sql_A.json",
    "claims_sql_B.json": "run/sql/extraction/claims_sql_B.json"
}

# Verificar existência
all_exist = True
for name, path in required_files.items():
    exists = file_exists(path)
    status = "✅ OK" if exists else "❌ FALTA"
    print(f"   {name}: {status}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n❌ BLOQUEIO: Extrações SQL incompletas")
    print("\nAÇÃO REQUERIDA:")
    print("1. Executar [EXT-SQL] para gerar claims_sql_A.json")
    print("2. Executar [EXT-SQL-B] para gerar claims_sql_B.json")
    print("3. Retornar para [REC-SQL]")
    exit(1)

print("✅ Gate: PASS - Ambas extrações encontradas")
```

---

### Etapa 2: Carregar Claims A e B

```python
print("\n📂 Carregando claims...")

# Carregar A
claims_a = load_json("run/sql/extraction/claims_sql_A.json")
queries_a = claims_a.get("queries", [])

print(f"   Claims A: {len(queries_a)} queries")

# Carregar B
claims_b = load_json("run/sql/extraction/claims_sql_B.json")
queries_b = claims_b.get("queries", [])

print(f"   Claims B: {len(queries_b)} queries")

print("✅ Claims carregados")
```

---

### Etapa 3: Normalizar Queries

```python
print("\n🔧 Normalizando queries...")

def normalize_sql(sql):
    # Remover espaços extras
    sql = re.sub(r'\s+', ' ', sql)
    # Uppercase
    sql = sql.upper()
    # Trim
    sql = sql.strip()
    return sql

# Normalizar A
for query in queries_a:
    query["sql_normalized"] = normalize_sql(query.get("sql_statement", ""))

# Normalizar B
for query in queries_b:
    query["sql_normalized"] = normalize_sql(query.get("sql_statement", ""))

print("✅ Queries normalizadas")
```

---

### Etapa 4: Comparar Queries

```python
print("\n⚖️ Comparando queries...")

matches = []
conflicts = []
hallucinations = []
omissions = []

# Índice de B por evidence_pointer
b_index = {}
for query_b in queries_b:
    ep = query_b.get("evidence_pointer")
    if ep:
        b_index[ep] = query_b

# Comparar A com B
for query_a in queries_a:
    ep_a = query_a.get("evidence_pointer")
    query_b = b_index.get(ep_a)
    
    if not query_b:
        # HALLUCINATION
        hallucinations.append({
            "query_a": query_a,
            "query_b": None,
            "reason": "Query em A mas não em B"
        })
        continue
    
    # Calcular match score
    score = 0.0
    
    # Evidence pointer (0.5)
    if query_a.get("evidence_pointer") == query_b.get("evidence_pointer"):
        score += 0.5
    
    # SQL (0.3)
    if query_a.get("sql_normalized") == query_b.get("sql_normalized"):
        score += 0.3
    
    # Tables (0.1)
    tables_a = set(query_a.get("affected_tables", []))
    tables_b = set(query_b.get("affected_tables", []))
    if tables_a == tables_b:
        score += 0.1
    
    # Operation (0.1)
    if query_a.get("operation_type") == query_b.get("operation_type"):
        score += 0.1
    
    if score >= 0.9:
        # MATCH
        matches.append({
            "query_a": query_a,
            "query_b": query_b,
            "score": score
        })
    else:
        # CONFLICT
        differences = []
        if query_a.get("sql_normalized") != query_b.get("sql_normalized"):
            differences.append("SQL diferente")
        if tables_a != tables_b:
            differences.append(f"Tabelas: A={tables_a}, B={tables_b}")
        if query_a.get("operation_type") != query_b.get("operation_type"):
            differences.append(f"Operação: A={query_a['operation_type']}, B={query_b['operation_type']}")
        
        conflicts.append({
            "query_a": query_a,
            "query_b": query_b,
            "score": score,
            "differences": differences
        })

# Detectar omissões
a_evidence_pointers = {q.get("evidence_pointer") for q in queries_a}
for query_b in queries_b:
    ep_b = query_b.get("evidence_pointer")
    if ep_b not in a_evidence_pointers:
        # OMISSION
        omissions.append({
            "query_a": None,
            "query_b": query_b,
            "reason": "Query em B mas não em A"
        })

print(f"   ✅ MATCH: {len(matches)}")
print(f"   ⚠️ CONFLICT: {len(conflicts)}")
print(f"   🔴 HALLUCINATION: {len(hallucinations)}")
print(f"   🔴 OMISSION: {len(omissions)}")

print("✅ Comparação concluída")
```

---

### Etapa 5: Gerar Ledger de Dados

```python
print("\n📖 Gerando Ledger de Dados...")

ledger_queries = []
ledger_id = 1

# MATCHES
for match in matches:
    ledger_queries.append({
        "query_id": f"QRY-SQL-LEDGER-{ledger_id:03d}",
        "reconciliation_status": "MATCH",
        "confidence_score": match["score"],
        "source_a_query_id": match["query_a"]["query_id"],
        "source_b_query_id": match["query_b"]["query_id"],
        "sql_statement": match["query_a"]["sql_statement"],
        "affected_tables": match["query_a"]["affected_tables"],
        "operation_type": match["query_a"]["operation_type"],
        "evidence_pointer": match["query_a"]["evidence_pointer"],
        "resolution": "A e B concordam"
    })
    ledger_id += 1

# CONFLICTS
for conflict in conflicts:
    ledger_queries.append({
        "query_id": f"QRY-SQL-LEDGER-{ledger_id:03d}",
        "reconciliation_status": "CONFLICT",
        "confidence_score": conflict["score"],
        "source_a_query_id": conflict["query_a"]["query_id"],
        "source_b_query_id": conflict["query_b"]["query_id"],
        "sql_statement": conflict["query_a"]["sql_statement"],
        "affected_tables": conflict["query_a"]["affected_tables"],
        "operation_type": conflict["query_a"]["operation_type"],
        "evidence_pointer": conflict["query_a"]["evidence_pointer"],
        "conflict_details": conflict["differences"],
        "resolution": "Usar A (revisar manualmente)"
    })
    ledger_id += 1

# HALLUCINATIONS
for hall in hallucinations:
    ledger_queries.append({
        "query_id": f"QRY-SQL-LEDGER-{ledger_id:03d}",
        "reconciliation_status": "HALLUCINATION",
        "confidence_score": 0.5,
        "source_a_query_id": hall["query_a"]["query_id"],
        "source_b_query_id": None,
        "sql_statement": hall["query_a"]["sql_statement"],
        "affected_tables": hall["query_a"]["affected_tables"],
        "operation_type": hall["query_a"]["operation_type"],
        "evidence_pointer": hall["query_a"]["evidence_pointer"],
        "resolution": "Query em A mas não em B - revisar A"
    })
    ledger_id += 1

# OMISSIONS
for omis in omissions:
    ledger_queries.append({
        "query_id": f"QRY-SQL-LEDGER-{ledger_id:03d}",
        "reconciliation_status": "OMISSION",
        "confidence_score": 0.5,
        "source_a_query_id": None,
        "source_b_query_id": omis["query_b"]["query_id"],
        "sql_statement": omis["query_b"]["sql_statement"],
        "affected_tables": omis["query_b"]["affected_tables"],
        "operation_type": omis["query_b"]["operation_type"],
        "evidence_pointer": omis["query_b"]["evidence_pointer"],
        "resolution": "Query em B mas não em A - adicionar ao Ledger"
    })
    ledger_id += 1

# Calcular confidence score
total = len(ledger_queries)
confidence = (len(matches) / total * 100) if total > 0 else 0

# Montar Ledger
ledger = {
    "metadata": {
        "reconciliation_date": datetime.now().isoformat(),
        "reconciliator_agent": "reconciliador-a-sql",
        "total_queries": total,
        "match_count": len(matches),
        "conflict_count": len(conflicts),
        "hallucination_count": len(hallucinations),
        "omission_count": len(omissions),
        "confidence_score": round(confidence, 2)
    },
    "queries": ledger_queries
}

# Salvar
ledger_path = "run/sql/analysis/claim_ledger_sql.json"
save_json(ledger_path, ledger, indent=2)

print(f"✅ Ledger gerado: {ledger_path}")
print(f"   Queries: {total}")
print(f"   Confidence: {confidence:.2f}%")
```

---

### Etapa 6: Gerar Diff Report

```python
print("\n📄 Gerando Diff Report...")

report = f"""# Diff Report SQL

**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Sumário

- Queries A: {len(queries_a)}
- Queries B: {len(queries_b)}
- MATCH: {len(matches)} ({len(matches)/total*100:.1f}%)
- CONFLICT: {len(conflicts)} ({len(conflicts)/total*100:.1f}%)
- HALLUCINATION: {len(hallucinations)}
- OMISSION: {len(omissions)}
- Confidence: {confidence:.2f}%

## Recomendações

"""

if len(hallucinations) > 0:
    report += f"- ⚠️ {len(hallucinations)} alucinações - revisar A\n"
if len(omissions) > 0:
    report += f"- ⚠️ {len(omissions)} omissões - revisar A\n"
if confidence >= 90:
    report += f"- ✅ Alta confiança ({confidence:.2f}%)\n"
else:
    report += f"- ⚠️ Baixa confiança ({confidence:.2f}%) - revisar\n"

# Salvar
report_path = "run/sql/validation/diff_report_sql.md"
save_file(report_path, report)

print(f"✅ Diff Report gerado: {report_path}")
```

---

### Etapa 7: Exibir Resumo

```python
print("\n" + "="*60)
print("✅ RECONCILIAÇÃO SQL CONCLUÍDA")
print("="*60)

print(f"\n📊 Estatísticas:")
print(f"   Queries A: {len(queries_a)}")
print(f"   Queries B: {len(queries_b)}")
print(f"   MATCH: {len(matches)} ({len(matches)/total*100:.1f}%)")
print(f"   CONFLICT: {len(conflicts)} ({len(conflicts)/total*100:.1f}%)")
print(f"   HALLUCINATION: {len(hallucinations)}")
print(f"   OMISSION: {len(omissions)}")
print(f"   Confidence Score: {confidence:.2f}%")

print(f"\n📄 Outputs:")
print(f"   ✅ run/sql/analysis/claim_ledger_sql.json")
print(f"   ✅ run/sql/validation/diff_report_sql.md")

print("\n✅ Versão única da verdade gerada!")
```

---

## Output

**Arquivos Gerados**:
1. `run/sql/analysis/claim_ledger_sql.json` - Ledger de Dados oficial
2. `run/sql/validation/diff_report_sql.md` - Relatório de divergências

---

## Validação

Verificar:
- ✅ Ledger gerado
- ✅ Diff Report gerado
- ✅ Confidence Score calculado
- ✅ Todas queries classificadas (MATCH/CONFLICT/HALLUCINATION/OMISSION)

---

**Status**: ✅ Workflow Completo  
**Versão**: 1.0  
**Data**: 2025-12-28



