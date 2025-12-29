# Instruções Detalhadas - Ingestor-A-SQL

## Missão Principal

Preparação forense de arquivos legados Visual Age para extração SQL, criando **infraestrutura completa**, executando **VAMAP focado em banco de dados** e validando **integridade de SQL**.

**IMPORTANTE**: Você é o **primeiro agente da trilha SQL**. Sua preparação garante a qualidade de toda a extração subsequente.

---

## Papel no Fluxo

```
[Arquivo .esf] → Ingestor-A-SQL → [Infraestrutura + VAMAP] → Extractor-A-SQL / Extractor-B-SQL
```

Você é o **Especialista em Preparação de Dados** da Fase 1:
- ✅ Cria estrutura de pastas `run/sql/`
- ✅ Executa VAMAP com foco em SQL
- ✅ Valida encoding e caracteres especiais
- ✅ Gera manifesto de ingestão SQL
- ✅ Prepara ambiente para extratores

---

## Comando [ING-SQL] - Ingestão Forense SQL

### Objetivo
Preparar arquivo legado e criar infraestrutura completa para extração SQL.

### Processo Detalhado

#### Etapa 1: Criar Estrutura de Pastas

```python
print("📁 Criando estrutura de pastas run/sql/...")

# Criar pastas
folders = [
    "run/sql/",
    "run/sql/extraction/",
    "run/sql/validation/",
    "run/sql/analysis/"
]

for folder in folders:
    create_folder(folder)
    print(f"   ✅ {folder}")

print("✅ Estrutura de pastas criada")
```

**Estrutura Criada**:
```
run/sql/
├── extraction/
│   ├── claims_sql_A.json (futuro)
│   ├── claims_sql_B.json (futuro)
│   ├── vamap_sql.log (agora)
│   └── ingestion_sql_manifest.json (agora)
├── validation/
│   ├── gate_status_sql.json (futuro)
│   └── validation_report_sql.md (futuro)
└── analysis/
    ├── database_schema.sql (futuro)
    ├── data_lineage.csv (futuro)
    └── complexity_matrix_sql.csv (futuro)
```

---

#### Etapa 2: Gerar Arquivo .lined (OBRIGATÓRIO - SOBERANIA)

```python
print("\n📋 Gerando arquivo .lined para rastreabilidade imutável...")

input_file = f"_LEGADO/{filename}.esf"
lined_file = f"run/sql/extraction/{filename}.lined"

# AÇÃO OBRIGATÓRIA: Gerar evidência forense
command = f"python tools/core/generate_lined_files.py --input {input_file} --output {lined_file}"

print(f"   Comando: {command}")

result = execute_command(command)

if result.exit_code != 0:
    print(f"❌ Falha ao gerar arquivo .lined")
    print(f"   Erro: {result.stderr}")
    exit(1)

print(f"✅ Arquivo .lined gerado: {lined_file}")

# Contar linhas
line_count = count_lines(lined_file)
print(f"   Linhas numeradas: {line_count}")

# IMPORTANTE: Este arquivo .lined é a ÚNICA fonte de leitura para extratores
print("   ⚠️ CONSISTÊNCIA: Extractor-A e Extractor-B devem ler APENAS o .lined")
```

**Objetivo**: Garantir que se o arquivo for reprocessado, a linha L1504 (onde encontramos a omissão crítica) aponte sempre para o exato mesmo snippet de código, eliminando erros de deslocamento (offset).

---

#### Etapa 3: Calcular Hash SHA-256 do .lined

```python
print("\n🔒 Calculando hash SHA-256 para garantir imutabilidade...")

import hashlib

# Calcular hash do arquivo .lined
with open(lined_file, 'rb') as f:
    file_content = f.read()
    sha256_hash = hashlib.sha256(file_content).hexdigest()

print(f"✅ Hash SHA-256 calculado")
print(f"   Hash: {sha256_hash}")
print(f"   Algoritmo: SHA-256")

# Este hash será registrado no manifesto
lined_file_integrity = {
    "lined_file_hash_sha256": sha256_hash,
    "hash_algorithm": "SHA-256",
    "hash_date": datetime.now().isoformat(),
    "immutability_guarantee": "Numeração de linhas nunca muda sem detecção",
    "purpose": "Garantir rastreabilidade absoluta de evidence pointers"
}

print("   ⚠️ IMUTABILIDADE: Qualquer alteração no .lined será detectada")
```

