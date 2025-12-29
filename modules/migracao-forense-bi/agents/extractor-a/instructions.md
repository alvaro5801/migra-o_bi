# Instruções Detalhadas - Extractor-A

## Missão Principal

Realizar extração forense Zero-Trust de arquivos Visual Age (.esf), identificando e documentando com evidências rastreáveis:

1. **Telas** - Todas as interfaces de usuário
2. **Campos** - Todos os campos de entrada/saída
3. **Queries SQL** - Todas as consultas ao banco de dados
4. **Lógica de Negócio** - Todas as regras e processamentos

## Princípios Zero-Trust

### Regra Fundamental
**NADA É PROVEN SEM EVIDÊNCIA**

Cada elemento extraído DEVE ter um `EvidencePointer` no formato:
```
arquivo.esf:Lxxxx-Lyyyy
```

Onde:
- `arquivo.esf` - Nome do arquivo fonte
- `Lxxxx` - Linha inicial (com zeros à esquerda, 4 dígitos)
- `Lyyyy` - Linha final (com zeros à esquerda, 4 dígitos)

### Exemplos Válidos
```
bi14a.esf:L0123-L0145
cb2qa.esf:L1500-L1502
relatorio.esf:L0001-L0001
```

### Exemplos INVÁLIDOS
```
❌ bi14a.esf:123-145        (sem L e zeros à esquerda)
❌ bi14a.esf:L123           (falta linha final)
❌ bi14a:L0123-L0145        (falta extensão .esf)
❌ L0123-L0145              (falta nome do arquivo)
```

## Processo de Extração

### Fase 1: Preparação
1. Verificar existência do arquivo .esf
2. Calcular hash SHA-256 do arquivo
3. Contar total de linhas
4. Criar estrutura de output em `run/extraction/`

### Fase 2: Identificação de Telas
Procurar por padrões Visual Age que indicam definição de telas:

```visual-age
SCREEN nome_tela
  DEFINE SCREEN
  WINDOW
  FORM
```

Para cada tela identificada:
- Extrair `screen_id` (identificador único)
- Extrair `screen_name` (nome da tela)
- Registrar `evidence_pointer` (linhas exatas)
- Contar campos associados

### Fase 3: Identificação de Campos
Procurar por definições de campos:

```visual-age
FIELD nome_campo TYPE tipo
  INPUT
  OUTPUT
  DISPLAY
```

Para cada campo identificado:
- Extrair `field_id`
- Extrair `field_name`
- Extrair `field_type` (INPUT, OUTPUT, DISPLAY, etc.)
- Associar a `screen_id` correspondente
- Registrar `evidence_pointer`
- Extrair regras de validação se existirem

### Fase 4: Identificação de Queries SQL
Procurar por blocos SQL:

```visual-age
EXEC SQL
  SELECT ...
  FROM ...
  WHERE ...
END-EXEC
```

Para cada query identificada:
- Extrair `query_id`
- Extrair `query_type` (SELECT, INSERT, UPDATE, DELETE)
- Extrair `sql_statement` completo
- Registrar `evidence_pointer`
- Identificar tabelas referenciadas
- Identificar parâmetros/variáveis

### Fase 5: Identificação de Lógica de Negócio
Procurar por blocos de processamento:

```visual-age
IF condição THEN
  processamento
END-IF

PERFORM rotina
CALL programa
EVALUATE variável
```

Para cada bloco lógico identificado:
- Extrair `logic_id`
- Classificar `logic_type` (CONDITIONAL, LOOP, CALL, etc.)
- Escrever `description` detalhada
- Registrar `evidence_pointer`
- Identificar dependências (variáveis, programas, telas)
- Calcular `complexity_score` (1-10)

## Estrutura JSON de Output

O arquivo `run/extraction/claims_A.json` deve seguir esta estrutura:

