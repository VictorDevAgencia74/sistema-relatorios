"""
Serviço para integração com Supabase
"""
from supabase import create_client, Client
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    """Serviço para operações com Supabase"""
    
    def __init__(self):
        """Inicializa o cliente Supabase"""
        Config.validate()
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def setup_storage(self):
        """Configura o storage do Supabase"""
        try:
            # Listar buckets existentes
            response = self.client.storage.list_buckets()
            buckets = response if isinstance(response, list) else getattr(response, 'buckets', [])
            bucket_names = [bucket['name'] if isinstance(bucket, dict) else bucket.name for bucket in buckets]
            
            if 'relatorios-fotos' not in bucket_names:
                # Criar bucket se não existir
                self.client.storage.create_bucket('relatorios-fotos')
                logger.info("Bucket 'relatorios-fotos' criado com sucesso")
            else:
                logger.info("Bucket 'relatorios-fotos' já existe")
                
        except Exception as e:
            logger.error(f"Erro ao configurar storage: {str(e)}")
            # Em desenvolvimento, não falhar se não conseguir configurar storage
            pass
    
    def get_table(self, table_name):
        """Retorna referência para uma tabela"""
        return self.client.table(table_name)
    
    def get_storage(self):
        """Retorna referência para o storage"""
        return self.client.storage

# Instância global do serviço
supabase_service = SupabaseService()

