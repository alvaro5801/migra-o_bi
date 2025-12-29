# Workflow: Análise Estrutural e Identificação de Riscos

## Metadata
- **ID**: analyze-structure
- **Agente**: Analyzer-A
- **Fase**: 1 - As-Is Forense
- **Gate**: G1 - Certificador Estrutural
- **Duração Estimada**: 10-30 segundos
- **Complexidade**: Alta

## Objetivo

Analisar estrutura completa do código legado, identificar zonas de risco, mapear dependências e certificar conclusão da Fase 1.

## Pré-requisitos

- [x] Gate G1 está PASS
- [x] `run/extraction/gate_status.json` com status = "PASS"
- [x] `run/extraction/claims_A.json` existe
- [x] `run/extraction/validation_report.md` existe

## Inputs

1. **gate_status.json** (obrigatório)
2. **claims_A.json** (obrigatório)
3. **validation_report.md** (contexto)

## Outputs

1. **taint_report.md** - Relatório de zonas de risco
2. **dependency_graph.json** - Mapa de dependências
3. **complexity_matrix.csv** - Matriz de complexidade
4. **analysis_log.txt** - Log de operações
5. **phase1_certification.json** - Certificação da Fase 1

## Processo

### Passo 1: Verificação de Gate (BLOQUEIO)
**Duração**: < 1 segundo

```markdown
1. Verificar existência de run/extraction/gate_status.json
2. Carregar JSON
3. Verificar se status = "PASS"

SE status != "PASS":
  - ABORTAR análise
  - Exibir mensagem de bloqueio
  - EXIT com erro
```

**Mensagem de Bloqueio**:
```
❌ BLOQUEIO: Gate G1 não está PASS

Status atual: FAIL
GroundingScore: XX.X%

AÇÃO REQUERIDA:
1. Executar [VAL] Validar extração
2. Corrigir erros
3. Aguardar Gate G1 PASS

STATUS: ANÁLISE BLOQUEADA
```

### Passo 2: Carregamento de Claims
**Duração**: 1-2 segundos

```markdown
1. Carregar run/extraction/claims_A.json
2. Validar estrutura
3. Extrair componentes (screens, fields, queries, business_logic)
```

### Passo 3: Detecção de Lógica Complexa
**Duração**: 3-5 segundos

```markdown
Para cada business_logic:
  1. Analisar complexity_score
  2. Detectar EVALUATE encadeados (>= 3)
  3. Detectar IF aninhados (>= 4)
  4. Detectar PERFORM recursivos (>= 3)
  5. Contar condições AND/OR (>= 5)
  6. Calcular risk_score
  7. Atribuir risk_level (LOW/MEDIUM/HIGH)
```

**Output Parcial**: Lista de componentes com lógica complexa

### Passo 4: Detecção de Chamadas Externas
**Duração**: 2-3 segundos

```markdown
Para cada business_logic tipo CALL:
  1. Extrair nome do programa
  2. Verificar documentação (length description)
  3. Contar parâmetros
  4. Verificar se está em loop
  5. Calcular risk_score
```

**Output Parcial**: Lista de chamadas externas não documentadas

### Passo 5: Detecção de Dependências Ocultas
**Duração**: 3-5 segundos

```markdown
1. Analisar dependencies compartilhadas
2. Identificar variáveis usadas por >= 3 componentes
3. Detectar side effects não documentados
4. Identificar estado compartilhado entre telas
```

**Output Parcial**: Lista de dependências ocultas

### Passo 6: Detecção de Variáveis Globais
**Duração**: 2-3 segundos

```markdown
1. Analisar uso de variáveis WS-
2. Contar uso por componente
3. Identificar variáveis usadas >= 5 vezes
4. Verificar contextos de uso
```

**Output Parcial**: Lista de variáveis globais

### Passo 7: Mapeamento de Dependências
**Duração**: 5-10 segundos

