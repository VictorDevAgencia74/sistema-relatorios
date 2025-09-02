#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de números de OS
"""

import os
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "codigo": "12345",  # Substitua por um código válido
    "setor": "porteiro"  # Substitua por um setor válido
}

def test_login():
    """Testa o login para obter sessão"""
    print("🔐 Testando login...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login realizado com sucesso")
                return data.get('user', {})
            else:
                print(f"❌ Falha no login: {data.get('message')}")
                return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_criar_relatorio(user_data):
    """Testa a criação de um relatório para verificar se o número de OS é gerado"""
    print("\n📝 Testando criação de relatório...")
    
    # Dados do relatório de teste
    relatorio_data = {
        "tipo_id": 1,  # Substitua por um tipo válido
        "dados": {
            "descricao": "Teste de número de OS",
            "local": "Local de teste"
        },
        "destinatario_whatsapp": "11999999999"
    }
    
    try:
        # Fazer login primeiro
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/login", json=TEST_USER)
        
        if login_response.status_code != 200:
            print("❌ Falha no login para teste")
            return None
        
        # Criar relatório
        response = session.post(f"{BASE_URL}/api/relatorios", json=relatorio_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                relatorio_id = data.get('id')
                print(f"✅ Relatório criado com ID: {relatorio_id}")
                return relatorio_id
            else:
                print(f"❌ Falha ao criar relatório: {data.get('message')}")
                return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_buscar_relatorio(relatorio_id):
    """Testa a busca do relatório criado para verificar o número de OS"""
    print(f"\n🔍 Testando busca do relatório {relatorio_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/relatorios/{relatorio_id}")
        
        if response.status_code == 200:
            relatorio = response.json()
            numero_os = relatorio.get('numero_os')
            
            if numero_os:
                print(f"✅ Número de OS encontrado: {numero_os}")
                return numero_os
            else:
                print("❌ Número de OS não foi gerado")
                return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_buscar_por_numero(numero_os):
    """Testa a busca por número de OS"""
    print(f"\n🔍 Testando busca por número de OS: {numero_os}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/relatorios/numero/{numero_os}")
        
        if response.status_code == 200:
            relatorio = response.json()
            print(f"✅ Relatório encontrado por número de OS")
            print(f"   ID: {relatorio.get('id')}")
            print(f"   Número OS: {relatorio.get('numero_os')}")
            print(f"   Status: {relatorio.get('status')}")
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_filtro_numero_os(numero_os):
    """Testa o filtro por número de OS na listagem"""
    print(f"\n📋 Testando filtro por número de OS: {numero_os}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/relatorios?numero_os={numero_os}")
        
        if response.status_code == 200:
            data = response.json()
            relatorios = data.get('data', [])
            
            if relatorios:
                print(f"✅ Filtro funcionando: {len(relatorios)} relatório(s) encontrado(s)")
                for rel in relatorios:
                    print(f"   - ID: {rel.get('id')}, OS: {rel.get('numero_os')}")
                return True
            else:
                print("❌ Filtro não retornou resultados")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_estatisticas_numero_os(numero_os):
    """Testa as estatísticas com filtro por número de OS"""
    print(f"\n📊 Testando estatísticas com filtro por número de OS: {numero_os}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/estatisticas?numero_os={numero_os}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            por_status = data.get('por_status', {})
            
            print(f"✅ Estatísticas funcionando:")
            print(f"   Total: {total}")
            print(f"   Por status: {por_status}")
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DO SISTEMA DE NÚMEROS DE OS")
    print("=" * 50)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ Servidor não está respondendo (HTTP {response.status_code})")
            print("   Certifique-se de que o Flask está rodando em http://localhost:5000")
            return
    except Exception as e:
        print(f"❌ Não foi possível conectar ao servidor: {e}")
        print("   Certifique-se de que o Flask está rodando em http://localhost:5000")
        return
    
    print("✅ Servidor está respondendo")
    
    # Testar login
    user_data = test_login()
    if not user_data:
        print("\n❌ Teste interrompido: falha no login")
        return
    
    # Testar criação de relatório
    relatorio_id = test_criar_relatorio(user_data)
    if not relatorio_id:
        print("\n❌ Teste interrompido: falha na criação do relatório")
        return
    
    # Testar busca do relatório
    numero_os = test_buscar_relatorio(relatorio_id)
    if not numero_os:
        print("\n❌ Teste interrompido: número de OS não foi gerado")
        return
    
    # Testar busca por número de OS
    if not test_buscar_por_numero(numero_os):
        print("\n❌ Teste falhou: busca por número de OS")
        return
    
    # Testar filtro na listagem
    if not test_filtro_numero_os(numero_os):
        print("\n❌ Teste falhou: filtro por número de OS")
        return
    
    # Testar estatísticas
    if not test_estatisticas_numero_os(numero_os):
        print("\n❌ Teste falhou: estatísticas com filtro por número de OS")
        return
    
    print("\n" + "=" * 50)
    print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("✅ Sistema de números de OS está funcionando perfeitamente")
    print(f"✅ Número de OS gerado: {numero_os}")
    print("=" * 50)

if __name__ == '__main__':
    main()

