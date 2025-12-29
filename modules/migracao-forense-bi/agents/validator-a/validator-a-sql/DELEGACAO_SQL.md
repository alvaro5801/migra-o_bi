# Delegação SQL - Validator-A → Validator-A-SQL

## 🎯 Objetivo

Documentar a delegação de tarefas de validação SQL do **Validator-A** (agente geral) para o **Validator-A-SQL** (especialista em dados).

---

## 📊 Divisão de Responsabilidades

### Validator-A (Agente Geral)

**Responsabilidades**:
- ✅ Validação geral de extração (UI, Business Logic, Workflows)
- ✅ Cálculo de GroundingScore geral
- ✅ Validação de evidence_pointers gerais
- ✅ Fechamento do Gate G1 geral
- ✅ Validação de estrutura JSON
- ✅ Validação de metadata

**Comandos**:
- `[VAL]`: Validação geral de extração
- `[RPT]`: Resumo executivo de qualidade
- `[GATE]`: Status do Gate G1 geral

**Outputs**:
- `run/extraction/validation_report.md`
- `run/extraction/gate_status.json`
- `run/extraction/validation_details.json`

---

### Validator-A-SQL (Especialista SQL)

**Responsabilidades**:
- ✅ Validação exclusiva de SQL (Ledger de Dados)
- ✅ Confrontação SQL vs VAMAP
- ✅ Validação de evidence_pointers SQL
- ✅ Validação de type mapping (COBOL → SQL)
- ✅ Cálculo de Grounding Score SQL
- ✅ Fechamento do Gate G1-SQL

**Comandos**:
- `[VAL-SQL]`: Validação especializada SQL

**Outputs**:
- `run/sql/validation/gate_status_sql.json`
- `run/sql/validation/validation_report_sql.md`

---

## 🔄 Fluxo de Delegação

### Cenário 1: Validação Geral (UI + Business Logic)

```
Usuário → [VAL] → Validator-A
                      ↓
                Validação Geral
                      ↓
            Gate G1: PASS/FAIL
```

**Não envolve SQL** → Validator-A processa sozinho

---

### Cenário 2: Validação SQL (Banco de Dados)

```
Usuário → [VAL-SQL] → Validator-A (delega) → Validator-A-SQL
                                                    ↓
                                          Validação SQL vs VAMAP
                                                    ↓
                                          Gate G1-SQL: PASS/FAIL
```

**Envolve SQL** → Validator-A delega ao Validator-A-SQL

---

## 📋 Regras de Delegação

### Quando Delegar?

O **Validator-A** delega ao **Validator-A-SQL** quando:

1. ✅ Comando é `[VAL-SQL]`
2. ✅ Validação envolve tabelas/colunas SQL
3. ✅ Confrontação com VAMAP é necessária
4. ✅ Validação de Ledger de Dados (`claim_ledger_sql.json`)
5. ✅ Fechamento do Gate G1-SQL

### Quando NÃO Delegar?

O **Validator-A** processa sozinho quando:

1. ✅ Comando é `[VAL]` (validação geral)
2. ✅ Validação envolve apenas UI/Business Logic
3. ✅ Validação de `claims_A.json` (não SQL)
4. ✅ Fechamento do Gate G1 geral

---

## 🎯 Integração

### Validator-A (agent.yaml)

```yaml
persona:
  identity: |
    ...
    DELEGAÇÃO SQL:
    Para validações específicas de banco de dados (SQL), delega ao especialista validator-a-sql.
    O validator-a-sql é responsável por validar Ledger SQL contra VAMAP e fechar o Gate G1-SQL.

menu:
  - trigger: VAL-SQL or fuzzy match on validar-sql
    exec: "{project-root}/_bmad/migracao-forense-bi/agents/validator-a/validator-a-sql/workflows/validate-sql.md"
    description: "[VAL-SQL] DELEGADO ao validator-a-sql - Validação especializada SQL contra VAMAP (Gate G1-SQL)"
```

### Validator-A-SQL (agent.yaml)

```yaml
persona:
  role: Auditor de Integridade de Dados e Guardião do Gate SQL
  identity: |
    Especialista forense em validação de dados SQL contra gabarito oficial VAMAP.
    Opera como guardião do Gate G1-SQL - última linha de defesa contra alucinações.
    Expertise em validação cruzada: Ledger vs VAMAP vs Evidence Pointers.
    Verifica 100% de grounding: cada claim SQL deve ter prova no VAMAP.
```

---

## 📊 Comparação

| Aspecto | Validator-A | Validator-A-SQL |
|---------|-------------|-----------------|
| **Foco** | UI + Business Logic | SQL + Banco de Dados |
| **Input** | claims_A.json | claim_ledger_sql.json |
| **Validação** | Geral | SQL vs VAMAP |
| **Gate** | G1 (geral) | G1-SQL (SQL) |
| **Output** | validation_report.md | validation_report_sql.md |
| **Grounding** | Geral | SQL específico |
| **VAMAP** | Opcional | Obrigatório |

---

## ✅ Benefícios da Delegação

### 1. Separação de Responsabilidades

Cada agente foca em sua especialidade:
- **Validator-A**: UI e lógica de negócio
- **Validator-A-SQL**: Banco de dados e persistência

### 2. Expertise Especializada

**Validator-A-SQL** tem conhecimento profundo de:
- Validação SQL vs VAMAP
- Type mapping COBOL → SQL
- Grounding Score SQL
- Integridade referencial

### 3. Outputs Isolados

Validações SQL geram outputs separados:
- `run/sql/validation/` (SQL)
- `run/extraction/` (Geral)

### 4. Gates Independentes

Dois gates independentes:
- **G1**: Validação geral (UI + Business Logic)
- **G1-SQL**: Validação SQL (Banco de Dados)

### 5. Manutenibilidade

Mudanças em validação SQL não afetam validação geral, e vice-versa.

---

## 🚀 Exemplo de Uso

### Validação Geral

```bash
[VAL] bi14a.esf
```

**Processamento**:
- Validator-A valida `claims_A.json`
- Gera `run/extraction/validation_report.md`
- Fecha Gate G1 (PASS/FAIL)

---

### Validação SQL

```bash
[VAL-SQL] bi14a.esf
```

**Processamento**:
- Validator-A delega ao Validator-A-SQL
- Validator-A-SQL valida `claim_ledger_sql.json` vs `vamap_sql.log`
- Gera `run/sql/validation/validation_report_sql.md`
- Fecha Gate G1-SQL (PASS/FAIL)

---

## 📚 Documentação

### Validator-A

- **Configuração**: `agents/validator-a/validator-a.agent.yaml`
- **Instruções**: `agents/validator-a/instructions.md`
- **Workflows**: `workflows/validate-extraction/workflow.md`

### Validator-A-SQL

- **Configuração**: `agents/validator-a/validator-a-sql.agent.yaml`
- **Instruções**: `agents/validator-a/validator-a-sql/instructions.md`
- **Workflows**: `agents/validator-a/validator-a-sql/workflows/validate-sql.md`

---

## ✅ Checklist de Integração

- [x] Validator-A atualizado com delegação SQL
- [x] Validator-A-SQL criado
- [x] Workflow [VAL-SQL] delegado
- [x] Outputs SQL isolados em `run/sql/validation/`
- [x] Gate G1-SQL independente
- [x] Documentação completa

---

**Status**: ✅ Delegação implementada com sucesso!

**Validator-A** e **Validator-A-SQL** agora trabalham em harmonia, cada um focado em sua especialidade! 🎯

