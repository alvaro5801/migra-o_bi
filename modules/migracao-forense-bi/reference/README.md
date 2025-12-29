# Referências - Migração Forense BI

## Visão Geral

Esta pasta contém exemplos de referência, templates e casos de uso para o módulo de Migração Forense BI.

## Conteúdo

### Exemplos de Extração
- [exemplo-extracao.md](./exemplo-extracao.md) - Exemplo completo de extração forense com input e output esperado

### Templates (Em Desenvolvimento)
- `template-claims.json` - Template para claims_A.json
- `template-analysis.json` - Template para analysis_A.json
- `template-design.json` - Template para design_B.json

### Casos de Uso (Em Desenvolvimento)
- `caso-uso-01-tela-simples.md` - Extração de tela simples
- `caso-uso-02-tela-complexa.md` - Extração de tela com múltiplos campos e validações
- `caso-uso-03-queries-complexas.md` - Extração de queries SQL complexas
- `caso-uso-04-logica-aninhada.md` - Extração de lógica de negócio aninhada

## Como Usar

### Para Aprender
1. Comece com [exemplo-extracao.md](./exemplo-extracao.md)
2. Entenda a estrutura de input (arquivo .esf)
3. Analise o output esperado (claims_A.json)
4. Observe as validações aplicadas

### Para Testar
1. Use os exemplos como casos de teste
2. Execute a extração no arquivo de exemplo
3. Compare o output gerado com o esperado
4. Valide se todas as regras foram cumpridas

### Para Desenvolver
1. Use os templates como base
2. Adapte para seu caso específico
3. Mantenha o formato de evidence pointer
4. Siga as regras de validação

## Estrutura de Exemplo

Cada exemplo deve conter:

### 1. Arquivo Fonte
```visual-age
* Código Visual Age comentado
* Com números de linha
* Formatado corretamente
```

### 2. Output Esperado
```json
{
  "metadata": { ... },
  "screens": [ ... ],
  "fields": [ ... ],
  "queries": [ ... ],
  "business_logic": [ ... ],
  "summary": { ... }
}
```

### 3. Análise
- Elementos extraídos
- Métricas de qualidade
- Rastreabilidade
- Validações aplicadas

### 4. Instruções de Uso
- Como testar
- Como validar
- Como usar para aprendizado

## Contribuindo

Ao adicionar novos exemplos:

1. **Siga o padrão** estabelecido em exemplo-extracao.md
2. **Inclua evidence pointers** válidos
3. **Documente métricas** de qualidade
4. **Valide JSON** antes de commitar
5. **Teste completamente** o exemplo

## Checklist para Novos Exemplos

- [ ] Arquivo .esf válido e comentado
- [ ] Output JSON completo e válido
- [ ] Evidence pointers no formato correto
- [ ] Análise detalhada incluída
- [ ] Métricas calculadas
- [ ] Validações documentadas
- [ ] Instruções de uso claras
- [ ] Testado com Extractor-A

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-12-27  
**Módulo**: migracao-forense-bi




