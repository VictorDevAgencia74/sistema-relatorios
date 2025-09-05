"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Configurações de backup
    BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backups')
    
    @staticmethod
    def validate():
        """Valida se as configurações obrigatórias estão presentes"""
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL ou SUPABASE_KEY não configurados")

