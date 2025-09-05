"""
Rotas de autenticação
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.services.supabase_service import supabase_service
from app.services.auth_service import require_login
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Página inicial - redireciona para login"""
    if 'user' in session:
        user = session['user']
        if user.get('tipo') == 'ADMIN':
            return redirect(url_for('admin.admin'))
        elif user.get('tipo') == 'DP':
            return redirect(url_for('dp.dp'))
        elif user.get('tipo') == 'TRAFEGO':
            return redirect(url_for('trafego.trafego'))
    return render_template('login.html')

@auth_bp.route('/api/check-auth')
def check_auth():
    """Verifica se o usuário está autenticado"""
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']})
    return jsonify({'authenticated': False})

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username e password são obrigatórios'}), 400
        
        # Buscar usuário no Supabase
        response = supabase_service.get_table('administradores').select('*').eq('username', username).execute()
        
        if not response.data:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 401
        
        user = response.data[0]
        
        # Verificar senha (em produção, usar hash)
        if user['password'] != password:
            return jsonify({'success': False, 'message': 'Senha incorreta'}), 401
        
        # Armazenar na sessão
        session['user'] = {
            'id': user['id'],
            'username': user['username'],
            'nome': user['nome'],
            'tipo': user['tipo']
        }
        
        logger.info(f"Usuário {username} logado com sucesso")
        return jsonify({'success': True, 'message': 'Login realizado com sucesso'})
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Endpoint de logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

