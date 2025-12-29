# Workflow: Validação de Extração Forense - Gate G1

## Metadata
- **ID**: validate-extraction
- **Agente**: Validator-A
- **Fase**: 1 - As-Is Forense
- **Gate**: G1 - Quality Gate
- **Duração Estimada**: 5-15 segundos
- **Complexidade**: Alta

## Objetivo

Auditar o output do Extractor-A, calcular o GroundingScore e determinar se o Gate G1 permite a execução do Analyzer-A.

## Pré-requisitos

- [x] Extração forense concluída ([EXT] executado)
- [x] `run/extraction/claims_A.json` existe
- [x] `run/extraction/extraction_log.txt` existe
- [x] `knowledge/extraction-rules.csv` disponível

## Inputs

1. **claims_A.json**
   - Caminho: `run/extraction/claims_A.json`
   - Formato: JSON estruturado
   - Conteúdo: Claims extraídos pelo Extractor-A

2. **extraction_log.txt**
   - Caminho: `run/extraction/extraction_log.txt`
   - Formato: Texto plano
   - Conteúdo: Log da extração

3. **extraction-rules.csv**
   - Caminho: `knowledge/extraction-rules.csv`
   - Formato: CSV
   - Conteúdo: Regras de validação (CRITICAL/HIGH/MEDIUM)

## Outputs

1. **validation_report.md**
   - Caminho: `run/extraction/validation_report.md`
   - Formato: Markdown
   - Conteúdo: Relatório humano detalhado

2. **gate_status.json**
   - Caminho: `run/extraction/gate_status.json`
   - Formato: JSON
   - Conteúdo: Semáforo PASS/FAIL

3. **validation_details.json** (opcional)
   - Caminho: `run/extraction/validation_details.json`
   - Formato: JSON
   - Conteúdo: Detalhes técnicos para debug

## Processo

### Passo 1: Verificação de Bloqueio
**Duração**: < 1 segundo

```markdown
1. Verificar existência de run/extraction/claims_A.json
2. Verificar existência de run/extraction/extraction_log.txt

SE qualquer arquivo ausente:
  - ABORTAR validação
  - Exibir mensagem de bloqueio
  - NÃO gerar outputs
  - EXIT com erro
```

**Validações**:
- ✅ claims_A.json existe e é legível
- ✅ extraction_log.txt existe e é legível

**Mensagem de Bloqueio**:
```
❌ BLOQUEIO DE VALIDAÇÃO

Arquivos obrigatórios não encontrados:
- run/extraction/claims_A.json: [AUSENTE/PRESENTE]
- run/extraction/extraction_log.txt: [AUSENTE/PRESENTE]

AÇÃO REQUERIDA:
Execute [EXT] Extrair arquivo antes de validar.

STATUS: VALIDAÇÃO ABORTADA
```

### Passo 2: Carregamento e Validação JSON
**Duração**: < 1 segundo

```markdown
1. Carregar claims_A.json
2. Validar sintaxe JSON
3. Verificar estrutura básica (metadata, screens, fields, queries, business_logic)

SE JSON inválido:
  - gate_status = FAIL
  - Motivo: "JSON sintaticamente inválido"
  - Gerar relatório com erro
  - EXIT
```

**Validações**:
- ✅ JSON parse sem erro
- ✅ Seção metadata presente
- ✅ Arrays principais presentes

### Passo 3: Cálculo do GroundingScore
**Duração**: 1-3 segundos

```markdown
1. Extrair metadata (total_lines, source_file)
2. Contar total de elementos:
   - screens
   - fields
   - queries
   - business_logic

3. Para cada elemento:
   a. Verificar presença de evidence_pointer
   b. Validar formato (arquivo.esf:Lxxxx-Lyyyy)
   c. Validar linhas (início <= fim <= total_lines)
   d. Marcar como válido ou inválido

4. Calcular score:
   GroundingScore = (válidos / total) × 100

5. Registrar elementos inválidos com detalhes
```

**Fórmula**:
```
GroundingScore = (Elementos Válidos / Total Elementos) × 100
```

**Critério**:
```python
if grounding_score < 100.0:
    gate_status = "FAIL"
    motivo = f"GroundingScore {grounding_score}% < 100%"
```

**Output Parcial**:
```json
{
  "grounding_score": 100.0,
  "total_elementos": 93,
  "elementos_validos": 93,
  "elementos_invalidos": 0
}
```

### Passo 4: Validação de Regras CRITICAL
**Duração**: 2-5 segundos

```markdown
1. Carregar extraction-rules.csv
2. Filtrar regras com severity = "CRITICAL"
3. Para cada regra CRITICAL:
   a. Aplicar validação ao claims_A.json
   b. Registrar PASS ou FAIL
   c. Se FAIL, registrar detalhes

4. Contar total de falhas CRITICAL

SE critical_failures > 0:
  - gate_status = FAIL
  - Motivo: "X falhas CRITICAL encontradas"
```

