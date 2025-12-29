# Workflow: [ANA-SQL] - Análise Completa SQL

## Objetivo
Executar análise completa SQL: DDL + Linhagem + Complexidade + EF Core Mapping.

---

## Pré-requisitos

### 1. Verificar SQL-Gate PASS
```
Arquivo: run/sql/validation/gate_status_sql.json
Conteúdo obrigatório: "sql_gate_status": "PASS"
```

Se FAIL → ABORTAR com mensagem de bloqueio

### 2. Verificar Claims SQL
```
Arquivo: run/sql/extraction/claims_sql_A.json
Deve conter: tabelas, queries, colunas
```

---

## Etapas do Workflow

### Etapa 1: Verificar SQL-Gate

```python
gate_status = load_json("run/sql/validation/gate_status_sql.json")

if gate_status.get("sql_gate_status") != "PASS":
    print("❌ BLOQUEIO: SQL-Gate não está PASS")
    print(f"   Status: {gate_status.get('sql_gate_status')}")
    print(f"   Conformidade: {gate_status.get('conformidade_sql_percentage')}%")
    print("\nAÇÃO REQUERIDA:")
    print("1. Executar [EXT-SQL] para extrair SQL")
    print("2. Executar [VAL-SQL] para validar")
    print("3. Corrigir erros até SQL-Gate = PASS")
    print("4. Retornar para [ANA-SQL]")
    exit(1)

print("✅ SQL-Gate: PASS")
print(f"   Conformidade: {gate_status.get('conformidade_sql_percentage')}%")
```

### Etapa 2: Executar [DDL-GEN]

```python
print("\n🔄 Executando [DDL-GEN]...")
result_ddl = execute_workflow("generate-ddl.md")

if result_ddl.status == "SUCCESS":
    print("✅ DDL gerado com sucesso")
    print(f"   Arquivo: {result_ddl.output_path}")
    print(f"   Linhas: {result_ddl.line_count}")
    print(f"   Tabelas: {result_ddl.table_count}")
    print(f"   Views: {result_ddl.view_count}")
    print(f"   Stored Procedures: {result_ddl.proc_count}")
else:
    print("❌ Erro ao gerar DDL")
    print(f"   Erro: {result_ddl.error}")
    exit(1)
```

### Etapa 3: Executar [LINEAGE]

```python
print("\n🔄 Executando [LINEAGE]...")
result_lineage = execute_workflow("map-lineage.md")

if result_lineage.status == "SUCCESS":
    print("✅ Linhagem mapeada com sucesso")
    print(f"   Arquivo: {result_lineage.output_path}")
    print(f"   Tabelas: {result_lineage.table_count}")
    print(f"   Operações: {result_lineage.operation_count}")
    print(f"   Risco HIGH: {result_lineage.high_risk_count}")
    print(f"   Risco MEDIUM: {result_lineage.medium_risk_count}")
    print(f"   Risco LOW: {result_lineage.low_risk_count}")
else:
    print("❌ Erro ao mapear linhagem")
    print(f"   Erro: {result_lineage.error}")
    exit(1)
```

### Etapa 4: Gerar Matriz de Complexidade SQL

```python
print("\n🔄 Gerando matriz de complexidade SQL...")

claims = load_json("run/sql/extraction/claims_sql_A.json")
queries = claims.get("queries", [])

complexity_matrix = []

for query in queries:
    complexity = calculate_complexity(query)
    
    complexity_matrix.append({
        "query_id": query.get("query_id"),
        "query_type": query.get("query_type"),
        "complexity_score": complexity["score"],
        "risk_level": complexity["risk_level"],
        "tables_count": len(query.get("affected_tables", [])),
        "joins_count": query.get("joins_count", 0),
        "subqueries_count": query.get("subqueries_count", 0),
        "dynamic_sql": query.get("query_type") == "DYNAMIC",
        "notes": complexity["notes"]
    })

# Salvar CSV
csv_lines = [
    "query_id,query_type,complexity_score,risk_level,tables_count,joins_count,subqueries_count,dynamic_sql,notes"
]

for item in complexity_matrix:
    line = f"{item['query_id']},{item['query_type']},{item['complexity_score']},{item['risk_level']},{item['tables_count']},{item['joins_count']},{item['subqueries_count']},{item['dynamic_sql']},\"{item['notes']}\""
    csv_lines.append(line)

output_path = "run/sql/analysis/complexity_matrix_sql.csv"
save_file(output_path, "\n".join(csv_lines))

print(f"✅ Matriz de complexidade gerada: {output_path}")
print(f"   Queries analisadas: {len(complexity_matrix)}")
```