```markdown
1. Criar nós para todos componentes
2. Criar arestas (relacionamentos):
   - UI_TO_LOGIC
   - LOGIC_TO_DATA
   - FIELD_TO_QUERY
   - LOGIC_TO_LOGIC
   - QUERY_TO_TABLE
3. Calcular estatísticas
```

**Output**: dependency_graph.json

### Passo 8: Cálculo de Complexidade
**Duração**: 5-8 segundos

```markdown
Para cada componente:
  1. Calcular complexidade ciclomática
  2. Calcular complexidade estrutural
  3. Calcular complexidade de dependências
  4. Calcular complexidade de dados
  5. Calcular risco final (weighted)
  6. Atribuir risk_level
```

**Output**: complexity_matrix.csv

### Passo 9: Geração de Taint Report
**Duração**: 2-3 segundos

```markdown
1. Consolidar todas as zonas de risco
2. Gerar estatísticas gerais
3. Identificar Top 10 componentes de alto risco
4. Gerar recomendações de mitigação
5. Definir estratégia de migração
6. Salvar taint_report.md
```

**Output**: taint_report.md

### Passo 10: Certificação da Fase 1
**Duração**: 1-2 segundos

```markdown
1. Verificar critérios de certificação:
   - Extração completa (coverage >= 95%)
   - Validação aprovada (gate_status = PASS)
   - Análise estrutural completa (taint_report.md)
   - Dependências mapeadas (dependency_graph.json)
   - Complexidade calculada (complexity_matrix.csv)
   - Riscos identificados (todos com risk_level)

2. Gerar certificação
3. Preparar handover para Fase 2
4. Salvar phase1_certification.json
```

**Output**: phase1_certification.json

## Exemplo de Execução

### Input
```bash
[ANA] Analisar estrutura
```

### Processo
```
[00:00] 🔍 Verificando Gate G1...
[00:00] ✅ Gate G1: PASS
[00:01] 📊 Carregando claims_A.json...
[00:01] ✅ 93 componentes carregados
[00:02] 🔬 Detectando lógica complexa...
[00:05] ⚠️  15 componentes com lógica complexa
[00:06] 📞 Detectando chamadas externas...
[00:08] ⚠️  8 chamadas não documentadas
[00:09] 🔗 Detectando dependências ocultas...
[00:12] ⚠️  5 dependências ocultas
[00:13] 🌐 Detectando variáveis globais...
[00:15] ⚠️  12 variáveis globais
[00:16] 🗺️  Mapeando dependências...
[00:22] ✅ 150 nós, 320 arestas
[00:23] 🧮 Calculando complexidade...
[00:28] ✅ Complexidade calculada
[00:29] 📝 Gerando taint_report.md...
[00:31] ✅ Taint report gerado
[00:32] 🎓 Certificando Fase 1...
[00:33] ✅ FASE 1 CERTIFICADA
[00:33] ✅ Análise completa!
```

### Output
```
✅ ANÁLISE ESTRUTURAL COMPLETA

Componentes analisados: 93
Zonas de risco: 40
  - HIGH: 15 (🔴)
  - MEDIUM: 18 (🟡)
  - LOW: 7 (🟢)

Dependências mapeadas: 320
Complexidade média: 45.2

Artefatos gerados:
✅ run/analysis/taint_report.md
✅ run/analysis/dependency_graph.json
✅ run/analysis/complexity_matrix.csv
✅ run/analysis/analysis_log.txt
✅ run/analysis/phase1_certification.json

🎓 FASE 1 CERTIFICADA
→ Pronto para Fase 2: To-Be Arquitetura
→ Próximo agente: Architect-B
```

## Próximos Passos

### Se Certificado
1. ✅ Fase 1 completa
2. ✅ Gate G1 fechado
3. → Execute: **[ARC] Projetar arquitetura moderna** (Fase 2)

### Se Não Certificado
1. ❌ Revisar critérios não atendidos
2. ❌ Corrigir problemas
3. ❌ Re-executar análise

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Agente**: Analyzer-A


