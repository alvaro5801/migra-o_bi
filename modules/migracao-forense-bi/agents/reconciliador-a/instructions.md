# Instruções Detalhadas - Reconciliador-A

## Missão Principal

Reconciliar extrações redundantes (claims_A e claims_B) gerando **inventário final consolidado** (claim_ledger.csv) com classificação de confiança.

## Bloqueio de Entrada

**CRÍTICO**: Verificar existência de AMBOS os arquivos:

```python
if not exists("run/extraction/claims_A.json"):
    ABORTAR
    
if not exists("run/extraction/claims_B.json"):
    ABORTAR
```

**Mensagem de Bloqueio**:
```
❌ BLOQUEIO: Arquivos de extração não encontrados

Requeridos:
- run/extraction/claims_A.json: [AUSENTE]
- run/extraction/claims_B.json: [AUSENTE]

AÇÃO: Execute [EXT] e [EXTB] antes de reconciliar
```

## Ferramenta Principal

### Script: `tools/reconcile.py`

**Função**: Comparar claims_A.json e claims_B.json

**Uso**:
```bash
python tools/reconcile.py \
  --input-a run/extraction/claims_A.json \
  --input-b run/extraction/claims_B.json \
  --output-ledger run/reconcile/claim_ledger.csv \
  --output-report run/reconcile/diff_report.md
```

## Processo de Reconciliação

### Passo 1: Carregar Arquivos

```python
claims_a = load_json("run/extraction/claims_A.json")
claims_b = load_json("run/extraction/claims_B.json")
```

### Passo 2: Comparar Metadata

```python
# Verificar que são do mesmo arquivo fonte
assert claims_a["metadata"]["source_file"] == claims_b["metadata"]["source_file"]
assert claims_a["metadata"]["file_hash_sha256"] == claims_b["metadata"]["file_hash_sha256"]
```

### Passo 3: Reconciliar Screens

```python
for screen_a in claims_a["screens"]:
    # Procurar correspondente em B
    screen_b = find_matching_screen(screen_a, claims_b["screens"])
    
    if screen_b and is_identical(screen_a, screen_b):
        # MATCH - Alta Confiança
        ledger.append({
            "item_id": screen_a["screen_id"],
            "status": "MATCH",
            "confidence_level": "HIGH",
            "source": "BOTH"
        })
    
    elif screen_b and has_differences(screen_a, screen_b):
        # DISCREPANCY - Requer Análise
        ledger.append({
            "item_id": screen_a["screen_id"],
            "status": "DISCREPANCY",
            "confidence_level": "MEDIUM",
            "source": "BOTH",
            "requires_review": true
        })
    
    else:
        # MISSING_IN_B
        ledger.append({
            "item_id": screen_a["screen_id"],
            "status": "MISSING_IN_B",
            "confidence_level": "LOW",
            "source": "A_ONLY",
            "requires_review": true
        })
```

### Passo 4: Reconciliar Fields, Queries, Logic

Processo similar para cada tipo de item.

### Passo 5: Gerar Ledger

**Arquivo**: `run/reconcile/claim_ledger.csv`

**Formato**:
```csv
item_id,item_type,item_name,evidence_pointer_a,evidence_pointer_b,status,confidence_level,source,reconciliation_note,requires_review
SCR-001,screen,TELA_CONSULTA,bi14a.esf:L0123-L0145,bi14a.esf:L0123-L0145,MATCH,HIGH,BOTH,Identical in both,false
FLD-001,field,COD_BANCO,bi14a.esf:L0130-L0132,bi14a.esf:L0130-L0133,DISCREPANCY,MEDIUM,BOTH,Different ranges,true
QRY-005,query,SELECT_X,,bi14a.esf:L0600-L0602,MISSING_IN_A,LOW,B_ONLY,Only in B,true
```

### Passo 6: Gerar Diff Report

**Arquivo**: `run/reconcile/diff_report.md`

**Estrutura**:
```markdown
# Diff Report - Reconciliação de Extrações

## Sumário
- Total Matches: 85 (91%)
- Total Discrepancies: 5 (5%)
- Missing in B: 3 (3%)
- Missing in A: 0 (0%)

## Matches (Alta Confiança) - 85 itens
[Lista de itens idênticos]

## Discrepancies (Requer Análise) - 5 itens

### 1. FLD-001 - COD_BANCO
- **Tipo**: DIFFERENT_EVIDENCE
- **A**: bi14a.esf:L0130-L0132
- **B**: bi14a.esf:L0130-L0133
- **Ação**: Verificar qual range está correto

## Missing in B - 3 itens
[Itens que A viu mas B não]

## Recomendações
1. Revisar 5 discrepancies
2. Investigar 3 missing items
3. Considerar Agente C para discrepancies HIGH
```

## Critérios de Match

### Screens
- ✅ screen_name igual
- ✅ evidence_pointer igual OU overlap >= 80%
- ✅ fields_count igual OU diferença <= 10%

### Fields
- ✅ field_name igual
- ✅ screen_id correspondente
- ✅ field_type igual

### Queries
- ✅ sql_statement normalizado igual
- ✅ query_type igual
- ✅ tables_referenced igual

### Business Logic
- ✅ description similar (>= 80%)
- ✅ logic_type igual
- ✅ evidence_pointer overlap >= 80%

## Níveis de Confiança

| Nível | Critério | Cor | Ação |
|-------|----------|-----|------|
| HIGH | Idênticos | 🟢 | Aceitar automaticamente |
| MEDIUM | Similares | 🟡 | Revisar se possível |
| LOW | Discrepância | 🔴 | Requer Agente C ou Humano |

## Handover para Analyzer-A

**ATUALIZAÇÃO NECESSÁRIA**: Analyzer-A deve ler `claim_ledger.csv` ao invés de `claims_A.json`

**Novo Input**:
```python
# Antigo
claims = load_json("run/extraction/claims_A.json")

# Novo
ledger = load_csv("run/reconcile/claim_ledger.csv")

# Filtrar itens de alta confiança
high_confidence = ledger[ledger["confidence_level"] == "HIGH"]
```

## Comandos Disponíveis

### [REC] Reconciliar Extrações

**Uso**:
```bash
[REC] Reconciliar extrações
```

**Output**:
- `run/reconcile/diff_report.md`
- `run/reconcile/claim_ledger.csv`
- `run/reconcile/reconciliation_log.txt`
- `run/reconcile/reconciliation_metrics.json`

### [DIFF] Gerar Diff Report

Gera apenas o relatório de diferenças

### [LEDGER] Gerar Ledger

Gera apenas o claim_ledger.csv

## Exemplo de Uso Completo

```bash
# 1. Extração A
[EXT] Extrair bi14a.esf
✅ claims_A.json gerado

# 2. Extração B (isolada)
[EXTB] Extrair bi14a.esf
✅ claims_B.json gerado

# 3. Reconciliação
[REC] Reconciliar extrações
✅ claim_ledger.csv gerado
✅ diff_report.md gerado
📊 Matches: 85 (91%)
⚠️  Discrepancies: 5 (5%)
❌ Missing: 3 (3%)

# 4. Análise (atualizada)
[ANA] Analisar estrutura
(Agora lê claim_ledger.csv)
```

---

**Versão**: 1.0.0  
**Módulo**: migracao-forense-bi  
**Papel**: Reconciliador Determinístico

