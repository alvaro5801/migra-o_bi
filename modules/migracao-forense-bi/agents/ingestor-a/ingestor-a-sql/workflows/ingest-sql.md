# Workflow: [ING-SQL] - Ingestão Forense SQL

## Objetivo
Preparar arquivo legado Visual Age e criar infraestrutura completa para extração SQL, incluindo execução do VAMAP focado em banco de dados.

---

## Pré-requisitos

### 1. Verificar Arquivo de Entrada
```
Arquivo: input/{filename}.esf
Formato: Visual Age COBOL
```

### 2. Verificar Ferramentas
```
- tools/vamap.exe (executável VAMAP)
```

### 3. Verificar Knowledge Base
```
- knowledge/sql/sql-patterns-visualage.csv
- knowledge/sql/sql-mapping-rules.csv
```

---

## Etapas do Workflow

### Etapa 1: Criar Estrutura de Pastas

```python
print("📁 Criando estrutura de pastas run/sql/...")

# Definir pastas
folders = [
    "run/sql/",
    "run/sql/extraction/",
    "run/sql/validation/",
    "run/sql/analysis/"
]

# Criar pastas
for folder in folders:
    if not folder_exists(folder):
        create_folder(folder)
        print(f"   ✅ Criado: {folder}")
    else:
        print(f"   ℹ️ Já existe: {folder}")

print("✅ Estrutura de pastas criada")
```

**Estrutura Resultante**:
```
run/sql/
├── extraction/       # Claims SQL e VAMAP log
├── validation/       # Gate status e relatórios
└── analysis/         # DDL, linhagem e análises
```

---

### Etapa 2: Validar Arquivo de Entrada

```python
print("\n🔍 Validando arquivo de entrada...")

input_file = f"input/{filename}.esf"

# 1. Verificar existência
if not file_exists(input_file):
    print(f"❌ Arquivo não encontrado: {input_file}")
    exit(1)

print(f"✅ Arquivo encontrado: {input_file}")

# 2. Verificar tamanho
file_size = get_file_size(input_file)
if file_size == 0:
    print(f"❌ Arquivo vazio")
    exit(1)

print(f"   Tamanho: {file_size:,} bytes ({file_size / 1024:.2f} KB)")

# 3. Detectar encoding
encoding = detect_encoding(input_file)
print(f"   Encoding: {encoding}")

if encoding not in ["UTF-8", "ISO-8859-1", "Windows-1252"]:
    print(f"   ⚠️ Encoding não padrão: {encoding}")

# 4. Verificar BOM
has_bom = check_bom(input_file)
if has_bom:
    print("   ⚠️ Arquivo contém BOM (Byte Order Mark)")

# 5. Detectar line endings
line_endings = detect_line_endings(input_file)
print(f"   Line endings: {line_endings}")

# 6. Contar linhas
line_count = count_lines(input_file)
print(f"   Linhas: {line_count:,}")

print("✅ Validação de arquivo concluída")
```

---

### Etapa 3: Análise de Sanidade SQL

```python
print("\n🔍 Analisando sanidade SQL...")

file_content = load_file(input_file)
issues = []

# 1. Verificar aspas SQL
print("   🔍 Verificando aspas SQL...")
smart_quotes = find_smart_quotes(file_content)
if smart_quotes:
    issues.append({
        "type": "SMART_QUOTES",
        "severity": "HIGH",
        "count": len(smart_quotes),
        "description": "Aspas inteligentes encontradas",
        "recommendation": "Substituir por aspas simples ASCII (')",
        "examples": [sq["character"] for sq in smart_quotes[:5]]
    })
    print(f"      ⚠️ {len(smart_quotes)} aspas inteligentes")
else:
    print(f"      ✅ Aspas SQL válidas")

# 2. Verificar quebras de linha em strings SQL
print("   🔍 Verificando quebras de linha em strings SQL...")
sql_line_breaks = find_line_breaks_in_sql_strings(file_content)
if sql_line_breaks:
    issues.append({
        "type": "LINE_BREAKS_IN_SQL",
        "severity": "HIGH",
        "count": len(sql_line_breaks),
        "description": "Quebras de linha dentro de strings SQL",
        "recommendation": "Remover quebras ou usar concatenação"
    })
    print(f"      ⚠️ {len(sql_line_breaks)} quebras de linha em strings")
else:
    print(f"      ✅ Sem quebras de linha em strings SQL")

# 3. Verificar blocos EXEC SQL malformados
print("   🔍 Verificando blocos EXEC SQL...")
malformed_blocks = find_malformed_exec_sql(file_content)
if malformed_blocks:
    issues.append({
        "type": "MALFORMED_EXEC_SQL",
        "severity": "HIGH",
        "count": len(malformed_blocks),
        "description": "Blocos EXEC SQL malformados",
        "recommendation": "Corrigir sintaxe EXEC SQL ... END-EXEC"
    })
    print(f"      ⚠️ {len(malformed_blocks)} blocos malformados")
else:
    print(f"      ✅ Blocos EXEC SQL bem formados")

# 4. Verificar caracteres de controle
print("   🔍 Verificando caracteres de controle...")
control_chars = find_control_characters(file_content)
if control_chars:
    issues.append({
        "type": "CONTROL_CHARACTERS",
        "severity": "MEDIUM",
        "count": len(control_chars),
        "description": "Caracteres de controle encontrados",
        "recommendation": "Remover caracteres de controle"
    })
    print(f"      ⚠️ {len(control_chars)} caracteres de controle")
else:
    print(f"      ✅ Sem caracteres de controle")

# 5. Contar elementos SQL
print("   📊 Contando elementos SQL...")
exec_sql_blocks = count_exec_sql_blocks(file_content)
declare_cursors = count_declare_cursors(file_content)
table_refs = count_table_references(file_content)
sqlca_refs = count_sqlca_references(file_content)

print(f"      - EXEC SQL blocks: {exec_sql_blocks}")
print(f"      - DECLARE CURSOR: {declare_cursors}")
print(f"      - Table references: {table_refs}")
print(f"      - SQLCA references: {sqlca_refs}")

# Resumo
if issues:
    print(f"\n   ⚠️ {len(issues)} issues de integridade SQL")
    for issue in issues:
        print(f"      - {issue['type']}: {issue['count']} ({issue['severity']})")
else:
    print(f"\n   ✅ SQL íntegro - nenhum issue encontrado")

print("✅ Análise de sanidade SQL concluída")
```

