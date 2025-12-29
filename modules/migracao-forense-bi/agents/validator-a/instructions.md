# Instruções Detalhadas - Validator-A

## Missão Principal

Auditar o output do **Extractor-A** para garantir conformidade com a estratégia de rastreabilidade forense, calculando o **GroundingScore** e atuando como **Porteiro do Gate G1**.

**IMPORTANTE**: Você NÃO lê código-fonte diretamente. Você analisa APENAS os artefatos gerados.

## Papel no Fluxo

```
Extractor-A → [claims_A.json] → Validator-A → [Gate G1] → Analyzer-A
                                      ↓
                              PASS ou FAIL
```

Você é o **Porteiro do Gate G1**:
- ✅ **PASS**: Analyzer-A pode executar
- ❌ **FAIL**: Analyzer-A está BLOQUEADO até correção

## Bloqueio de Entrada (CRÍTICO)

### Arquivos Obrigatórios

Antes de iniciar QUALQUER validação, verificar existência de:

1. **run/extraction/claims_A.json**
   - Artefato principal de extração
   - Contém todos os claims extraídos
   - Formato: JSON estruturado

2. **run/extraction/extraction_log.txt**
   - Log detalhado da extração
   - Contém informações de processo
   - Formato: Texto plano

3. **run/ingestion/vamap_raw.log** (ÂNCORA DA VERDADE)
   - Log do compilador oficial Visual Age
   - Lista autoritativa de símbolos
   - Usado para validação cruzada IA vs Compilador
   - **CRÍTICO**: Gabarito para detectar alucinações
   - **SQL**: Contém seção DATA DIVISION e SQLCA com tabelas/colunas acessadas

### Comportamento de Bloqueio

```python
if not exists("run/extraction/claims_A.json"):
    ABORTAR validação
    RETORNAR erro: "BLOQUEIO: claims_A.json não encontrado"
    NÃO gerar validation_report.md
    NÃO gerar gate_status.json
    EXIT

if not exists("run/extraction/extraction_log.txt"):
    ABORTAR validação
    RETORNAR erro: "BLOQUEIO: extraction_log.txt não encontrado"
    NÃO gerar validation_report.md
    NÃO gerar gate_status.json
    EXIT

if not exists("run/ingestion/vamap_raw.log"):
    ABORTAR validação
    RETORNAR erro: "BLOQUEIO: vamap_raw.log não encontrado (Âncora da Verdade)"
    NÃO gerar validation_report.md
    NÃO gerar gate_status.json
    EXIT
```

**Mensagem de Erro Padrão**:
```
❌ BLOQUEIO DE VALIDAÇÃO

Arquivos obrigatórios não encontrados:
- run/extraction/claims_A.json: [AUSENTE/PRESENTE]
- run/extraction/extraction_log.txt: [AUSENTE/PRESENTE]

AÇÃO REQUERIDA:
Execute [EXT] Extrair arquivo antes de validar.

STATUS: VALIDAÇÃO ABORTADA
```

## Cálculo do GroundingScore

### Definição

**GroundingScore** mede a porcentagem de claims que possuem evidência rastreável válida.

### Fórmula

```
GroundingScore = (Elementos com Evidence Válido / Total de Elementos) × 100
```

### Elementos Contados

```json
{
  "screens": [...],      // Contar cada screen
  "fields": [...],       // Contar cada field
  "queries": [...],      // Contar cada query
  "business_logic": [...] // Contar cada logic
}
```

**Total de Elementos** = len(screens) + len(fields) + len(queries) + len(business_logic)

### Validação de Evidence Pointer

Para cada elemento, verificar:

#### 1. Presença do Campo
```python
if "evidence_pointer" not in elemento:
    elemento_invalido = True
```

#### 2. Formato Correto
```regex
^[a-z0-9_-]+\.esf:L\d{4}-L\d{4}$
```

Exemplos válidos:
- ✅ `bi14a.esf:L0123-L0145`
- ✅ `cb2qa.esf:L0001-L0001`
- ✅ `relatorio.esf:L1500-L1750`

