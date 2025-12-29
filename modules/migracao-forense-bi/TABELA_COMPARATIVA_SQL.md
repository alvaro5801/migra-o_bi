# 📊 Tabela Comparativa - Antes vs Depois (Especialização SQL)

## Comparação Completa: Extração Genérica vs Trilha SQL Especializada

---

## 1. Visão Geral

| Aspecto | ANTES (Genérico) | DEPOIS (Especialização SQL) |
|---------|------------------|----------------------------|
| **Abordagem** | Extração única de tudo (UI + SQL + Lógica) | Trilha dedicada 100% SQL |
| **Foco** | Genérico, sem especialização | Cirúrgico, apenas SQL |
| **Validação** | Heurística genérica | Cruzamento IA × VAMAP (DATA DIVISION/SQLCA) |
| **Linhagem** | Difícil rastrear SQL especificamente | Mapeamento completo lógica → query → tabela |
| **Schema** | Não gerado automaticamente | DDL SQL moderno gerado |
| **Riscos SQL** | Não identificados especificamente | SQL dinâmico, mass ops, queries complexas |

---

## 2. Comandos Disponíveis

| Comando | ANTES | DEPOIS |
|---------|-------|--------|
| **Extração** | `[EXT]` - Extrai tudo | `[EXT-SQL]` - Extrai apenas SQL |
| **Validação** | `[VAL]` - Validação genérica | `[VAL-SQL]` - Validação SQL vs VAMAP |
| **Análise** | `[ANA]` - Análise genérica | `[ANA-SQL]` - Análise SQL + Linhagem |

---

## 3. Extração (Extractor-A)

| Aspecto | ANTES | DEPOIS |
|---------|-------|--------|
| **Comando** | `[EXT]` | `[EXT-SQL]` |
| **Foco** | UI + SQL + Lógica (tudo) | Apenas SQL (EXEC SQL, CURSOR, INSERT, UPDATE, DELETE) |
| **Ignora** | Nada (extrai tudo) | UI, Cores, Layouts, Campos de tela |
| **Campos JSON** | `query_id`, `query_type`, `sql_statement`, `evidence_pointer`, `tables_referenced`, `parameters` | + `affected_tables` (lista de tabelas citadas)<br>+ `operation_type` (CRUD) |
| **Output** | `claims_A.json` (genérico) | `claims_A_sql.json` (apenas SQL)<br>`sql_extraction_log.txt`<br>`sql_tables_summary.csv` |
| **Rastreabilidade** | `evidence_pointer` obrigatório | `evidence_pointer` + `affected_tables` obrigatórios |
| **Padrões Detectados** | Genéricos | 30 padrões SQL específicos (sql-patterns-visualage.csv) |

---

## 4. Validação (Validator-A)

| Aspecto | ANTES | DEPOIS |
|---------|-------|--------|
| **Comando** | `[VAL]` | `[VAL-SQL]` |
| **Validação** | Heurística genérica | Cruzamento IA × VAMAP (DATA DIVISION/SQLCA) |
| **Âncora da Verdade** | VAMAP genérico | VAMAP SQL específico (DATA DIVISION/SQLCA) |
| **Detecção** | Alucinações genéricas | Alucinações SQL (IA tem, VAMAP não)<br>Omissões SQL (VAMAP tem, IA não) |
| **Critério PASS** | GroundingScore = 100% | GroundingScore = 100%<br>+ Conformidade SQL = 100%<br>+ Zero omissões SQL<br>+ Zero alucinações SQL |
| **Critério FAIL** | GroundingScore < 100% | GroundingScore < 100%<br>+ Conformidade SQL < 100%<br>+ Omissões SQL > 0<br>+ Alucinações SQL > 0 |
| **Output** | `validation_report.md`<br>`gate_status.json` | + `sql_validation_report.md`<br>+ `sql_gate_status.json`<br>+ `sql_conformance_matrix.csv` (IA × VAMAP) |
| **Regras** | RULE-001 a RULE-021 | + RULE-VAMAP-SQL (cruzamento SQL) |

---

## 5. Análise (Analyzer-A)

| Aspecto | ANTES | DEPOIS |
|---------|-------|--------|
| **Comando** | `[ANA]` | `[ANA-SQL]` |
| **Foco** | Análise estrutural genérica | Análise SQL + Linhagem de dados |
| **Schema SQL** | ❌ Não gerado | ✅ `database_schema.sql` (DDL moderno) |
| **Linhagem** | ❌ Não documentada | ✅ `data_lineage_report.md` (lógica → query → tabela) |
| **Riscos SQL** | ❌ Não identificados | ✅ `sql_risk_matrix.csv` (dinâmico, mass ops, complexas) |
| **Relacionamentos** | Genéricos | ✅ FKs identificadas via JOINs |
| **Output** | `taint_report.md`<br>`dependency_graph.json`<br>`complexity_matrix.csv`<br>`phase1_certification.json` | + `database_schema.sql`<br>+ `data_lineage_report.md`<br>+ `sql_risk_matrix.csv`<br>+ `table_dependencies_graph.json` |
| **Geração DDL** | ❌ Não | ✅ CREATE TABLE, VIEWS, STORED PROCEDURES |
| **Mapeamento** | Genérico | ✅ Qual lógica legado afeta qual tabela |

