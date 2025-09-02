#!/usr/bin/env python3
"""
Script para corrigir o último registro que ficou sem numero_os
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
        print("🔍 Buscando registros sem numero_os...")
        
        # Buscar registros sem numero_os
        response = supabase.table('relatorios').select('id, criado_em, numero_os').is_('numero_os', 'null').execute()
        
        if not response.data:
            print("✅ Nenhum registro sem numero_os encontrado!")
            return
        
        print(f"📋 Encontrados {len(response.data)} registros sem numero_os")
        
        for i, registro in enumerate(response.data, 1):
            print(f"\n📝 Registro {i}:")
            print(f"  ID: {registro['id']}")
            print(f"  Data: {registro['criado_em']}")
            print(f"  Numero OS: {registro['numero_os']}")
            
            # Gerar um numero_os único baseado na data
            data_criacao = datetime.fromisoformat(registro['criado_em'].replace('Z', '+00:00'))
            ano = data_criacao.year
            
            # Usar um número alto para evitar conflitos
            numero_os = f"OS-{ano}-99999{i}"
            
            print(f"  Novo numero_os: {numero_os}")
            
            # Atualizar o registro
            update_response = supabase.table('relatorios').update({
                'numero_os': numero_os
            }).eq('id', registro['id']).execute()
            
            if update_response.data:
                print(f"  ✅ Registro atualizado com sucesso!")
            else:
                print(f"  ❌ Erro ao atualizar registro")
        
        # Verificar se ainda há registros sem numero_os
        print(f"\n🔍 Verificando se ainda há registros sem numero_os...")
        verificar = supabase.table('relatorios').select('id', count='exact').is_('numero_os', 'null').execute()
        restantes = verificar.count
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