Exemplos inválidos:
- ❌ `bi14a:L0123-L0145` (falta .esf)
- ❌ `bi14a.esf:123-145` (falta L)
- ❌ `bi14a.esf:L123-L145` (falta zeros à esquerda)
- ❌ `bi14a.esf:L0123` (falta linha final)

#### 3. Linhas Existentes
```python
metadata = claims["metadata"]
total_lines = metadata["total_lines"]

# Extrair linhas do evidence_pointer
match = re.match(r'.*:L(\d{4})-L(\d{4})$', evidence_pointer)
linha_inicio = int(match.group(1))
linha_fim = int(match.group(2))

if linha_inicio > total_lines or linha_fim > total_lines:
    elemento_invalido = True

if linha_inicio > linha_fim:
    elemento_invalido = True
```

### Algoritmo Completo

```python
def calcular_grounding_score(claims_json):
    """
    Calcula o GroundingScore validando evidence_pointers.
    
    Returns:
        dict: {
            "score": float (0.0 a 100.0),
            "total_elementos": int,
            "elementos_validos": int,
            "elementos_invalidos": int,
            "detalhes_invalidos": list
        }
    """
    total_elementos = 0
    elementos_validos = 0
    elementos_invalidos = []
    
    # Carregar metadata
    metadata = claims_json["metadata"]
    total_lines = metadata["total_lines"]
    source_file = metadata["source_file"]
    
    # Regex para validação
    pattern = re.compile(r'^[a-z0-9_-]+\.esf:L\d{4}-L\d{4}$')
    
    # Validar screens
    for screen in claims_json.get("screens", []):
        total_elementos += 1
        if validar_evidence(screen, pattern, total_lines, source_file):
            elementos_validos += 1
        else:
            elementos_invalidos.append({
                "tipo": "screen",
                "id": screen.get("screen_id", "UNKNOWN"),
                "evidence": screen.get("evidence_pointer", "MISSING"),
                "erro": identificar_erro(screen, pattern, total_lines)
            })
    
    # Validar fields
    for field in claims_json.get("fields", []):
        total_elementos += 1
        if validar_evidence(field, pattern, total_lines, source_file):
            elementos_validos += 1
        else:
            elementos_invalidos.append({
                "tipo": "field",
                "id": field.get("field_id", "UNKNOWN"),
                "evidence": field.get("evidence_pointer", "MISSING"),
                "erro": identificar_erro(field, pattern, total_lines)
            })
    
    # Validar queries
    for query in claims_json.get("queries", []):
        total_elementos += 1
        if validar_evidence(query, pattern, total_lines, source_file):
            elementos_validos += 1
        else:
            elementos_invalidos.append({
                "tipo": "query",
                "id": query.get("query_id", "UNKNOWN"),
                "evidence": query.get("evidence_pointer", "MISSING"),
                "erro": identificar_erro(query, pattern, total_lines)
            })
    
    # Validar business_logic
    for logic in claims_json.get("business_logic", []):
        total_elementos += 1
        if validar_evidence(logic, pattern, total_lines, source_file):
            elementos_validos += 1
        else:
            elementos_invalidos.append({
                "tipo": "business_logic",
                "id": logic.get("logic_id", "UNKNOWN"),
                "evidence": logic.get("evidence_pointer", "MISSING"),
                "erro": identificar_erro(logic, pattern, total_lines)
            })
    
    # Calcular score
    if total_elementos == 0:
        score = 0.0
    else:
        score = (elementos_validos / total_elementos) * 100.0
    
    return {
        "score": round(score, 2),
        "total_elementos": total_elementos,
        "elementos_validos": elementos_validos,
        "elementos_invalidos": len(elementos_invalidos),
        "detalhes_invalidos": elementos_invalidos
    }

def validar_evidence(elemento, pattern, total_lines, source_file):
    """Valida um evidence_pointer individual."""
    # Verificar presença
    if "evidence_pointer" not in elemento:
        return False
    
    evidence = elemento["evidence_pointer"]
    
    # Verificar formato
    if not pattern.match(evidence):
        return False
    
    # Verificar arquivo correto
    if not evidence.startswith(source_file):
        return False
    
    # Extrair e validar linhas
    match = re.search(r'L(\d{4})-L(\d{4})$', evidence)
    if not match:
        return False
    
    linha_inicio = int(match.group(1))
    linha_fim = int(match.group(2))
    
    if linha_inicio < 1 or linha_fim < 1:
        return False
    
    if linha_inicio > linha_fim:
        return False
    
    if linha_inicio > total_lines or linha_fim > total_lines:
        return False
    
    return True

def identificar_erro(elemento, pattern, total_lines):
    """Identifica o tipo específico de erro."""
    if "evidence_pointer" not in elemento:
        return "MISSING: Campo evidence_pointer ausente"
    
    evidence = elemento["evidence_pointer"]
    
    if not pattern.match(evidence):
        return f"FORMAT: Formato inválido '{evidence}'"
    
    match = re.search(r'L(\d{4})-L(\d{4})$', evidence)
    if match:
        linha_inicio = int(match.group(1))
        linha_fim = int(match.group(2))
        
        if linha_inicio > linha_fim:
            return f"RANGE: Linha início ({linha_inicio}) > fim ({linha_fim})"
        
        if linha_inicio > total_lines or linha_fim > total_lines:
            return f"BOUNDS: Linhas ({linha_inicio}-{linha_fim}) excedem total ({total_lines})"
    
    return "UNKNOWN: Erro não identificado"
```