---

## 6. Base de Conhecimento

| Aspecto | ANTES | DEPOIS |
|---------|-------|--------|
| **Arquivos** | `visual-age-patterns.csv`<br>`extraction-rules.csv`<br>`vamap-standards.csv` | + `sql-patterns-visualage.csv` (30 padrões SQL) |
| **Padrões SQL** | Genéricos | Específicos (EXEC SQL, CURSOR, INSERT, UPDATE, DELETE, etc.) |
| **Classificação** | Não específica | `operation_type` (READ/CREATE/UPDATE/DELETE/EXECUTE) |
| **Riscos** | Genéricos | SQL-específicos (LOW/MEDIUM/HIGH) |

---

## 7. Outputs Gerados

| Output | ANTES | DEPOIS |
|--------|-------|--------|
| **Claims** | `claims_A.json` (genérico) | + `claims_A_sql.json` (apenas SQL) |
| **Logs** | `extraction_log.txt` | + `sql_extraction_log.txt` |
| **Sumários** | Não | + `sql_tables_summary.csv` (tabelas × operações) |
| **Validação** | `validation_report.md`<br>`gate_status.json` | + `sql_validation_report.md`<br>+ `sql_gate_status.json`<br>+ `sql_conformance_matrix.csv` |
| **Schema** | ❌ Não | ✅ `database_schema.sql` (DDL moderno) |
| **Linhagem** | ❌ Não | ✅ `data_lineage_report.md` |
| **Riscos SQL** | ❌ Não | ✅ `sql_risk_matrix.csv` |
| **Dependências** | `dependency_graph.json` (genérico) | + `table_dependencies_graph.json` (SQL) |

---

## 8. Fluxo de Trabalho

| Etapa | ANTES | DEPOIS |
|-------|-------|--------|
| **1. Ingestão** | vamap.exe → vamap_raw.log | vamap.exe → vamap_raw.log (com DATA DIVISION/SQLCA) |
| **2. Extração** | [EXT] → claims_A.json (tudo) | [EXT-SQL] → claims_A_sql.json (apenas SQL) |
| **3. Validação** | [VAL] → gate_status.json (genérico) | [VAL-SQL] → sql_gate_status.json (IA × VAMAP SQL) |
| **4. Análise** | [ANA] → taint_report.md (genérico) | [ANA-SQL] → database_schema.sql + data_lineage_report.md |

---

## 9. Métricas de Qualidade

| Métrica | ANTES | DEPOIS |
|---------|-------|--------|
| **GroundingScore** | 100% (evidências válidas) | 100% (evidências válidas) |
| **Conformidade VAMAP** | Genérica | + Conformidade SQL = 100% |
| **Taxa de Omissão** | Genérica | + Taxa de Omissão SQL = 0% |
| **Taxa de Alucinação** | Genérica | + Taxa de Alucinação SQL = 0% |
| **Queries com affected_tables** | ❌ Não | ✅ 100% |
| **Queries com operation_type** | ❌ Não | ✅ 100% |
| **Schema SQL Gerado** | ❌ Não | ✅ 100% tabelas |
| **Linhagem Documentada** | ❌ Não | ✅ 100% queries |

---

## 10. Benefícios

| Benefício | ANTES | DEPOIS |
|-----------|-------|--------|
| **Foco Cirúrgico** | ❌ Extração genérica mistura UI + SQL | ✅ Trilha dedicada 100% SQL |
| **Validação Autoritativa** | ⚠️ Validação heurística | ✅ Cruzamento IA × VAMAP (DATA DIVISION/SQLCA) |
| **Linhagem de Dados** | ❌ Difícil rastrear | ✅ Mapeamento completo lógica → query → tabela |
| **Schema Moderno** | ❌ Não gerado | ✅ DDL SQL moderno gerado automaticamente |
| **Detecção de Riscos SQL** | ❌ Não identificados | ✅ SQL dinâmico, mass ops, queries complexas |
| **Separação de Soberanias** | ❌ Tudo misturado | ✅ SQL independente de UI/Cores |

---

## 11. Casos de Uso