**Regras CRITICAL (10)**:
- RULE-001: Evidence Pointer Obrigatório
- RULE-002: Formato Evidence Pointer
- RULE-003: Linhas Existentes
- RULE-004: Screen ID Válido
- RULE-005: Dependências Válidas
- RULE-006: Campo Obrigatório Preenchido
- RULE-012: JSON Válido
- RULE-013: Metadata Completo
- RULE-016: Evidence Validity 100%
- RULE-021: IDs Únicos

**Output Parcial**:
```json
{
  "critical_failures": 0,
  "critical_validations": [
    {
      "rule_id": "RULE-001",
      "status": "PASS"
    }
  ]
}
```

### Passo 5: Validação de Regras HIGH
**Duração**: 1-3 segundos

```markdown
1. Filtrar regras com severity = "HIGH"
2. Para cada regra HIGH:
   a. Aplicar validação
   b. Registrar PASS ou FAIL
   c. Se FAIL, registrar detalhes

3. Contar total de falhas HIGH
4. Calcular taxa de falha: (falhas / total_high) × 100

SE taxa_falha > 5%:
  - gate_status = FAIL
  - Motivo: "Taxa de falha HIGH {taxa}% > 5%"
```

**Regras HIGH (8)**:
- RULE-007: SQL Statement Completo (95%)
- RULE-015: Coverage Mínimo (>= 95%)
- RULE-017: Telas Completas (100%)
- RULE-018: Campos Completos (100%)
- RULE-019: Queries Completas (100%)
- RULE-024: Tables Referenced (95%)
- RULE-026: Line Range Consistente (100%)
- RULE-028: Summary Correto (100%)

**Output Parcial**:
```json
{
  "high_failures": 0,
  "high_failure_rate": 0.0
}
```

### Passo 6: Validação de Regras MEDIUM (Informativo)
**Duração**: 1-2 segundos

```markdown
1. Filtrar regras com severity = "MEDIUM"
2. Para cada regra MEDIUM:
   a. Aplicar validação
   b. Registrar PASS ou FAIL
   c. Registrar para relatório

3. Falhas MEDIUM NÃO afetam gate_status
4. Apenas informativo para melhoria contínua
```

**Regras MEDIUM (12)**:
- RULE-008: Description Mínima
- RULE-023: Complexity Score Válido
- RULE-025: Parameters Identificados
- RULE-027: Fields Count Correto
- RULE-031: Pseudo Code Presente
- RULE-032: Validation Rules Listadas
- Outras...

### Passo 7: Determinação do Gate Status
**Duração**: < 1 segundo

```markdown
1. Avaliar todas as condições:
   - GroundingScore == 100.0?
   - critical_failures == 0?
   - high_failure_rate <= 5%?
   - JSON válido?
   - Arquivos presentes?

2. Determinar status:
   SE todas condições PASS:
     gate_status = "PASS"
     next_agent_allowed = True
   SENÃO:
     gate_status = "FAIL"
     next_agent_allowed = False

3. Registrar motivo se FAIL
```

**Lógica**:
```python
pass_conditions = [
    grounding_score == 100.0,
    critical_failures == 0,
    high_failure_rate <= 5.0,
    json_valido == True,
    arquivos_presentes == True
]

gate_status = "PASS" if all(pass_conditions) else "FAIL"
```

### Passo 8: Geração de Relatórios
**Duração**: 1-2 segundos

```markdown
1. Gerar validation_report.md:
   - Sumário Executivo (PASS/FAIL)
   - GroundingScore Detalhado
   - Falhas CRITICAL (se houver)
   - Falhas HIGH (se houver)
   - Métricas de Qualidade
   - Recomendações de Correção
   - Status do Gate G1
   - Próximos Passos

2. Gerar gate_status.json:
   - status: PASS/FAIL
   - grounding_score
   - critical_failures
   - high_failures
   - next_agent_allowed
   - timestamp

3. Gerar validation_details.json (opcional):
   - Detalhes completos de todas validações
   - Para debug e análise técnica
```

### Passo 9: Comunicação de Resultado
**Duração**: < 1 segundo

```markdown
SE gate_status == "PASS":
  Exibir:
    ✅ Gate G1 PASS
    ✅ GroundingScore: 100.0%
    ✅ Zero falhas CRITICAL
    ✅ Analyzer-A PERMITIDO
    → Execute: [ANA] Analisar estrutura

SENÃO:
  Exibir:
    ❌ Gate G1 FAIL
    ❌ GroundingScore: XX.X%
    ❌ X falhas CRITICAL
    ❌ Analyzer-A BLOQUEADO
    → Corrija erros e execute: [EXT] Extrair novamente
```

## Validações Finais

