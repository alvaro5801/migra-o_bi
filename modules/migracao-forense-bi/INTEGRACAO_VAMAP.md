# Integração VAMAP - Âncora da Verdade

## Sumário Executivo

Este documento descreve a integração do **vamap.exe** (compilador oficial Visual Age) como **Âncora da Verdade** na Fase 1 (As-Is Forense) do módulo de Migração Forense BI.

**Data**: 2025-12-28  
**Versão**: 1.0  
**Status**: ✅ IMPLEMENTADO

---

## Contexto e Motivação

### Problema Original

Na configuração inicial, a extração forense dependia exclusivamente da análise da IA (LLM) sobre o código-fonte Visual Age. Isso apresentava riscos:

1. **Alucinações**: IA pode extrair símbolos inexistentes
2. **Omissões**: IA pode não detectar símbolos reais
3. **Falta de Gabarito**: Sem referência autoritativa para validação

### Solução: VAMAP como Âncora da Verdade

O **vamap.exe** é o compilador oficial Visual Age que:
- ✅ Analisa código Visual Age nativamente
- ✅ Detecta TODOS os símbolos reais (Screens, Fields, Queries, Procedures)
- ✅ Fornece lista autoritativa para validação cruzada
- ✅ Elimina ambiguidade sobre o que é real vs alucinado

**Princípio**: A IA deve estar **100% alinhada** com o VAMAP. Qualquer discrepância = FAIL.

---

## Arquitetura da Integração

### Fluxo Atualizado

```
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: AS-IS FORENSE (com VAMAP)                              │
└─────────────────────────────────────────────────────────────────┘

1. INGESTOR-A (Agente de Origem)
   ├─ Passo 0: Invocar vamap.exe (NOVO)
   │  └─ Output: run/ingestion/vamap_raw.log
   ├─ Passo 1: Validar arquivo original
   ├─ Passo 2: Calcular hash SHA-256
   ├─ Passo 3: Taint analysis
   ├─ Passo 4: Gerar .lined
   └─ Passo 5: Atualizar manifest (com símbolos VAMAP)

2. EXTRACTOR-A (Extração IA)
   └─ Extrai símbolos → claims_A.json

3. VALIDATOR-A (Auditor + Gate G1)
   ├─ RULE-VAMAP (NOVA - CRÍTICA)
   │  ├─ Carregar vamap_raw.log
   │  ├─ Carregar claims_A.json
   │  ├─ Confrontar símbolos IA vs VAMAP
   │  ├─ Detectar alucinações (IA tem, VAMAP não)
   │  ├─ Detectar omissões (VAMAP tem, IA não)
   │  └─ Calcular conformidade (deve ser 100%)
   ├─ GroundingScore (100% evidence_pointer)
   └─ Gate G1: PASS apenas se conformidade = 100%

4. ANALYZER-A (Certificador Estrutural)
   └─ Taint Report → Seção "Conformidade VAMAP" (NOVA)
```

---

## Alterações Implementadas

### 1. Agente Ingestor-A

#### Arquivos Modificados
- `agents/ingestor-a.agent.yaml`
- `agents/ingestor-a/instructions.md`

#### Mudanças Principais

**Novo Passo 0: Invocação do VAMAP**

```python
def invocar_vamap(filepath):
    """
    Invoca vamap.exe e captura output.
    
    Returns:
        dict: Resultado da invocação com símbolos extraídos
    """
    cmd = ["tools/vamap.exe", filepath]
    
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300
    )
    
    # Salvar output completo
    with open("run/ingestion/vamap_raw.log", 'w') as f:
        f.write(process.stdout)
    
    # Extrair símbolos do log
    symbols = extrair_simbolos_vamap(process.stdout)
    
    return {
        "status": "SUCCESS" if process.returncode == 0 else "FAILED",
        "vamap_log": "run/ingestion/vamap_raw.log",
        "symbols_extracted": symbols
    }
```

**Output Esperado do VAMAP**

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

**Manifest Atualizado**

```json
{
  "vamap_enabled": true,
  "files": [
    {
      "original_file": "_LEGADO/bi14a.esf",
      "vamap_log": "run/ingestion/vamap_raw.log",
      "vamap_status": "SUCCESS",
      "vamap_symbols": {
        "screens": 5,
        "fields": 47,
        "queries": 23,
        "procedures": 18
      },
      "sha256_original": "b6fe2994...",
      "status": "SUCCESS"
    }
  ]
}
```

---

### 2. Agente Validator-A

#### Arquivos Modificados
- `agents/validator-a.agent.yaml`
- `agents/validator-a/instructions.md`

#### Mudanças Principais

**Nova Regra RULE-VAMAP (CRÍTICA)**