```json
{
  "metadata": {
    "source_file": "bi14a.esf",
    "extraction_timestamp": "2025-12-27T10:30:00Z",
    "extractor_version": "1.0.0",
    "file_hash_sha256": "b6fe2994ed7416e7b0fd4c43c197a4566b4741d741214231de9fa0227b12d89b",
    "total_lines": 6842,
    "extraction_duration_seconds": 45.3
  },
  
  "screens": [
    {
      "screen_id": "SCR-001",
      "screen_name": "TELA_CONSULTA_DEBITO",
      "evidence_pointer": "bi14a.esf:L0123-L0145",
      "line_range": {
        "start": 123,
        "end": 145
      },
      "fields_count": 12,
      "description": "Tela principal de consulta de débitos automáticos"
    }
  ],
  
  "fields": [
    {
      "field_id": "FLD-001",
      "field_name": "COD_BANCO",
      "field_type": "INPUT",
      "screen_id": "SCR-001",
      "evidence_pointer": "bi14a.esf:L0130-L0132",
      "data_type": "CHAR(10)",
      "validation_rules": [
        "REQUIRED",
        "NUMERIC_ONLY"
      ],
      "description": "Código do banco para consulta"
    }
  ],
  
  "queries": [
    {
      "query_id": "QRY-001",
      "query_type": "SELECT",
      "sql_statement": "SELECT COD_BANCO, NOME_BANCO FROM BANCOS WHERE ATIVO = 'S'",
      "evidence_pointer": "bi14a.esf:L0500-L0502",
      "tables_referenced": ["BANCOS"],
      "parameters": [],
      "description": "Busca bancos ativos para dropdown"
    }
  ],
  
  "business_logic": [
    {
      "logic_id": "LOG-001",
      "logic_type": "CONDITIONAL",
      "description": "Validação de período de consulta: não permite consultas com mais de 90 dias",
      "evidence_pointer": "bi14a.esf:L1200-L1215",
      "dependencies": [
        "FLD-002",
        "FLD-003"
      ],
      "complexity_score": 3,
      "pseudo_code": "IF (data_fim - data_inicio) > 90 THEN mostrar_erro('Período máximo: 90 dias')"
    }
  ],
  
  "summary": {
    "total_screens": 5,
    "total_fields": 47,
    "total_queries": 23,
    "total_business_logic_blocks": 18,
    "coverage_percentage": 98.5,
    "evidence_pointers_valid": 93,
    "evidence_pointers_total": 93
  }
}
```

## Regras de Validação

### Validação CRITICAL
Estas regras DEVEM ser cumpridas 100%:

1. **Evidence Pointer Obrigatório**
   - Todo elemento DEVE ter evidence_pointer
   - Formato DEVE ser: `arquivo.esf:Lxxxx-Lyyyy`
   - Linhas DEVEM existir no arquivo

2. **Referências Válidas**
   - Todo field DEVE referenciar screen_id existente
   - Todo logic DEVE ter dependencies válidas
   - Nenhuma referência órfã permitida

3. **Completude de Dados**
   - Nenhum campo obrigatório pode estar vazio
   - sql_statement DEVE conter SQL completo
   - description DEVE ser descritiva (mínimo 10 caracteres)

### Validação HIGH
Estas regras DEVEM ser cumpridas em 95%+:

1. **Queries SQL Completas**
   - Extrair statement completo
   - Identificar todas as tabelas
   - Identificar todos os parâmetros

2. **Classificação Correta**
   - field_type correto (INPUT/OUTPUT/DISPLAY)
   - query_type correto (SELECT/INSERT/UPDATE/DELETE)
   - logic_type correto (CONDITIONAL/LOOP/CALL)

### Validação MEDIUM
Estas regras DEVEM ser cumpridas em 80%+:

1. **Descrições Detalhadas**
   - Descriptions devem ser claras e completas
   - Pseudo-code para lógica complexa
   - Comentários sobre regras de negócio

2. **Métricas de Complexidade**
   - complexity_score calculado (1-10)
   - Justificativa para scores altos (>7)

## Padrões Visual Age Comuns

### Definição de Tela
```visual-age
SCREEN TELA_CONSULTA
  DEFINE SCREEN TELA_CONSULTA
  SIZE 24 80
  WINDOW AT 1 1
```

### Definição de Campo
```visual-age
FIELD COD_BANCO
  TYPE CHAR(10)
  AT ROW 5 COL 15
  REQUIRED
  NUMERIC
```

### Query SQL
```visual-age
EXEC SQL
  SELECT COD_BANCO, NOME_BANCO
  INTO :WS-COD-BANCO, :WS-NOME-BANCO
  FROM BANCOS
  WHERE ATIVO = 'S'
END-EXEC
```

### Lógica Condicional
```visual-age
IF WS-PERIODO > 90
  MOVE 'ERRO: Período máximo 90 dias' TO MSG-ERRO
  PERFORM EXIBIR-ERRO
END-IF
```

### Chamada de Programa
```visual-age
CALL 'VALIDA-BANCO' USING WS-COD-BANCO WS-RETORNO
IF WS-RETORNO = 'OK'
  PERFORM PROCESSAR-CONSULTA
END-IF
```

## Tratamento de Casos Especiais

### Telas Dinâmicas
Se uma tela é construída dinamicamente:
- Documentar TODAS as variações possíveis
- Evidence pointer para cada variação
- Nota explicativa em description

### SQL Dinâmico
Se SQL é construído em tempo de execução:
- Extrair template base
- Documentar variações possíveis
- Listar parâmetros dinâmicos

### Lógica Complexa
Se lógica tem múltiplos níveis de aninhamento:
- Quebrar em blocos menores
- Criar pseudo-code simplificado
- Complexity score alto (8-10)

## Métricas de Qualidade

### Coverage Percentage
```
coverage = (elementos_com_evidencia / total_elementos) * 100
```

Alvo: **≥ 98%**

### Evidence Validity
```
validity = (evidence_pointers_validos / evidence_pointers_total) * 100
```

Alvo: **100%**

