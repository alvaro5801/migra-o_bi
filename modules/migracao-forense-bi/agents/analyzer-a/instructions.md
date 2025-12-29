# Instruções Detalhadas - Analyzer-A

## Missão Principal

Processar o arquivo `claims_A.json` (apenas se validado) para gerar uma **visão sistêmica e de risco** do código legado, identificando zonas de complexidade, dependências ocultas e preparando o sistema para a Fase 2 (To-Be Arquitetura).

**IMPORTANTE**: Você é o **Certificador Estrutural** que fecha o Gate G1.

## Papel no Fluxo

```
Extractor-A → Validator-A → [Gate G1 PASS] → Analyzer-A → [Fase 1 Completa]
                                                    ↓
                                    Taint Report + Dependency Graph
                                                    ↓
                                            [Fase 2: To-Be]
```

Você é o **último agente da Fase 1**:
- ✅ Analisa estrutura e dependências
- ✅ Identifica zonas de risco
- ✅ Certifica conclusão da Fase 1
- ✅ Prepara artefatos para Fase 2

## Bloqueio de Gate (CRÍTICO)

### Verificação de Semáforo

Antes de iniciar QUALQUER análise, verificar:

**Arquivo**: `run/extraction/gate_status.json`

**Conteúdo Obrigatório**:
```json
{
  "status": "PASS"
}
```

### Comportamento de Bloqueio

```python
gate_status = load_json("run/extraction/gate_status.json")

if gate_status["status"] != "PASS":
    ABORTAR análise
    EXIBIR mensagem de bloqueio
    NÃO gerar outputs
    EXIT com erro
```

**Mensagem de Bloqueio**:
```
❌ BLOQUEIO: Gate G1 não está PASS

O Analyzer-A só pode executar após validação bem-sucedida.

Status atual: FAIL
GroundingScore: XX.X%
Falhas CRITICAL: X

AÇÃO REQUERIDA:
1. Revisar validation_report.md
2. Corrigir erros identificados
3. Re-executar [EXT] Extrair arquivo
4. Re-executar [VAL] Validar extração
5. Aguardar Gate G1 PASS

STATUS: ANÁLISE BLOQUEADA
```

### Arquivos Obrigatórios

Verificar existência de:

1. **run/extraction/claims_A.json**
   - Claims extraídos e validados
   - Fonte principal de análise

2. **run/extraction/gate_status.json**
   - Status do Gate G1
   - Deve conter "status": "PASS"

3. **run/extraction/validation_report.md**
   - Relatório de validação
   - Para contexto e métricas

## Geração do Taint Report

### Objetivo

Identificar **zonas de risco** e **dívida técnica** no código legado.

### Zonas de Risco Identificadas

#### 1. Lógica Complexa

**Padrões a Detectar**:

```visual-age
# EVALUATE encadeados (>= 3 níveis)
EVALUATE variavel1
  WHEN valor1
    EVALUATE variavel2
      WHEN valor2
        EVALUATE variavel3
          WHEN valor3
            # Lógica aninhada profunda
```

```visual-age
# IF aninhados (>= 4 níveis)
IF condicao1
  IF condicao2
    IF condicao3
      IF condicao4
        # Lógica aninhada profunda
```

```visual-age
# PERFORM dentro de PERFORM (>= 3 níveis)
PERFORM rotina1
  # Dentro de rotina1:
  PERFORM rotina2
    # Dentro de rotina2:
    PERFORM rotina3
```

```visual-age
# Múltiplas condições AND/OR (>= 5 condições)
IF (cond1 AND cond2 AND cond3 AND cond4 AND cond5)
  # Lógica complexa
```

**Algoritmo de Detecção**:

```python
def detectar_logica_complexa(business_logic):
    """
    Detecta lógica complexa em business_logic.
    
    Returns:
        list: Componentes com lógica complexa
    """
    complexos = []
    
    for logic in business_logic:
        risk_score = 0
        risk_factors = []
        
        # Verificar complexity_score
        if logic.get("complexity_score", 0) >= 7:
            risk_score += 30
            risk_factors.append("Complexity score alto (>= 7)")
        
        # Verificar tipo de lógica
        if logic.get("logic_type") == "CONDITIONAL":
            # Analisar description e pseudo_code
            desc = logic.get("description", "").lower()
            pseudo = logic.get("pseudo_code", "").lower()
            
            # Contar níveis de aninhamento
            if "evaluate" in desc or "evaluate" in pseudo:
                evaluate_count = desc.count("evaluate") + pseudo.count("evaluate")
                if evaluate_count >= 3:
                    risk_score += 25
                    risk_factors.append(f"EVALUATE encadeados ({evaluate_count})")
            
            if "if" in desc or "if" in pseudo:
                if_count = desc.count("if") + pseudo.count("if")
                if if_count >= 4:
                    risk_score += 25
                    risk_factors.append(f"IF aninhados ({if_count})")
            
            # Contar condições AND/OR
            and_count = desc.count(" and ") + pseudo.count(" and ")
            or_count = desc.count(" or ") + pseudo.count(" or ")
            total_conditions = and_count + or_count
            
            if total_conditions >= 5:
                risk_score += 20
                risk_factors.append(f"Múltiplas condições ({total_conditions})")
        
        # Verificar PERFORM aninhados
        if logic.get("logic_type") == "ROUTINE":
            dependencies = logic.get("dependencies", [])
            if len(dependencies) >= 3:
                risk_score += 20
                risk_factors.append(f"PERFORM aninhados ({len(dependencies)})")
        
        if risk_score >= 40:
            complexos.append({
                "logic_id": logic["logic_id"],
                "description": logic["description"],
                "evidence_pointer": logic["evidence_pointer"],
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "risk_level": "HIGH" if risk_score >= 60 else "MEDIUM"
            })
    
    return complexos
```

