# Workflow: [LINEAGE] - Mapear Linhagem de Dados

## Objetivo
Gerar `run/sql/analysis/lineage/data_lineage.csv` mapeando a linhagem completa de dados: lógica → query → tabela.

---

## Pré-requisitos

### 1. Verificar SQL-Gate PASS
```
Arquivo: run/sql/validation/gate_status_sql.json
Conteúdo obrigatório: "sql_gate_status": "PASS"
```

### 2. Verificar Claims SQL
```
Arquivo: run/sql/extraction/claims_sql_A.json
Deve conter: queries com affected_tables e operation_type
```

---

## Etapas do Workflow

### Etapa 1: Carregar Claims SQL

```python
claims = load_json("run/sql/extraction/claims_sql_A.json")
queries = claims.get("queries", [])
```

### Etapa 2: Agrupar Queries por Tabela

```python
lineage = {}

for query in queries:
    # Para cada tabela afetada pela query
    for table in query.get("affected_tables", []):
        if table not in lineage:
            lineage[table] = []
        
        # Adicionar operação
        lineage[table].append({
            "operation_type": query.get("operation_type"),
            "query_id": query.get("query_id"),
            "evidence_pointer": query.get("evidence_pointer"),
            "business_logic_id": query.get("business_logic_id", "NONE"),
            "screen_id": query.get("screen_id", "NONE"),
            "risk_level": calculate_risk(query),
            "notes": generate_notes(query)
        })
```

### Etapa 3: Calcular Risco

```python
def calculate_risk(query):
    """
    Calcula nível de risco da query
    HIGH: SQL dinâmico, mass ops, muitos JOINs
    MEDIUM: Cursores, subqueries, locks
    LOW: Queries simples
    """
    
    sql = query.get("sql_statement", "").upper()
    
    # HIGH RISK
    if query.get("query_type") == "DYNAMIC":
        return "HIGH"
    
    if "DELETE" in sql and "WHERE" not in sql:
        return "HIGH"
    
    if "UPDATE" in sql and "WHERE" not in sql:
        return "HIGH"
    
    if query.get("joins_count", 0) >= 5:
        return "HIGH"
    
    # MEDIUM RISK
    if query.get("query_type") == "CURSOR":
        return "MEDIUM"
    
    if query.get("subqueries_count", 0) > 0:
        return "MEDIUM"
    
    if "LOCK TABLE" in sql:
        return "MEDIUM"
    
    if query.get("joins_count", 0) >= 3:
        return "MEDIUM"
    
    # LOW RISK
    return "LOW"
```

### Etapa 4: Gerar Notas Explicativas

```python
def generate_notes(query):
    """
    Gera notas explicativas sobre a query
    """
    notes = []
    
    sql = query.get("sql_statement", "").upper()
    
    # SQL dinâmico
    if query.get("query_type") == "DYNAMIC":
        notes.append("SQL dinâmico - difícil rastrear")
    
    # Mass operations
    if "DELETE" in sql and "WHERE" not in sql:
        notes.append("DELETE sem WHERE - risco mass delete")
    
    if "UPDATE" in sql and "WHERE" not in sql:
        notes.append("UPDATE sem WHERE - risco mass update")
    
    # Complexidade
    joins = query.get("joins_count", 0)
    if joins >= 5:
        notes.append(f"Query complexa - {joins} JOINs")
    
    # Cursores
    if query.get("query_type") == "CURSOR":
        notes.append("Cursor - considerar otimização")
    
    # Subqueries
    subqueries = query.get("subqueries_count", 0)
    if subqueries > 0:
        notes.append(f"{subqueries} subqueries - revisar performance")
    
    # Locks
    if "LOCK TABLE" in sql:
        notes.append("Lock explícito - revisar necessidade")
    
    # Query simples
    if not notes:
        notes.append("Query simples")
    
    return "; ".join(notes)
```

### Etapa 5: Gerar CSV

```python
csv_lines = [
    "table_name,operation_type,query_id,evidence_pointer,business_logic_id,screen_id,risk_level,notes"
]

for table, operations in sorted(lineage.items()):
    for op in operations:
        line = f"{table},{op['operation_type']},{op['query_id']},{op['evidence_pointer']},{op['business_logic_id']},{op['screen_id']},{op['risk_level']},\"{op['notes']}\""
        csv_lines.append(line)

csv_content = "\n".join(csv_lines)
```

### Etapa 6: Criar Pasta Lineage

```python
# Criar pasta se não existir
import os
os.makedirs("run/sql/analysis/lineage", exist_ok=True)
```

### Etapa 7: Salvar CSV

```python
output_path = "run/sql/analysis/lineage/data_lineage.csv"
save_file(output_path, csv_content)
```

### Etapa 8: Gerar Estatísticas