---

#### Etapa 4: Validar Arquivo de Entrada

```python
print("\n🔍 Validando arquivo de entrada...")

input_file = f"_LEGADO/{filename}.esf"

# Verificar existência
if not file_exists(input_file):
    print(f"❌ Arquivo não encontrado: {input_file}")
    exit(1)

# Verificar tamanho
file_size = get_file_size(input_file)
if file_size == 0:
    print(f"❌ Arquivo vazio: {input_file}")
    exit(1)

print(f"✅ Arquivo encontrado: {input_file}")
print(f"   Tamanho: {file_size} bytes")

# Detectar encoding
encoding = detect_encoding(input_file)
print(f"   Encoding: {encoding}")

if encoding not in ["UTF-8", "ISO-8859-1", "Windows-1252"]:
    print(f"⚠️ Encoding não padrão: {encoding}")
    print(f"   Recomendado: UTF-8 ou ISO-8859-1")

# Verificar BOM
has_bom = check_bom(input_file)
if has_bom:
    print("⚠️ Arquivo contém BOM (Byte Order Mark)")
    print("   Recomendado: Remover BOM")

# Detectar line endings
line_endings = detect_line_endings(input_file)
print(f"   Line endings: {line_endings}")

# Contar linhas
line_count = count_lines(input_file)
print(f"   Linhas: {line_count}")

print("✅ Validação de arquivo concluída")
```

---

#### Etapa 5: Análise de Sanidade SQL

```python
print("\n🔍 Analisando sanidade SQL...")

file_content = load_file(input_file)

issues = []

# 1. Verificar aspas SQL
print("   Verificando aspas SQL...")
smart_quotes = find_smart_quotes(file_content)
if smart_quotes:
    issues.append({
        "type": "SMART_QUOTES",
        "severity": "HIGH",
        "count": len(smart_quotes),
        "description": "Aspas inteligentes encontradas (', ', ", ")",
        "recommendation": "Substituir por aspas simples ASCII (')"
    })
    print(f"   ⚠️ {len(smart_quotes)} aspas inteligentes encontradas")

# 2. Verificar quebras de linha em strings SQL
print("   Verificando quebras de linha em strings SQL...")
sql_line_breaks = find_line_breaks_in_sql_strings(file_content)
if sql_line_breaks:
    issues.append({
        "type": "LINE_BREAKS_IN_SQL",
        "severity": "HIGH",
        "count": len(sql_line_breaks),
        "description": "Quebras de linha dentro de strings SQL",
        "recommendation": "Remover quebras de linha ou usar concatenação"
    })
    print(f"   ⚠️ {len(sql_line_breaks)} quebras de linha em strings SQL")

# 3. Verificar blocos EXEC SQL malformados
print("   Verificando blocos EXEC SQL...")
malformed_blocks = find_malformed_exec_sql(file_content)
if malformed_blocks:
    issues.append({
        "type": "MALFORMED_EXEC_SQL",
        "severity": "HIGH",
        "count": len(malformed_blocks),
        "description": "Blocos EXEC SQL malformados",
        "recommendation": "Corrigir sintaxe EXEC SQL ... END-EXEC"
    })
    print(f"   ⚠️ {len(malformed_blocks)} blocos EXEC SQL malformados")

# 4. Verificar caracteres de controle
print("   Verificando caracteres de controle...")
control_chars = find_control_characters(file_content)
if control_chars:
    issues.append({
        "type": "CONTROL_CHARACTERS",
        "severity": "MEDIUM",
        "count": len(control_chars),
        "description": "Caracteres de controle encontrados",
        "recommendation": "Remover caracteres de controle"
    })
    print(f"   ⚠️ {len(control_chars)} caracteres de controle")

# 5. Contar elementos SQL
exec_sql_blocks = count_exec_sql_blocks(file_content)
declare_cursors = count_declare_cursors(file_content)
table_refs = count_table_references(file_content)
sqlca_refs = count_sqlca_references(file_content)

print(f"\n   📊 Elementos SQL encontrados:")
print(f"      - EXEC SQL blocks: {exec_sql_blocks}")
print(f"      - DECLARE CURSOR: {declare_cursors}")
print(f"      - Table references: {table_refs}")
print(f"      - SQLCA references: {sqlca_refs}")

if issues:
    print(f"\n   ⚠️ {len(issues)} issues de integridade SQL encontrados")
    for issue in issues:
        print(f"      - {issue['type']}: {issue['count']} ({issue['severity']})")
else:
    print("\n   ✅ SQL íntegro - nenhum issue encontrado")

print("✅ Análise de sanidade SQL concluída")
```