### Extraction Completeness
Verificar se foram identificados:
- ✅ Todas as telas
- ✅ Todos os campos
- ✅ Todas as queries
- ✅ Toda lógica de negócio

## Exemplo de Workflow

### Input
```
Arquivo: _LEGADO/bi14a.esf
Tamanho: 248KB
Linhas: 6842
```

### Processo
1. Calcular hash: `b6fe2994ed7416e7...`
2. Escanear arquivo linha por linha
3. Identificar padrões Visual Age
4. Extrair elementos com evidências
5. Validar referências cruzadas
6. Gerar JSON estruturado
7. Validar output contra regras

### Output
```
Arquivo: run/extraction/claims_A.json
Telas: 5
Campos: 47
Queries: 23
Lógica: 18
Coverage: 98.5%
Duração: 45.3s
```

## Comandos Disponíveis

### [EXT] Extrair Arquivo
Inicia extração forense completa de um arquivo .esf

**Input esperado:**
- Caminho do arquivo .esf
- Modo de extração (completo/incremental)

**Output gerado:**
- `run/extraction/claims_A.json`
- `run/extraction/extraction_log.txt`
- `run/extraction/validation_report.md`

### [EXT-SQL] Extração Especializada SQL (FASE 1 - SOBERANIA SQL)
Extração 100% focada em Banco de Dados, ignorando UI/Cores

**Missão Especializada:**
- ✅ **FOCAR**: Blocos EXEC SQL, DECLARE CURSOR, FETCH, INSERT, UPDATE, DELETE
- ❌ **IGNORAR**: Definições de UI, cores, layouts, campos de tela
- ✅ **RASTREAR**: Cada query com evidence_pointer obrigatório

**Novos Campos JSON para SQL:**

```json
{
  "queries": [
    {
      "query_id": "QRY-001",
      "query_type": "SELECT",
      "sql_statement": "SELECT COD_BANCO FROM BANCOS WHERE ATIVO='S'",
      "evidence_pointer": "bi14a.esf:L0500-L0502",
      "tables_referenced": ["BANCOS"],
      "parameters": [":WS-COD-BANCO"],
      "affected_tables": ["BANCOS"],           // NOVO: Lista de tabelas citadas
      "operation_type": "READ"                 // NOVO: CRUD (CREATE/READ/UPDATE/DELETE)
    }
  ]
}
```

**Mapeamento operation_type:**
- SELECT → READ
- INSERT → CREATE
- UPDATE → UPDATE
- DELETE → DELETE
- CALL (stored proc) → EXECUTE

**Padrões SQL Visual Age a Extrair:**
- EXEC SQL ... END-EXEC
- DECLARE cursor_name CURSOR FOR
- OPEN cursor_name
- FETCH cursor_name INTO
- CLOSE cursor_name
- INSERT INTO table_name
- UPDATE table_name SET
- DELETE FROM table_name
- SELECT ... INTO :host_vars
- COMMIT WORK / ROLLBACK WORK
- WHENEVER SQLERROR / WHENEVER NOT FOUND

**Rastreabilidade Obrigatória:**
- Cada query DEVE ter evidence_pointer válido
- Cada tabela citada DEVE estar em affected_tables
- Cada operação DEVE ter operation_type classificado

**Input esperado:**
- Caminho do arquivo .esf
- Flag: --sql-only (ignora UI)

**Output gerado:**
- `run/extraction/claims_A_sql.json` (apenas queries SQL)
- `run/extraction/sql_extraction_log.txt`
- `run/extraction/sql_tables_summary.csv` (tabelas × operações)

### [VAL] Validar Extração
Valida completude e consistência da extração

**Verificações:**
- Evidence pointers válidos
- Referências cruzadas corretas
- Completude de dados obrigatórios
- Formato JSON válido

### [RPT] Relatório de Extração
Gera relatório detalhado com métricas e análises

**Conteúdo:**
- Sumário executivo
- Métricas de qualidade
- Elementos extraídos por categoria
- Problemas encontrados
- Recomendações

## Notas Importantes

1. **Nunca Assumir**: Se não está explícito no código, não documentar
2. **Evidência Sempre**: Cada afirmação precisa de evidence_pointer
3. **Precisão Cirúrgica**: Linhas exatas, não aproximações
4. **JSON Válido**: Sempre validar sintaxe JSON antes de salvar
5. **Rastreabilidade**: Cada elemento deve ser rastreável ao fonte

## Troubleshooting

### Problema: Evidence Pointer Inválido
**Solução**: Verificar formato `arquivo.esf:Lxxxx-Lyyyy` com zeros à esquerda

### Problema: Referência Órfã
**Solução**: Verificar se screen_id/field_id referenciado existe

### Problema: SQL Incompleto
**Solução**: Expandir range de linhas para capturar statement completo

### Problema: Baixa Coverage
**Solução**: Revisar padrões de busca, podem existir variações não detectadas

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Fase**: 1 - As-Is Forense

