#!/usr/bin/env python3
"""
Script para gerar números de OS para registros existentes na tabela relatorios
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

def main():
    # Carregar variáveis de ambiente
    load_dotenv()
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas")
        return

    # Conectar ao Supabase
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        print("🔍 Verificando registros existentes...")
        
        # Contar registros sem numero_os
        response = supabase.table('relatorios').select('id', count='exact').is_('numero_os', 'null').execute()
        registros_sem_os = response.count
        print(f"📊 Registros sem numero_os: {registros_sem_os}")
        
        # Contar total de registros
        total_response = supabase.table('relatorios').select('id', count='exact').execute()
        total_registros = total_response.count
        print(f"📊 Total de registros: {total_registros}")
        
        if registros_sem_os == 0:
            print("✅ Todos os registros já têm numero_os!")
            return
        
        # Buscar registros sem numero_os ordenados por data de criação
        print(f"\n🔄 Buscando {registros_sem_os} registros sem numero_os...")
        registros = supabase.table('relatorios').select('id, criado_em').is_('numero_os', 'null').order('criado_em', desc=False).execute()
        
        print(f"📋 Encontrados {len(registros.data)} registros para atualizar")
        
        # Mostrar alguns exemplos
        print("\n📝 Exemplos de registros que serão atualizados:")
        for i, reg in enumerate(registros.data[:5]):
            print(f"  {i+1}. ID: {reg['id']}, Data: {reg['criado_em']}")
        
        if len(registros.data) > 5:
            print(f"  ... e mais {len(registros.data) - 5} registros")
        
        # Confirmar antes de prosseguir
        print(f"\n⚠️  ATENÇÃO: Este script irá gerar números de OS para {len(registros.data)} registros existentes.")
        confirmacao = input("Deseja continuar? (s/N): ").strip().lower()
        
        if confirmacao not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada pelo usuário")
            return
        
        # Gerar números de OS para cada registro
        print(f"\n🚀 Iniciando geração de números de OS...")
        
        sucessos = 0
        erros = 0
        
        for i, registro in enumerate(registros.data, 1):
            try:
                # Extrair ano da data de criação
                data_criacao = datetime.fromisoformat(registro['criado_em'].replace('Z', '+00:00'))
                ano = data_criacao.year
                
                # Gerar número de OS baseado no ano e sequência
                # Formato: OS-YYYY-NNNNNN
                numero_os = f"OS-{ano}-{i:06d}"
                
                # Atualizar o registro
                update_response = supabase.table('relatorios').update({
                    'numero_os': numero_os
                }).eq('id', registro['id']).execute()
                
                if update_response.data:
                    sucessos += 1
                    print(f"✅ {i}/{len(registros.data)} - ID: {registro['id']} -> {numero_os}")
                else:
                    erros += 1
                    print(f"❌ {i}/{len(registros.data)} - Erro ao atualizar ID: {registro['id']}")
                    
            except Exception as e:
                erros += 1
                print(f"❌ {i}/{len(registros.data)} - Erro no ID {registro['id']}: {str(e)}")
        
        # Resultado final
        print(f"\n📊 RESULTADO FINAL:")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Erros: {erros}")
        print(f"📋 Total processado: {sucessos + erros}")
        
        if sucessos > 0:
            print(f"\n🎉 {sucessos} registros foram atualizados com sucesso!")
            
            # Verificar se ainda há registros sem numero_os
            print("\n🔍 Verificando se ainda há registros sem numero_os...")
            verificar_response = supabase.table('relatorios').select('id', count='exact').is_('numero_os', 'null').execute()
            restantes = verificar_response.count
            print(f"📊 Registros sem numero_os restantes: {restantes}")
            
            if restantes == 0:
                print("🎉 Todos os registros agora têm numero_os!")
            else:
                print(f"⚠️  Ainda há {restantes} registros sem numero_os")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
