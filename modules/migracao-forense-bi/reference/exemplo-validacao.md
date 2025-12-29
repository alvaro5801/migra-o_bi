# Exemplo de Validação Forense - Validator-A

## Cenário: Validação com PASS

### Input: gate_status.json

Após extração bem-sucedida do exemplo.esf:

```json
{
  "metadata": {
    "source_file": "exemplo.esf",
    "extraction_timestamp": "2025-12-27T10:30:00Z",
    "file_hash_sha256": "a1b2c3d4e5f6...",
    "total_lines": 58
  },
  "summary": {
    "total_screens": 1,
    "total_fields": 3,
    "total_queries": 1,
    "total_business_logic_blocks": 3,
    "coverage_percentage": 100.0,
    "evidence_pointers_valid": 8,
    "evidence_pointers_total": 8
  }
}
```

### Processo de Validação

#### 1. Verificação de Bloqueio ✅
```
✅ run/extraction/claims_A.json: PRESENTE
✅ run/extraction/extraction_log.txt: PRESENTE
→ Prosseguir com validação
```

#### 2. Validação JSON ✅
```
✅ JSON sintaticamente válido
✅ Estrutura completa (metadata + arrays)
```

#### 3. Cálculo do GroundingScore ✅

**Contagem de Elementos**:
- Screens: 1
- Fields: 3
- Queries: 1
- Business Logic: 3
- **Total**: 8 elementos

**Validação de Evidence Pointers**:

| Tipo | ID | Evidence Pointer | Status |
|------|----|--------------------|--------|
| Screen | SCR-001 | exemplo.esf:L0005-L0026 | ✅ VÁLIDO |
| Field | FLD-001 | exemplo.esf:L0010-L0014 | ✅ VÁLIDO |
| Field | FLD-002 | exemplo.esf:L0016-L0019 | ✅ VÁLIDO |
| Field | FLD-003 | exemplo.esf:L0021-L0025 | ✅ VÁLIDO |
| Query | QRY-001 | exemplo.esf:L0038-L0043 | ✅ VÁLIDO |
| Logic | LOG-001 | exemplo.esf:L0031-L0035 | ✅ VÁLIDO |
| Logic | LOG-002 | exemplo.esf:L0046-L0052 | ✅ VÁLIDO |
| Logic | LOG-003 | exemplo.esf:L0056-L0058 | ✅ VÁLIDO |

**Resultado**:
```
GroundingScore = (8 válidos / 8 total) × 100 = 100.0%
```

#### 4. Validação de Regras CRITICAL ✅

| Rule ID | Nome | Status | Detalhes |
|---------|------|--------|----------|
| RULE-001 | Evidence Pointer Obrigatório | ✅ PASS | 8/8 elementos com evidence_pointer |
| RULE-002 | Formato Evidence Pointer | ✅ PASS | 8/8 formato correto |
| RULE-003 | Linhas Existentes | ✅ PASS | Todas linhas <= 58 |
| RULE-004 | Screen ID Válido | ✅ PASS | 3/3 fields referenciam SCR-001 |
| RULE-005 | Dependências Válidas | ✅ PASS | Todas dependencies existem |
| RULE-006 | Campos Obrigatórios | ✅ PASS | Nenhum campo vazio |
| RULE-012 | JSON Válido | ✅ PASS | Sintaxe correta |
| RULE-013 | Metadata Completo | ✅ PASS | Todos campos presentes |
| RULE-016 | Evidence Validity 100% | ✅ PASS | 8 válidos = 8 total |
| RULE-021 | IDs Únicos | ✅ PASS | Nenhum ID duplicado |

**Resultado**: 0 falhas CRITICAL

#### 5. Validação de Regras HIGH ✅

| Rule ID | Nome | Status | Detalhes |
|---------|------|--------|----------|
| RULE-007 | SQL Statement Completo | ✅ PASS | 1/1 queries com SQL |
| RULE-015 | Coverage Mínimo | ✅ PASS | 100% >= 95% |
| RULE-017 | Telas Completas | ✅ PASS | 1/1 telas extraídas |
| RULE-018 | Campos Completos | ✅ PASS | 3/3 campos extraídos |
| RULE-019 | Queries Completas | ✅ PASS | 1/1 queries extraídas |
| RULE-024 | Tables Referenced | ✅ PASS | 1/1 queries com tables |
| RULE-026 | Line Range Consistente | ✅ PASS | 8/8 consistentes |
| RULE-028 | Summary Correto | ✅ PASS | Todos valores corretos |

**Resultado**: 0 falhas HIGH (0.0%)

#### 6. Determinação do Gate Status ✅

**Condições de PASS**:
- ✅ GroundingScore = 100.0%
- ✅ Critical failures = 0
- ✅ High failure rate = 0.0% (<= 5%)
- ✅ JSON válido = True
- ✅ Arquivos presentes = True

**Resultado**: PASS

### Output: validation_report.md

