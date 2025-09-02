#!/usr/bin/env python3
"""
Script para configurar o campo numero_os na tabela relatorios
Este script executa as alterações necessárias no banco de dados Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_numero_os():
    """Configura o campo numero_os na tabela relatorios"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configuração do Supabase
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL ou SUPABASE_KEY não configurados")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    try:
        logger.info("Iniciando configuração do campo numero_os...")
        
        # 1. Adicionar o campo numero_os
        logger.info("Adicionando campo numero_os...")
        response = supabase.rpc('exec_sql', {
            'sql': '''
                ALTER TABLE public.relatorios 
                ADD COLUMN IF NOT EXISTS numero_os VARCHAR(20);
            '''
        }).execute()
        logger.info("Campo numero_os adicionado com sucesso")
        
        # 2. Criar índice para melhor performance
        logger.info("Criando índice...")
        response = supabase.rpc('exec_sql', {
            'sql': '''
                CREATE INDEX IF NOT EXISTS idx_relatorios_numero_os 
                ON public.relatorios(numero_os);
            '''
        }).execute()
        logger.info("Índice criado com sucesso")
        
        # 3. Criar sequência para gerar números automáticos
        logger.info("Criando sequência...")
        response = supabase.rpc('exec_sql', {
            'sql': '''
                CREATE SEQUENCE IF NOT EXISTS public.relatorios_numero_os_seq
                    INCREMENT 1
                    START 1
                    MINVALUE 1
                    MAXVALUE 999999
                    CACHE 1;
            '''
        }).execute()
        logger.info("Sequência criada com sucesso")
        
        # 4. Criar função para gerar número de OS automaticamente
        logger.info("Criando função gerar_numero_os...")
        response = supabase.rpc('exec_sql', {
            'sql': '''
                CREATE OR REPLACE FUNCTION gerar_numero_os()
                RETURNS TRIGGER AS $$
                DECLARE
                    proximo_numero INTEGER;
                    numero_formatado VARCHAR(20);
                    ano_atual VARCHAR(4);
                BEGIN
                    -- Obter o próximo número da sequência
                    SELECT nextval('public.relatorios_numero_os_seq') INTO proximo_numero;
                    
                    -- Obter o ano atual
                    SELECT EXTRACT(YEAR FROM CURRENT_DATE)::VARCHAR INTO ano_atual;
                    
                    -- Formatar o número: OS-2024-000001
                    numero_formatado := 'OS-' || ano_atual || '-' || LPAD(proximo_numero::VARCHAR, 6, '0');
                    
                    -- Atribuir o número gerado
                    NEW.numero_os := numero_formatado;
                    
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            '''
        }).execute()
        logger.info("Função gerar_numero_os criada com sucesso")
        
        # 5. Criar trigger para executar automaticamente
        logger.info("Criando trigger...")
        response = supabase.rpc('exec_sql', {
            'sql': '''
                DROP TRIGGER IF EXISTS trigger_gerar_numero_os ON public.relatorios;
                CREATE TRIGGER trigger_gerar_numero_os
                    BEFORE INSERT ON public.relatorios
                    FOR EACH ROW
                    EXECUTE FUNCTION gerar_numero_os();
            '''
        }).execute()
        logger.info("Trigger criado com sucesso")
        
        # 6. Atualizar registros existentes (se houver)
        logger.info("Verificando registros existentes...")
        response = supabase.table('relatorios').select('id, numero_os').execute()
        
        if response.data:
            registros_sem_numero = [r for r in response.data if not r.get('numero_os')]
            if registros_sem_numero:
                logger.info(f"Encontrados {len(registros_sem_numero)} registros sem número de OS")
                logger.info("Atualizando registros existentes...")
                
                for registro in registros_sem_numero:
                    # Gerar número de OS para registros existentes
                    response = supabase.rpc('exec_sql', {
                        'sql': f'''
                            UPDATE public.relatorios 
                            SET numero_os = 'OS-2024-' || LPAD(nextval('public.relatorios_numero_os_seq')::VARCHAR, 6, '0')
                            WHERE id = '{registro['id']}';
                        '''
                    }).execute()
                
                logger.info("Registros existentes atualizados com sucesso")
            else:
                logger.info("Todos os registros já possuem número de OS")
        
        logger.info("Configuração do campo numero_os concluída com sucesso!")
        
        # 7. Verificar se tudo está funcionando
        logger.info("Testando funcionalidade...")
        test_response = supabase.table('relatorios').select('id, numero_os').limit(5).execute()
        if test_response.data:
            logger.info("Exemplos de números de OS:")
            for registro in test_response.data:
                logger.info(f"ID: {registro['id']} -> Número OS: {registro.get('numero_os', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a configuração: {e}")
        logger.error("Verifique se você tem permissões de administrador no Supabase")
        return False

def verificar_configuracao():
    """Verifica se a configuração está funcionando corretamente"""
    
    load_dotenv()
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("Variáveis de ambiente não configuradas")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    try:
        # Verificar se o campo existe
        response = supabase.rpc('exec_sql', {
            'sql': '''
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'relatorios' AND column_name = 'numero_os';
            '''
        }).execute()
        
        if response.data:
            logger.info("Campo numero_os encontrado na tabela")
            return True
        else:
            logger.error("Campo numero_os não encontrado")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao verificar configuração: {e}")
        return False

if __name__ == '__main__':
    print("=== Configuração do Campo numero_os ===")
    print()
    
    # Verificar configuração atual
    print("Verificando configuração atual...")
    if verificar_configuracao():
        print("✅ Campo numero_os já está configurado!")
    else:
        print("❌ Campo numero_os não está configurado")
        print()
        
        # Perguntar se deseja configurar
        resposta = input("Deseja configurar o campo numero_os agora? (s/n): ").lower().strip()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            print()
            print("Iniciando configuração...")
            if setup_numero_os():
                print("✅ Configuração concluída com sucesso!")
            else:
                print("❌ Erro durante a configuração")
        else:
            print("Configuração cancelada pelo usuário")
    
    print()
    print("=== Fim da Configuração ===")