### Etapa 5: Gerar Mapeamento Entity Framework Core

```python
print("\n🔄 Gerando mapeamento Entity Framework Core...")

tables = claims.get("tables", [])
foreign_keys = extract_foreign_keys(queries)

ef_mapping = {
    "entities": [],
    "dbcontext": {
        "name": "ApplicationDbContext",
        "dbsets": []
    },
    "configurations": []
}

for table in tables:
    entity_name = to_pascal_case(table["table_name"])
    
    # Entidade
    entity = {
        "entity_name": entity_name,
        "table_name": entity_name,
        "properties": [],
        "navigation_properties": [],
        "indexes": [],
        "constraints": []
    }
    
    # Propriedades
    for column in table["columns"]:
        prop = {
            "name": to_pascal_case(column["name"]),
            "type": map_to_csharp_type(column["cobol_type"]),
            "is_required": column.get("required", False),
            "is_primary_key": column.get("is_primary_key", False),
            "max_length": column.get("max_length")
        }
        entity["properties"].append(prop)
    
    # Auditoria
    entity["properties"].extend([
        {"name": "CreatedAt", "type": "DateTime", "is_required": True},
        {"name": "UpdatedAt", "type": "DateTime?", "is_required": False},
        {"name": "IsDeleted", "type": "bool", "is_required": True}
    ])
    
    # Navigation Properties
    for fk in foreign_keys:
        if fk["table"] == entity_name:
            nav_prop = {
                "name": fk["ref_table"],
                "type": fk["ref_table"],
                "is_collection": False
            }
            entity["navigation_properties"].append(nav_prop)
        
        if fk["ref_table"] == entity_name:
            nav_prop = {
                "name": f"{fk['table']}s",
                "type": f"ICollection<{fk['table']}>",
                "is_collection": True
            }
            entity["navigation_properties"].append(nav_prop)
    
    # Índices
    for column in table["columns"]:
        if column.get("is_unique"):
            entity["indexes"].append({
                "name": f"IX_{entity_name}_{to_pascal_case(column['name'])}",
                "columns": [to_pascal_case(column["name"])],
                "is_unique": True
            })
    
    ef_mapping["entities"].append(entity)
    ef_mapping["dbcontext"]["dbsets"].append({
        "name": f"{entity_name}s",
        "type": entity_name
    })

# Salvar JSON
output_path = "run/sql/analysis/ef_core_mapping.json"
save_json(output_path, ef_mapping)

print(f"✅ Mapeamento EF Core gerado: {output_path}")
print(f"   Entidades: {len(ef_mapping['entities'])}")
```

### Etapa 6: Gerar Relatório Consolidado

