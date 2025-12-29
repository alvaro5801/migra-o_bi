# Migração Forense BI - Módulo BMad

Módulo especializado em migração forense de sistemas legados Visual Age para arquiteturas modernas, com foco em rastreabilidade completa e abordagem Zero-Trust.

## Visão Geral

Este módulo implementa uma metodologia forense para extração, análise e migração de sistemas BI legados escritos em Visual Age (.esf), garantindo que cada afirmação seja respaldada por evidências rastreáveis.

**3 Fases** | **9 Agentes Especializados** | **Rastreabilidade 100%**

## Fases da Migração

### Fase 1: As-Is Forense
Extração e documentação do estado atual do sistema legado com evidências completas.

**Agentes:**
- `ingestor-a` - Preparação forense e invocação do VAMAP (Âncora da Verdade)
- `extractor-a` - Extração Forense Zero-Trust de arquivos .esf
- `extractor-b` - Extração independente para reconciliação
- `validator-a` - Validação de completude, consistência e conformidade VAMAP
- `reconciliador-a` - Reconciliação de extrações múltiplas
- `analyzer-a` - Análise estrutural, dependências e certificação da Fase 1

### Fase 2: To-Be Arquitetura
Design da arquitetura moderna baseado nas evidências coletadas.

**Agentes:**
- `architect-b` - Design de arquitetura moderna
- `mapper-b` - Mapeamento legado → moderno
- `validator-b` - Validação de viabilidade técnica

### Fase 3: Implementação Controlada
Implementação incremental com testes e validação contínua.

**Agentes:**
- `generator-c` - Geração de código moderno
- `tester-c` - Testes automatizados e validação
- `auditor-c` - Auditoria de conformidade e rastreabilidade

## Princípios Zero-Trust

1. **Nada é PROVEN sem evidência** - Cada afirmação deve ter um EvidencePointer
2. **Formato de Evidência Rígido** - `arquivo.esf:Lxxxx-Lyyyy`
3. **VAMAP como Âncora da Verdade** - Validação cruzada IA vs Compilador Oficial
4. **100% Conformidade VAMAP** - Zero tolerância para alucinações ou omissões
5. **Output Estruturado** - JSON padronizado em `run/extraction/`
6. **Rastreabilidade Completa** - Do código legado ao código moderno

## Documentação

Para documentação completa, guias de arquitetura e materiais de referência:

**[→ Documentação do Módulo](./docs/index.md)**

## Links Rápidos

- [Guia de Agentes](./docs/agents/index.md) - Detalhes de cada agente
- [Workflows](./docs/workflows/index.md) - Fluxos de trabalho
- [Exemplos de Referência](./reference/) - Exemplos práticos
- [Integração VAMAP](./INTEGRACAO_VAMAP.md) - Âncora da Verdade (compilador oficial)

### 🆕 Squad SQL - Especialistas em Dados (COMPLETO!)

**[🎉 Squad SQL 100% Completa!](./SQUAD_SQL_COMPLETA.md)** - 6 especialistas focados em banco de dados:

1. **[🔧 Ingestor-A-SQL](./INGESTOR_A_SQL_IMPLEMENTADO.md)** - Preparação e VAMAP SQL
2. **[🔍 Extractor-A-SQL](./EXTRACTOR_A_SQL_IMPLEMENTADO.md)** - Extração SQL (A)
3. **[🔍 Extractor-B-SQL](./EXTRACTOR_B_SQL_IMPLEMENTADO.md)** - Extração SQL (B) - BLIND
4. **[⚖️ Reconciliador-A-SQL](./RECONCILIADOR_A_SQL_IMPLEMENTADO.md)** - Reconciliação A vs B
5. **[🛡️ Validator-A-SQL](./VALIDATOR_A_SQL_IMPLEMENTADO.md)** - Validação vs VAMAP (Gate G1-SQL) ⭐ NOVO!
6. **[🗄️ Analyzer-A-SQL](./RESUMO_ANALYZER_A_SQL.md)** - Análise e DDL

**Documentação**:
- **[🗄️ Trilha SQL](./docs/trilha-sql.md)** - 🎯 Índice Oficial da Soberania SQL
- **[📚 Índice de Navegação](./INDICE_ESPECIALIZACAO_SQL.md)** - Guia completo de navegação
- **[Resumo Final](./RESUMO_FINAL_ESPECIALIZACAO_SQL.md)** - ⭐ Comece aqui!
- [Documentação Completa](./ESPECIALIZACAO_SQL_FASE1.md) - Trilha SQL 100%
- [Resumo Executivo](./RESUMO_ESPECIALIZACAO_SQL.md) - Visão geral
- [Diagrama Visual](./DIAGRAMA_TRILHA_SQL.md) - Fluxo ilustrado
- [Exemplos Práticos](./EXEMPLOS_USO_SQL.md) - Guia de uso
- [Tabela Comparativa](./TABELA_COMPARATIVA_SQL.md) - Antes vs Depois
- [Checklist de Implementação](./CHECKLIST_IMPLEMENTACAO_SQL.md) - Status

## Documentos de Setup

- [SETUP_COMPLETO.md](./SETUP_COMPLETO.md) - Setup do Extractor-A
- [VALIDATOR_A_COMPLETO.md](./VALIDATOR_A_COMPLETO.md) - Setup do Validator-A
- [ANALYZER_A_COMPLETO.md](./ANALYZER_A_COMPLETO.md) - Setup do Analyzer-A
- [INGESTOR_A_COMPLETO.md](./INGESTOR_A_COMPLETO.md) - Setup do Ingestor-A
- [RECONCILIACAO_COMPLETA.md](./RECONCILIACAO_COMPLETA.md) - Setup da Reconciliação
- [INTEGRACAO_VAMAP.md](./INTEGRACAO_VAMAP.md) - Integração VAMAP (Âncora da Verdade)
- [ESPECIALIZACAO_SQL_FASE1.md](./ESPECIALIZACAO_SQL_FASE1.md) - Especialização SQL (Soberania SQL)

---

Parte do [BMad Method](https://github.com/bmadcode/bmad-method) v6.0

