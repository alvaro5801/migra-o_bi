# 🔄 Delegação SQL - Analyzer-A → Analyzer-A-SQL

## Arquitetura de Especialização

O **Analyzer-A** agora delega todas as tarefas de banco de dados para o **Analyzer-A-SQL**, mantendo foco em análise estrutural geral.

---

## Divisão de Responsabilidades

### Analyzer-A (Geral)
**Foco**: Análise estrutural, dependências, taint analysis, complexidade geral

**Responsabilidades**:
- ✅ Análise de lógica de negócio
- ✅ Mapeamento de dependências UI → Logic
- ✅ Taint analysis (zonas de risco)
- ✅ Complexidade ciclomática
- ✅ Chamadas externas
- ✅ Variáveis globais
- ✅ Certificação da Fase 1

**Comandos**:
- `[ANA]` - Análise estrutural geral
- `[MAP]` - Mapa de dependências
- `[RISK]` - Avaliação de risco
- `[CERT]` - Certificação Fase 1

**Outputs**:
- `run/analysis/taint_report.md`
- `run/analysis/dependency_graph.json`
- `run/analysis/complexity_matrix.csv`
- `run/analysis/phase1_certification.json`

---

### Analyzer-A-SQL (Especialista)
**Foco**: Persistência, DDL, linhagem de dados, Entity Framework Core

**Responsabilidades**:
- ✅ Geração de DDL SQL Server moderno
- ✅ Mapeamento de linhagem de dados
- ✅ Identificação de relacionamentos (FKs)
- ✅ Sugestão de índices
- ✅ Mapeamento Entity Framework Core
- ✅ Otimização de queries
- ✅ Análise de complexidade SQL

**Comandos**:
- `[DDL-GEN]` - Gerar database_schema.sql
- `[LINEAGE]` - Mapear linhagem de dados
- `[ANA-SQL]` - Análise completa SQL

**Outputs**:
- `run/sql/analysis/database_schema.sql`
- `run/sql/analysis/data_lineage.csv`
- `run/sql/analysis/complexity_matrix_sql.csv`
- `run/sql/analysis/ef_core_mapping.json`

---

## Fluxo de Delegação

```
┌─────────────────────────────────────────────────────────────────┐
│ ANALYZER-A (Geral)                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input: claims_A.json (completo: UI + SQL + Lógica)            │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │ Análise Estrutural Geral                 │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ • Taint analysis                         │                  │
│  │ • Dependency mapping (UI → Logic)        │                  │
│  │ • Complexity analysis                    │                  │
│  │ • Risk assessment                        │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  Output: taint_report.md, dependency_graph.json                │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │ Delegação SQL                            │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ Se houver claims SQL:                    │                  │
│  │   → Delegar para Analyzer-A-SQL          │                  │
│  │   → Aguardar conclusão                   │                  │
│  │   → Integrar resultados                  │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ ANALYZER-A-SQL (Especialista)                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input: claims_sql_A.json (apenas SQL)                         │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │ Verificar SQL-Gate                       │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ • Carregar gate_status_sql.json          │                  │
│  │ • Se PASS → Continuar                    │                  │
│  │ • Se FAIL → Bloquear                     │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │ Análise SQL Especializada                │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ • Gerar DDL SQL Server moderno           │                  │
│  │ • Mapear linhagem de dados               │                  │
│  │ • Identificar relacionamentos (FKs)      │                  │
│  │ • Sugerir índices                        │                  │
│  │ • Gerar mapeamento EF Core               │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  Output: database_schema.sql, data_lineage.csv, ef_core_mapping│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quando Delegar

### Analyzer-A deve delegar para Analyzer-A-SQL quando:

1. ✅ Comando `[ANA]` é executado E existem claims SQL
2. ✅ Comando `[ANA-SQL]` é explicitamente solicitado
3. ✅ Certificação da Fase 1 requer análise SQL completa

### Analyzer-A NÃO deve delegar quando:

1. ❌ Apenas análise estrutural geral é solicitada
2. ❌ Não existem claims SQL no projeto
3. ❌ SQL-Gate não está PASS

---

## Protocolo de Delegação

### Passo 1: Verificar Necessidade

```python
def should_delegate_to_sql_specialist():
    # Verificar se existem claims SQL
    if not exists("run/sql/extraction/claims_sql_A.json"):
        return False
    
    # Verificar se SQL-Gate está PASS
    gate_status = load_json("run/sql/validation/gate_status_sql.json")
    if gate_status.get("sql_gate_status") != "PASS":
        return False
    
    return True