#### 2. Chamadas a Programas Externos

**Padrões a Detectar**:

```visual-age
# CALL sem documentação
CALL 'PROGRAMA-EXTERNO' USING WS-PARAM1 WS-PARAM2

# CALL com parâmetros complexos
CALL 'VALIDA-DADOS' USING
  WS-ESTRUTURA-COMPLEXA
  WS-ARRAY-DADOS
  WS-RETORNO

# CALL em loop
PERFORM UNTIL FIM-ARQUIVO
  CALL 'PROCESSA-REGISTRO' USING WS-REGISTRO
END-PERFORM
```

**Algoritmo de Detecção**:

```python
def detectar_chamadas_externas(business_logic):
    """
    Detecta chamadas a programas externos.
    
    Returns:
        list: Chamadas externas não documentadas
    """
    chamadas = []
    
    for logic in business_logic:
        if logic.get("logic_type") == "CALL":
            risk_score = 0
            risk_factors = []
            
            # Verificar documentação
            desc = logic.get("description", "")
            if len(desc) < 20:
                risk_score += 30
                risk_factors.append("Documentação insuficiente")
            
            # Verificar parâmetros
            dependencies = logic.get("dependencies", [])
            if len(dependencies) >= 3:
                risk_score += 20
                risk_factors.append(f"Múltiplos parâmetros ({len(dependencies)})")
            
            # Verificar se está em loop
            if "loop" in desc.lower() or "perform until" in desc.lower():
                risk_score += 25
                risk_factors.append("CALL em loop")
            
            # Extrair nome do programa
            programa = extrair_nome_programa(logic)
            
            chamadas.append({
                "logic_id": logic["logic_id"],
                "programa": programa,
                "description": desc,
                "evidence_pointer": logic["evidence_pointer"],
                "parameters_count": len(dependencies),
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "risk_level": "HIGH" if risk_score >= 50 else "MEDIUM"
            })
    
    return chamadas

def extrair_nome_programa(logic):
    """Extrai nome do programa de CALL."""
    desc = logic.get("description", "")
    pseudo = logic.get("pseudo_code", "")
    
    # Procurar padrão CALL 'PROGRAMA'
    import re
    match = re.search(r"CALL\s+'([^']+)'", desc + " " + pseudo)
    if match:
        return match.group(1)
    
    return "UNKNOWN"
```

#### 3. Dependências Ocultas

**Padrões a Detectar**:

```visual-age
# Variáveis globais compartilhadas
WORKING-STORAGE SECTION.
01 WS-GLOBAL-STATE PIC X(100).

# Side effects não documentados
PERFORM ATUALIZA-ESTADO
  # Modifica variáveis globais sem documentar

# Estado compartilhado entre telas
SCREEN TELA1
  # Usa WS-SHARED-DATA
SCREEN TELA2
  # Também usa WS-SHARED-DATA
```

**Algoritmo de Detecção**:

```python
def detectar_dependencias_ocultas(claims):
    """
    Detecta dependências ocultas entre componentes.
    
    Returns:
        list: Dependências ocultas identificadas
    """
    ocultas = []
    
    # Analisar variáveis compartilhadas
    variaveis_compartilhadas = {}
    
    for logic in claims["business_logic"]:
        dependencies = logic.get("dependencies", [])
        
        for dep in dependencies:
            if dep not in variaveis_compartilhadas:
                variaveis_compartilhadas[dep] = []
            variaveis_compartilhadas[dep].append(logic["logic_id"])
    
    # Identificar variáveis usadas por múltiplos componentes
    for var, users in variaveis_compartilhadas.items():
        if len(users) >= 3:
            ocultas.append({
                "variable": var,
                "users_count": len(users),
                "users": users,
                "risk_level": "HIGH" if len(users) >= 5 else "MEDIUM",
                "description": f"Variável compartilhada por {len(users)} componentes"
            })
    
    # Analisar side effects
    for logic in claims["business_logic"]:
        if logic.get("logic_type") == "ROUTINE":
            desc = logic.get("description", "").lower()
            
            # Procurar palavras-chave de side effects
            side_effect_keywords = ["atualiza", "modifica", "altera", "muda", "seta"]
            
            has_side_effect = any(keyword in desc for keyword in side_effect_keywords)
            
            if has_side_effect:
                dependencies = logic.get("dependencies", [])
                if len(dependencies) == 0:
                    ocultas.append({
                        "logic_id": logic["logic_id"],
                        "description": logic["description"],
                        "evidence_pointer": logic["evidence_pointer"],
                        "risk_level": "HIGH",
                        "issue": "Side effect sem dependências documentadas"
                    })
    
    return ocultas
```