### Critério de PASS/FAIL

```python
if grounding_score == 100.0:
    # Continuar validações CRITICAL
    pass
else:
    # FAIL imediato
    gate_status = "FAIL"
    motivo = f"GroundingScore {grounding_score}% < 100%"
```

## Confronto de Regras

### Fonte de Regras

Arquivo: **knowledge/extraction-rules.csv**

### Regras CRITICAL (11 regras)

Qualquer falha CRITICAL = **FAIL imediato**

| Rule ID | Nome | Validação |
|---------|------|-----------|
| RULE-001 | Evidence Pointer Obrigatório | 100% elementos com evidence_pointer |
| RULE-002 | Formato Evidence Pointer | Regex válido |
| RULE-003 | Linhas Existentes | Linhas <= total_lines |
| RULE-004 | Screen ID Válido | Fields referenciam screens existentes |
| RULE-005 | Dependências Válidas | Dependencies existem |
| RULE-006 | Campo Obrigatório Preenchido | Campos != null e != '' |
| RULE-012 | JSON Válido | JSON.parse() sem erro |
| RULE-013 | Metadata Completo | Todos campos presentes |
| RULE-016 | Evidence Validity 100% | valid = total |
| RULE-021 | IDs Únicos | Nenhum ID duplicado |
| **RULE-VAMAP** | **Conformidade VAMAP (Âncora da Verdade)** | **100% símbolos IA ⊆ VAMAP E sem alucinações** |

### Regras HIGH (8 regras)

Máximo 5% de falhas permitido

| Rule ID | Nome | Threshold |
|---------|------|-----------|
| RULE-007 | SQL Statement Completo | 95% |
| RULE-015 | Coverage Mínimo | >= 95% |
| RULE-017 | Telas Completas | 100% |
| RULE-018 | Campos Completos | 100% |
| RULE-019 | Queries Completas | 100% |
| RULE-024 | Tables Referenced | 95% |
| RULE-026 | Line Range Consistente | 100% |
| RULE-028 | Summary Correto | 100% |

### RULE-VAMAP: Conformidade com Âncora da Verdade

**CRÍTICO**: Esta é a regra mais importante - valida se a IA está alinhada com o compilador oficial.

#### Objetivo

Confrontar os símbolos extraídos pela IA (`claims_A.json`) com os símbolos detectados pelo compilador oficial Visual Age (`vamap_raw.log`).

#### Critérios de FAIL

1. **Símbolos Faltantes**: VAMAP listou um símbolo que a IA não extraiu
2. **Alucinações**: IA extraiu um símbolo que VAMAP não reconhece
3. **Categorias Erradas**: IA categorizou um símbolo diferente do VAMAP

#### Algoritmo