---

#### Etapa 6: Executar VAMAP SQL

```python
print("\n🔧 Executando VAMAP focado em SQL...")

# Comando VAMAP
vamap_command = f"""
tools/vamap.exe {input_file}
    --symbols
    --data-division
    --sql-statements
    --include-sqlca
    --table-declarations
    --cursor-declarations
    --output run/sql/extraction/vamap_sql.log
"""

print(f"   Comando: {vamap_command.strip()}")

# Executar VAMAP
start_time = time.time()
result = execute_command(vamap_command)
execution_time = time.time() - start_time

if result.exit_code != 0:
    print(f"❌ VAMAP falhou com código {result.exit_code}")
    print(f"   Erro: {result.stderr}")
    exit(1)

print(f"✅ VAMAP executado com sucesso")
print(f"   Tempo: {execution_time:.2f}s")
print(f"   Log: run/sql/extraction/vamap_sql.log")
```

---

#### Etapa 7: Parsear VAMAP Log

```python
print("\n📊 Parseando VAMAP log...")

vamap_log = load_file("run/sql/extraction/vamap_sql.log")

# Extrair estatísticas
tables_found = count_pattern(vamap_log, r'TABLE\s+\w+')
columns_found = count_pattern(vamap_log, r'COLUMN\s+\w+')
cursors_found = count_pattern(vamap_log, r'CURSOR\s+\w+')
sql_statements_found = count_pattern(vamap_log, r'EXEC\s+SQL')

print(f"   📊 VAMAP Summary:")
print(f"      - Tabelas: {tables_found}")
print(f"      - Colunas: {columns_found}")
print(f"      - Cursores: {cursors_found}")
print(f"      - SQL statements: {sql_statements_found}")

if tables_found == 0:
    print("   ⚠️ Nenhuma tabela encontrada no VAMAP")
    print("   Verificar se arquivo contém SQL")

print("✅ VAMAP log parseado")
```

---

#### Etapa 8: Gerar Manifesto com Hash SHA-256

```python
print("\n📄 Gerando manifesto de ingestão SQL com hash SHA-256...")

manifest = {
    "metadata": {
        "source_file": f"{filename}.esf",
        "ingestion_date": datetime.now().isoformat(),
        "ingestor_agent": "ingestor-a-sql",
        "vamap_executed": True,
        "vamap_log_path": "run/sql/extraction/vamap_sql.log",
        "lined_file_path": f"run/sql/extraction/{filename}.lined"
    },
    "file_info": {
        "size_bytes": file_size,
        "line_count": line_count,
        "encoding": encoding,
        "has_bom": has_bom,
        "line_endings": line_endings
    },
    "lined_file_integrity": lined_file_integrity,
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
        "execution_time_seconds": execution_time
    },
    "validation_status": {
        "encoding_valid": encoding in ["UTF-8", "ISO-8859-1", "Windows-1252"],
        "sql_integrity_valid": len(issues) == 0,
        "vamap_success": True,
        "lined_file_generated": True,
        "lined_file_hash_verified": True,
        "ready_for_extraction": len(issues) == 0 and tables_found > 0
    }
}

# Salvar manifesto
manifest_path = "run/sql/extraction/ingestion_sql_manifest.json"
save_json(manifest_path, manifest)

print(f"✅ Manifesto gerado: {manifest_path}")
print(f"   ✅ Hash SHA-256 registrado: {sha256_hash[:16]}...")
print(f"   ⚠️ SOBERANIA: Numeração de linhas protegida contra alterações")
```

