# Workflow: Extração Forense Visual Age

## Metadata
- **ID**: extract-visual-age
- **Agente**: Extractor-A
- **Fase**: 1 - As-Is Forense
- **Duração Estimada**: 5-15 minutos por arquivo
- **Complexidade**: Alta

## Objetivo

Realizar extração forense completa de um arquivo Visual Age (.esf), identificando e documentando com evidências rastreáveis todos os elementos do sistema: telas, campos, queries SQL e lógica de negócio.

## Pré-requisitos

- [ ] Arquivo .esf disponível em `_LEGADO/`
- [ ] Pasta `run/extraction/` criada
- [ ] Permissões de leitura no arquivo fonte
- [ ] Permissões de escrita em `run/`

## Inputs

1. **Arquivo Fonte**
   - Caminho: `_LEGADO/[nome].esf`
   - Formato: Visual Age source file
   - Encoding: UTF-8 ou EBCDIC

2. **Modo de Extração**
   - `completo`: Extrai todos os elementos
   - `incremental`: Extrai apenas mudanças desde última extração

3. **Nível de Detalhe**
   - `básico`: Apenas estrutura principal
   - `completo`: Todos os detalhes e dependências
   - `forense`: Máximo detalhe + validações extras

## Outputs

1. **claims_A.json**
   - Caminho: `run/extraction/claims_A.json`
   - Formato: JSON estruturado
   - Conteúdo: Todos elementos extraídos com evidências

2. **extraction_log.txt**
   - Caminho: `run/extraction/extraction_log.txt`
   - Formato: Texto plano
   - Conteúdo: Log detalhado do processo

3. **validation_report.md**
   - Caminho: `run/extraction/validation_report.md`
   - Formato: Markdown
   - Conteúdo: Relatório de validação e métricas

## Processo

### Passo 1: Preparação
**Duração**: 30 segundos

```markdown
1. Verificar existência do arquivo fonte
2. Calcular hash SHA-256 do arquivo
3. Contar total de linhas
4. Criar estrutura de output
5. Inicializar log de extração
```

**Validações**:
- ✅ Arquivo existe e é legível
- ✅ Hash calculado com sucesso
- ✅ Pasta de output criada

### Passo 2: Extração de Telas
**Duração**: 1-3 minutos

```markdown
1. Escanear arquivo procurando padrão SCREEN
2. Para cada tela encontrada:
   a. Extrair screen_id e screen_name
   b. Registrar evidence_pointer (linhas exatas)
   c. Identificar campos associados
   d. Extrair descrição se disponível
3. Validar completude das telas
```

**Padrões Buscados**:
- `SCREEN nome_tela`
- `DEFINE SCREEN nome`
- `WINDOW AT linha coluna`

**Output Parcial**:
```json
{
  "screens": [
    {
      "screen_id": "SCR-001",
      "screen_name": "TELA_CONSULTA",
      "evidence_pointer": "bi14a.esf:L0123-L0145",
      "fields_count": 12
    }
  ]
}
```

### Passo 3: Extração de Campos
**Duração**: 2-5 minutos

```markdown
1. Escanear arquivo procurando padrão FIELD
2. Para cada campo encontrado:
   a. Extrair field_id, field_name, field_type
   b. Associar a screen_id correspondente
   c. Registrar evidence_pointer
   d. Extrair regras de validação
   e. Extrair tipo de dados
3. Validar referências a telas
```

**Padrões Buscados**:
- `FIELD nome_campo TYPE tipo`
- `INPUT` / `OUTPUT` / `DISPLAY`
- `REQUIRED` / `NUMERIC` / `VALID VALUES`

**Output Parcial**:
```json
{
  "fields": [
    {
      "field_id": "FLD-001",
      "field_name": "COD_BANCO",
      "field_type": "INPUT",
      "screen_id": "SCR-001",
      "evidence_pointer": "bi14a.esf:L0130-L0132",
      "validation_rules": ["REQUIRED", "NUMERIC"]
    }
  ]
}
```

### Passo 4: Extração de Queries SQL
**Duração**: 2-4 minutos

```markdown
1. Escanear arquivo procurando EXEC SQL
2. Para cada query encontrada:
   a. Extrair sql_statement completo
   b. Classificar query_type (SELECT/INSERT/UPDATE/DELETE)
   c. Registrar evidence_pointer
   d. Identificar tabelas referenciadas
   e. Identificar parâmetros (:variavel)
3. Validar sintaxe SQL básica
```

**Padrões Buscados**:
- `EXEC SQL ... END-EXEC`
- `SELECT ... FROM ... WHERE`
- `INSERT INTO ... VALUES`
- `UPDATE ... SET ... WHERE`
- `DELETE FROM ... WHERE`

**Output Parcial**:
```json
{
  "queries": [
    {
      "query_id": "QRY-001",
      "query_type": "SELECT",
      "sql_statement": "SELECT COD_BANCO, NOME_BANCO FROM BANCOS WHERE ATIVO = 'S'",
      "evidence_pointer": "bi14a.esf:L0500-L0502",
      "tables_referenced": ["BANCOS"],
      "parameters": []
    }
  ]
}
```

### Passo 5: Extração de Lógica de Negócio
**Duração**: 3-6 minutos

```markdown
1. Escanear arquivo procurando estruturas lógicas
2. Para cada bloco lógico encontrado:
   a. Classificar logic_type (CONDITIONAL/LOOP/CALL/ROUTINE)
   b. Extrair descrição detalhada
   c. Registrar evidence_pointer
   d. Identificar dependências (variáveis, campos, telas)
   e. Calcular complexity_score (1-10)
   f. Gerar pseudo_code se complexidade >= 7
3. Validar dependências
```