---

### Etapa 4: Executar VAMAP SQL

```python
print("\n🔧 Executando VAMAP focado em SQL...")

# Verificar se vamap.exe existe
if not file_exists("tools/vamap.exe"):
    print("❌ VAMAP não encontrado: tools/vamap.exe")
    print("   Por favor, instalar VAMAP antes de continuar")
    exit(1)

# Construir comando
vamap_command = [
    "tools/vamap.exe",
    input_file,
    "--symbols",
    "--data-division",
    "--sql-statements",
    "--include-sqlca",
    "--table-declarations",
    "--cursor-declarations",
    "--output", "run/sql/extraction/vamap_sql.log"
]

print(f"   Comando: {' '.join(vamap_command)}")

# Executar VAMAP
start_time = time.time()
result = execute_command(vamap_command)
execution_time = time.time() - start_time

if result.exit_code != 0:
    print(f"❌ VAMAP falhou com código {result.exit_code}")
    print(f"   Stderr: {result.stderr}")
    exit(1)

print(f"✅ VAMAP executado com sucesso")
print(f"   Tempo: {execution_time:.2f}s")
print(f"   Log: run/sql/extraction/vamap_sql.log")

# Verificar se log foi gerado
if not file_exists("run/sql/extraction/vamap_sql.log"):
    print("❌ VAMAP log não foi gerado")
    exit(1)

vamap_log_size = get_file_size("run/sql/extraction/vamap_sql.log")
print(f"   Tamanho do log: {vamap_log_size:,} bytes")
```

---

### Etapa 5: Parsear VAMAP Log

```python
print("\n📊 Parseando VAMAP log...")

vamap_log = load_file("run/sql/extraction/vamap_sql.log")

# Extrair estatísticas
print("   🔍 Extraindo estatísticas...")

tables_found = count_pattern(vamap_log, r'TABLE\s+\w+')
columns_found = count_pattern(vamap_log, r'COLUMN\s+\w+')
cursors_found = count_pattern(vamap_log, r'CURSOR\s+\w+')
sql_statements_found = count_pattern(vamap_log, r'EXEC\s+SQL')

print(f"\n   📊 VAMAP Summary:")
print(f"      - Tabelas: {tables_found}")
print(f"      - Colunas: {columns_found}")
print(f"      - Cursores: {cursors_found}")
print(f"      - SQL statements: {sql_statements_found}")

# Alertas
if tables_found == 0:
    print(f"\n   ⚠️ Nenhuma tabela encontrada no VAMAP")
    print(f"      Verificar se arquivo contém SQL")

if sql_statements_found == 0:
    print(f"\n   ⚠️ Nenhum SQL statement encontrado")
    print(f"      Verificar se arquivo contém EXEC SQL")

print("✅ VAMAP log parseado")
```

---

### Etapa 6: Gerar Manifesto