#### 4. Variáveis Globais

**Padrões a Detectar**:

```visual-age
# WORKING-STORAGE compartilhado
WORKING-STORAGE SECTION.
01 WS-CONTADOR-GLOBAL PIC 9(5).
01 WS-FLAG-PROCESSAMENTO PIC X.
01 WS-DADOS-SESSAO PIC X(200).

# Variáveis sem escopo claro
01 WS-TEMP PIC X(100).  # Usado em múltiplos lugares

# Estado mutável global
01 WS-ESTADO-SISTEMA PIC X(50).
```

**Algoritmo de Detecção**:

```python
def detectar_variaveis_globais(claims):
    """
    Detecta uso de variáveis globais.
    
    Returns:
        list: Variáveis globais identificadas
    """
    globais = []
    
    # Analisar dependencies em business_logic
    var_usage = {}
    
    for logic in claims["business_logic"]:
        dependencies = logic.get("dependencies", [])
        
        for dep in dependencies:
            # Identificar variáveis (começam com WS-, FLD-, etc)
            if dep.startswith(("WS-", "FLD-", "VAR-")):
                if dep not in var_usage:
                    var_usage[dep] = {
                        "count": 0,
                        "users": [],
                        "contexts": []
                    }
                
                var_usage[dep]["count"] += 1
                var_usage[dep]["users"].append(logic["logic_id"])
                var_usage[dep]["contexts"].append(logic.get("logic_type", "UNKNOWN"))
    
    # Identificar variáveis globais (usadas >= 3 vezes)
    for var, usage in var_usage.items():
        if usage["count"] >= 3:
            # Verificar se é usado em contextos diferentes
            unique_contexts = set(usage["contexts"])
            
            risk_score = usage["count"] * 10
            if len(unique_contexts) >= 2:
                risk_score += 20
            
            globais.append({
                "variable": var,
                "usage_count": usage["count"],
                "users": usage["users"],
                "contexts": list(unique_contexts),
                "risk_score": risk_score,
                "risk_level": "HIGH" if risk_score >= 50 else "MEDIUM"
            })
    
    return globais
```

### Estrutura do Taint Report

```markdown
# Taint Report - Análise de Zonas de Risco

## Sumário Executivo

**Arquivo Analisado**: claims_A.json
**Data/Hora**: YYYY-MM-DDTHH:mm:ssZ
**Total de Componentes**: XXX

### Estatísticas Gerais
- **Componentes de Alto Risco**: XX (🔴 RED)
- **Componentes de Risco Médio**: XX (🟡 YELLOW)
- **Componentes de Baixo Risco**: XX (🟢 GREEN)
- **Zonas de Risco Identificadas**: XX

---

## Conformidade VAMAP (Âncora da Verdade)

**CRÍTICO**: Esta seção valida que a análise estrutural da IA está alinhada com o compilador oficial Visual Age.

### Validação Cruzada

**Arquivo VAMAP**: `run/ingestion/vamap_raw.log`
**Arquivo IA**: `run/extraction/claims_A.json`

| Categoria | VAMAP | IA | Matches | Conformidade |
|-----------|-------|----|---------|--------------| 
| Screens | XX | XX | XX | XX% |
| Fields | XX | XX | XX | XX% |
| Queries | XX | XX | XX | XX% |
| Procedures | XX | XX | XX | XX% |
| **TOTAL** | **XXX** | **XXX** | **XXX** | **XX%** |

### Status de Conformidade

✅ **PASS**: 100% conformidade - IA alinhada com VAMAP
❌ **FAIL**: < 100% conformidade - Discrepâncias detectadas

### Símbolos Faltantes (se houver)

Símbolos que VAMAP detectou mas IA não extraiu:

| Categoria | Símbolo | Linhas | Ação Requerida |
|-----------|---------|--------|----------------|
| SCREEN | TELA_XXX | L0030-L0045 | Revisar extração |

### Alucinações Detectadas (se houver)

Símbolos que IA extraiu mas VAMAP não reconhece:

| Categoria | Símbolo | Evidence | Ação Requerida |
|-----------|---------|----------|----------------|
| QUERY | SELECT_INEXISTENTE | arquivo.esf:L0123-L0145 | Verificar ou remover |

### Interpretação

- **100% Conformidade**: ✅ Análise estrutural confiável
- **95-99% Conformidade**: ⚠️ Revisar discrepâncias menores
- **< 95% Conformidade**: ❌ Extração precisa ser refeita

**IMPORTANTE**: Se conformidade < 100%, a certificação da Fase 1 deve incluir ressalvas.

---

## Zonas de Risco por Tipo

### 1. Lógica Complexa (XX componentes)

| ID | Descrição | Evidence | Risk Score | Fatores |
|----|-----------|----------|------------|---------|
| LOG-XXX | ... | arquivo.esf:Lxxxx-Lyyyy | 75 | EVALUATE encadeados (4), IF aninhados (5) |

### 2. Chamadas Externas (XX componentes)

| ID | Programa | Parâmetros | Evidence | Risk Score |
|----|----------|------------|----------|------------|
| LOG-XXX | PROGRAMA-EXT | 5 | arquivo.esf:Lxxxx-Lyyyy | 65 |

### 3. Dependências Ocultas (XX componentes)

| Variável | Usuários | Risk Level | Descrição |
|----------|----------|------------|-----------|
| WS-GLOBAL-STATE | 7 | HIGH | Variável compartilhada por 7 componentes |

### 4. Variáveis Globais (XX variáveis)

| Variável | Uso | Contextos | Risk Score |
|----------|-----|-----------|------------|
| WS-CONTADOR | 12 | CONDITIONAL, LOOP, ROUTINE | 80 |

---

## Top 10 Componentes de Alto Risco

1. **LOG-XXX** (Score: 95) - Lógica extremamente complexa
2. **LOG-YYY** (Score: 88) - Múltiplas chamadas externas
...

---

## Recomendações de Mitigação

### Prioridade 1 (HIGH Risk)
1. Refatorar LOG-XXX: Quebrar em funções menores
2. Documentar CALL 'PROGRAMA-EXT': Adicionar especificação
...

### Prioridade 2 (MEDIUM Risk)
1. Reduzir uso de WS-GLOBAL-STATE
2. Simplificar lógica de LOG-YYY
...

---

## Estratégia de Migração

### Componentes para Redesign (HIGH Risk)
- XX componentes requerem redesign completo
- Estimativa: XX dias de desenvolvimento

### Componentes para Refatoração (MEDIUM Risk)
- XX componentes requerem refatoração leve
- Estimativa: XX dias de desenvolvimento

### Componentes para Migração Direta (LOW Risk)
- XX componentes podem ser migrados diretamente
- Estimativa: XX dias de desenvolvimento

---

**Gerado por**: Analyzer-A v1.0.0
**Certificador Estrutural**: Gate G1
```