### Validações PASS (todas obrigatórias)
- [ ] GroundingScore = 100.0%
- [ ] Zero falhas CRITICAL
- [ ] Taxa falha HIGH <= 5%
- [ ] JSON sintaticamente válido
- [ ] Arquivos obrigatórios presentes
- [ ] validation_report.md gerado
- [ ] gate_status.json gerado

### Validações FAIL (qualquer uma)
- [ ] GroundingScore < 100.0%
- [ ] Falhas CRITICAL > 0
- [ ] Taxa falha HIGH > 5%
- [ ] JSON inválido
- [ ] Arquivos obrigatórios ausentes

## Métricas de Sucesso

### Qualidade
- **GroundingScore**: 100.0%
- **Critical Failures**: 0
- **High Failure Rate**: <= 5%

### Performance
- **Tempo Total**: <= 15 segundos
- **Geração de Relatórios**: <= 5 segundos

### Completude
- **Validações Executadas**: 100%
- **Relatórios Gerados**: 100%

## Troubleshooting

### Erro: Arquivos obrigatórios ausentes
**Causa**: Extração não foi executada  
**Solução**: Execute [EXT] Extrair arquivo

### Erro: JSON inválido
**Causa**: Sintaxe incorreta em claims_A.json  
**Solução**: Verifique log de extração e re-execute

### Erro: GroundingScore < 100%
**Causa**: Elementos sem evidence_pointer ou formato inválido  
**Solução**: 
1. Verifique validation_report.md
2. Identifique elementos inválidos
3. Corrija Extractor-A
4. Re-execute extração

### Erro: Falhas CRITICAL
**Causa**: Violação de regras obrigatórias  
**Solução**:
1. Verifique validation_report.md seção CRITICAL
2. Corrija cada falha
3. Re-execute extração
4. Re-execute validação

## Exemplo Completo

### Cenário 1: PASS

**Input**:
```bash
[VAL] Validar extração
```

**Processo**:
```
[00:00] 🔍 Verificando arquivos obrigatórios...
[00:00] ✅ claims_A.json encontrado
[00:00] ✅ extraction_log.txt encontrado
[00:01] 📊 Carregando claims_A.json...
[00:01] ✅ JSON válido
[00:02] 🧮 Calculando GroundingScore...
[00:02] ✅ GroundingScore: 100.0% (93/93)
[00:03] 🔍 Validando regras CRITICAL...
[00:05] ✅ 0 falhas CRITICAL
[00:06] 🔍 Validando regras HIGH...
[00:08] ✅ 0 falhas HIGH (0.0%)
[00:09] 📝 Gerando relatórios...
[00:11] ✅ validation_report.md gerado
[00:11] ✅ gate_status.json gerado
[00:11] ✅ Gate G1: PASS
[00:11] ✅ Analyzer-A: PERMITIDO
```

**Output**:
```json
{
  "status": "PASS",
  "grounding_score": 100.0,
  "critical_failures": 0,
  "high_failures": 0,
  "next_agent_allowed": true
}
```

### Cenário 2: FAIL

**Input**:
```bash
[VAL] Validar extração
```

**Processo**:
```
[00:00] 🔍 Verificando arquivos obrigatórios...
[00:00] ✅ claims_A.json encontrado
[00:00] ✅ extraction_log.txt encontrado
[00:01] 📊 Carregando claims_A.json...
[00:01] ✅ JSON válido
[00:02] 🧮 Calculando GroundingScore...
[00:02] ❌ GroundingScore: 95.7% (89/93)
[00:02] ❌ 4 elementos inválidos encontrados
[00:03] 🔍 Validando regras CRITICAL...
[00:05] ❌ 4 falhas CRITICAL
  - RULE-001: 4 elementos sem evidence_pointer
[00:06] 🔍 Validando regras HIGH...
[00:08] ❌ 2 falhas HIGH (25.0%)
[00:09] 📝 Gerando relatórios...
[00:11] ✅ validation_report.md gerado
[00:11] ✅ gate_status.json gerado
[00:11] ❌ Gate G1: FAIL
[00:11] ❌ Analyzer-A: BLOQUEADO
```

**Output**:
```json
{
  "status": "FAIL",
  "grounding_score": 95.7,
  "critical_failures": 4,
  "high_failures": 2,
  "next_agent_allowed": false,
  "blocking_reason": "GroundingScore < 100% e 4 falhas CRITICAL"
}
```

## Próximos Passos

### Se PASS
1. ✅ Gate G1 aprovado
2. ✅ Analyzer-A pode executar
3. → Execute: **[ANA] Analisar estrutura**

### Se FAIL
1. ❌ Revisar validation_report.md
2. ❌ Corrigir erros identificados
3. ❌ Re-executar: **[EXT] Extrair arquivo**
4. ❌ Re-executar: **[VAL] Validar extração**

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Agente**: Validator-A  
**Gate**: G1 - Quality Gate


