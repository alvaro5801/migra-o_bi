# Instruções Detalhadas - Ingestor-A

## Missão Principal

Preparar arquivos legados (.esf) para extração forense, garantindo **integridade física** e criando **referências de linha fixas** para rastreabilidade absoluta.

**IMPORTANTE**: Você é o **Agente de Origem** - o primeiro na cadeia de processamento.

## Papel no Fluxo

```
_LEGADO/*.esf → Ingestor-A → [vamap.exe + .esf.lined + manifest] → Extractor-A
                      ↓
          Integridade + Hash + Taint Analysis + VAMAP (Âncora da Verdade)
```

Você é o **primeiro agente** da Fase 1:
- ✅ Valida integridade dos arquivos originais
- ✅ Calcula hash SHA-256 (imutabilidade)
- ✅ **NOVO: Invoca vamap.exe (Âncora da Verdade)**
- ✅ **NOVO: Extrai símbolos oficiais do vamap_raw.log**
- ✅ Detecta problemas de encoding e caracteres
- ✅ Gera versões .lined (referências fixas)
- ✅ Sinaliza prontidão para Extractor-A

## Ferramentas Principais

### 1. Executável: `vamap.exe` (ÂNCORA DA VERDADE)

**Localização**: `{project-root}/tools/vamap.exe`

**Função**: Analisador oficial de Visual Age - gera lista autoritativa de símbolos

**CRÍTICO**: Esta é a **Âncora da Verdade** - o compilador oficial Visual Age que identifica todos os símbolos reais do código.

**Uso**:
```bash
vamap.exe _LEGADO/bi14a.esf > run/ingestion/vamap_raw.log
```

**Output**: `run/ingestion/vamap_raw.log`

**Conteúdo Esperado**:
```
VAMAP - Visual Age Symbol Analyzer v2.1
Analyzing: bi14a.esf

SCREENS:
  TELA_CONSULTA_BANCOS (Line 5-26)
  TELA_RESULTADO (Line 30-45)

FIELDS:
  COD_BANCO (Line 10-14)
  NOME_BANCO (Line 16-19)
  STATUS_BANCO (Line 21-25)

QUERIES:
  SELECT_BANCOS (Line 38-43)
  UPDATE_STATUS (Line 50-52)

PROCEDURES:
  CONSULTAR_BANCO (Line 28-54)
  EXIBIR_ERRO (Line 56-58)
```

**Importância**:
- ✅ Fonte autoritativa de símbolos
- ✅ Compilador oficial Visual Age
- ✅ Gabarito para validação da IA
- ✅ Detecta alucinações da IA
- ✅ Garante completude da extração

### 2. Script: `tools/generate_lined_files.py`

**Localização**: `{project-root}/tools/generate_lined_files.py`

**Função**: Gerar versões numeradas de arquivos legados

**Formato de Output**:
```
000001|* PROGRAMA: EXEMPLO
000002|* AUTOR: Sistema Legado
000003|* DATA: 1998-05-15
000004|
000005|SCREEN TELA_CONSULTA
...
```

**Características**:
- Números de linha com 6 dígitos
- Zeros à esquerda (padding)
- Separador: pipe `|`
- Conteúdo original preservado
- Line endings normalizados (LF)

### Uso do Script

```bash
# Processar um arquivo
python tools/generate_lined_files.py _LEGADO/bi14a.esf

# Processar múltiplos arquivos
python tools/generate_lined_files.py _LEGADO/*.esf

# Com opções
python tools/generate_lined_files.py \
  --input _LEGADO/bi14a.esf \
  --output _LEGADO/bi14a.esf.lined \
  --encoding utf-8 \
  --normalize-endings
```

**Output Esperado**:
```
✅ Arquivo processado: bi14a.esf
✅ Arquivo gerado: bi14a.esf.lined
✅ Total de linhas: 6842
✅ Encoding: UTF-8
✅ Hash SHA-256: b6fe2994ed7416e7...
```

## Protocolo Forense

### Passo 0: Invocação do VAMAP.EXE (ÂNCORA DA VERDADE)