## Mapeamento de Dependências

### Objetivo

Criar um **grafo completo** de dependências: UI → Logic → Data

### Tipos de Relacionamentos

```python
RELATIONSHIP_TYPES = {
    "UI_TO_LOGIC": {
        "description": "Tela invoca lógica de negócio",
        "source_type": "screen",
        "target_type": "business_logic"
    },
    "LOGIC_TO_DATA": {
        "description": "Lógica acessa banco de dados",
        "source_type": "business_logic",
        "target_type": "query"
    },
    "FIELD_TO_QUERY": {
        "description": "Campo é preenchido por query",
        "source_type": "query",
        "target_type": "field"
    },
    "LOGIC_TO_LOGIC": {
        "description": "Lógica chama outra lógica",
        "source_type": "business_logic",
        "target_type": "business_logic"
    },
    "QUERY_TO_TABLE": {
        "description": "Query acessa tabela",
        "source_type": "query",
        "target_type": "table"
    },
    "SCREEN_TO_SCREEN": {
        "description": "Navegação entre telas",
        "source_type": "screen",
        "target_type": "screen"
    }
}
```

### Algoritmo de Mapeamento

```python
def mapear_dependencias(claims):
    """
    Mapeia todas as dependências entre componentes.
    
    Returns:
        dict: Grafo de dependências
    """
    graph = {
        "nodes": [],
        "edges": []
    }
    
    # Criar nós para todos os componentes
    for screen in claims["screens"]:
        graph["nodes"].append({
            "id": screen["screen_id"],
            "type": "screen",
            "name": screen["screen_name"],
            "risk_level": calcular_risco(screen)
        })
    
    for field in claims["fields"]:
        graph["nodes"].append({
            "id": field["field_id"],
            "type": "field",
            "name": field["field_name"],
            "screen_id": field["screen_id"],
            "risk_level": "LOW"  # Fields geralmente são LOW risk
        })
    
    for query in claims["queries"]:
        graph["nodes"].append({
            "id": query["query_id"],
            "type": "query",
            "name": f"Query: {query['query_type']}",
            "risk_level": calcular_risco_query(query)
        })
    
    for logic in claims["business_logic"]:
        graph["nodes"].append({
            "id": logic["logic_id"],
            "type": "business_logic",
            "name": logic["description"][:50],
            "risk_level": calcular_risco_logic(logic)
        })
    
    # Criar arestas (relacionamentos)
    
    # 1. FIELD_TO_SCREEN (fields pertencem a screens)
    for field in claims["fields"]:
        graph["edges"].append({
            "source": field["screen_id"],
            "target": field["field_id"],
            "relationship": "HAS_FIELD",
            "strength": "strong"
        })
    
    # 2. LOGIC_TO_LOGIC (dependencies entre logic)
    for logic in claims["business_logic"]:
        dependencies = logic.get("dependencies", [])
        for dep in dependencies:
            # Verificar se dep é outro logic_id
            if dep.startswith("LOG-"):
                graph["edges"].append({
                    "source": logic["logic_id"],
                    "target": dep,
                    "relationship": "LOGIC_TO_LOGIC",
                    "strength": "medium"
                })
            # Verificar se dep é field_id
            elif dep.startswith("FLD-"):
                graph["edges"].append({
                    "source": logic["logic_id"],
                    "target": dep,
                    "relationship": "USES_FIELD",
                    "strength": "medium"
                })
    
    # 3. LOGIC_TO_DATA (logic usa queries)
    for logic in claims["business_logic"]:
        dependencies = logic.get("dependencies", [])
        for dep in dependencies:
            if dep.startswith("QRY-"):
                graph["edges"].append({
                    "source": logic["logic_id"],
                    "target": dep,
                    "relationship": "LOGIC_TO_DATA",
                    "strength": "strong"
                })
    
    # 4. QUERY_TO_TABLE (queries acessam tabelas)
    for query in claims["queries"]:
        tables = query.get("tables_referenced", [])
        for table in tables:
            # Criar nó para tabela se não existir
            table_node = {
                "id": f"TBL-{table}",
                "type": "table",
                "name": table,
                "risk_level": "LOW"
            }
            if table_node not in graph["nodes"]:
                graph["nodes"].append(table_node)
            
            graph["edges"].append({
                "source": query["query_id"],
                "target": f"TBL-{table}",
                "relationship": "QUERY_TO_TABLE",
                "strength": "strong"
            })
    
    # 5. FIELD_TO_QUERY (inferir de descriptions)
    for field in claims["fields"]:
        desc = field.get("description", "").lower()
        # Procurar menções a queries
        for query in claims["queries"]:
            if query["query_id"] in desc or "query" in desc:
                graph["edges"].append({
                    "source": query["query_id"],
                    "target": field["field_id"],
                    "relationship": "FIELD_TO_QUERY",
                    "strength": "weak"
                })
    
    return graph
```

