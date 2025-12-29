# Workflow: [DDL-GEN] - Gerar DDL Moderno

## Objetivo
Gerar `run/sql/analysis/ddl/database_schema.sql` com DDL SQL Server moderno a partir dos claims SQL validados.

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

### Etapa 1: Carregar Inputs

```python
# Carregar claims SQL
claims = load_json("run/sql/extraction/claims_sql_A.json")
tables = claims.get("tables", [])
queries = claims.get("queries", [])

# Carregar regras de mapeamento
mapping_rules = load_csv("knowledge/sql/sql-mapping-rules.csv")
```

### Etapa 2: Gerar Header do DDL

```sql
-- ============================================
-- DATABASE SCHEMA - Gerado do Legado Visual Age
-- Arquivo Fonte: {source_file}
-- Data: {current_date}
-- Gerado por: Analyzer-A-SQL
-- Conformidade VAMAP: {conformance_percentage}%
-- ============================================
```

### Etapa 3: Gerar CREATE TABLE

Para cada tabela em `tables`:

```python
for table in tables:
    # Normalizar nome (PascalCase, singular)
    table_name = to_pascal_case(table["table_name"])
    
    ddl += f"\n-- Tabela: {table_name}\n"
    ddl += f"-- Fonte: {table['evidence_pointer']}\n"
    ddl += f"-- Operações: {count_operations(table)}\n"
    ddl += f"CREATE TABLE {table_name} (\n"
    
    # Adicionar colunas
    for column in table["columns"]:
        col_name = to_pascal_case(column["name"])
        cobol_type = column["cobol_type"]
        sql_type = map_type(cobol_type, mapping_rules)
        
        ddl += f"    {col_name} {sql_type}"
        
        # PRIMARY KEY
        if column.get("is_primary_key"):
            ddl += " PRIMARY KEY IDENTITY(1,1)"
        
        # NOT NULL
        if column.get("required") or column.get("is_primary_key"):
            ddl += " NOT NULL"
        else:
            ddl += " NULL"
        
        # DEFAULT
        if column.get("default_value"):
            ddl += f" DEFAULT {column['default_value']}"
        
        ddl += ",\n"
    
    # Adicionar colunas de auditoria
    ddl += "    \n"
    ddl += "    -- Auditoria\n"
    ddl += "    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),\n"
    ddl += "    UpdatedAt DATETIME2 NULL,\n"
    ddl += "    IsDeleted BIT NOT NULL DEFAULT 0\n"
    
    ddl += ");\n"
    ddl += "GO\n\n"
```

### Etapa 4: Identificar Relacionamentos (FKs)

Analisar JOINs nas queries para identificar Foreign Keys:

```python
foreign_keys = []

for query in queries:
    if "JOIN" in query.get("sql_statement", ""):
        # Extrair FKs do JOIN
        fks = extract_foreign_keys_from_join(query["sql_statement"])
        foreign_keys.extend(fks)

# Remover duplicatas
foreign_keys = deduplicate(foreign_keys)

# Gerar ALTER TABLE para FKs
for fk in foreign_keys:
    ddl += f"-- FK: {fk['table']} → {fk['ref_table']}\n"
    ddl += f"ALTER TABLE {fk['table']}\n"
    ddl += f"ADD CONSTRAINT FK_{fk['table']}_{fk['ref_table']}\n"
    ddl += f"FOREIGN KEY ({fk['column']})\n"
    ddl += f"REFERENCES {fk['ref_table']}({fk['ref_column']})\n"
    ddl += f"ON DELETE NO ACTION\n"
    ddl += f"ON UPDATE CASCADE;\n"
    ddl += "GO\n\n"
```

### Etapa 5: Criar Índices

```python
# Índices para FKs
for fk in foreign_keys:
    ddl += f"CREATE INDEX IX_{fk['table']}_{fk['column']}\n"
    ddl += f"ON {fk['table']}({fk['column']});\n"
    ddl += "GO\n\n"

# Índices para colunas em WHERE
where_columns = extract_where_columns(queries)
for col in where_columns:
    if not has_index(col) and not is_primary_key(col):
        ddl += f"-- Índice para WHERE frequente\n"
        ddl += f"CREATE INDEX IX_{col['table']}_{col['column']}\n"
        ddl += f"ON {col['table']}({col['column']});\n"
        ddl += "GO\n\n"
```

### Etapa 6: Criar Views