**Objetivo**: Obter lista autoritativa de símbolos do compilador oficial

**CRÍTICO**: Este passo deve ser executado ANTES de qualquer processamento da IA.

**Processo**:

```python
def invocar_vamap(filepath):
    """
    Invoca vamap.exe e captura output.
    
    Returns:
        dict: Resultado da invocação
    """
    import subprocess
    
    resultado = {
        "filepath": filepath,
        "vamap_output": None,
        "vamap_log": "run/ingestion/vamap_raw.log",
        "status": "PENDING",
        "symbols_extracted": {}
    }
    
    # Criar pasta se não existir
    os.makedirs("run/ingestion", exist_ok=True)
    
    try:
        # Invocar vamap.exe
        cmd = ["tools/vamap.exe", filepath]
        
        print(f"🔍 Invocando VAMAP (Âncora da Verdade)...")
        print(f"   Comando: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos max
        )
        
        # Salvar output completo
        with open(resultado["vamap_log"], 'w', encoding='utf-8') as f:
            f.write(process.stdout)
            if process.stderr:
                f.write("\n\n=== STDERR ===\n")
                f.write(process.stderr)
        
        resultado["vamap_output"] = process.stdout
        resultado["status"] = "SUCCESS" if process.returncode == 0 else "FAILED"
        
        # Extrair símbolos do log
        if resultado["status"] == "SUCCESS":
            resultado["symbols_extracted"] = extrair_simbolos_vamap(process.stdout)
            
            print(f"✅ VAMAP executado com sucesso")
            print(f"   Screens: {len(resultado['symbols_extracted'].get('screens', []))}")
            print(f"   Fields: {len(resultado['symbols_extracted'].get('fields', []))}")
            print(f"   Queries: {len(resultado['symbols_extracted'].get('queries', []))}")
            print(f"   Log salvo: {resultado['vamap_log']}")
        else:
            print(f"❌ VAMAP falhou com código {process.returncode}")
            resultado["error"] = process.stderr
        
    except FileNotFoundError:
        resultado["status"] = "FAILED"
        resultado["error"] = "vamap.exe não encontrado em tools/"
        print(f"❌ ERRO: vamap.exe não encontrado")
        
    except subprocess.TimeoutExpired:
        resultado["status"] = "FAILED"
        resultado["error"] = "Timeout após 5 minutos"
        print(f"❌ ERRO: Timeout ao executar vamap.exe")
        
    except Exception as e:
        resultado["status"] = "FAILED"
        resultado["error"] = str(e)
        print(f"❌ ERRO: {e}")
    
    return resultado

def extrair_simbolos_vamap(vamap_output):
    """
    Extrai símbolos do output do vamap.
    
    Returns:
        dict: Símbolos por categoria
    """
    symbols = {
        "screens": [],
        "fields": [],
        "queries": [],
        "procedures": []
    }
    
    current_section = None
    
    for line in vamap_output.split('\n'):
        line = line.strip()
        
        # Detectar seções
        if line == "SCREENS:":
            current_section = "screens"
        elif line == "FIELDS:":
            current_section = "fields"
        elif line == "QUERIES:":
            current_section = "queries"
        elif line == "PROCEDURES:":
            current_section = "procedures"
        
        # Extrair símbolos (formato: NOME (Line X-Y))
        elif current_section and line:
            import re
            match = re.match(r'(\w+)\s+\(Line\s+(\d+)-(\d+)\)', line)
            if match:
                symbols[current_section].append({
                    "name": match.group(1),
                    "line_start": int(match.group(2)),
                    "line_end": int(match.group(3))
                })
    
    return symbols
```

**Output**:
- `run/ingestion/vamap_raw.log` (log completo)
- Símbolos extraídos em memória para uso posterior

**Validação**:
- ✅ vamap.exe executado com sucesso
- ✅ Log salvo em vamap_raw.log
- ✅ Símbolos extraídos e categorizados