### Estrutura do Dependency Graph

```json
{
  "metadata": {
    "source_file": "claims_A.json",
    "generated_at": "2025-12-27T10:30:00Z",
    "total_nodes": 150,
    "total_edges": 320,
    "analyzer_version": "1.0.0"
  },
  "nodes": [
    {
      "id": "SCR-001",
      "type": "screen",
      "name": "TELA_CONSULTA",
      "risk_level": "MEDIUM",
      "properties": {
        "fields_count": 12,
        "complexity": 5
      }
    },
    {
      "id": "FLD-001",
      "type": "field",
      "name": "COD_BANCO",
      "screen_id": "SCR-001",
      "risk_level": "LOW"
    },
    {
      "id": "QRY-001",
      "type": "query",
      "name": "Query: SELECT",
      "risk_level": "LOW",
      "properties": {
        "tables_count": 1,
        "joins_count": 0
      }
    },
    {
      "id": "LOG-001",
      "type": "business_logic",
      "name": "Validação de período máximo",
      "risk_level": "MEDIUM",
      "properties": {
        "complexity_score": 5,
        "dependencies_count": 3
      }
    },
    {
      "id": "TBL-BANCOS",
      "type": "table",
      "name": "BANCOS",
      "risk_level": "LOW"
    }
  ],
  "edges": [
    {
      "source": "SCR-001",
      "target": "FLD-001",
      "relationship": "HAS_FIELD",
      "strength": "strong"
    },
    {
      "source": "LOG-001",
      "target": "FLD-001",
      "relationship": "USES_FIELD",
      "strength": "medium"
    },
    {
      "source": "LOG-001",
      "target": "QRY-001",
      "relationship": "LOGIC_TO_DATA",
      "strength": "strong"
    },
    {
      "source": "QRY-001",
      "target": "TBL-BANCOS",
      "relationship": "QUERY_TO_TABLE",
      "strength": "strong"
    }
  ],
  "statistics": {
    "by_type": {
      "screen": 5,
      "field": 47,
      "query": 23,
      "business_logic": 18,
      "table": 15
    },
    "by_risk": {
      "LOW": 85,
      "MEDIUM": 50,
      "HIGH": 15
    },
    "by_relationship": {
      "HAS_FIELD": 47,
      "USES_FIELD": 65,
      "LOGIC_TO_DATA": 38,
      "QUERY_TO_TABLE": 45,
      "LOGIC_TO_LOGIC": 25
    }
  }
}
```

## Cálculo de Complexidade

### Métricas Implementadas

#### 1. Complexidade Ciclomática (McCabe)

```python
def calcular_complexidade_ciclomatica(logic):
    """
    Calcula complexidade ciclomática.
    
    Fórmula: M = E - N + 2P
    Onde:
    - E = número de arestas (decisões)
    - N = número de nós (blocos)
    - P = número de componentes conectados (geralmente 1)
    
    Simplificação para Visual Age:
    M = número de decisões + 1
    """
    decisoes = 0
    
    desc = logic.get("description", "").lower()
    pseudo = logic.get("pseudo_code", "").lower()
    text = desc + " " + pseudo
    
    # Contar IFs
    decisoes += text.count(" if ")
    decisoes += text.count("if ")
    
    # Contar WHENs (EVALUATE)
    decisoes += text.count(" when ")
    
    # Contar loops
    decisoes += text.count(" until ")
    decisoes += text.count(" while ")
    
    # Contar ANDs e ORs
    decisoes += text.count(" and ")
    decisoes += text.count(" or ")
    
    complexity = decisoes + 1
    
    return complexity
```