```python
print("\n📄 Gerando manifesto de ingestão SQL...")

manifest = {
    "metadata": {
        "source_file": f"{filename}.esf",
        "ingestion_date": datetime.now().isoformat(),
        "ingestor_agent": "ingestor-a-sql",
        "vamap_executed": True,
        "vamap_log_path": "run/sql/extraction/vamap_sql.log"
    },
    "file_info": {
        "size_bytes": file_size,
        "line_count": line_count,
        "encoding": encoding,
        "has_bom": has_bom,
        "line_endings": line_endings
    },
    "sql_analysis": {
        "exec_sql_blocks": exec_sql_blocks,
        "declare_cursor_count": declare_cursors,
        "table_references": table_refs,
        "sqlca_references": sqlca_refs,
        "sql_integrity_issues": issues
    },
    "vamap_summary": {
        "tables_found": tables_found,
        "columns_found": columns_found,
        "cursors_found": cursors_found,
        "sql_statements_found": sql_statements_found,
        "execution_time_seconds": round(execution_time, 2)
    },
    "validation_status": {
        "encoding_valid": encoding in ["UTF-8", "ISO-8859-1", "Windows-1252"],
        "sql_integrity_valid": len([i for i in issues if i["severity"] == "HIGH"]) == 0,
        "vamap_success": True,
        "ready_for_extraction": (
            len([i for i in issues if i["severity"] == "HIGH"]) == 0 and
            tables_found > 0
        )
    }
}

# Salvar manifesto
manifest_path = "run/sql/extraction/ingestion_sql_manifest.json"
save_json(manifest_path, manifest, indent=2)

print(f"✅ Manifesto gerado: {manifest_path}")
```

---

### Etapa 7: Validar Preparação

```python
print("\n✅ Validando preparação...")

checks = [
    {
        "name": "Estrutura de pastas",
        "status": (
            folder_exists("run/sql/") and
            folder_exists("run/sql/extraction/") and
            folder_exists("run/sql/validation/") and
            folder_exists("run/sql/analysis/")
        )
    },
    {
        "name": "VAMAP log",
        "status": file_exists("run/sql/extraction/vamap_sql.log")
    },
    {
        "name": "Manifesto",
        "status": file_exists("run/sql/extraction/ingestion_sql_manifest.json")
    },
    {
        "name": "Encoding válido",
        "status": manifest["validation_status"]["encoding_valid"]
    },
    {
        "name": "SQL íntegro",
        "status": manifest["validation_status"]["sql_integrity_valid"]
    },
    {
        "name": "Pronto para extração",
        "status": manifest["validation_status"]["ready_for_extraction"]
    }
]

# Exibir resultados
all_passed = True
for check in checks:
    status_icon = "✅" if check["status"] else "❌"
    print(f"   {status_icon} {check['name']}")
    if not check["status"]:
        all_passed = False

if all_passed:
    print("\n✅ Preparação completa - pronto para extração SQL")
else:
    print("\n⚠️ Preparação incompleta - revisar issues")

print("✅ Validação concluída")
```

---

### Etapa 8: Exibir Resumo

```python
print("\n" + "="*60)
print("✅ INGESTÃO SQL CONCLUÍDA")
print("="*60)

print(f"\n📁 Estrutura de pastas:")
print(f"   ✅ run/sql/extraction/")
print(f"   ✅ run/sql/validation/")
print(f"   ✅ run/sql/analysis/")

print(f"\n🔧 VAMAP:")
print(f"   ✅ Executado com sucesso")
print(f"   ⏱️ Tempo: {execution_time:.2f}s")
print(f"   📊 Tabelas: {tables_found}")
print(f"   📊 Colunas: {columns_found}")
print(f"   📊 Cursores: {cursors_found}")
print(f"   📊 SQL statements: {sql_statements_found}")

print(f"\n🔍 Análise de sanidade SQL:")
print(f"   Encoding: {encoding}")
print(f"   SQL íntegro: {'✅ Sim' if len([i for i in issues if i['severity'] == 'HIGH']) == 0 else f'⚠️ {len([i for i in issues if i["severity"] == "HIGH"])} issues HIGH'}")

print(f"\n📄 Arquivos gerados:")
print(f"   ✅ run/sql/extraction/vamap_sql.log ({vamap_log_size:,} bytes)")
print(f"   ✅ run/sql/extraction/ingestion_sql_manifest.json")

if manifest["validation_status"]["ready_for_extraction"]:
    print(f"\n✅ Pronto para extração SQL:")
    print(f"   → Extractor-A-SQL: [EXT-SQL]")
    print(f"   → Extractor-B-SQL: [EXT-SQL-B]")
else:
    print(f"\n⚠️ NÃO pronto para extração:")
    if not manifest["validation_status"]["sql_integrity_valid"]:
        print(f"   - Corrigir issues de integridade SQL")
    if tables_found == 0:
        print(f"   - Nenhuma tabela encontrada no VAMAP")

print("\n✅ Ingestão SQL concluída!")
```

---

## Output

**Arquivos Gerados**:
1. `run/sql/extraction/vamap_sql.log` - Log VAMAP focado em SQL
2. `run/sql/extraction/ingestion_sql_manifest.json` - Manifesto de ingestão

**Estrutura Criada**:
```
run/sql/
├── extraction/
├── validation/
└── analysis/
```

---

## Validação

Verificar:
- ✅ Estrutura de pastas criada
- ✅ VAMAP executado com sucesso
- ✅ vamap_sql.log gerado
- ✅ ingestion_sql_manifest.json gerado
- ✅ Encoding validado
- ✅ SQL íntegro
- ✅ Tabelas encontradas no VAMAP
- ✅ ready_for_extraction: true

---

**Status**: ✅ Workflow Completo  
**Versão**: 1.0  
**Data**: 2025-12-28