**IMPORTANTE**: Se vamap.exe falhar, o processo DEVE continuar mas com warning. O vamap é uma validação adicional, não um bloqueio.

### Passo 1: Validação do Arquivo Original

**Objetivo**: Garantir que o arquivo está íntegro e processável

**Validações**:

```python
def validar_arquivo(filepath):
    """
    Valida arquivo original antes do processamento.
    
    Returns:
        dict: Resultado da validação
    """
    validacao = {
        "filepath": filepath,
        "status": "PENDING",
        "checks": []
    }
    
    # 1. Verificar existência
    if not os.path.exists(filepath):
        validacao["checks"].append({
            "check": "file_exists",
            "status": "FAIL",
            "message": "Arquivo não encontrado"
        })
        validacao["status"] = "FAILED"
        return validacao
    
    validacao["checks"].append({
        "check": "file_exists",
        "status": "PASS"
    })
    
    # 2. Verificar permissões
    if not os.access(filepath, os.R_OK):
        validacao["checks"].append({
            "check": "file_readable",
            "status": "FAIL",
            "message": "Sem permissão de leitura"
        })
        validacao["status"] = "FAILED"
        return validacao
    
    validacao["checks"].append({
        "check": "file_readable",
        "status": "PASS"
    })
    
    # 3. Verificar tamanho
    size = os.path.getsize(filepath)
    
    if size == 0:
        validacao["checks"].append({
            "check": "file_not_empty",
            "status": "FAIL",
            "message": "Arquivo vazio"
        })
        validacao["status"] = "FAILED"
        return validacao
    
    if size > 100 * 1024 * 1024:  # 100 MB
        validacao["checks"].append({
            "check": "file_size",
            "status": "WARN",
            "message": f"Arquivo grande: {size / 1024 / 1024:.2f} MB"
        })
    
    validacao["checks"].append({
        "check": "file_not_empty",
        "status": "PASS",
        "size_bytes": size
    })
    
    # 4. Detectar encoding
    encoding = detectar_encoding(filepath)
    
    if encoding is None:
        validacao["checks"].append({
            "check": "encoding_valid",
            "status": "FAIL",
            "message": "Encoding não detectado"
        })
        validacao["status"] = "FAILED"
        return validacao
    
    validacao["checks"].append({
        "check": "encoding_valid",
        "status": "PASS",
        "encoding": encoding
    })
    
    # 5. Verificar se é arquivo texto
    if is_binary_file(filepath):
        validacao["checks"].append({
            "check": "is_text_file",
            "status": "FAIL",
            "message": "Arquivo binário não suportado"
        })
        validacao["status"] = "FAILED"
        return validacao
    
    validacao["checks"].append({
        "check": "is_text_file",
        "status": "PASS"
    })
    
    # 6. Detectar line endings
    line_endings = detectar_line_endings(filepath)
    
    if "MIXED" in line_endings:
        validacao["checks"].append({
            "check": "line_endings_consistent",
            "status": "WARN",
            "message": f"Line endings mistos: {line_endings}"
        })
    else:
        validacao["checks"].append({
            "check": "line_endings_consistent",
            "status": "PASS",
            "line_endings": line_endings
        })
    
    # Determinar status final
    failed = any(c["status"] == "FAIL" for c in validacao["checks"])
    if failed:
        validacao["status"] = "FAILED"
    else:
        validacao["status"] = "SUCCESS"
    
    return validacao
```

### Passo 2: Cálculo de Hash SHA-256

**Objetivo**: Garantir imutabilidade e rastreabilidade

**Algoritmo**:

```python
import hashlib

def calcular_hash_sha256(filepath):
    """
    Calcula hash SHA-256 do arquivo.
    
    Returns:
        str: Hash hexadecimal
    """
    sha256 = hashlib.sha256()
    
    with open(filepath, 'rb') as f:
        # Ler em chunks para arquivos grandes
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    
    return sha256.hexdigest()
```

**Exemplo**:
```python
hash_original = calcular_hash_sha256("_LEGADO/bi14a.esf")
# Output: "b6fe2994ed7416e7b0fd4c43c197a4566b4741d741214231de9fa0227b12d89b"
```