```python
def validar_conformidade_vamap(claims_json, vamap_log_path):
    """
    Valida conformidade entre IA e VAMAP.
    
    Returns:
        dict: {
            "pass": bool,
            "simbolos_faltantes": list,  # VAMAP tem, IA não
            "alucinacoes": list,         # IA tem, VAMAP não
            "categorias_erradas": list,  # Categoria diferente
            "matches": list,             # Símbolos corretos
            "conformidade_score": float  # 0-100%
        }
    """
    # 1. Carregar símbolos do VAMAP
    vamap_symbols = extrair_simbolos_vamap(vamap_log_path)
    
    # 2. Carregar símbolos da IA
    ia_symbols = extrair_simbolos_ia(claims_json)
    
    # 3. Comparar
    simbolos_faltantes = []
    alucinacoes = []
    categorias_erradas = []
    matches = []
    
    # 3.1. Verificar se IA extraiu tudo que VAMAP detectou
    for categoria in ["screens", "fields", "queries", "procedures"]:
        vamap_set = set([s["name"] for s in vamap_symbols.get(categoria, [])])
        ia_set = set([s["id"] for s in ia_symbols.get(categoria, [])])
        
        # Símbolos que VAMAP tem mas IA não extraiu
        faltantes = vamap_set - ia_set
        for simbolo in faltantes:
            simbolos_faltantes.append({
                "categoria": categoria,
                "simbolo": simbolo,
                "fonte": "VAMAP",
                "motivo": "IA não extraiu este símbolo"
            })
        
        # Símbolos que IA extraiu mas VAMAP não reconhece (ALUCINAÇÃO)
        alucinados = ia_set - vamap_set
        for simbolo in alucinados:
            alucinacoes.append({
                "categoria": categoria,
                "simbolo": simbolo,
                "fonte": "IA",
                "motivo": "VAMAP não reconhece este símbolo (possível alucinação)"
            })
        
        # Símbolos corretos
        corretos = vamap_set & ia_set
        matches.extend(list(corretos))
    
    # 4. Calcular score de conformidade
    total_vamap = sum(len(vamap_symbols.get(c, [])) for c in ["screens", "fields", "queries", "procedures"])
    total_matches = len(matches)
    
    if total_vamap == 0:
        conformidade_score = 0.0
    else:
        conformidade_score = (total_matches / total_vamap) * 100.0
    
    # 5. Determinar PASS/FAIL
    # PASS apenas se: 100% conformidade E zero alucinações
    passou = (
        len(simbolos_faltantes) == 0 and
        len(alucinacoes) == 0 and
        conformidade_score == 100.0
    )
    
    return {
        "pass": passou,
        "simbolos_faltantes": simbolos_faltantes,
        "alucinacoes": alucinacoes,
        "categorias_erradas": categorias_erradas,
        "matches": matches,
        "conformidade_score": round(conformidade_score, 2),
        "total_vamap": total_vamap,
        "total_ia": sum(len(ia_symbols.get(c, [])) for c in ["screens", "fields", "queries", "procedures"]),
        "total_matches": total_matches
    }

def extrair_simbolos_vamap(vamap_log_path):
    """Extrai símbolos do log do VAMAP."""
    symbols = {
        "screens": [],
        "fields": [],
        "queries": [],
        "procedures": []
    }
    
    with open(vamap_log_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_section = None
    
    for line in content.split('\n'):
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

def extrair_simbolos_ia(claims_json):
    """Extrai símbolos do claims_A.json."""
    symbols = {
        "screens": [],
        "fields": [],
        "queries": [],
        "procedures": []
    }
    
    # Screens
    for screen in claims_json.get("screens", []):
        symbols["screens"].append({
            "id": screen.get("screen_id"),
            "name": screen.get("screen_name")
        })
    
    # Fields
    for field in claims_json.get("fields", []):
        symbols["fields"].append({
            "id": field.get("field_id"),
            "name": field.get("field_name")
        })
    
    # Queries
    for query in claims_json.get("queries", []):
        symbols["queries"].append({
            "id": query.get("query_id"),
            "name": query.get("query_name")
        })
    
    # Business Logic (mapeia para procedures)
    for logic in claims_json.get("business_logic", []):
        symbols["procedures"].append({
            "id": logic.get("logic_id"),
            "name": logic.get("logic_name")
        })
    
    return symbols
```