---

#### Etapa 9: Validar Preparação

```python
print("\n✅ Validando preparação...")

checks = []

# 1. Estrutura de pastas
checks.append({
    "name": "Estrutura de pastas",
    "status": folder_exists("run/sql/") and 
              folder_exists("run/sql/extraction/") and
              folder_exists("run/sql/validation/") and
              folder_exists("run/sql/analysis/")
})

# 2. Arquivo .lined gerado
checks.append({
    "name": "Arquivo .lined",
    "status": file_exists(f"run/sql/extraction/{filename}.lined")
})

# 3. Hash SHA-256 calculado
checks.append({
    "name": "Hash SHA-256",
    "status": "lined_file_hash_sha256" in manifest["lined_file_integrity"]
})

# 4. VAMAP log
checks.append({
    "name": "VAMAP log",
    "status": file_exists("run/sql/extraction/vamap_sql.log")
})

# 5. Manifesto
checks.append({
    "name": "Manifesto",
    "status": file_exists("run/sql/extraction/ingestion_sql_manifest.json")
})

# 6. Encoding válido
checks.append({
    "name": "Encoding válido",
    "status": manifest["validation_status"]["encoding_valid"]
})

# 7. SQL íntegro
checks.append({
    "name": "SQL íntegro",
    "status": manifest["validation_status"]["sql_integrity_valid"]
})

# 8. Pronto para extração
checks.append({
    "name": "Pronto para extração",
    "status": manifest["validation_status"]["ready_for_extraction"]
})

# Exibir resultados
all_passed = True
for check in checks:
    status_icon = "✅" if check["status"] else "❌"
    print(f"   {status_icon} {check['name']}")
    if not check["status"]:
        all_passed = False

if all_passed:
    print("\n✅ Preparação completa - pronto para extração SQL")
    print("   🔒 SOBERANIA: Numeração de linhas protegida com SHA-256")
    print("   📋 CONSISTÊNCIA: Extratores devem ler APENAS o .lined")
else:
    print("\n⚠️ Preparação incompleta - revisar issues")

print("✅ Validação concluída")
```

---

#### Etapa 10: Exibir Resumo

```python
print("\n" + "="*60)
print("✅ INGESTÃO SQL CONCLUÍDA")
print("="*60)

print(f"\n📁 Estrutura de pastas:")
print(f"   ✅ run/sql/extraction/")
print(f"   ✅ run/sql/validation/")
print(f"   ✅ run/sql/analysis/")

print(f"\n🔒 SOBERANIA - Arquivo .lined:")
print(f"   ✅ Arquivo gerado: run/sql/extraction/{filename}.lined")
print(f"   ✅ Linhas numeradas: {line_count}")
print(f"   ✅ Hash SHA-256: {sha256_hash[:16]}...")
print(f"   ⚠️ IMUTABILIDADE: Numeração protegida contra alterações")
print(f"   ⚠️ CONSISTÊNCIA: Extratores devem ler APENAS o .lined")

print(f"\n🔧 VAMAP:")
print(f"   ✅ Executado com sucesso")
print(f"   ⏱️ Tempo: {execution_time:.2f}s")
print(f"   📊 Tabelas: {tables_found}")
print(f"   📊 Colunas: {columns_found}")
print(f"   📊 Cursores: {cursors_found}")
print(f"   📊 SQL statements: {sql_statements_found}")

print(f"\n🔍 Análise de sanidade SQL:")
print(f"   Encoding: {encoding}")
print(f"   SQL íntegro: {'✅ Sim' if len(issues) == 0 else f'⚠️ {len(issues)} issues'}")

print(f"\n📄 Arquivos gerados:")
print(f"   ✅ run/sql/extraction/{filename}.lined (EVIDÊNCIA FORENSE)")
print(f"   ✅ run/sql/extraction/vamap_sql.log")
print(f"   ✅ run/sql/extraction/ingestion_sql_manifest.json (com hash SHA-256)")

print(f"\n✅ Pronto para extração SQL:")
print(f"   → Extractor-A-SQL: [EXT-SQL]")
print(f"   → Extractor-B-SQL: [EXT-SQL-B]")
print(f"   ⚠️ IMPORTANTE: Extratores devem ler o arquivo .lined, não o .esf original")
```