```

### Passo 2: Executar Delegação

```python
if should_delegate_to_sql_specialist():
    print("🔄 Delegando análise SQL para Analyzer-A-SQL...")
    
    # Invocar Analyzer-A-SQL
    result = invoke_agent("analyzer-a-sql", command="[ANA-SQL]")
    
    if result.status == "SUCCESS":
        print("✅ Análise SQL concluída por Analyzer-A-SQL")
        print(f"   - DDL gerado: {result.outputs['ddl']}")
        print(f"   - Linhagem mapeada: {result.outputs['lineage']}")
    else:
        print("❌ Análise SQL falhou")
        print(f"   Erro: {result.error}")
```

### Passo 3: Integrar Resultados

```python
# Carregar resultados do Analyzer-A-SQL
sql_analysis = {
    "ddl": load_file("run/sql/analysis/database_schema.sql"),
    "lineage": load_csv("run/sql/analysis/data_lineage.csv"),
    "complexity": load_csv("run/sql/analysis/complexity_matrix_sql.csv")
}

# Integrar no relatório geral
taint_report += "\n## Análise SQL\n"
taint_report += f"DDL gerado: {len(sql_analysis['ddl'])} linhas\n"
taint_report += f"Linhagem mapeada: {len(sql_analysis['lineage'])} entradas\n"
taint_report += "\nPara detalhes completos, consulte:\n"
taint_report += "- run/sql/analysis/database_schema.sql\n"
taint_report += "- run/sql/analysis/data_lineage.csv\n"
```

---

## Exemplo de Uso

### Cenário 1: Análise Completa (com SQL)

```bash
# Usuário executa
[ANA] Analisar estrutura

# Analyzer-A executa:
# 1. Análise estrutural geral
# 2. Verifica existência de SQL
# 3. Delega para Analyzer-A-SQL
# 4. Integra resultados
# 5. Gera relatório completo
```

**Output**:
```
✅ Análise estrutural concluída
   - Taint report: run/analysis/taint_report.md
   - Dependency graph: run/analysis/dependency_graph.json

🔄 Delegando análise SQL para Analyzer-A-SQL...

✅ Análise SQL concluída
   - DDL: run/sql/analysis/database_schema.sql (150 linhas)
   - Linhagem: run/sql/analysis/data_lineage.csv (47 entradas)
   - EF Core: run/sql/analysis/ef_core_mapping.json

✅ Análise completa finalizada
```

### Cenário 2: Análise SQL Direta

```bash
# Usuário executa
[ANA-SQL] Analisar SQL

# Analyzer-A-SQL executa diretamente:
# 1. Verifica SQL-Gate PASS
# 2. Gera DDL
# 3. Mapeia linhagem
# 4. Gera mapeamento EF Core
```

**Output**:
```
✅ SQL-Gate: PASS
✅ DDL gerado: run/sql/analysis/database_schema.sql
✅ Linhagem mapeada: run/sql/analysis/data_lineage.csv
✅ EF Core mapping: run/sql/analysis/ef_core_mapping.json
```

---

## Benefícios da Especialização

### 1. Separação de Responsabilidades
- **Analyzer-A**: Foco em estrutura geral
- **Analyzer-A-SQL**: Foco em persistência

### 2. Expertise Dedicada
- SQL Server best practices
- Entity Framework Core
- Otimização de queries
- Modelagem de dados

### 3. Manutenibilidade
- Código mais limpo
- Mais fácil de testar
- Mais fácil de evoluir

### 4. Escalabilidade
- Possibilidade de adicionar mais especialistas
- Analyzer-A-UI (futuro)
- Analyzer-A-Logic (futuro)

---

## Próximos Passos

### Implementar Delegação no Analyzer-A

1. ✅ Criar Analyzer-A-SQL (completo)
2. ⏳ Atualizar Analyzer-A para detectar SQL
3. ⏳ Implementar protocolo de delegação
4. ⏳ Integrar resultados no relatório geral
5. ⏳ Testar fluxo completo

---

**Versão**: 1.0  
**Data**: 2025-12-28  
**Autor**: BMad Method v6.0


