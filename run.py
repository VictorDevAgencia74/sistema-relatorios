"""
Arquivo principal para executar a aplicação
"""
from app import create_app
from config.settings import Config
import logging

# Configurar logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    # Configurar storage do Supabase (opcional em desenvolvimento)
    try:
        from app.services.supabase_service import supabase_service
        supabase_service.setup_storage()
    except Exception as e:
        logger.warning(f"Não foi possível configurar storage: {e}")
    
    # Executar aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)