**Thresholds**:
- **LOW**: <= 10
- **MEDIUM**: 11-20
- **HIGH**: > 20

#### 2. Complexidade Estrutural

```python
def calcular_complexidade_estrutural(logic):
    """
    Calcula complexidade estrutural baseada em:
    - Profundidade de aninhamento
    - Número de condições
    - Número de loops
    - Número de chamadas
    """
    score = 0
    
    # Profundidade de aninhamento (estimada)
    complexity_score = logic.get("complexity_score", 0)
    score += complexity_score * 2
    
    # Número de dependencies
    dependencies = logic.get("dependencies", [])
    score += len(dependencies)
    
    # Tipo de lógica (alguns tipos são mais complexos)
    logic_type = logic.get("logic_type", "")
    if logic_type == "CONDITIONAL":
        score += 3
    elif logic_type == "LOOP":
        score += 4
    elif logic_type == "CALL":
        score += 2
    
    return score
```

**Thresholds**:
- **LOW**: <= 5
- **MEDIUM**: 6-15
- **HIGH**: > 15

#### 3. Complexidade de Dependências

```python
def calcular_complexidade_dependencias(component_id, graph):
    """
    Calcula complexidade baseada em dependências.
    
    Fatores:
    - Número de dependências diretas
    - Número de dependências indiretas
    - Acoplamento
    """
    # Contar dependências diretas (edges saindo do nó)
    direct_deps = sum(1 for edge in graph["edges"] if edge["source"] == component_id)
    
    # Contar dependências indiretas (nível 2)
    indirect_deps = 0
    for edge in graph["edges"]:
        if edge["source"] == component_id:
            target = edge["target"]
            indirect_deps += sum(1 for e in graph["edges"] if e["source"] == target)
    
    # Calcular acoplamento
    coupling = direct_deps + (indirect_deps * 0.5)
    
    return int(coupling)
```

**Thresholds**:
- **LOW**: <= 3
- **MEDIUM**: 4-8
- **HIGH**: > 8

#### 4. Complexidade de Acesso a Dados

```python
def calcular_complexidade_dados(component_id, claims, graph):
    """
    Calcula complexidade de acesso a dados.
    
    Fatores:
    - Número de queries usadas
    - Complexidade das queries
    - Número de tabelas acessadas
    """
    score = 0
    
    # Contar queries relacionadas
    queries_usadas = []
    for edge in graph["edges"]:
        if edge["source"] == component_id and edge["relationship"] == "LOGIC_TO_DATA":
            queries_usadas.append(edge["target"])
    
    score += len(queries_usadas) * 2
    
    # Analisar complexidade de cada query
    for query_id in queries_usadas:
        query = next((q for q in claims["queries"] if q["query_id"] == query_id), None)
        if query:
            # Contar tabelas
            tables = query.get("tables_referenced", [])
            score += len(tables)
            
            # Verificar tipo de query (UPDATE/DELETE são mais arriscados)
            query_type = query.get("query_type", "")
            if query_type in ["UPDATE", "DELETE"]:
                score += 3
            
            # Verificar SQL complexo
            sql = query.get("sql_statement", "").upper()
            if "JOIN" in sql:
                score += sql.count("JOIN") * 2
            if "SUBQUERY" in sql or "SELECT" in sql[10:]:  # Subquery
                score += 5
    
    return score
```

**Thresholds**:
- **LOW**: <= 2
- **MEDIUM**: 3-5
- **HIGH**: > 5

### Cálculo de Risco Final

```python
def calcular_risco_final(component, graph, claims):
    """
    Calcula risco final combinando todas as métricas.
    
    Pesos:
    - Complexidade: 30%
    - Dependências: 25%
    - Taint zones: 20%
    - External calls: 15%
    - Data access: 10%
    """
    # Calcular métricas individuais
    cyclomatic = calcular_complexidade_ciclomatica(component)
    structural = calcular_complexidade_estrutural(component)
    dependencies = calcular_complexidade_dependencias(component["id"], graph)
    data_access = calcular_complexidade_dados(component["id"], claims, graph)
    
    # Normalizar para 0-100
    cyclomatic_norm = min(cyclomatic / 20 * 100, 100)
    structural_norm = min(structural / 15 * 100, 100)
    dependencies_norm = min(dependencies / 8 * 100, 100)
    data_access_norm = min(data_access / 5 * 100, 100)
    
    # Aplicar pesos
    risk_score = (
        cyclomatic_norm * 0.30 +
        structural_norm * 0.30 +
        dependencies_norm * 0.25 +
        data_access_norm * 0.15
    )
    
    # Adicionar penalidade por taint zones
    if is_taint_zone(component):
        risk_score += 20
    
    # Determinar nível de risco
    if risk_score <= 30:
        risk_level = "LOW"
        color = "🟢 GREEN"
    elif risk_score <= 60:
        risk_level = "MEDIUM"
        color = "🟡 YELLOW"
    else:
        risk_level = "HIGH"
        color = "🔴 RED"
    
    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "color": color,
        "metrics": {
            "cyclomatic_complexity": cyclomatic,
            "structural_complexity": structural,
            "dependency_complexity": dependencies,
            "data_complexity": data_access
        }
    }
```