```markdown
# Relatório de Validação Forense - Gate G1

## Sumário Executivo

**Status do Gate G1**: ✅ PASS
**GroundingScore**: 100.0%
**Data/Hora**: 2025-12-27T10:30:00Z
**Arquivo Validado**: claims_A.json

---

## GroundingScore Detalhado

### Cálculo
- **Total de Elementos**: 8
- **Elementos Válidos**: 8
- **Elementos Inválidos**: 0
- **Score Final**: 100.0%

### Breakdown por Tipo
| Tipo | Total | Válidos | Inválidos | Score |
|------|-------|---------|-----------|-------|
| Screens | 1 | 1 | 0 | 100% |
| Fields | 3 | 3 | 0 | 100% |
| Queries | 1 | 1 | 0 | 100% |
| Business Logic | 3 | 3 | 0 | 100% |

---

## Validações CRITICAL

**Total de Regras CRITICAL**: 10
**Falhas Encontradas**: 0

✅ Todas as validações CRITICAL passaram com sucesso.

---

## Validações HIGH

**Total de Regras HIGH**: 8
**Falhas Encontradas**: 0
**Taxa de Falha**: 0.0%
**Threshold Permitido**: 5%

✅ Todas as validações HIGH passaram com sucesso.

---

## Métricas de Qualidade

| Métrica | Valor | Status |
|---------|-------|--------|
| Coverage | 100% | ✅ PASS |
| Evidence Validity | 100% | ✅ PASS |
| Referências Válidas | 100% | ✅ PASS |
| IDs Únicos | 100% | ✅ PASS |

---

## Status do Gate G1

**Decisão Final**: ✅ PASS

**Próximo Agente**: Analyzer-A
**Status**: ✅ PERMITIDO

**Timestamp**: 2025-12-27T10:30:00Z

---

## Próximos Passos

✅ Gate G1 aprovado
✅ Extração forense validada com sucesso
✅ Analyzer-A pode executar

→ Execute: [ANA] Analisar estrutura
```

### Output: gate_status.json

```json
{
  "status": "PASS",
  "grounding_score": 100.0,
  "timestamp": "2025-12-27T10:30:00Z",
  "critical_failures": 0,
  "high_failures": 0,
  "medium_failures": 0,
  "next_agent_allowed": true,
  "next_agent": "Analyzer-A",
  "validation_duration_seconds": 2.3,
  "metadata": {
    "validator_version": "1.0.0",
    "claims_file": "run/extraction/claims_A.json",
    "claims_hash": "a1b2c3d4e5f6...",
    "total_elements_validated": 8
  }
}
```

## Cenário: Validação com FAIL

### Input: claims_A.json com Erros

Suponha que o Extractor-A falhou em 2 campos:

```json
{
  "fields": [
    {
      "field_id": "FLD-001",
      "field_name": "COD_BANCO",
      "evidence_pointer": "exemplo.esf:L0010-L0014"
    },
    {
      "field_id": "FLD-002",
      "field_name": "NOME_BANCO",
      "evidence_pointer": ""  // ❌ VAZIO
    },
    {
      "field_id": "FLD-003",
      "field_name": "STATUS_BANCO"
      // ❌ SEM evidence_pointer
    }
  ]
}
```

### Processo de Validação

#### 3. Cálculo do GroundingScore ❌

**Validação de Evidence Pointers**:

| Tipo | ID | Evidence Pointer | Status | Erro |
|------|----|--------------------|--------|------|
| Field | FLD-001 | exemplo.esf:L0010-L0014 | ✅ VÁLIDO | - |
| Field | FLD-002 | "" | ❌ INVÁLIDO | FORMAT: Formato inválido |
| Field | FLD-003 | (ausente) | ❌ INVÁLIDO | MISSING: Campo ausente |

**Resultado**:
```
GroundingScore = (6 válidos / 8 total) × 100 = 75.0%
```

#### 4. Validação de Regras CRITICAL ❌

| Rule ID | Nome | Status | Detalhes |
|---------|------|--------|----------|
| RULE-001 | Evidence Pointer Obrigatório | ❌ FAIL | 1 elemento sem evidence_pointer |
| RULE-002 | Formato Evidence Pointer | ❌ FAIL | 1 elemento com formato inválido |

**Resultado**: 2 falhas CRITICAL

#### 6. Determinação do Gate Status ❌

**Condições de FAIL**:
- ❌ GroundingScore = 75.0% (< 100%)
- ❌ Critical failures = 2 (> 0)

**Resultado**: FAIL

### Output: gate_status.json

```json
{
  "status": "FAIL",
  "grounding_score": 75.0,
  "timestamp": "2025-12-27T10:35:00Z",
  "critical_failures": 2,
  "high_failures": 0,
  "medium_failures": 0,
  "next_agent_allowed": false,
  "next_agent": "Analyzer-A",
  "blocking_reason": "GroundingScore < 100% e 2 falhas CRITICAL",
  "validation_duration_seconds": 2.1,
  "metadata": {
    "validator_version": "1.0.0",
    "claims_file": "run/extraction/claims_A.json",
    "claims_hash": "x9y8z7w6...",
    "total_elements_validated": 8
  }
}
```

### Ações Requeridas

```
❌ Gate G1 FAIL

Problemas encontrados:
1. FLD-002: Evidence pointer vazio
2. FLD-003: Evidence pointer ausente

Ações:
1. Corrigir Extractor-A para garantir evidence_pointer em todos elementos
2. Re-executar: [EXT] Extrair exemplo.esf
3. Re-executar: [VAL] Validar extração
```

## Uso do Exemplo

### Para Testar Validator-A

```bash
# 1. Usar claims_A.json do exemplo de extração
cp reference/exemplo-extracao-claims.json run/extraction/claims_A.json

# 2. Executar validação
[VAL] Validar extração

# 3. Verificar output
cat run/extraction/gate_status.json
cat run/extraction/validation_report.md
```

### Para Simular Falha

```bash
# 1. Modificar claims_A.json para remover evidence_pointer
# 2. Executar validação
[VAL] Validar extração

# 3. Verificar FAIL
# Esperado: GroundingScore < 100%, Gate FAIL
```

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Tipo**: Exemplo de Referência  
**Agente**: Validator-A