```python
print("\n🔄 Gerando relatório consolidado...")

report = f"""
# Relatório de Análise SQL Completa

**Data**: {current_date}
**Arquivo Fonte**: {source_file}
**Conformidade VAMAP**: {gate_status.get('conformidade_sql_percentage')}%

---

## Sumário Executivo

### DDL Gerado
- **Arquivo**: run/sql/analysis/database_schema.sql
- **Linhas**: {result_ddl.line_count}
- **Tabelas**: {result_ddl.table_count}
- **Views**: {result_ddl.view_count}
- **Stored Procedures**: {result_ddl.proc_count}
- **Índices**: {result_ddl.index_count}

### Linhagem de Dados
- **Arquivo**: run/sql/analysis/data_lineage.csv
- **Tabelas**: {result_lineage.table_count}
- **Operações**: {result_lineage.operation_count}
  - READ: {result_lineage.read_count}
  - CREATE: {result_lineage.create_count}
  - UPDATE: {result_lineage.update_count}
  - DELETE: {result_lineage.delete_count}

### Riscos Identificados
- **HIGH**: {result_lineage.high_risk_count} operações
- **MEDIUM**: {result_lineage.medium_risk_count} operações
- **LOW**: {result_lineage.low_risk_count} operações

### Complexidade SQL
- **Queries Analisadas**: {len(complexity_matrix)}
- **Complexidade Média**: {calculate_average_complexity(complexity_matrix)}
- **Queries Complexas (>= 5 JOINs)**: {count_complex_queries(complexity_matrix)}

### Entity Framework Core
- **Entidades**: {len(ef_mapping['entities'])}
- **DbSets**: {len(ef_mapping['dbcontext']['dbsets'])}
- **Navigation Properties**: {count_navigation_properties(ef_mapping)}

---

## Próximos Passos

1. ✅ Revisar DDL gerado e ajustar conforme necessário
2. ✅ Implementar stored procedures para lógica complexa
3. ✅ Configurar migrations do Entity Framework Core
4. ✅ Revisar operações de alto risco
5. ✅ Otimizar queries complexas
6. ✅ Implementar testes de integração para persistência

---

## Arquivos Gerados

1. `run/sql/analysis/database_schema.sql` - DDL SQL Server moderno
2. `run/sql/analysis/data_lineage.csv` - Linhagem de dados
3. `run/sql/analysis/complexity_matrix_sql.csv` - Matriz de complexidade
4. `run/sql/analysis/ef_core_mapping.json` - Mapeamento EF Core
5. `run/sql/analysis/sql_analysis_report.md` - Este relatório

---

**Status**: ✅ ANÁLISE SQL COMPLETA
**Versão**: 1.0
**Gerado por**: Analyzer-A-SQL
"""

output_path = "run/sql/analysis/sql_analysis_report.md"
save_file(output_path, report)

print(f"✅ Relatório consolidado: {output_path}")
```

### Etapa 7: Exibir Resumo Final

```python
print("\n" + "="*60)
print("✅ ANÁLISE SQL COMPLETA")
print("="*60)
print(f"\n📊 Estatísticas:")
print(f"   - Tabelas: {result_ddl.table_count}")
print(f"   - Queries: {len(queries)}")
print(f"   - Operações: {result_lineage.operation_count}")
print(f"   - Risco HIGH: {result_lineage.high_risk_count}")
print(f"   - Entidades EF Core: {len(ef_mapping['entities'])}")
print(f"\n📁 Arquivos Gerados:")
print(f"   1. run/sql/analysis/database_schema.sql")
print(f"   2. run/sql/analysis/data_lineage.csv")
print(f"   3. run/sql/analysis/complexity_matrix_sql.csv")
print(f"   4. run/sql/analysis/ef_core_mapping.json")
print(f"   5. run/sql/analysis/sql_analysis_report.md")
print(f"\n✅ Análise SQL concluída com sucesso!")
```

---

## Funções Auxiliares

### calculate_complexity(query)
Calcula complexidade da query baseado em JOINs, subqueries, etc.

### map_to_csharp_type(cobol_type)
Mapeia tipo COBOL para tipo C#

### extract_foreign_keys(queries)
Extrai FKs de todas as queries

### count_navigation_properties(ef_mapping)
Conta navigation properties no mapeamento EF Core

### calculate_average_complexity(complexity_matrix)
Calcula complexidade média das queries

### count_complex_queries(complexity_matrix)
Conta queries complexas

---

## Outputs

### 1. database_schema.sql
DDL SQL Server moderno com tabelas, views, stored procedures

### 2. data_lineage.csv
Mapeamento de linhagem de dados

### 3. complexity_matrix_sql.csv
Matriz de complexidade das queries

### 4. ef_core_mapping.json
Mapeamento para Entity Framework Core

### 5. sql_analysis_report.md
Relatório consolidado da análise

---

## Validação

Verificar:
- ✅ SQL-Gate está PASS
- ✅ DDL foi gerado corretamente
- ✅ Linhagem foi mapeada
- ✅ Complexidade foi calculada
- ✅ Mapeamento EF Core foi gerado
- ✅ Relatório consolidado foi criado
- ✅ Todos os arquivos estão em run/sql/analysis/

---

**Status**: ✅ Workflow Completo  
**Versão**: 1.0  
**Data**: 2025-12-28