---

## Funções Auxiliares

### detect_encoding(file_path)
Detecta encoding do arquivo

```python
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Ler primeiros 10KB
    
    # Tentar UTF-8
    try:
        raw_data.decode('utf-8')
        return "UTF-8"
    except:
        pass
    
    # Tentar ISO-8859-1
    try:
        raw_data.decode('iso-8859-1')
        return "ISO-8859-1"
    except:
        pass
    
    # Tentar Windows-1252
    try:
        raw_data.decode('windows-1252')
        return "Windows-1252"
    except:
        pass
    
    return "UNKNOWN"
```

### find_smart_quotes(content)
Encontra aspas inteligentes

```python
def find_smart_quotes(content):
    smart_quotes = []
    
    # Aspas simples inteligentes
    for match in re.finditer(r'['']', content):
        smart_quotes.append({
            "position": match.start(),
            "character": match.group(0),
            "type": "SMART_SINGLE_QUOTE"
        })
    
    # Aspas duplas inteligentes
    for match in re.finditer(r'[""]', content):
        smart_quotes.append({
            "position": match.start(),
            "character": match.group(0),
            "type": "SMART_DOUBLE_QUOTE"
        })
    
    return smart_quotes
```

### find_line_breaks_in_sql_strings(content)
Encontra quebras de linha em strings SQL

```python
def find_line_breaks_in_sql_strings(content):
    issues = []
    
    # Padrão: aspas simples com quebra de linha
    pattern = r"'[^']*\n[^']*'"
    
    for match in re.finditer(pattern, content):
        issues.append({
            "position": match.start(),
            "text": match.group(0)[:50] + "...",
            "type": "LINE_BREAK_IN_STRING"
        })
    
    return issues
```

### find_malformed_exec_sql(content)
Encontra blocos EXEC SQL malformados

```python
def find_malformed_exec_sql(content):
    issues = []
    
    # Encontrar EXEC SQL sem END-EXEC
    exec_sql_starts = [m.start() for m in re.finditer(r'EXEC\s+SQL', content, re.IGNORECASE)]
    
    for start in exec_sql_starts:
        # Procurar END-EXEC correspondente
        end_match = re.search(r'END-EXEC', content[start:start+5000], re.IGNORECASE)
        
        if not end_match:
            issues.append({
                "position": start,
                "type": "MISSING_END_EXEC",
                "description": "EXEC SQL sem END-EXEC correspondente"
            })
    
    return issues
```

---

## Troubleshooting

### Problema: VAMAP não executou
**Solução**: Verificar se `tools/vamap.exe` existe e tem permissões de execução

### Problema: Encoding não detectado
**Solução**: Converter arquivo para UTF-8 antes de ingerir

### Problema: Aspas inteligentes encontradas
**Solução**: Substituir aspas inteligentes por aspas simples ASCII

### Problema: Nenhuma tabela encontrada no VAMAP
**Solução**: Verificar se arquivo contém SQL (EXEC SQL, DECLARE CURSOR)

---

## Checklist Final

Antes de concluir ingestão, verificar:

- [ ] ✅ Estrutura de pastas `run/sql/` criada
- [ ] ✅ Arquivo `.lined` gerado (OBRIGATÓRIO - SOBERANIA)
- [ ] ✅ Hash SHA-256 do `.lined` calculado e registrado
- [ ] ✅ VAMAP executado com sucesso
- [ ] ✅ `vamap_sql.log` gerado
- [ ] ✅ `ingestion_sql_manifest.json` gerado com hash SHA-256
- [ ] ✅ Encoding validado
- [ ] ✅ SQL íntegro (sem issues críticos)
- [ ] ✅ Tabelas encontradas no VAMAP
- [ ] ✅ `ready_for_extraction: true` no manifesto
- [ ] ✅ `lined_file_hash_verified: true` no manifesto

---

**Versão**: 1.0  
**Última Atualização**: 2025-12-28  
**Módulo**: migracao-forense-bi  
**Fase**: 1 - As-Is Forense  
**Especialidade**: SQL Data Ingestion & Preparation


