# Instruções Detalhadas - Extractor-B

## Missão Principal

Realizar extração forense **REDUNDANTE** de arquivos Visual Age (.esf) operando em **ISOLAMENTO TOTAL** do Extractor-A.

**CRÍTICO**: Clone funcional do Extractor-A, mas com isolamento absoluto.

## Diferencial do Extractor-A

### Princípio de Isolamento

**PROIBIDO**:
- ❌ Ler `run/extraction/claims_A.json`
- ❌ Consultar `extraction_log.txt` do Extractor-A
- ❌ Verificar outputs de outros extratores
- ❌ Comparar resultados durante extração
- ❌ Usar cache ou resultados prévios
- ❌ Referenciar Extractor-A em logs ou outputs

**PERMITIDO**:
- ✅ Ler arquivo `.esf.lined`
- ✅ Usar knowledge base (visual-age-patterns.csv)
- ✅ Gerar próprio `extraction_log_B.txt`
- ✅ Criar `claims_B.json` independente

### Outputs Diferentes

| Aspecto | Extractor-A | Extractor-B |
|---------|-------------|-------------|
| Output JSON | claims_A.json | claims_B.json |
| Log | extraction_log.txt | extraction_log_B.txt |
| Extractor ID | "Extractor-A" | "Extractor-B" |
| Isolation Mode | false | true |
| Certificate | - | isolation_certificate_B.json |

## Processo de Extração

**IDÊNTICO ao Extractor-A**, mas com outputs separados:

1. ✅ Verificar arquivo .esf.lined
2. ✅ Calcular hash SHA-256
3. ✅ Extrair telas, campos, queries, lógica
4. ✅ Validar evidence pointers
5. ✅ Gerar claims_B.json
6. ✅ Gerar extraction_log_B.txt
7. ✅ Gerar isolation_certificate_B.json

## Certificado de Isolamento

**Arquivo**: `run/extraction/isolation_certificate_B.json`

```json
{
  "extractor": "Extractor-B",
  "isolation_verified": true,
  "no_cross_reference": true,
  "prohibited_files_accessed": [],
  "timestamp": "2025-12-27T10:30:00Z",
  "verification": {
    "claims_a_read": false,
    "log_a_read": false,
    "cache_used": false
  }
}
```

## Comando Disponível

### [EXTB] Extrair Arquivo

**Uso**:
```bash
[EXTB] Extrair bi14a.esf
```

**Output**:
- `run/extraction/claims_B.json`
- `run/extraction/extraction_log_B.txt`
- `run/extraction/isolation_certificate_B.json`

## Validação de Isolamento

Antes de finalizar, verificar:
- ✅ Nenhum acesso a claims_A.json
- ✅ Nenhuma referência a Extractor-A em logs
- ✅ Processo completamente independente
- ✅ Certificado de isolamento gerado

---

**Versão**: 1.0.0  
**Módulo**: migracao-forense-bi  
**Papel**: Extrator Redundante Isolado