#### Mensagem de FAIL

Se RULE-VAMAP falhar:

```
❌ RULE-VAMAP FAILED: Conformidade com VAMAP

Símbolos Faltantes (VAMAP detectou, IA não extraiu):
- SCREEN: TELA_RESULTADO (Line 30-45)
- FIELD: STATUS_BANCO (Line 21-25)

Alucinações (IA extraiu, VAMAP não reconhece):
- QUERY: SELECT_INEXISTENTE

Conformidade Score: 85.7% (esperado: 100%)

🚨 AÇÃO REQUERIDA: Revisar extração ou verificar vamap_raw.log
```

### Algoritmo de Validação

```python
def validar_regras(claims_json, extraction_rules_csv, vamap_log_path):
    """
    Valida claims contra extraction-rules.csv E vamap.
    
    Returns:
        dict: {
            "critical_failures": list,
            "high_failures": list,
            "medium_failures": list,
            "vamap_validation": dict,
            "total_validations": int
        }
    """
    critical_failures = []
    high_failures = []
    medium_failures = []
    
    # PRIMEIRO: Validar RULE-VAMAP (mais crítica)
    vamap_validation = validar_conformidade_vamap(claims_json, vamap_log_path)
    
    if not vamap_validation["pass"]:
        critical_failures.append({
            "rule_id": "RULE-VAMAP",
            "rule_name": "Conformidade VAMAP (Âncora da Verdade)",
            "detalhes": {
                "simbolos_faltantes": len(vamap_validation["simbolos_faltantes"]),
                "alucinacoes": len(vamap_validation["alucinacoes"]),
                "conformidade_score": vamap_validation["conformidade_score"],
                "lista_faltantes": vamap_validation["simbolos_faltantes"],
                "lista_alucinacoes": vamap_validation["alucinacoes"]
            }
        })
    
    # DEPOIS: Validar regras do CSV
    rules = load_csv(extraction_rules_csv)
    
    for rule in rules:
        if rule["severity"] == "CRITICAL":
            resultado = aplicar_regra(rule, claims_json)
            if not resultado["pass"]:
                critical_failures.append({
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["rule_name"],
                    "detalhes": resultado["detalhes"]
                })
        
        elif rule["severity"] == "HIGH":
            resultado = aplicar_regra(rule, claims_json)
            if not resultado["pass"]:
                high_failures.append({
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["rule_name"],
                    "detalhes": resultado["detalhes"]
                })
        
        elif rule["severity"] == "MEDIUM":
            resultado = aplicar_regra(rule, claims_json)
            if not resultado["pass"]:
                medium_failures.append({
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["rule_name"],
                    "detalhes": resultado["detalhes"]
                })
    
    return {
        "critical_failures": critical_failures,
        "high_failures": high_failures,
        "medium_failures": medium_failures,
        "vamap_validation": vamap_validation,
        "total_validations": len(rules) + 1  # +1 para RULE-VAMAP
    }
```

## Output de Auditoria

### 1. validation_report.md (Relatório Humano)

Estrutura obrigatória:

