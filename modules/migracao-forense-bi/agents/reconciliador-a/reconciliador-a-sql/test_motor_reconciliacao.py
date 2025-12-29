#!/usr/bin/env python3
"""
Script de Teste - Motor de Reconciliação
Valida configuração do Reconciliador-A-SQL

Uso:
    python test_motor_reconciliacao.py
"""

import os
import json
from pathlib import Path

def test_configuration():
    """Testa configuração do Motor de Reconciliação."""
    
    print("🔍 Testando Configuração do Motor de Reconciliação...\n")
    
    results = {
        "passed": [],
        "failed": []
    }
    
    # Teste 1: Verificar reconcile.py existe
    print("1. Verificando tools/reconciliation/reconcile.py...")
    reconcile_script = Path("tools/reconciliation/reconcile.py")
    if reconcile_script.exists():
        results["passed"].append("✅ reconcile.py encontrado")
        print("   ✅ PASS")
    else:
        results["failed"].append("❌ reconcile.py não encontrado")
        print("   ❌ FAIL")
    
    # Teste 2: Verificar agent.yaml existe
    print("\n2. Verificando reconciliador-a-sql.agent.yaml...")
    agent_yaml = Path("bmad-core/src/modules/migracao-forense-bi/agents/reconciliador-a/reconciliador-a-sql/reconciliador-a-sql.agent.yaml")
    if agent_yaml.exists():
        results["passed"].append("✅ agent.yaml encontrado")
        print("   ✅ PASS")
        
        # Verificar se contém reconcile_tool
        content = agent_yaml.read_text(encoding='utf-8')
        if "reconcile_tool:" in content:
            results["passed"].append("✅ reconcile_tool configurado")
            print("   ✅ reconcile_tool configurado")
        else:
            results["failed"].append("❌ reconcile_tool não encontrado no YAML")
            print("   ❌ reconcile_tool não encontrado")
    else:
        results["failed"].append("❌ agent.yaml não encontrado")
        print("   ❌ FAIL")
    
    # Teste 3: Verificar instructions.md existe
    print("\n3. Verificando instructions.md...")
    instructions = Path("bmad-core/src/modules/migracao-forense-bi/agents/reconciliador-a/reconciliador-a-sql/instructions.md")
    if instructions.exists():
        results["passed"].append("✅ instructions.md encontrado")
        print("   ✅ PASS")
        
        # Verificar se contém Motor de Reconciliação
        content = instructions.read_text(encoding='utf-8')
        if "Motor de Reconciliação" in content:
            results["passed"].append("✅ Instruções atualizadas")
            print("   ✅ Instruções atualizadas com Motor")
        else:
            results["failed"].append("❌ Instruções não atualizadas")
            print("   ❌ Instruções não atualizadas")
    else:
        results["failed"].append("❌ instructions.md não encontrado")
        print("   ❌ FAIL")
    
    # Teste 4: Verificar conflict-resolution-strategies.csv
    print("\n4. Verificando knowledge/conflict-resolution-strategies.csv...")
    strategies_csv = Path("bmad-core/src/modules/migracao-forense-bi/knowledge/conflict-resolution-strategies.csv")
    if strategies_csv.exists():
        results["passed"].append("✅ conflict-resolution-strategies.csv encontrado")
        print("   ✅ PASS")
        
        # Contar estratégias
        content = strategies_csv.read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        strategy_count = len(lines) - 1  # Excluir header
        print(f"   📊 {strategy_count} estratégias disponíveis")
    else:
        results["failed"].append("❌ conflict-resolution-strategies.csv não encontrado")
        print("   ❌ FAIL")
    
    # Teste 5: Verificar reconciliation-rules.csv
    print("\n5. Verificando knowledge/reconciliation-rules.csv...")
    rules_csv = Path("bmad-core/src/modules/migracao-forense-bi/knowledge/reconciliation-rules.csv")
    if rules_csv.exists():
        results["passed"].append("✅ reconciliation-rules.csv encontrado")
        print("   ✅ PASS")
        
        # Contar regras
        content = rules_csv.read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        rule_count = len(lines) - 1  # Excluir header
        print(f"   📊 {rule_count} regras disponíveis")
    else:
        results["failed"].append("❌ reconciliation-rules.csv não encontrado")
        print("   ❌ FAIL")
    
    # Teste 6: Verificar estrutura de diretórios
    print("\n6. Verificando estrutura de diretórios...")
    dirs_to_check = [
        "run/sql/extraction",
        "run/sql/analysis",
        "run/sql/validation"
    ]
    
    all_dirs_exist = True
    for dir_path in dirs_to_check:
        path = Path("bmad-core/src/modules/bmb") / dir_path
        if path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ⚠️ {dir_path} (será criado automaticamente)")
            all_dirs_exist = False
    
    if all_dirs_exist:
        results["passed"].append("✅ Todos os diretórios existem")
    else:
        results["passed"].append("⚠️ Alguns diretórios serão criados automaticamente")
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    print(f"\n✅ PASSED: {len(results['passed'])}")
    for item in results["passed"]:
        print(f"   {item}")
    
    if results["failed"]:
        print(f"\n❌ FAILED: {len(results['failed'])}")
        for item in results["failed"]:
            print(f"   {item}")
    
    # Status final
    print("\n" + "="*60)
    if not results["failed"]:
        print("🎉 CONFIGURAÇÃO VÁLIDA - Motor de Reconciliação OPERACIONAL")
        print("="*60)
        print("\n✅ Pronto para executar primeiro teste de reconciliação!")
        print("\nPróximos passos:")
        print("1. Certifique-se de ter claims_sql_A.json e claims_sql_B.json")
        print("2. Execute o comando [REC-SQL] no agente Reconciliador-A-SQL")
        print("3. Verifique os outputs gerados:")
        print("   - run/sql/analysis/claim_ledger_sql.json")
        print("   - run/sql/validation/diff_report_sql.md")
        return True
    else:
        print("⚠️ CONFIGURAÇÃO INCOMPLETA - Corrigir problemas acima")
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_configuration()
    exit(0 if success else 1)