**Uso**:
- Registrar no manifest
- Verificar integridade em processamentos futuros
- Detectar modificações não autorizadas

### Passo 3: Taint Analysis (Análise de Sanidade)

**Objetivo**: Identificar problemas que podem "sujar" a extração

#### 3.1 Problemas de Encoding

```python
def analisar_encoding(filepath):
    """
    Analisa problemas de encoding.
    
    Returns:
        list: Problemas detectados
    """
    problemas = []
    
    # Tentar detectar encoding
    encoding = detectar_encoding(filepath)
    
    if encoding is None:
        problemas.append({
            "issue": "ENCODING_UNKNOWN",
            "severity": "HIGH",
            "message": "Encoding não detectado",
            "action": "Tentar múltiplos encodings"
        })
        return problemas
    
    # Verificar se é EBCDIC (mainframe)
    if encoding == "EBCDIC":
        problemas.append({
            "issue": "EBCDIC_DETECTED",
            "severity": "MEDIUM",
            "message": "Arquivo em EBCDIC (mainframe)",
            "action": "Converter para UTF-8"
        })
    
    # Tentar ler com encoding detectado
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            content = f.read()
            
        # Verificar BOM
        if content.startswith('\ufeff'):
            problemas.append({
                "issue": "BOM_PRESENT",
                "severity": "LOW",
                "message": "Byte Order Mark presente",
                "action": "Remover BOM na versão .lined"
            })
        
        # Verificar caracteres corrompidos
        if '�' in content:
            problemas.append({
                "issue": "CORRUPTED_CHARS",
                "severity": "HIGH",
                "message": "Caracteres corrompidos detectados",
                "action": "Investigar encoding original"
            })
        
    except UnicodeDecodeError as e:
        problemas.append({
            "issue": "INVALID_UTF8",
            "severity": "HIGH",
            "message": f"Erro de decode: {e}",
            "action": "Tentar converter de EBCDIC ou Latin-1"
        })
    
    return problemas
```

#### 3.2 Problemas de Caracteres

```python
def analisar_caracteres(filepath, encoding='utf-8'):
    """
    Analisa problemas de caracteres.
    
    Returns:
        list: Problemas detectados
    """
    problemas = []
    
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Verificar caracteres de controle inválidos
        control_chars = [c for c in content if ord(c) < 32 and c not in '\n\r\t']
        
        if control_chars:
            unique_controls = set(control_chars)
            problemas.append({
                "issue": "CONTROL_CHARS",
                "severity": "MEDIUM",
                "message": f"Caracteres de controle inválidos: {len(control_chars)}",
                "chars": [f"0x{ord(c):02x}" for c in unique_controls],
                "action": "Remover ou substituir"
            })
        
        # Verificar null bytes
        if '\x00' in content:
            problemas.append({
                "issue": "NULL_BYTES",
                "severity": "HIGH",
                "message": "Null bytes encontrados em arquivo texto",
                "action": "Remover null bytes"
            })
        
        # Verificar caracteres não-ASCII
        non_ascii = [c for c in content if ord(c) > 127]
        
        if non_ascii and encoding == 'ascii':
            problemas.append({
                "issue": "NON_ASCII",
                "severity": "LOW",
                "message": f"Caracteres não-ASCII: {len(non_ascii)}",
                "action": "Validar encoding correto"
            })
        
    except Exception as e:
        problemas.append({
            "issue": "READ_ERROR",
            "severity": "HIGH",
            "message": f"Erro ao ler arquivo: {e}",
            "action": "Verificar encoding e permissões"
        })
    
    return problemas
```

#### 3.3 Problemas de Line Endings