| Rule ID | Nome | Validação |
|---------|------|-----------|
| **RULE-VAMAP** | **Conformidade VAMAP (Âncora da Verdade)** | **100% símbolos IA ⊆ VAMAP E sem alucinações** |

**Algoritmo de Validação Cruzada**

```python
def validar_conformidade_vamap(claims_json, vamap_log_path):
    """
    Valida conformidade entre IA e VAMAP.
    
    Returns:
        dict: {
            "pass": bool,
            "simbolos_faltantes": list,  # VAMAP tem, IA não
            "alucinacoes": list,         # IA tem, VAMAP não
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
    matches = []
    
    for categoria in ["screens", "fields", "queries", "procedures"]:
        vamap_set = set([s["name"] for s in vamap_symbols.get(categoria, [])])
        ia_set = set([s["id"] for s in ia_symbols.get(categoria, [])])
        
        # Símbolos que VAMAP tem mas IA não extraiu
        faltantes = vamap_set - ia_set
        for simbolo in faltantes:
            simbolos_faltantes.append({
                "categoria": categoria,
                "simbolo": simbolo,
                "motivo": "IA não extraiu este símbolo"
            })
        
        # Símbolos que IA extraiu mas VAMAP não reconhece (ALUCINAÇÃO)
        alucinados = ia_set - vamap_set
        for simbolo in alucinados:
            alucinacoes.append({
                "categoria": categoria,
                "simbolo": simbolo,
                "motivo": "VAMAP não reconhece (possível alucinação)"
            })
        
        # Símbolos corretos
        corretos = vamap_set & ia_set
        matches.extend(list(corretos))
    
    # 4. Calcular score de conformidade
    total_vamap = sum(len(vamap_symbols.get(c, [])) for c in ["screens", "fields", "queries", "procedures"])
    conformidade_score = (len(matches) / total_vamap) * 100.0 if total_vamap > 0 else 0.0
    
    # 5. PASS apenas se: 100% conformidade E zero alucinações
    passou = (
        len(simbolos_faltantes) == 0 and
        len(alucinacoes) == 0 and
        conformidade_score == 100.0
    )
    
    return {
        "pass": passou,
        "simbolos_faltantes": simbolos_faltantes,
        "alucinacoes": alucinacoes,
        "matches": matches,
        "conformidade_score": round(conformidade_score, 2)
    }
```

**Critérios de FAIL**

1. **Símbolos Faltantes**: VAMAP listou um símbolo que a IA não extraiu → FAIL
2. **Alucinações**: IA extraiu um símbolo que VAMAP não reconhece → FAIL
3. **Conformidade < 100%**: Qualquer discrepância → FAIL

**Mensagem de FAIL**

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

**Bloqueio de Entrada Atualizado**

```python
if not exists("run/ingestion/vamap_raw.log"):
    ABORTAR validação
    RETORNAR erro: "BLOQUEIO: vamap_raw.log não encontrado (Âncora da Verdade)"
    EXIT
```

---

### 3. Agente Analyzer-A

#### Arquivos Modificados
- `agents/analyzer-a.agent.yaml`
- `agents/analyzer-a/instructions.md`

#### Mudanças Principais

**Nova Seção no Taint Report: Conformidade VAMAP**

```markdown
## Conformidade VAMAP (Âncora da Verdade)

**CRÍTICO**: Esta seção valida que a análise estrutural da IA está alinhada com o compilador oficial Visual Age.

### Validação Cruzada

**Arquivo VAMAP**: `run/ingestion/vamap_raw.log`
**Arquivo IA**: `run/extraction/claims_A.json`

| Categoria | VAMAP | IA | Matches | Conformidade |
|-----------|-------|----|---------|--------------| 
| Screens | 5 | 5 | 5 | 100% |
| Fields | 47 | 47 | 47 | 100% |
| Queries | 23 | 23 | 23 | 100% |
| Procedures | 18 | 18 | 18 | 100% |
| **TOTAL** | **93** | **93** | **93** | **100%** |

### Status de Conformidade

✅ **PASS**: 100% conformidade - IA alinhada com VAMAP

### Interpretação

- **100% Conformidade**: ✅ Análise estrutural confiável
- **95-99% Conformidade**: ⚠️ Revisar discrepâncias menores
- **< 95% Conformidade**: ❌ Extração precisa ser refeita

**IMPORTANTE**: Se conformidade < 100%, a certificação da Fase 1 deve incluir ressalvas.
```

---

### 4. Base de Conhecimento: vamap-standards.csv

**Localização**: `knowledge/vamap-standards.csv`

**Conteúdo**: 21 padrões de log do VAMAP

