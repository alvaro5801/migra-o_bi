# Workflow: Resumo de Qualidade

## Metadata
- **ID**: quality-summary
- **Agente**: Validator-A
- **Fase**: 1 - As-Is Forense
- **Duração Estimada**: < 5 segundos
- **Complexidade**: Baixa

## Objetivo

Gerar resumo executivo de qualidade baseado no gate_status.json, apresentando métricas principais de forma clara e acionável.

## Pré-requisitos

- [x] Validação executada ([VAL] executado)
- [x] `run/extraction/gate_status.json` existe

## Inputs

1. **gate_status.json**
   - Caminho: `run/extraction/gate_status.json`
   - Formato: JSON
   - Conteúdo: Status do Gate G1

2. **validation_report.md** (opcional)
   - Caminho: `run/extraction/validation_report.md`
   - Formato: Markdown
   - Conteúdo: Relatório detalhado

## Outputs

**Console Output**: Resumo executivo formatado

## Processo

### Passo 1: Carregar gate_status.json

```markdown
1. Verificar existência de run/extraction/gate_status.json
2. Carregar JSON
3. Extrair métricas principais
```

### Passo 2: Formatar Resumo

```markdown
1. Status do Gate (PASS/FAIL)
2. GroundingScore
3. Falhas por severidade
4. Próximo agente permitido
5. Recomendações
```

## Exemplo de Output

### Cenário PASS

```
═══════════════════════════════════════════════════════
  RESUMO DE QUALIDADE - GATE G1
═══════════════════════════════════════════════════════

Status do Gate: ✅ PASS

GroundingScore: 100.0%
├─ Total de Elementos: 93
├─ Elementos Válidos: 93
└─ Elementos Inválidos: 0

Validações:
├─ CRITICAL: ✅ 0 falhas
├─ HIGH: ✅ 0 falhas (0.0%)
└─ MEDIUM: ⚠️  2 falhas (informativo)

Próximo Agente: Analyzer-A
Status: ✅ PERMITIDO

Timestamp: 2025-12-27T10:30:00Z
Duração: 3.5s

═══════════════════════════════════════════════════════
  PRÓXIMOS PASSOS
═══════════════════════════════════════════════════════

✅ Gate G1 aprovado
✅ Extração forense validada com sucesso
→ Execute: [ANA] Analisar estrutura

═══════════════════════════════════════════════════════
```

### Cenário FAIL

```
═══════════════════════════════════════════════════════
  RESUMO DE QUALIDADE - GATE G1
═══════════════════════════════════════════════════════

Status do Gate: ❌ FAIL

GroundingScore: 95.7%
├─ Total de Elementos: 93
├─ Elementos Válidos: 89
└─ Elementos Inválidos: 4

Validações:
├─ CRITICAL: ❌ 4 falhas
├─ HIGH: ❌ 2 falhas (25.0%)
└─ MEDIUM: ⚠️  5 falhas (informativo)

Próximo Agente: Analyzer-A
Status: ❌ BLOQUEADO

Motivo do Bloqueio:
GroundingScore < 100% e 4 falhas CRITICAL

Timestamp: 2025-12-27T10:30:00Z
Duração: 3.5s

═══════════════════════════════════════════════════════
  AÇÕES REQUERIDAS
═══════════════════════════════════════════════════════

❌ Revisar validation_report.md para detalhes
❌ Corrigir 4 elementos sem evidence_pointer
❌ Re-executar: [EXT] Extrair arquivo
❌ Re-executar: [VAL] Validar extração

═══════════════════════════════════════════════════════
```

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Agente**: Validator-A