```python
def analisar_line_endings(filepath, encoding='utf-8'):
    """
    Analisa problemas de line endings.
    
    Returns:
        list: Problemas detectados
    """
    problemas = []
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Contar tipos de line endings
        crlf_count = content.count(b'\r\n')
        lf_count = content.count(b'\n') - crlf_count
        cr_count = content.count(b'\r') - crlf_count
        
        # Verificar se há mix
        endings_types = sum([crlf_count > 0, lf_count > 0, cr_count > 0])
        
        if endings_types > 1:
            problemas.append({
                "issue": "MIXED_LINE_ENDINGS",
                "severity": "MEDIUM",
                "message": f"Mix de line endings: CRLF={crlf_count}, LF={lf_count}, CR={cr_count}",
                "action": "Normalizar para LF"
            })
        
        # Verificar se termina com newline
        if not content.endswith(b'\n') and not content.endswith(b'\r\n'):
            problemas.append({
                "issue": "NO_FINAL_NEWLINE",
                "severity": "LOW",
                "message": "Arquivo não termina com newline",
                "action": "Adicionar newline final"
            })
        
    except Exception as e:
        problemas.append({
            "issue": "READ_ERROR",
            "severity": "HIGH",
            "message": f"Erro ao ler arquivo: {e}"
        })
    
    return problemas
```

### Passo 4: Geração de Arquivo .lined

**Objetivo**: Criar versão com números de linha fixos

**Algoritmo**:

```python
def gerar_arquivo_lined(input_file, output_file=None, encoding='utf-8'):
    """
    Gera versão .lined do arquivo.
    
    Args:
        input_file: Arquivo de entrada
        output_file: Arquivo de saída (default: input_file.lined)
        encoding: Encoding do arquivo
    
    Returns:
        dict: Resultado do processamento
    """
    if output_file is None:
        output_file = f"{input_file}.lined"
    
    resultado = {
        "input_file": input_file,
        "output_file": output_file,
        "status": "PENDING",
        "total_lines": 0,
        "encoding": encoding
    }
    
    try:
        # Ler arquivo original
        with open(input_file, 'r', encoding=encoding, errors='replace') as f:
            lines = f.readlines()
        
        # Gerar versão numerada
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            for i, line in enumerate(lines, start=1):
                # Remover newline original
                line = line.rstrip('\r\n')
                
                # Escrever com número de linha
                f.write(f"{i:06d}|{line}\n")
        
        resultado["total_lines"] = len(lines)
        resultado["status"] = "SUCCESS"
        
    except UnicodeDecodeError as e:
        resultado["status"] = "FAILED"
        resultado["error"] = f"Erro de encoding: {e}"
        
    except Exception as e:
        resultado["status"] = "FAILED"
        resultado["error"] = str(e)
    
    return resultado
```

**Exemplo de Output**:

**Input** (`bi14a.esf`):
```
* PROGRAMA: BI14A
* AUTOR: Sistema Legado
SCREEN TELA_CONSULTA
  FIELD COD_BANCO
```

**Output** (`bi14a.esf.lined`):
```
000001|* PROGRAMA: BI14A
000002|* AUTOR: Sistema Legado
000003|SCREEN TELA_CONSULTA
000004|  FIELD COD_BANCO
```

### Passo 5: Verificação do Arquivo .lined

**Objetivo**: Garantir que o arquivo .lined foi gerado corretamente

