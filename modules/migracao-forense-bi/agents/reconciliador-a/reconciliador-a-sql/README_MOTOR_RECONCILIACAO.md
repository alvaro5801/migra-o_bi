# Motor de Reconciliação - Reconciliador-A-SQL

## ✅ Status: OPERACIONAL

O Motor de Reconciliação foi ativado com sucesso no agente **Reconciliador-A-SQL**.

---

## 🎯 O Que Foi Implementado

### 1. Ferramenta de Reconciliação Automatizada
- ✅ Script Python: `tools/reconciliation/reconcile.py`
- ✅ Integrado ao agente via `reconcile_tool`
- ✅ Permissões configuradas para leitura e escrita

### 2. Comando [REC-SQL] Refinado
- ✅ Execução automatizada via script Python
- ✅ Análise inteligente de outputs
- ✅ Resumo de conflitos para o usuário

### 3. Inteligência de Conflitos
- ✅ 10 estratégias de resolução em `conflict-resolution-strategies.csv`
- ✅ 15 regras de matching em `reconciliation-rules.csv`
- ✅ Funções auxiliares para aplicação automática

### 4. Sistema de Status
- ✅ **MATCH**: 100% de concordância
- ✅ **MERGE**: Ajustado automaticamente
- ✅ **CONFLICT**: Exige revisão do Analyzer

---

## 🚀 Como Usar

### Passo 1: Preparar Extrações
Certifique-se de ter os arquivos de entrada:
```
run/sql/extraction/
├── claims_sql_A.json  (Extractor-A-SQL)
└── claims_sql_B.json  (Extractor-B-SQL)
```

### Passo 2: Executar [REC-SQL]
No agente Reconciliador-A-SQL, execute o comando:
```
[REC-SQL]
```

### Passo 3: Verificar Outputs
O agente gerará automaticamente:
```
run/sql/analysis/
└── claim_ledger_sql.json  (Única Fonte da Verdade)

run/sql/validation/
└── diff_report_sql.md     (Relatório Detalhado)
```

---

## 📊 Outputs Gerados

### claim_ledger_sql.json
Inventário consolidado com:
- Metadata (métricas, confidence score)
- Queries reconciliadas
- Status de cada query (MATCH/CONFLICT/HALLUCINATION/OMISSION)
- Resoluções aplicadas

### diff_report_sql.md
Relatório detalhado com:
- Sumário executivo
- Estatísticas de concordância
- Queries em MATCH
- Queries em CONFLICT
- Alucinações detectadas
- Omissões detectadas
- Recomendações

---

## 🧠 Inteligência de Conflitos

### Estratégias Automáticas

| Estratégia | Quando Aplicar | Ação |
|------------|----------------|------|
| STR-001 | Evidence pointers diferentes | Preferir range menor (mais preciso) |
| STR-002 | Contagens diferentes | Preferir contagem maior (mais completo) |
| STR-007 | SQL diferente | Normalizar e comparar (case-insensitive) |
| STR-008 | Tabelas diferentes | Comparar como conjunto (ordem não importa) |

### Regras de Matching

| Regra | Critério | Threshold | Confidence |
|-------|----------|-----------|------------|
| REC-008 | Query SQL Match | 0% | HIGH |
| REC-009 | Query Type Match | 0% | HIGH |
| REC-010 | Query Tables Match | 0% | HIGH |

---

## 📈 Métricas de Qualidade

### Confidence Score
- **≥ 90%**: ✅ Extração de alta qualidade
- **70-89%**: ⚠️ Extração aceitável, revisar
- **< 70%**: 🔴 Extração problemática, refazer

### Status de Reconciliação
- **MATCH**: Extrações idênticas ou diferenças mínimas
- **MERGE**: Conflitos resolvidos automaticamente
- **CONFLICT**: Requer revisão manual

---

## 🧪 Validação da Configuração

Execute o script de teste:
```bash
python bmad-core/src/modules/migracao-forense-bi/agents/reconciliador-a/reconciliador-a-sql/test_motor_reconciliacao.py
```

**Resultado Esperado:**
```
🎉 CONFIGURAÇÃO VÁLIDA - Motor de Reconciliação OPERACIONAL
✅ Pronto para executar primeiro teste de reconciliação!
```

---

## 📁 Arquivos Modificados

### Configuração do Agente
- ✅ `reconciliador-a-sql.agent.yaml` - Adicionado reconcile_tool
- ✅ `instructions.md` - Refinado comando [REC-SQL]

### Documentação
- ✅ `MOTOR_RECONCILIACAO_ATIVADO.md` - Resumo completo
- ✅ `README_MOTOR_RECONCILIACAO.md` - Este arquivo
- ✅ `test_motor_reconciliacao.py` - Script de validação

### Arquivos de Conhecimento (Existentes)
- ✅ `knowledge/conflict-resolution-strategies.csv` - 10 estratégias
- ✅ `knowledge/reconciliation-rules.csv` - 15 regras

---

## 🔧 Troubleshooting

### Problema: Gate bloqueado
**Causa**: Arquivos de entrada não encontrados  
**Solução**: Executar [EXT-SQL] e [EXT-SQL-B] antes de reconciliar

### Problema: Muitos conflitos
**Causa**: Extrações muito divergentes  
**Solução**: 
1. Revisar regras em `reconciliation-rules.csv`
2. Adicionar estratégias em `conflict-resolution-strategies.csv`
3. Verificar qualidade das extrações

### Problema: Confidence Score baixo
**Causa**: Baixa concordância entre A e B  
**Solução**: 
1. Verificar logs das extrações
2. Refazer extrações se necessário
3. Revisar padrões SQL

---

## 📚 Documentação Adicional

- **Arquitetura Completa**: `MOTOR_RECONCILIACAO_ATIVADO.md`
- **Instruções Detalhadas**: `instructions.md`
- **Configuração do Agente**: `reconciliador-a-sql.agent.yaml`

---

## 🎯 Próximos Passos

1. ✅ **Executar Primeiro Teste**
   - Preparar claims_sql_A.json e claims_sql_B.json
   - Executar [REC-SQL]
   - Validar outputs

2. ✅ **Analisar Resultados**
   - Revisar claim_ledger_sql.json
   - Ler diff_report_sql.md
   - Verificar confidence score

3. ✅ **Ajustar Configurações** (se necessário)
   - Adicionar novas estratégias
   - Ajustar thresholds
   - Refinar regras de matching

4. ✅ **Integrar com Analyzer**
   - Configurar Analyzer-A-SQL para consumir ledger
   - Usar como entrada para análise de padrões

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consultar seção Troubleshooting acima
2. Revisar `instructions.md` para detalhes técnicos
3. Executar `test_motor_reconciliacao.py` para validar configuração

---

**Versão**: 2.0  
**Data de Ativação**: 2025-12-28  
**Status**: ✅ OPERACIONAL  
**Pronto para**: Primeiro teste de reconciliação automatizada