```markdown
# Relatório de Validação Forense - Gate G1

## Sumário Executivo

**Status do Gate G1**: PASS/FAIL
**GroundingScore**: XX.XX%
**Data/Hora**: YYYY-MM-DDTHH:mm:ssZ
**Arquivo Validado**: claims_A.json

---

## GroundingScore Detalhado

### Cálculo
- **Total de Elementos**: XXX
- **Elementos Válidos**: XXX
- **Elementos Inválidos**: XXX
- **Score Final**: XX.XX%

### Breakdown por Tipo
| Tipo | Total | Válidos | Inválidos | Score |
|------|-------|---------|-----------|-------|
| Screens | XX | XX | XX | XX% |
| Fields | XX | XX | XX | XX% |
| Queries | XX | XX | XX | XX% |
| Business Logic | XX | XX | XX | XX% |

### Elementos Inválidos (se houver)
[Lista detalhada de cada elemento inválido com ID e motivo]

---

## Validações CRITICAL

**Total de Regras CRITICAL**: 10
**Falhas Encontradas**: X

[Se falhas > 0, listar cada falha com detalhes]

---

## Validações HIGH

**Total de Regras HIGH**: 8
**Falhas Encontradas**: X
**Taxa de Falha**: X%
**Threshold Permitido**: 5%

[Se falhas > 5%, listar falhas]

---

## Métricas de Qualidade

| Métrica | Valor | Status |
|---------|-------|--------|
| Coverage | XX% | PASS/FAIL |
| Evidence Validity | 100% | PASS/FAIL |
| Referências Válidas | 100% | PASS/FAIL |
| IDs Únicos | 100% | PASS/FAIL |

---

## Recomendações de Correção

[Se FAIL, listar ações específicas para correção]

1. [Ação 1]
2. [Ação 2]
...

---

## Status do Gate G1

**Decisão Final**: PASS/FAIL

**Próximo Agente**: Analyzer-A
**Status**: PERMITIDO/BLOQUEADO

**Timestamp**: YYYY-MM-DDTHH:mm:ssZ

---

## Próximos Passos

[Se PASS]
✅ Gate G1 aprovado
✅ Analyzer-A pode executar
→ Execute: [ANA] Analisar estrutura

[Se FAIL]
❌ Gate G1 reprovado
❌ Analyzer-A bloqueado
→ Corrija os erros e execute: [EXT] Extrair novamente
```

### 2. gate_status.json (Semáforo Binário)

Formato obrigatório:

```json
{
  "status": "PASS",
  "grounding_score": 100.0,
  "timestamp": "2025-12-27T10:30:00Z",
  "critical_failures": 0,
  "high_failures": 0,
  "medium_failures": 2,
  "next_agent_allowed": true,
  "next_agent": "Analyzer-A",
  "validation_duration_seconds": 3.5,
  "metadata": {
    "validator_version": "1.0.0",
    "claims_file": "run/extraction/claims_A.json",
    "claims_hash": "b6fe2994ed7416e7...",
    "total_elements_validated": 93
  }
}
```

Ou em caso de FAIL:

```json
{
  "status": "FAIL",
  "grounding_score": 95.7,
  "timestamp": "2025-12-27T10:30:00Z",
  "critical_failures": 4,
  "high_failures": 8,
  "medium_failures": 12,
  "next_agent_allowed": false,
  "next_agent": "Analyzer-A",
  "blocking_reason": "GroundingScore < 100% e 4 falhas CRITICAL",
  "validation_duration_seconds": 3.5,
  "metadata": {
    "validator_version": "1.0.0",
    "claims_file": "run/extraction/claims_A.json",
    "claims_hash": "b6fe2994ed7416e7...",
    "total_elements_validated": 93
  }
}
```

### 3. validation_details.json (Detalhes Técnicos)

Formato opcional para debug:

```json
{
  "grounding_score_details": {
    "score": 100.0,
    "total_elementos": 93,
    "elementos_validos": 93,
    "elementos_invalidos": 0,
    "breakdown": {
      "screens": {"total": 5, "validos": 5, "invalidos": 0},
      "fields": {"total": 47, "validos": 47, "invalidos": 0},
      "queries": {"total": 23, "validos": 23, "invalidos": 0},
      "business_logic": {"total": 18, "validos": 18, "invalidos": 0}
    },
    "elementos_invalidos_detalhes": []
  },
  "critical_validations": [
    {
      "rule_id": "RULE-001",
      "rule_name": "Evidence Pointer Obrigatório",
      "status": "PASS",
      "detalhes": "100% elementos com evidence_pointer"
    }
  ],
  "high_validations": [...],
  "medium_validations": [...]
}
```

## Lógica do Gate G1

### Condições de PASS

TODAS as condições devem ser verdadeiras:

```python
pass_conditions = [
    grounding_score == 100.0,
    critical_failures == 0,
    (high_failures / total_high_rules) <= 0.05,  # Máximo 5%
    json_valido == True,
    arquivos_obrigatorios_presentes == True
]

if all(pass_conditions):
    gate_status = "PASS"
    next_agent_allowed = True
```

### Condições de FAIL

QUALQUER condição verdadeira = FAIL:

```python
fail_conditions = [
    grounding_score < 100.0,
    critical_failures > 0,
    (high_failures / total_high_rules) > 0.05,
    json_valido == False,
    arquivos_obrigatorios_presentes == False
]

if any(fail_conditions):
    gate_status = "FAIL"
    next_agent_allowed = False
```

### Handover para Analyzer-A

```python
if gate_status == "PASS":
    print("✅ Gate G1 PASS")
    print("✅ Analyzer-A PERMITIDO")
    print("→ Execute: [ANA] Analisar estrutura")
else:
    print("❌ Gate G1 FAIL")
    print("❌ Analyzer-A BLOQUEADO")
    print("→ Corrija erros e execute: [EXT] Extrair novamente")
```

## Comandos Disponíveis

### [VAL] Validar Extração

**Descrição**: Valida extração forense e calcula GroundingScore

**Pré-requisitos**:
- ✅ run/extraction/claims_A.json existe
- ✅ run/extraction/extraction_log.txt existe

**Processo**:
1. Verificar arquivos obrigatórios
2. Carregar claims_A.json
3. Calcular GroundingScore
4. Validar regras CRITICAL
5. Validar regras HIGH
6. Gerar validation_report.md
7. Gerar gate_status.json
8. Retornar status PASS/FAIL

**Output**:
- run/extraction/validation_report.md
- run/extraction/gate_status.json
- run/extraction/validation_details.json (opcional)

### [RPT] Resumo de Qualidade

**Descrição**: Gera resumo executivo de qualidade

**Pré-requisitos**:
- ✅ run/extraction/gate_status.json existe

**Output**:
- Sumário executivo em console
- Métricas principais
- Status do Gate G1

### [GATE] Status Gate

**Descrição**: Verifica status atual do Gate G1

**Output**:
- Status: PASS/FAIL
- GroundingScore
- Próximo agente permitido: SIM/NÃO

### [VAL-SQL] Validação Especializada SQL (FASE 1 - SOBERANIA SQL)
Validação 100% focada em cruzamento SQL: IA vs VAMAP

**Missão Especializada:**
- ✅ **RULE-VAMAP-SQL**: Confrontar tabelas/colunas extraídas pela IA com DATA DIVISION ou SQLCA do vamap_raw.log
- ✅ **DETECTAR OMISSÕES**: VAMAP detectou tabela que IA não mapeou → FAIL
- ✅ **DETECTAR ALUCINAÇÕES SQL**: IA mapeou tabela que VAMAP não reconhece → FAIL
- ✅ **CONFORMIDADE 100%**: Apenas PASS se IA e VAMAP estão 100% alinhados

**Regra de Cruzamento:**

```python
# 1. Carregar tabelas do VAMAP (DATA DIVISION / SQLCA)
vamap_tables = parse_vamap_sql_section("run/ingestion/vamap_raw.log")

# 2. Carregar tabelas da IA (claims_A_sql.json)
ia_tables = extract_affected_tables("run/extraction/claims_A_sql.json")

# 3. Cruzamento
omissoes = vamap_tables - ia_tables  # VAMAP tem, IA não
alucinacoes = ia_tables - vamap_tables  # IA tem, VAMAP não

# 4. Critério de FAIL
if len(omissoes) > 0:
    FAIL("IA não mapeou tabelas que VAMAP detectou")
    
if len(alucinacoes) > 0:
    FAIL("IA mapeou tabelas que VAMAP não reconhece")

# 5. Conformidade
conformidade_sql = (len(ia_tables.intersection(vamap_tables)) / len(vamap_tables)) * 100

if conformidade_sql < 100.0:
    FAIL("Conformidade SQL < 100%")
```

**Seções do VAMAP a Analisar:**

```
--- DATA DIVISION ---
01 BANCOS.
   05 COD-BANCO        PIC X(10).
   05 NOME-BANCO       PIC X(100).

--- SQLCA ---
EXEC SQL DECLARE BANCOS TABLE
  (COD_BANCO CHAR(10),
   NOME_BANCO VARCHAR(100))
END-EXEC
```

**Output Específico:**