```python
def verificar_arquivo_lined(original_file, lined_file):
    """
    Verifica se arquivo .lined foi gerado corretamente.
    
    Returns:
        dict: Resultado da verificação
    """
    verificacao = {
        "original_file": original_file,
        "lined_file": lined_file,
        "status": "PENDING",
        "checks": []
    }
    
    # 1. Verificar se arquivo .lined existe
    if not os.path.exists(lined_file):
        verificacao["checks"].append({
            "check": "lined_file_exists",
            "status": "FAIL",
            "message": "Arquivo .lined não foi criado"
        })
        verificacao["status"] = "FAILED"
        return verificacao
    
    verificacao["checks"].append({
        "check": "lined_file_exists",
        "status": "PASS"
    })
    
    # 2. Contar linhas do original
    with open(original_file, 'r', encoding='utf-8', errors='replace') as f:
        original_lines = len(f.readlines())
    
    # 3. Contar linhas do .lined
    with open(lined_file, 'r', encoding='utf-8') as f:
        lined_lines = len(f.readlines())
    
    if original_lines != lined_lines:
        verificacao["checks"].append({
            "check": "line_count_match",
            "status": "FAIL",
            "message": f"Número de linhas diferente: {original_lines} vs {lined_lines}"
        })
        verificacao["status"] = "FAILED"
        return verificacao
    
    verificacao["checks"].append({
        "check": "line_count_match",
        "status": "PASS",
        "original_lines": original_lines,
        "lined_lines": lined_lines
    })
    
    # 4. Verificar formato de numeração
    with open(lined_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            # Verificar formato: NNNNNN|CONTEUDO
            if not re.match(r'^\d{6}\|', line):
                verificacao["checks"].append({
                    "check": "numbering_format",
                    "status": "FAIL",
                    "message": f"Formato inválido na linha {i}: {line[:20]}"
                })
                verificacao["status"] = "FAILED"
                return verificacao
            
            # Verificar se número está correto
            line_num = int(line[:6])
            if line_num != i:
                verificacao["checks"].append({
                    "check": "numbering_sequence",
                    "status": "FAIL",
                    "message": f"Sequência incorreta: esperado {i}, encontrado {line_num}"
                })
                verificacao["status"] = "FAILED"
                return verificacao
    
    verificacao["checks"].append({
        "check": "numbering_format",
        "status": "PASS"
    })
    
    verificacao["status"] = "SUCCESS"
    return verificacao
```

### Passo 6: Atualização do Manifest

**Objetivo**: Registrar arquivo processado no manifest

```python
def atualizar_manifest(file_info):
    """
    Atualiza ingestion_manifest.json.
    
    Args:
        file_info: Informações do arquivo processado
    """
    manifest_path = "run/ingestion/ingestion_manifest.json"
    
    # Criar pasta se não existir
    os.makedirs("run/ingestion", exist_ok=True)
    
    # Carregar manifest existente ou criar novo
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "files": [],
            "summary": {
                "success_count": 0,
                "tainted_count": 0,
                "failed_count": 0,
                "total_lines": 0,
                "total_bytes": 0
            }
        }
    
    # Adicionar ou atualizar entrada
    existing = next((f for f in manifest["files"] if f["original_file"] == file_info["original_file"]), None)
    
    if existing:
        manifest["files"].remove(existing)
    
    manifest["files"].append(file_info)
    
    # Atualizar summary
    manifest["total_files"] = len(manifest["files"])
    manifest["summary"]["success_count"] = sum(1 for f in manifest["files"] if f["status"] == "SUCCESS")
    manifest["summary"]["tainted_count"] = sum(1 for f in manifest["files"] if f["status"] == "TAINTED")
    manifest["summary"]["failed_count"] = sum(1 for f in manifest["files"] if f["status"] == "FAILED")
    manifest["summary"]["total_lines"] = sum(f.get("total_lines", 0) for f in manifest["files"])
    manifest["summary"]["total_bytes"] = sum(f.get("size_bytes", 0) for f in manifest["files"])
    
    # Salvar manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
```

## Output de Ingestão

### 1. ingestion_manifest.json

**Localização**: `run/ingestion/ingestion_manifest.json`

**Estrutura**:

```json
{
  "version": "1.0",
  "timestamp": "2025-12-27T10:30:00Z",
  "total_files": 3,
  "vamap_enabled": true,
  "files": [
    {
      "original_file": "_LEGADO/bi14a.esf",
      "lined_file": "_LEGADO/bi14a.esf.lined",
      "vamap_log": "run/ingestion/vamap_raw.log",
      "vamap_status": "SUCCESS",
      "vamap_symbols": {
        "screens": 5,
        "fields": 47,
        "queries": 23,
        "procedures": 18
      },
      "sha256_original": "b6fe2994ed7416e7b0fd4c43c197a4566b4741d741214231de9fa0227b12d89b",
      "sha256_lined": "a7c3e5f8d9b2...",
      "size_bytes": 248106,
      "total_lines": 6842,
      "encoding": "UTF-8",
      "status": "SUCCESS",
      "timestamp": "2025-12-27T10:30:00Z",
      "taint_issues": [],
      "processing_duration_seconds": 2.5
    },
    {
      "original_file": "_LEGADO/cb2qa.esf",
      "lined_file": "_LEGADO/cb2qa.esf.lined",
      "sha256_original": "c8d4f6a9e1b3...",
      "sha256_lined": "b9e5g7c1f3d5...",
      "size_bytes": 156789,
      "total_lines": 4321,
      "encoding": "UTF-8",
      "status": "TAINTED",
      "timestamp": "2025-12-27T10:31:00Z",
      "taint_issues": [
        {
          "issue": "MIXED_LINE_ENDINGS",
          "severity": "MEDIUM",
          "message": "Mix de CRLF e LF",
          "action": "Normalizado para LF"
        }
      ],
      "processing_duration_seconds": 1.8
    }
  ],
  "summary": {
    "success_count": 1,
    "tainted_count": 1,
    "failed_count": 0,
    "total_lines": 11163,
    "total_bytes": 404895
  }
}
```

### 2. taint_report_preliminar.md

**Localização**: `run/ingestion/taint_report_preliminar.md`

**Estrutura**:

```markdown
# Taint Report Preliminar - Ingestão Forense

## Sumário de Ingestão

**Data/Hora**: 2025-12-27T10:30:00Z
**Total de Arquivos**: 3
**Arquivos Processados**: 3

### Estatísticas Gerais
- **SUCCESS**: 1 arquivo (33%)
- **TAINTED**: 1 arquivo (33%)
- **FAILED**: 1 arquivo (33%)
- **Total de Linhas**: 11,163
- **Total de Bytes**: 404,895

---

## Arquivos Processados com Sucesso

### 1. bi14a.esf ✅
- **Status**: SUCCESS
- **Linhas**: 6,842
- **Tamanho**: 248 KB
- **Encoding**: UTF-8
- **Hash**: b6fe2994ed7416e7...
- **Arquivo .lined**: _LEGADO/bi14a.esf.lined
- **Duração**: 2.5s

---

## Arquivos com Problemas (Tainted)

### 1. cb2qa.esf ⚠️
- **Status**: TAINTED
- **Linhas**: 4,321
- **Tamanho**: 157 KB
- **Encoding**: UTF-8
- **Hash**: c8d4f6a9e1b3...

**Problemas Detectados**:
1. **MIXED_LINE_ENDINGS** (MEDIUM)
   - Descrição: Mix de CRLF e LF
   - Ação Tomada: Normalizado para LF na versão .lined

---

## Arquivos com Falha

### 1. corrupted.esf ❌
- **Status**: FAILED
- **Erro**: Encoding não detectado

**Problemas Detectados**:
1. **ENCODING_UNKNOWN** (HIGH)
   - Descrição: Encoding não pôde ser detectado
   - Ação Requerida: Verificar arquivo manualmente

---

## Detalhes de Problemas

### Problemas de Encoding (1 arquivo)
- ENCODING_UNKNOWN: 1 arquivo

### Problemas de Caracteres (0 arquivos)

### Problemas de Line Endings (1 arquivo)
- MIXED_LINE_ENDINGS: 1 arquivo

---

## Recomendações de Correção

### Prioridade 1 (HIGH)
1. **corrupted.esf**: Investigar encoding original e corrigir

### Prioridade 2 (MEDIUM)
1. **cb2qa.esf**: Verificar se normalização de line endings está correta

---

## Status de Prontidão para Extração

### Prontos para Extração (2 arquivos)
✅ bi14a.esf → Pode ser extraído com [EXT]
⚠️ cb2qa.esf → Pode ser extraído com [EXT] (com warnings)

### Bloqueados (1 arquivo)
❌ corrupted.esf → Requer correção manual antes de extração

---

**Gerado por**: Ingestor-A v1.0.0
**Agente de Origem**: Preparação para Extractor-A
```