| Category | Pattern | Description | Severity |
|----------|---------|-------------|----------|
| HEADER | VAMAP - Visual Age Symbol Analyzer | Cabeçalho do log | INFO |
| FILE_ANALYSIS | Analyzing: | Arquivo sendo analisado | INFO |
| SECTION_SCREENS | SCREENS: | Início da seção de telas | CRITICAL |
| SECTION_FIELDS | FIELDS: | Início da seção de campos | CRITICAL |
| SECTION_QUERIES | QUERIES: | Início da seção de queries | CRITICAL |
| SECTION_PROCEDURES | PROCEDURES: | Início da seção de procedures | CRITICAL |
| SYMBOL_FORMAT | \w+ \(Line \d+-\d+\) | Formato padrão de símbolo | CRITICAL |
| ERROR_SYNTAX | Syntax Error: | Erro de sintaxe detectado | CRITICAL |
| ERROR_REFERENCE | Reference Error: | Referência inválida | HIGH |
| ... | ... | ... | ... |

---

### 5. Module Configuration (module.yaml)

**Adições**:

```yaml
vamap_executable:
  prompt: "Caminho para o executável vamap.exe (Âncora da Verdade)"
  default: "tools/vamap.exe"
  result: "{project-root}/{value}"

vamap_validation_enabled:
  prompt: "Ativar validação cruzada com VAMAP (compilador oficial)?"
  default: "true"
  result: "{value}"

# Artefatos Obrigatórios da Fase 1
required_artifacts:
  ingestion:
    - "run/ingestion/ingestion_manifest.json"
    - "run/ingestion/vamap_raw.log"  # NOVO
    - "run/ingestion/taint_report_preliminar.md"
```

---

## Benefícios da Integração

### 1. Eliminação de Alucinações

**Antes**: IA pode extrair símbolos inexistentes sem detecção  
**Depois**: Qualquer símbolo não reconhecido pelo VAMAP = FAIL imediato

### 2. Garantia de Completude

**Antes**: Sem forma de saber se IA extraiu tudo  
**Depois**: VAMAP fornece lista completa - qualquer omissão = FAIL

### 3. Validação Determinística

**Antes**: Validação baseada apenas em heurísticas  
**Depois**: Validação cruzada com compilador oficial (fonte autoritativa)

### 4. Confiança na Migração

**Antes**: Incerteza sobre qualidade da extração  
**Depois**: Certificação de que extração está 100% alinhada com realidade do código

### 5. Rastreabilidade Absoluta

**Antes**: Evidence pointers sem validação externa  
**Depois**: Evidence pointers + confirmação VAMAP = dupla garantia

---

## Impacto nos Agentes

| Agente | Impacto | Mudanças |
|--------|---------|----------|
| **Ingestor-A** | 🔴 ALTO | Novo passo 0 (vamap.exe), manifest atualizado |
| **Extractor-A** | 🟢 NENHUM | Continua extraindo normalmente |
| **Validator-A** | 🔴 ALTO | Nova regra RULE-VAMAP (crítica), bloqueio atualizado |
| **Analyzer-A** | 🟡 MÉDIO | Nova seção no taint_report.md |
| **Extractor-B** | 🟢 NENHUM | Opera em isolamento |
| **Reconciliador-A** | 🟢 NENHUM | Reconcilia claims já validados |

---

## Fluxo de Validação Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ VALIDAÇÃO MULTI-CAMADA (com VAMAP)                             │
└─────────────────────────────────────────────────────────────────┘

1. VAMAP (Âncora da Verdade)
   └─ Lista autoritativa de símbolos reais

2. EXTRACTOR-A (IA)
   └─ Extrai símbolos com evidence_pointers

3. VALIDATOR-A (Auditor)
   ├─ GroundingScore: 100% evidence_pointers válidos
   ├─ RULE-VAMAP: 100% conformidade IA vs VAMAP
   ├─ Regras CRITICAL: Todas devem passar
   └─ Gate G1: PASS apenas se tudo OK

4. ANALYZER-A (Certificador)
   └─ Confirma conformidade VAMAP no taint_report.md

Resultado: Extração validada por 3 camadas independentes
```

---

## Exemplo de Uso

### Passo 1: Ingestão (com VAMAP)

```bash
# Usuário executa
[ING] Ingerir bi14a.esf