**Padrões Buscados**:
- `IF ... THEN ... END-IF`
- `EVALUATE ... WHEN ... END-EVALUATE`
- `PERFORM ... UNTIL`
- `CALL 'programa' USING`
- `PERFORM rotina`

**Output Parcial**:
```json
{
  "business_logic": [
    {
      "logic_id": "LOG-001",
      "logic_type": "CONDITIONAL",
      "description": "Validação de período: máximo 90 dias",
      "evidence_pointer": "bi14a.esf:L1200-L1215",
      "dependencies": ["FLD-002", "FLD-003"],
      "complexity_score": 3
    }
  ]
}
```

### Passo 6: Validação e Consolidação
**Duração**: 1-2 minutos

```markdown
1. Validar referências cruzadas:
   - Todos fields referenciam screens existentes
   - Todas dependencies são válidas
   - Nenhuma referência órfã

2. Validar evidence pointers:
   - Formato correto (arquivo.esf:Lxxxx-Lyyyy)
   - Linhas existem no arquivo
   - Ranges válidos (início <= fim)

3. Calcular métricas:
   - coverage_percentage
   - evidence_pointers_valid
   - extraction_duration_seconds

4. Gerar summary
```

**Validações Críticas**:
- ✅ 100% evidence pointers válidos
- ✅ 0 referências órfãs
- ✅ Coverage >= 95%

### Passo 7: Geração de Outputs
**Duração**: 30 segundos

```markdown
1. Consolidar todos elementos em JSON
2. Adicionar metadata e summary
3. Validar sintaxe JSON
4. Salvar claims_A.json
5. Gerar extraction_log.txt
6. Gerar validation_report.md
```

**Arquivos Gerados**:
- ✅ `run/extraction/claims_A.json` (principal)
- ✅ `run/extraction/extraction_log.txt` (log)
- ✅ `run/extraction/validation_report.md` (relatório)

## Validações Finais

### Validações CRITICAL (100% obrigatório)
- [ ] Todos elementos têm evidence_pointer válido
- [ ] Formato de evidence_pointer correto
- [ ] Todas referências são válidas (sem órfãs)
- [ ] JSON sintaticamente válido
- [ ] Hash SHA-256 correto

### Validações HIGH (95%+ obrigatório)
- [ ] Coverage >= 95%
- [ ] Queries SQL completas
- [ ] Classificações corretas (field_type, query_type, logic_type)
- [ ] Tables referenced identificadas

### Validações MEDIUM (80%+ obrigatório)
- [ ] Descriptions detalhadas (>= 10 caracteres)
- [ ] Complexity scores calculados
- [ ] Validation rules extraídas

## Métricas de Sucesso

### Qualidade
- **Coverage**: >= 98%
- **Evidence Validity**: 100%
- **Referências Válidas**: 100%

### Performance
- **Tempo**: <= 5 min por 1000 linhas
- **Tamanho JSON**: <= 10MB

### Completude
- **Telas**: 100% extraídas
- **Campos**: 100% extraídos
- **Queries**: 100% extraídas
- **Lógica**: >= 95% extraída

## Troubleshooting

### Erro: Arquivo não encontrado
**Causa**: Caminho incorreto ou arquivo não existe  
**Solução**: Verificar caminho em `_LEGADO/` e nome do arquivo

### Erro: Evidence pointer inválido
**Causa**: Formato incorreto ou linhas inexistentes  
**Solução**: Revisar formato `arquivo.esf:Lxxxx-Lyyyy` e range de linhas

### Erro: Referência órfã
**Causa**: Field referencia screen_id inexistente  
**Solução**: Verificar se tela foi extraída corretamente

### Erro: Coverage baixo (<95%)
**Causa**: Padrões não detectados ou arquivo incompleto  
**Solução**: Revisar padrões de busca e verificar integridade do arquivo

### Erro: JSON inválido
**Causa**: Sintaxe incorreta ou caracteres especiais  
**Solução**: Validar JSON e escapar caracteres especiais

## Exemplo Completo

### Input
```bash
Arquivo: _LEGADO/bi14a.esf
Modo: completo
Nível: forense
```

### Processo
```
[00:00] Iniciando extração forense...
[00:01] ✅ Arquivo verificado: 248KB, 6842 linhas
[00:01] ✅ Hash calculado: b6fe2994ed7416e7...
[00:02] 🔍 Extraindo telas... 5 encontradas
[00:05] 🔍 Extraindo campos... 47 encontrados
[00:09] 🔍 Extraindo queries... 23 encontradas
[00:13] 🔍 Extraindo lógica... 18 blocos encontrados
[00:14] ✅ Validando referências... 0 órfãs
[00:14] ✅ Validando evidence pointers... 100% válidos
[00:15] ✅ Coverage: 98.5%
[00:15] 💾 Salvando outputs...
[00:15] ✅ Extração concluída com sucesso!
```

### Output
```json
{
  "metadata": {
    "source_file": "bi14a.esf",
    "extraction_timestamp": "2025-12-27T10:30:00Z",
    "file_hash_sha256": "b6fe2994ed7416e7...",
    "total_lines": 6842
  },
  "summary": {
    "total_screens": 5,
    "total_fields": 47,
    "total_queries": 23,
    "total_business_logic_blocks": 18,
    "coverage_percentage": 98.5,
    "evidence_pointers_valid": 93,
    "extraction_duration_seconds": 45.3
  }
}
```

## Próximos Passos

Após extração bem-sucedida:

1. **[VAL] Validar Extração** - Executar validação detalhada
2. **[RPT] Gerar Relatório** - Criar relatório executivo
3. **Fase 2: Análise** - Passar para agente Analyzer-A

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi  
**Agente**: Extractor-A