## Handover para Extractor-A

### Critérios de Prontidão

```python
def verificar_prontidao(arquivo):
    """
    Verifica se arquivo está pronto para extração.
    
    Returns:
        dict: Status de prontidão
    """
    manifest = carregar_manifest()
    
    file_info = next((f for f in manifest["files"] if arquivo in f["original_file"]), None)
    
    if not file_info:
        return {
            "ready": False,
            "message": "Arquivo não encontrado no manifest"
        }
    
    # Verificar critérios
    criterios = [
        {
            "criterion": "Arquivo .lined gerado",
            "check": os.path.exists(file_info["lined_file"]),
            "required": True
        },
        {
            "criterion": "Hash SHA-256 calculado",
            "check": "sha256_original" in file_info,
            "required": True
        },
        {
            "criterion": "Status não é FAILED",
            "check": file_info["status"] != "FAILED",
            "required": True
        }
    ]
    
    all_pass = all(c["check"] for c in criterios if c["required"])
    
    if all_pass:
        return {
            "ready": True,
            "status": file_info["status"],
            "lined_file": file_info["lined_file"],
            "hash": file_info["sha256_original"],
            "lines": file_info["total_lines"],
            "message": f"""
✅ ARQUIVO PRONTO PARA EXTRAÇÃO

Arquivo: {file_info["lined_file"]}
Hash: {file_info["sha256_original"]}
Linhas: {file_info["total_lines"]}
Status: {file_info["status"]}

PRÓXIMO COMANDO:
[EXT] Extrair {os.path.basename(file_info["original_file"])}
"""
        }
    else:
        falhas = [c for c in criterios if c["required"] and not c["check"]]
        return {
            "ready": False,
            "message": f"Critérios não atendidos: {', '.join(f['criterion'] for f in falhas)}"
        }
```

## Comandos Disponíveis

### [ING] Ingerir Arquivo

**Descrição**: Ingere um arquivo legado e prepara para extração

**Uso**:
```bash
[ING] Ingerir bi14a.esf
```

**Processo**:
1. Validar arquivo original
2. Calcular hash SHA-256
3. Analisar sanidade (taint analysis)
4. Gerar arquivo .lined
5. Verificar arquivo .lined
6. Atualizar manifest
7. Gerar taint report

**Output**:
- `_LEGADO/bi14a.esf.lined`
- `run/ingestion/ingestion_manifest.json` (atualizado)
- `run/ingestion/taint_report_preliminar.md` (atualizado)
- `run/ingestion/ingestion_log.txt`

### [BATCH] Ingerir Lote

**Descrição**: Ingere todos os arquivos .esf da pasta _LEGADO

**Uso**:
```bash
[BATCH] Ingerir lote
```

**Processo**: Executa [ING] para cada arquivo .esf encontrado

### [VERIFY] Verificar Integridade

**Descrição**: Verifica integridade de arquivos já ingeridos

**Uso**:
```bash
[VERIFY] Verificar integridade
```

**Verifica**:
- Arquivos .lined existem
- Hashes correspondem
- Números de linha corretos

### [STATUS] Status de Ingestão

**Descrição**: Exibe status de ingestão e prontidão

**Uso**:
```bash
[STATUS] Status de ingestão
```

**Output**:
```
📥 STATUS DE INGESTÃO

Total de arquivos: 3
✅ SUCCESS: 1
⚠️ TAINTED: 1
❌ FAILED: 1

Prontos para extração: 2
Bloqueados: 1
```

## Troubleshooting

### Problema: Encoding não detectado
**Solução**: Tentar múltiplos encodings (UTF-8, EBCDIC, Latin-1, ASCII)

### Problema: Arquivo binário
**Solução**: Verificar se arquivo é realmente texto, não processar binários

### Problema: Arquivo muito grande
**Solução**: Processar em chunks ou aumentar limite de tamanho

### Problema: Permissão negada
**Solução**: Verificar permissões de leitura/escrita nas pastas

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Fase**: 1 - As-Is Forense  
**Papel**: Agente de Origem


