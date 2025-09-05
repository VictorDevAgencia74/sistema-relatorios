"""
Serviço de autenticação
"""
from functools import wraps
from flask import session, jsonify
import logging

logger = logging.getLogger(__name__)

def require_login(f):
    """Decorator para verificar autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator para verificar se é administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        user = session.get('user', {})
        if user.get('tipo') != 'ADMIN':
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def require_dp_user(f):
    """Decorator para verificar se é usuário DP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        user = session.get('user', {})
        if user.get('tipo') not in ['ADMIN', 'DP']:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def require_trafego_user(f):
    """Decorator para verificar se é usuário Tráfego"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        user = session.get('user', {})
        if user.get('tipo') not in ['ADMIN', 'TRAFEGO']:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