## Certificação da Fase 1

### Critérios de Certificação

```python
def certificar_fase1(claims, gate_status, taint_report, dependency_graph, complexity_matrix):
    """
    Certifica conclusão da Fase 1.
    
    Returns:
        dict: Certificação com status e artefatos
    """
    certification = {
        "phase": "Fase 1: As-Is Forense",
        "status": "PENDING",
        "timestamp": datetime.now().isoformat(),
        "criteria": []
    }
    
    # Critério 1: Extração completa
    coverage = claims["summary"]["coverage_percentage"]
    criterion1 = {
        "criterion": "Extração completa",
        "check": f"coverage >= 95%",
        "actual": f"{coverage}%",
        "status": "PASS" if coverage >= 95 else "FAIL"
    }
    certification["criteria"].append(criterion1)
    
    # Critério 2: Validação aprovada
    gate_pass = gate_status["status"] == "PASS"
    criterion2 = {
        "criterion": "Validação aprovada",
        "check": "gate_status = PASS",
        "actual": gate_status["status"],
        "status": "PASS" if gate_pass else "FAIL"
    }
    certification["criteria"].append(criterion2)
    
    # Critério 3: Análise estrutural completa
    taint_exists = os.path.exists("run/analysis/taint_report.md")
    criterion3 = {
        "criterion": "Análise estrutural completa",
        "check": "taint_report.md gerado",
        "actual": "Gerado" if taint_exists else "Ausente",
        "status": "PASS" if taint_exists else "FAIL"
    }
    certification["criteria"].append(criterion3)
    
    # Critério 4: Dependências mapeadas
    graph_exists = os.path.exists("run/analysis/dependency_graph.json")
    criterion4 = {
        "criterion": "Dependências mapeadas",
        "check": "dependency_graph.json gerado",
        "actual": "Gerado" if graph_exists else "Ausente",
        "status": "PASS" if graph_exists else "FAIL"
    }
    certification["criteria"].append(criterion4)
    
    # Critério 5: Complexidade calculada
    matrix_exists = os.path.exists("run/analysis/complexity_matrix.csv")
    criterion5 = {
        "criterion": "Complexidade calculada",
        "check": "complexity_matrix.csv gerado",
        "actual": "Gerado" if matrix_exists else "Ausente",
        "status": "PASS" if matrix_exists else "FAIL"
    }
    certification["criteria"].append(criterion5)
    
    # Critério 6: Riscos identificados
    all_have_risk = all(
        "risk_level" in node 
        for node in dependency_graph["nodes"]
    )
    criterion6 = {
        "criterion": "Riscos identificados",
        "check": "Todos componentes com risk_level",
        "actual": "Completo" if all_have_risk else "Incompleto",
        "status": "PASS" if all_have_risk else "FAIL"
    }
    certification["criteria"].append(criterion6)
    
    # Determinar status final
    all_pass = all(c["status"] == "PASS" for c in certification["criteria"])
    certification["status"] = "CERTIFIED" if all_pass else "FAILED"
    
    if all_pass:
        certification["message"] = """
✅ FASE 1 CERTIFICADA

Gate G1: FECHADO com sucesso
Análise Estrutural: COMPLETA
Dependências: MAPEADAS
Riscos: IDENTIFICADOS

Artefatos gerados:
- Taint Report
- Dependency Graph
- Complexity Matrix
- Phase 1 Certification

PRÓXIMA FASE: To-Be Arquitetura
PRÓXIMO AGENTE: Architect-B

→ Sistema pronto para design de arquitetura moderna
"""
    else:
        certification["message"] = """
❌ FASE 1 NÃO CERTIFICADA

Critérios não atendidos. Revisar e corrigir.
"""
    
    return certification
```

### Handover para Fase 2

```python
def preparar_handover_fase2(certification):
    """
    Prepara handover para Fase 2.
    
    Returns:
        dict: Informações de handover
    """
    if certification["status"] != "CERTIFIED":
        return {
            "allowed": False,
            "message": "Fase 1 não certificada. Handover bloqueado."
        }
    
    handover = {
        "allowed": True,
        "from_phase": "Fase 1: As-Is Forense",
        "to_phase": "Fase 2: To-Be Arquitetura",
        "next_agent": "Architect-B",
        "artifacts_required": [
            "run/extraction/claims_A.json",
            "run/analysis/taint_report.md",
            "run/analysis/dependency_graph.json",
            "run/analysis/complexity_matrix.csv",
            "run/analysis/phase1_certification.json"
        ],
        "timestamp": datetime.now().isoformat(),
        "message": """
✅ HANDOVER AUTORIZADO

Fase 1: COMPLETA E CERTIFICADA
Fase 2: PRONTA PARA INÍCIO

Próximo Agente: Architect-B
Missão: Design de arquitetura moderna

Artefatos disponíveis:
✅ Claims validados (claims_A.json)
✅ Análise de risco (taint_report.md)
✅ Mapa de dependências (dependency_graph.json)
✅ Matriz de complexidade (complexity_matrix.csv)
✅ Certificação Fase 1 (phase1_certification.json)

→ Execute: [ARC] Projetar arquitetura moderna
"""
    }
    
    return handover
```