| Caso de Uso | ANTES | DEPOIS |
|-------------|-------|--------|
| **Extrair apenas SQL** | ❌ Não possível (extrai tudo) | ✅ [EXT-SQL] extrai apenas SQL |
| **Validar tabelas vs VAMAP** | ⚠️ Validação genérica | ✅ [VAL-SQL] cruzamento específico |
| **Gerar schema SQL moderno** | ❌ Não possível | ✅ [ANA-SQL] gera DDL automaticamente |
| **Mapear linhagem de dados** | ❌ Não possível | ✅ [ANA-SQL] documenta linhagem completa |
| **Identificar SQL dinâmico** | ❌ Não detectado | ✅ [ANA-SQL] detecta e classifica como HIGH risk |
| **Detectar mass delete** | ❌ Não detectado | ✅ [ANA-SQL] detecta DELETE sem WHERE |

---

## 12. Documentação

| Documento | ANTES | DEPOIS |
|-----------|-------|--------|
| **Guia de Uso** | README.md genérico | + ESPECIALIZACAO_SQL_FASE1.md (completo) |
| **Resumo Executivo** | Não | + RESUMO_ESPECIALIZACAO_SQL.md |
| **Diagrama Visual** | Não | + DIAGRAMA_TRILHA_SQL.md |
| **Exemplos Práticos** | reference/ genéricos | + EXEMPLOS_USO_SQL.md (5 exemplos) |
| **Checklist** | Não | + CHECKLIST_IMPLEMENTACAO_SQL.md |
| **Tabela Comparativa** | Não | + TABELA_COMPARATIVA_SQL.md (este documento) |

---

## 13. Implementação

| Aspecto | ANTES | DEPOIS |
|---------|-------|--------|
| **Agentes Atualizados** | 3 (genéricos) | 3 (+ comandos SQL especializados) |
| **Instruções Atualizadas** | 3 (genéricas) | 3 (+ seções SQL) |
| **Base de Conhecimento** | 3 arquivos | + 1 arquivo (sql-patterns-visualage.csv) |
| **Documentação** | 1 README | + 6 documentos SQL |
| **Status** | ✅ Implementado | ✅ Implementado + Especializado |

---

## 14. Próximos Passos

| Categoria | ANTES | DEPOIS |
|-----------|-------|--------|
| **Workflows Executáveis** | ⏳ Pendente | ⏳ Pendente (mesma prioridade) |
| **Parsers** | ⏳ Pendente | ⏳ Pendente + Parsers SQL específicos |
| **Geradores** | ⏳ Pendente | ⏳ Pendente + Geradores SQL específicos |
| **Dashboard** | 📅 Planejado | 📅 Planejado + Dashboard SQL |
| **Testes** | ⏳ Pendente | ⏳ Pendente + Testes SQL específicos |

---

## 15. Resumo Visual

### ANTES (Extração Genérica)

```
┌──────────────────────────────────────┐
│ [EXT] Extrair TUDO                   │
│ • UI + SQL + Lógica (misturado)      │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ [VAL] Validar (heurística)           │
│ • Sem cruzamento SQL específico      │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ [ANA] Analisar (genérico)            │
│ • Sem schema SQL                     │
│ • Sem linhagem de dados              │
└──────────────────────────────────────┘
```

### DEPOIS (Trilha SQL Especializada)

```
┌──────────────────────────────────────┐
│ [EXT-SQL] Extrair APENAS SQL         │
│ • Ignora UI/Cores                    │
│ • affected_tables + operation_type   │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ [VAL-SQL] Validar IA × VAMAP         │
│ • Cruzamento DATA DIVISION/SQLCA     │
│ • Detecta omissões e alucinações     │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ [ANA-SQL] Analisar SQL + Linhagem    │
│ • database_schema.sql (DDL moderno)  │
│ • data_lineage_report.md (linhagem)  │
│ • sql_risk_matrix.csv (riscos)       │
└──────────────────────────────────────┘
```

---

## 🎯 Conclusão

A **Especialização SQL** adiciona uma **trilha dedicada 100% Banco de Dados** à Fase 1, com:

| Aspecto | Melhoria |
|---------|----------|
| **Foco** | ✅ Cirúrgico (apenas SQL) |
| **Validação** | ✅ Autoritativa (IA × VAMAP SQL) |
| **Linhagem** | ✅ Completa (lógica → query → tabela) |
| **Schema** | ✅ Moderno (DDL gerado) |
| **Riscos** | ✅ Identificados (dinâmico, mass ops) |
| **Separação** | ✅ Soberania SQL independente |

**Resultado**: Migração SQL com **tripla garantia** (IA + VAMAP + Linhagem) e **zero tolerância** para omissões ou alucinações.

---

**Versão**: 1.0  
**Data**: 2025-12-28  
**Autor**: BMad Method v6.0


