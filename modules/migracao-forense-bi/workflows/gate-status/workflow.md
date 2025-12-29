# Workflow: Verificar Status do Gate

## Metadata
- **ID**: gate-status
- **Agente**: Validator-A
- **Fase**: 1 - As-Is Forense
- **Gate**: G1
- **Duração Estimada**: < 1 segundo
- **Complexidade**: Mínima

## Objetivo

Verificar rapidamente o status atual do Gate G1 sem re-executar validação completa.

## Pré-requisitos

- [x] Validação executada anteriormente
- [x] `run/extraction/gate_status.json` existe

## Inputs

1. **gate_status.json**
   - Caminho: `run/extraction/gate_status.json`
   - Formato: JSON

## Outputs

**Console Output**: Status rápido

## Processo

```markdown
1. Carregar gate_status.json
2. Exibir status (PASS/FAIL)
3. Exibir GroundingScore
4. Exibir se próximo agente está permitido
```

## Exemplo de Output

### PASS

```
🛡️ Gate G1 Status Check

Status: ✅ PASS
GroundingScore: 100.0%
Analyzer-A: ✅ PERMITIDO

Última validação: 2025-12-27T10:30:00Z
```

### FAIL

```
🛡️ Gate G1 Status Check

Status: ❌ FAIL
GroundingScore: 95.7%
Analyzer-A: ❌ BLOQUEADO

Motivo: GroundingScore < 100% e 4 falhas CRITICAL

Última validação: 2025-12-27T10:30:00Z

Ação: Execute [VAL] para detalhes completos
```

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Agente**: Validator-A