Queries recorrentes viram views:

```python
recurrent_queries = find_recurrent_queries(queries)

for query in recurrent_queries:
    view_name = f"vw_{query['purpose']}"
    
    ddl += f"-- View: {view_name}\n"
    ddl += f"-- Fonte: {query['evidence_pointer']}\n"
    ddl += f"-- Uso: {query['usage_description']}\n"
    ddl += f"CREATE VIEW {view_name} AS\n"
    ddl += f"{modernize_sql(query['sql_statement'])};\n"
    ddl += "GO\n\n"
```

### Etapa 7: Criar Stored Procedures

Lógica SQL complexa vira stored procedure:

```python
complex_queries = find_complex_queries(queries)

for query in complex_queries:
    proc_name = f"sp_{query['purpose']}"
    
    ddl += f"-- Procedure: {proc_name}\n"
    ddl += f"-- Fonte: {query['evidence_pointer']}\n"
    ddl += f"CREATE OR ALTER PROCEDURE {proc_name}\n"
    ddl += generate_parameters(query)
    ddl += "AS\n"
    ddl += "BEGIN\n"
    ddl += "    SET NOCOUNT ON;\n"
    ddl += "    \n"
    ddl += indent(modernize_sql(query['sql_statement']), 4)
    ddl += "\n"
    ddl += "END;\n"
    ddl += "GO\n\n"
```

### Etapa 8: Adicionar Comentários Finais

```sql
-- ============================================
-- COMENTÁRIOS FINAIS
-- ============================================

-- Total de tabelas: {table_count}
-- Total de views: {view_count}
-- Total de stored procedures: {proc_count}
-- Total de índices: {index_count}
-- Queries analisadas: {query_count}
-- Conformidade VAMAP: {conformance}%
-- Compatível com: Entity Framework Core 6.0+

-- Próximos passos:
-- 1. Revisar constraints e ajustar conforme necessário
-- 2. Adicionar índices adicionais baseados em performance
-- 3. Implementar stored procedures para lógica complexa
-- 4. Configurar backup e recovery
-- 5. Gerar migrations do Entity Framework Core
```

### Etapa 9: Criar Pasta DDL

```python
# Criar pasta se não existir
import os
os.makedirs("run/sql/analysis/ddl", exist_ok=True)
```

### Etapa 10: Salvar DDL

```python
output_path = "run/sql/analysis/ddl/database_schema.sql"
save_file(output_path, ddl)
print(f"✅ DDL gerado: {output_path}")
print(f"   - Tabelas: {table_count}")
print(f"   - Views: {view_count}")
print(f"   - Stored Procedures: {proc_count}")
print(f"   - Linhas: {len(ddl.split('\\n'))}")
```

---

## Funções Auxiliares

### map_type(cobol_type, mapping_rules)
Mapeia tipo COBOL para SQL Server usando `sql-mapping-rules.csv`

### to_pascal_case(name)
Converte nome para PascalCase (ex: `COD_BANCO` → `CodigoBanco`)

### extract_foreign_keys_from_join(sql)
Extrai FKs de cláusulas JOIN

### extract_where_columns(queries)
Extrai colunas usadas em WHERE

### find_recurrent_queries(queries)
Identifica queries que aparecem múltiplas vezes

### find_complex_queries(queries)
Identifica queries complexas (>= 3 JOINs, subqueries, etc)

### modernize_sql(sql)
Moderniza SQL legado para SQL Server moderno

---

## Output

**Arquivo**: `run/sql/analysis/ddl/database_schema.sql`

**Conteúdo**:
- CREATE TABLE statements
- PRIMARY KEY com IDENTITY
- FOREIGN KEY com ON DELETE/UPDATE
- Índices (PRIMARY, FOREIGN, WHERE columns)
- Constraints (CHECK, DEFAULT, UNIQUE)
- Colunas de auditoria
- Views
- Stored Procedures
- Comentários de documentação

---

## Validação

Verificar:
- ✅ DDL é válido SQL Server 2019+
- ✅ Todos os tipos COBOL foram mapeados
- ✅ PRIMARY KEYs definidas
- ✅ FOREIGN KEYs identificadas
- ✅ Índices criados para FKs
- ✅ Colunas de auditoria adicionadas
- ✅ Compatível com Entity Framework Core

---

**Status**: ✅ Workflow Completo  
**Versão**: 1.0  
**Data**: 2025-12-28

