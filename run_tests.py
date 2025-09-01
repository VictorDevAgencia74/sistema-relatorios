#!/usr/bin/env python3
"""
Script para executar testes do Sistema de Relatórios
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"\n{'='*60}")
    print(f"Executando: {description}")
    print(f"Comando: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Sucesso!")
        if result.stdout:
            print("Saída:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Erro!")
        print(f"Código de saída: {e.returncode}")
        if e.stdout:
            print("Saída padrão:")
            print(e.stdout)
        if e.stderr:
            print("Erro:")
            print(e.stderr)
        return False

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'pytest-flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def run_unit_tests():
    """Executa testes unitários"""
    return run_command(
        "python -m pytest tests/ -m unit -v --tb=short",
        "Testes Unitários"
    )

def run_security_tests():
    """Executa testes de segurança"""
    return run_command(
        "python -m pytest tests/ -m security -v --tb=short",
        "Testes de Segurança"
    )

def run_integration_tests():
    """Executa testes de integração"""
    return run_command(
        "python -m pytest tests/ -m integration -v --tb=short",
        "Testes de Integração"
    )

def run_all_tests():
    """Executa todos os testes"""
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "Todos os Testes"
    )

def run_tests_with_coverage():
    """Executa testes com cobertura"""
    return run_command(
        "python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing",
        "Testes com Cobertura"
    )

def run_specific_test_file(test_file):
    """Executa um arquivo de teste específico"""
    if not Path(test_file).exists():
        print(f"❌ Arquivo de teste não encontrado: {test_file}")
        return False
    
    return run_command(
        f"python -m pytest {test_file} -v --tb=short",
        f"Arquivo de Teste: {test_file}"
    )

def main():
    """Função principal"""
    print("🧪 Sistema de Relatórios - Executor de Testes")
    print("=" * 60)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "unit":
            success = run_unit_tests()
        elif command == "security":
            success = run_security_tests()
        elif command == "integration":
            success = run_integration_tests()
        elif command == "coverage":
            success = run_tests_with_coverage()
        elif command == "file" and len(sys.argv) > 2:
            success = run_specific_test_file(sys.argv[2])
        else:
            print(f"❌ Comando inválido: {command}")
            print("Comandos disponíveis:")
            print("  python run_tests.py unit        - Testes unitários")
            print("  python run_tests.py security    - Testes de segurança")
            print("  python run_tests.py integration - Testes de integração")
            print("  python run_tests.py coverage    - Testes com cobertura")
            print("  python run_tests.py file <arquivo> - Arquivo específico")
            print("  python run_tests.py             - Todos os testes")
            sys.exit(1)
    else:
        # Executar todos os testes
        success = run_all_tests()
    
    # Resultado final
    print(f"\n{'='*60}")
    if success:
        print("🎉 Todos os testes executados com sucesso!")
        sys.exit(0)
    else:
        print("💥 Alguns testes falharam!")
        sys.exit(1)

if __name__ == "__main__":
    main()