```python
# Contar operações por tipo
stats = {
    "READ": 0,
    "CREATE": 0,
    "UPDATE": 0,
    "DELETE": 0
}

for operations in lineage.values():
    for op in operations:
        op_type = op["operation_type"]
        stats[op_type] = stats.get(op_type, 0) + 1

# Contar riscos
risk_stats = {
    "HIGH": 0,
    "MEDIUM": 0,
    "LOW": 0
}

for operations in lineage.values():
    for op in operations:
        risk_stats[op["risk_level"]] += 1

# Exibir resumo
print(f"✅ Linhagem mapeada: {output_path}")
print(f"   - Tabelas: {len(lineage)}")
print(f"   - Operações: {sum(stats.values())}")
print(f"   - READ: {stats['READ']}")
print(f"   - CREATE: {stats['CREATE']}")
print(f"   - UPDATE: {stats['UPDATE']}")
print(f"   - DELETE: {stats['DELETE']}")
print(f"   - Risco HIGH: {risk_stats['HIGH']}")
print(f"   - Risco MEDIUM: {risk_stats['MEDIUM']}")
print(f"   - Risco LOW: {risk_stats['LOW']}")
```

---

## Análise de Linhagem

### Upstream Dependencies
Identificar quais lógicas/telas afetam cada tabela:

```python
for table, operations in lineage.items():
    upstream = set()
    for op in operations:
        if op["business_logic_id"] != "NONE":
            upstream.add(op["business_logic_id"])
        if op["screen_id"] != "NONE":
            upstream.add(op["screen_id"])
    
    print(f"Tabela {table}:")
    print(f"  Upstream: {', '.join(upstream)}")
```

### Downstream Dependencies
Identificar quais tabelas são afetadas por cada lógica:

```python
logic_to_tables = {}

for table, operations in lineage.items():
    for op in operations:
        logic_id = op["business_logic_id"]
        if logic_id != "NONE":
            if logic_id not in logic_to_tables:
                logic_to_tables[logic_id] = set()
            logic_to_tables[logic_id].add(table)

for logic_id, tables in logic_to_tables.items():
    print(f"Lógica {logic_id}:")
    print(f"  Downstream: {', '.join(tables)}")
```

### Tabelas de Alto Risco
Identificar tabelas com operações de alto risco:

```python
high_risk_tables = []

for table, operations in lineage.items():
    high_risk_ops = [op for op in operations if op["risk_level"] == "HIGH"]
    if high_risk_ops:
        high_risk_tables.append({
            "table": table,
            "high_risk_count": len(high_risk_ops),
            "operations": high_risk_ops
        })

# Ordenar por quantidade de operações de alto risco
high_risk_tables.sort(key=lambda x: x["high_risk_count"], reverse=True)

print("\n⚠️ Tabelas de Alto Risco:")
for item in high_risk_tables[:10]:  # Top 10
    print(f"   {item['table']}: {item['high_risk_count']} operações HIGH")
```

---

## Exemplo de Output (CSV)

```csv
table_name,operation_type,query_id,evidence_pointer,business_logic_id,screen_id,risk_level,notes
Banco,READ,QRY-SQL-001,bi14a.esf:L0500-L0503,LOG-005,SCR-001,LOW,"Query simples"
Banco,READ,QRY-SQL-003,bi14a.esf:L0600-L0605,LOG-007,SCR-002,LOW,"Query simples"
Banco,CREATE,QRY-SQL-015,bi14a.esf:L1500-L1502,LOG-012,SCR-003,MEDIUM,"Verificar duplicidade antes de inserir"
Banco,UPDATE,QRY-SQL-018,bi14a.esf:L1800-L1805,LOG-018,SCR-004,MEDIUM,"Cursor - considerar otimização"
Banco,DELETE,QRY-SQL-021,bi14a.esf:L2100-L2105,NONE,SCR-005,HIGH,"DELETE sem WHERE - risco mass delete"
Agencia,READ,QRY-SQL-008,bi14a.esf:L0700-L0705,LOG-008,SCR-002,LOW,"Query simples"
Agencia,READ,QRY-SQL-010,bi14a.esf:L0800-L0810,LOG-010,SCR-006,MEDIUM,"Query complexa - 3 JOINs"
Agencia,CREATE,QRY-SQL-020,bi14a.esf:L1700-L1710,LOG-015,SCR-006,MEDIUM,"Validar FK antes de inserir"
Transacao,READ,QRY-SQL-025,bi14a.esf:L2500-L2520,LOG-020,SCR-010,HIGH,"Query complexa - 5 JOINs; 2 subqueries - revisar performance"
Transacao,CREATE,QRY-SQL-030,bi14a.esf:L3000-L3010,LOG-025,SCR-012,MEDIUM,"SQL dinâmico - difícil rastrear"
```

---

## Output

**Arquivo**: `run/sql/analysis/lineage/data_lineage.csv`

**Colunas**:
- `table_name`: Nome da tabela
- `operation_type`: Tipo de operação (READ/CREATE/UPDATE/DELETE)
- `query_id`: ID da query
- `evidence_pointer`: Ponteiro para o código fonte
- `business_logic_id`: ID da lógica de negócio
- `screen_id`: ID da tela
- `risk_level`: Nível de risco (HIGH/MEDIUM/LOW)
- `notes`: Notas explicativas

---

## Validação

Verificar:
- ✅ Todas as queries foram mapeadas
- ✅ Todas as tabelas foram identificadas
- ✅ Riscos foram calculados corretamente
- ✅ Linhagem upstream/downstream está completa
- ✅ Operações de alto risco foram identificadas

---

**Status**: ✅ Workflow Completo  
**Versão**: 1.0  
**Data**: 2025-12-28