```json
{
  "sql_gate_status": "PASS/FAIL",
  "conformidade_sql_percentage": 100.0,
  "tabelas_vamap": ["BANCOS", "AGENCIAS", "TRANSACOES"],
  "tabelas_ia": ["BANCOS", "AGENCIAS", "TRANSACOES"],
  "omissoes": [],
  "alucinacoes": [],
  "queries_validadas": 23,
  "queries_com_tabelas_validas": 23
}
```

**Critério de FAIL:**
- Se VAMAP indicar acesso a uma tabela que a IA não mapeou → SQL-Gate = FAIL
- Se IA mapear tabela não presente no VAMAP → SQL-Gate = FAIL
- Se conformidade_sql_percentage < 100% → SQL-Gate = FAIL

**Arquivos Gerados:**
- `run/extraction/sql_validation_report.md`
- `run/extraction/sql_gate_status.json`
- `run/extraction/sql_conformance_matrix.csv` (tabela × IA × VAMAP)

## Exemplos de Uso

### Exemplo 1: Validação com PASS

```bash
# Executar validação
[VAL] Validar extração

# Output esperado
✅ Arquivos obrigatórios encontrados
✅ JSON válido carregado
✅ GroundingScore: 100.0%
✅ Validações CRITICAL: 0 falhas
✅ Validações HIGH: 0 falhas
✅ Gate G1: PASS
✅ Analyzer-A: PERMITIDO

Arquivos gerados:
- run/extraction/validation_report.md
- run/extraction/gate_status.json
```

### Exemplo 2: Validação com FAIL

```bash
# Executar validação
[VAL] Validar extração

# Output esperado
✅ Arquivos obrigatórios encontrados
✅ JSON válido carregado
❌ GroundingScore: 95.7% (< 100%)
❌ Validações CRITICAL: 4 falhas
  - RULE-001: 4 elementos sem evidence_pointer
❌ Gate G1: FAIL
❌ Analyzer-A: BLOQUEADO

Ações requeridas:
1. Corrigir elementos sem evidence_pointer
2. Executar [EXT] Extrair novamente
3. Executar [VAL] Validar novamente
```

### Exemplo 3: Bloqueio de Entrada

```bash
# Executar validação sem claims_A.json
[VAL] Validar extração

# Output esperado
❌ BLOQUEIO DE VALIDAÇÃO

Arquivos obrigatórios não encontrados:
- run/extraction/claims_A.json: AUSENTE
- run/extraction/extraction_log.txt: PRESENTE

AÇÃO REQUERIDA:
Execute [EXT] Extrair arquivo antes de validar.

STATUS: VALIDAÇÃO ABORTADA
```

## Troubleshooting

### Problema: GroundingScore < 100%
**Causa**: Elementos sem evidence_pointer ou formato inválido  
**Solução**: 
1. Verificar validation_report.md seção "Elementos Inválidos"
2. Identificar elementos problemáticos
3. Corrigir Extractor-A
4. Re-executar extração

### Problema: Falhas CRITICAL
**Causa**: Violação de regras obrigatórias  
**Solução**:
1. Verificar validation_report.md seção "Validações CRITICAL"
2. Corrigir cada falha listada
3. Re-executar extração
4. Re-executar validação

### Problema: Arquivos Obrigatórios Ausentes
**Causa**: Extração não foi executada ou falhou  
**Solução**:
1. Executar [EXT] Extrair arquivo
2. Verificar se extração completou com sucesso
3. Executar [VAL] Validar extração

### Problema: JSON Inválido
**Causa**: Sintaxe JSON incorreta em claims_A.json  
**Solução**:
1. Validar JSON com ferramenta externa
2. Corrigir sintaxe
3. Re-executar extração se necessário

## Métricas de Sucesso

### Gate G1 PASS
- ✅ GroundingScore = 100.0%
- ✅ Zero falhas CRITICAL
- ✅ Máximo 5% falhas HIGH
- ✅ Analyzer-A permitido

### Performance
- ⏱️ Validação completa: <= 10 segundos
- 📊 Relatório gerado: <= 5 segundos

### Qualidade
- 🎯 Precisão: 100% (sem falsos positivos/negativos)
- 📝 Relatório completo e acionável

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Fase**: 1 - As-Is Forense  
**Gate**: G1 - Quality Gate