# Ingestor-A executa internamente:
1. vamap.exe _LEGADO/bi14a.esf > run/ingestion/vamap_raw.log
2. Extrai símbolos do log
3. Calcula hash SHA-256
4. Gera bi14a.esf.lined
5. Atualiza manifest com símbolos VAMAP
```

**Output**: `vamap_raw.log` com 93 símbolos detectados

### Passo 2: Extração

```bash
[EXT] Extrair bi14a.esf
```

**Output**: `claims_A.json` com 93 claims

### Passo 3: Validação (com RULE-VAMAP)

```bash
[VAL] Validar Extração
```

**Validador-A executa**:
1. Carrega `vamap_raw.log` (93 símbolos)
2. Carrega `claims_A.json` (93 claims)
3. Confronta símbolo por símbolo
4. Calcula conformidade: 100%
5. Verifica alucinações: 0
6. Verifica omissões: 0
7. **RESULTADO**: PASS ✅

**Output**: `gate_status.json` com `"status": "PASS"`

### Passo 4: Análise

```bash
[ANA] Analisar Estrutura
```

**Analyzer-A inclui no taint_report.md**:

```markdown
## Conformidade VAMAP

| Categoria | VAMAP | IA | Conformidade |
|-----------|-------|----|--------------|
| Total | 93 | 93 | 100% ✅ |

Status: ✅ Análise estrutural confiável
```

---

## Tratamento de Erros

### Caso 1: VAMAP não instalado

```
❌ ERRO: vamap.exe não encontrado em tools/

AÇÃO: 
1. Baixar vamap.exe do repositório oficial
2. Colocar em tools/vamap.exe
3. Verificar permissões de execução
```

### Caso 2: VAMAP falha na análise

```
⚠️ WARNING: VAMAP falhou ao analisar bi14a.esf

Status: TAINTED (com warning)
Ação: Processo continua mas sem validação VAMAP
Nota: Validator-A irá BLOQUEAR se vamap_raw.log não existir
```

### Caso 3: Conformidade < 100%

```
❌ RULE-VAMAP FAILED

Conformidade: 85.7%
Símbolos Faltantes: 2
Alucinações: 11

AÇÃO REQUERIDA:
1. Revisar extração (Extractor-A)
2. Verificar vamap_raw.log
3. Re-executar extração
4. Re-validar
```

---

## Métricas de Sucesso

### KPIs da Integração VAMAP

| Métrica | Alvo | Descrição |
|---------|------|-----------|
| **Conformidade VAMAP** | 100% | IA alinhada com compilador |
| **Taxa de Alucinação** | 0% | Símbolos falsos extraídos |
| **Taxa de Omissão** | 0% | Símbolos reais não extraídos |
| **Tempo VAMAP** | < 5s | Performance da análise |
| **Taxa de Sucesso VAMAP** | > 95% | Arquivos analisados com sucesso |

---

## Próximos Passos

### Fase 1 (Atual) ✅
- [x] Integrar vamap.exe no Ingestor-A
- [x] Criar RULE-VAMAP no Validator-A
- [x] Adicionar seção Conformidade VAMAP no Analyzer-A
- [x] Criar base de conhecimento vamap-standards.csv
- [x] Atualizar module.yaml

### Fase 2 (Futuro)
- [ ] Criar dashboard de conformidade VAMAP
- [ ] Implementar análise de tendências (conformidade ao longo do tempo)
- [ ] Adicionar métricas de performance do VAMAP
- [ ] Criar relatório comparativo IA vs VAMAP por tipo de símbolo
- [ ] Implementar auto-correção de discrepâncias menores

---

## Conclusão

A integração do **vamap.exe** como **Âncora da Verdade** eleva significativamente o rigor técnico da Fase 1 (As-Is Forense), transformando a extração de um processo baseado exclusivamente em IA para um **processo híbrido validado por compilador oficial**.

**Resultado**: Migração forense com **dupla garantia** (IA + Compilador) e **zero tolerância** para alucinações ou omissões.

---

## Referências

### Arquivos Modificados

1. `agents/ingestor-a.agent.yaml`
2. `agents/ingestor-a/instructions.md`
3. `agents/validator-a.agent.yaml`
4. `agents/validator-a/instructions.md`
5. `agents/analyzer-a.agent.yaml`
6. `agents/analyzer-a/instructions.md`
7. `knowledge/vamap-standards.csv` (NOVO)
8. `module.yaml`

### Artefatos Novos

- `run/ingestion/vamap_raw.log` (output do vamap.exe)
- `knowledge/vamap-standards.csv` (padrões de log)

### Princípios Técnicos

- **Zero-Trust Extraction**: Nada é PROVEN sem evidência
- **Dual Validation**: IA + Compilador
- **100% Conformity**: Sem tolerância para discrepâncias
- **Forensic Traceability**: Rastreabilidade absoluta

---

**Documento gerado em**: 2025-12-28  
**Versão**: 1.0  
**Status**: ✅ IMPLEMENTADO E DOCUMENTADO