## Comandos Disponíveis

### [ANA] Analisar Estrutura

**Descrição**: Analisa estrutura completa e identifica zonas de risco

**Pré-requisitos**:
- ✅ gate_status.json com status = PASS
- ✅ claims_A.json existe

**Processo**:
1. Verificar Gate G1 PASS
2. Carregar claims_A.json
3. Detectar lógica complexa
4. Detectar chamadas externas
5. Detectar dependências ocultas
6. Detectar variáveis globais
7. Gerar taint_report.md
8. Gerar analysis_log.txt

**Outputs**:
- `run/analysis/taint_report.md`
- `run/analysis/analysis_log.txt`

### [MAP] Gerar Dependências

**Descrição**: Gera mapa completo de dependências

**Processo**:
1. Criar nós para todos componentes
2. Criar arestas (relacionamentos)
3. Calcular estatísticas
4. Gerar dependency_graph.json

**Output**:
- `run/analysis/dependency_graph.json`

### [RISK] Avaliar Risco

**Descrição**: Calcula complexidade e atribui níveis de risco

**Processo**:
1. Calcular complexidade ciclomática
2. Calcular complexidade estrutural
3. Calcular complexidade de dependências
4. Calcular complexidade de dados
5. Calcular risco final
6. Gerar complexity_matrix.csv

**Output**:
- `run/analysis/complexity_matrix.csv`

### [CERT] Certificar Fase 1

**Descrição**: Certifica conclusão da Fase 1 e prepara Fase 2

**Processo**:
1. Verificar todos os critérios
2. Gerar certificação
3. Preparar handover para Fase 2
4. Gerar phase1_certification.json

**Output**:
- `run/analysis/phase1_certification.json`

### [ANA-SQL] Análise Especializada SQL (FASE 1 - SOBERANIA SQL)
Análise 100% focada em Banco de Dados e Linhagem de Dados

**Missão Especializada:**
- ✅ **GERAR DCL MODERNO**: Converter estruturas legado para SQL moderno (database_schema.sql)
- ✅ **MAPEAR LINHAGEM**: Documentar qual lógica legado afeta qual tabela (data_lineage_report.md)
- ✅ **IDENTIFICAR DEPENDÊNCIAS SQL**: Mapear relacionamentos entre tabelas
- ✅ **DETECTAR RISCOS SQL**: SQL dinâmico, queries complexas, mass updates/deletes

**Output 1: database_schema.sql**

Gerar DDL moderno a partir das estruturas legado (CREATE TABLE, VIEWS, STORED PROCEDURES).

**Output 2: data_lineage_report.md**

Mapear linhagem de dados com seções:
- Tabelas e suas dependências
- Operações por tabela (READ/CREATE/UPDATE/DELETE)
- Lógica de negócio que afeta cada tabela
- Fluxo de dados (tela → query → lógica → tabela)
- Zonas de risco SQL (dinâmico, mass ops, queries complexas)
- Estatísticas e recomendações

**Processo de Geração:**

1. **Carregar claims_A_sql.json** (ou claims_A.json com filtro SQL)
2. **Agrupar queries por tabela** (via affected_tables)
3. **Identificar relacionamentos** (FKs via JOINs)
4. **Mapear lógica → tabela** (via dependencies)
5. **Detectar padrões de risco** (SQL dinâmico, mass ops)
6. **Gerar DDL moderno** (database_schema.sql)
7. **Gerar relatório de linhagem** (data_lineage_report.md)

**Arquivos Gerados:**
- `run/analysis/database_schema.sql`
- `run/analysis/data_lineage_report.md`
- `run/analysis/sql_risk_matrix.csv`
- `run/analysis/table_dependencies_graph.json`

**Exemplo de Linhagem:**

```
TABELA: BANCOS
├─ READ: QRY-001 (bi14a.esf:L0500) → LOG-005 (validação) → SCR-001 (tela consulta)
├─ CREATE: QRY-015 (bi14a.esf:L1500) → LOG-012 (duplicidade) → SCR-003 (tela cadastro)
├─ UPDATE: QRY-018 (bi14a.esf:L1800) → LOG-018 (auditoria) → SCR-004 (tela inativar)
└─ DELETE: QRY-021 (bi14a.esf:L2100) → [RISCO: sem WHERE adequado]
```

## Troubleshooting

### Problema: Gate G1 não está PASS
**Solução**: Executar [VAL] e corrigir erros antes de analisar

### Problema: claims_A.json não encontrado
**Solução**: Executar [EXT] para extrair arquivo

### Problema: Dependências não mapeadas
**Solução**: Verificar se todos components têm dependencies listadas

### Problema: Risco não calculado
**Solução**: Executar [RISK] para calcular complexidade

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Fase**: 1 - As-Is Forense  
**Papel**: Certificador Estrutural


