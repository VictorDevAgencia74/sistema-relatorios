"""
Rotas de relatórios
"""
from flask import Blueprint, request, jsonify
from app.services.supabase_service import supabase_service
from app.services.auth_service import require_login, require_admin, require_dp_user, require_trafego_user
from app.utils.security import sanitize_input
import logging
import traceback

logger = logging.getLogger(__name__)

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/api/tipos-relatorio')
@require_login
def get_tipos_relatorio():
    """Busca tipos de relatório"""
    try:
        response = supabase_service.get_table('tipos_relatorio').select('*').execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        logger.error(f"Erro ao buscar tipos de relatório: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/api/porteiros')
@require_login
def get_porteiros():
    """Busca porteiros"""
    try:
        response = supabase_service.get_table('porteiros').select('*').execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        logger.error(f"Erro ao buscar porteiros: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/api/relatorios', methods=['GET'])
@require_login
def get_relatorios():
    """Busca relatórios com filtros"""
    try:
        # Parâmetros de filtro
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Construir query
        query = supabase_service.get_table('relatorios').select('*')
        
        if status:
            query = query.eq('status', status)
        if tipo:
            query = query.eq('tipo_ocorrencia', tipo)
        if data_inicio:
            query = query.gte('data_ocorrencia', data_inicio)
        if data_fim:
            query = query.lte('data_ocorrencia', data_fim)
        
        response = query.order('data_ocorrencia', desc=True).execute()
        
        return jsonify({'success': True, 'data': response.data})
        
    except Exception as e:
        logger.error(f"Erro ao buscar relatórios: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/api/relatorios/numero/<numero_os>')
@require_login
def get_relatorio_by_numero(numero_os):
    """Busca relatório por número da OS"""
    try:
        response = supabase_service.get_table('relatorios').select('*').eq('numero_os', numero_os).execute()
        
        if not response.data:
            return jsonify({'success': False, 'message': 'Relatório não encontrado'}), 404
        
        return jsonify({'success': True, 'data': response.data[0]})
        
    except Exception as e:
        logger.error(f"Erro ao buscar relatório por número: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/api/relatorios/<id>')
@require_login
def get_relatorio_by_id(id):
    """Busca relatório por ID"""
    try:
        response = supabase_service.get_table('relatorios').select('*').eq('id', id).execute()
        
        if not response.data:
            return jsonify({'success': False, 'message': 'Relatório não encontrado'}), 404
        
        return jsonify({'success': True, 'data': response.data[0]})
        
    except Exception as e:
        logger.error(f"Erro ao buscar relatório por ID: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/api/relatorios', methods=['POST'])
@require_login
def criar_relatorio():
    """Cria novo relatório"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['tipo_ocorrencia', 'descricao', 'local', 'data_ocorrencia', 'hora_ocorrencia']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'success': False, 'message': f'Campo {campo} é obrigatório'}), 400
        
        # Sanitizar dados
        dados_sanitizados = {}
        for key, value in data.items():
            if isinstance(value, str):
                dados_sanitizados[key] = sanitize_input(value)
            else:
                dados_sanitizados[key] = value
        
        # Gerar número da OS
        from app.services.relatorio_service import gerar_numero_os
        numero_os = gerar_numero_os()
        
        # Preparar dados para inserção
        relatorio_data = {
            'numero_os': numero_os,
            'tipo_ocorrencia': dados_sanitizados['tipo_ocorrencia'],
            'descricao': dados_sanitizados['descricao'],
            'local': dados_sanitizados['local'],
            'data_ocorrencia': dados_sanitizados['data_ocorrencia'],
            'hora_ocorrencia': dados_sanitizados['hora_ocorrencia'],
            'status': 'EM_DP',
            'dados': dados_sanitizados.get('dados', {}),
            'motorista': dados_sanitizados.get('motorista', ''),
            'porteiros_id': dados_sanitizados.get('porteiros_id')
        }
        
        # Inserir no banco
        response = supabase_service.get_table('relatorios').insert(relatorio_data).execute()
        
        if response.data:
            logger.info(f"Relatório criado com sucesso: {numero_os}")
            return jsonify({'success': True, 'message': 'Relatório criado com sucesso', 'numero_os': numero_os})
        else:
            return jsonify({'success': False, 'message': 'Erro ao criar relatório'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao criar relatório: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Erro interno do servidor: {str(e)}'}), 500

@relatorios_bp.route('/api/relatorios/<id>/status', methods=['PUT'])
@require_login
def atualizar_status_relatorio(id):
    """Atualiza status do relatório"""
    try:
        data = request.get_json()
        novo_status = data.get('status')
        
        if not novo_status:
            return jsonify({'success': False, 'message': 'Status é obrigatório'}), 400
        
        # Validar status
        status_validos = ['EM_DP', 'EM_TRAFEGO', 'CONCLUIDO']
        if novo_status not in status_validos:
            return jsonify({'success': False, 'message': 'Status inválido'}), 400
        
        # Atualizar status
        response = supabase_service.get_table('relatorios').update({'status': novo_status}).eq('id', id).execute()
        
        if response.data:
            logger.info(f"Status do relatório {id} atualizado para {novo_status}")
            return jsonify({'success': True, 'message': 'Status atualizado com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Relatório não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/api/estatisticas')
@require_login
def get_estatisticas():
    """Busca estatísticas dos relatórios"""
    try:
        # Buscar todos os relatórios
        response = supabase_service.get_table('relatorios').select('*').execute()
        relatorios = response.data
        
        # Calcular estatísticas
        total = len(relatorios)
        em_dp = len([r for r in relatorios if r['status'] == 'EM_DP'])
        em_trafego = len([r for r in relatorios if r['status'] == 'EM_TRAFEGO'])
        concluidos = len([r for r in relatorios if r['status'] == 'CONCLUIDO'])
        
        # Estatísticas por tipo
        tipos = {}
        for relatorio in relatorios:
            tipo = relatorio.get('tipo_ocorrencia', 'Não especificado')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'em_dp': em_dp,
                'em_trafego': em_trafego,
                'concluidos': concluidos,
                'tipos': tipos
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@relatorios_bp.route('/api/exportar/html')
@require_login
def exportar_html():
    """Exporta relatórios em HTML"""
    try:
        # Buscar relatórios
        response = supabase_service.get_table('relatorios').select('*').order('data_ocorrencia', desc=True).execute()
        relatorios = response.data
        
        # Processar dados para exportação
        dados_exportacao = []
        for relatorio in relatorios:
            # Extrair nome do motorista dos dados
            motorista_nome = relatorio.get('motorista', '')
            if not motorista_nome and relatorio.get('dados'):
                dados = relatorio['dados']
                if isinstance(dados, str):
                    # Tentar extrair motorista de string JSON
                    import re
                    match = re.search(r'"motorista":\s*"([^"]+)"', dados)
                    if match:
                        motorista_nome = match.group(1)
                elif isinstance(dados, dict):
                    motorista_nome = dados.get('motorista', '')
            
            dados_exportacao.append({
                'numero_os': relatorio['numero_os'],
                'data': relatorio['data_ocorrencia'],
                'hora': relatorio['hora_ocorrencia'],
                'tipo': relatorio['tipo_ocorrencia'],
                'descricao': relatorio['descricao'],
                'local': relatorio['local'],
                'motorista': motorista_nome,
                'status': relatorio['status']
            })
        
        return jsonify({
            'success': True,
            'data': dados_exportacao
        })
        
    except Exception as e:
        logger.error(f"Erro ao exportar HTML: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

