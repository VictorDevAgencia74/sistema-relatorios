"""
Serviço para operações com relatórios
"""
from app.services.supabase_service import supabase_service
import logging

logger = logging.getLogger(__name__)

def gerar_numero_os():
    """Gera número sequencial para OS"""
    try:
        # Buscar último número usado
        response = supabase_service.get_table('relatorios').select('numero_os').order('numero_os', desc=True).limit(1).execute()
        
        if response.data:
            ultimo_numero = int(response.data[0]['numero_os'])
            novo_numero = ultimo_numero + 1
        else:
            novo_numero = 1
        
        # Garantir que o número seja único
        while True:
            check_response = supabase_service.get_table('relatorios').select('id').eq('numero_os', str(novo_numero)).execute()
            if not check_response.data:
                break
            novo_numero += 1
        
        return str(novo_numero)
        
    except Exception as e:
        logger.error(f"Erro ao gerar número OS: {str(e)}")
        # Fallback: usar timestamp
        import time
        return str(int(time.time()))

