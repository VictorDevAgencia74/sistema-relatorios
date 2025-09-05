"""
Rotas do Departamento Pessoal
"""
from flask import Blueprint, render_template, request, jsonify
from app.services.auth_service import require_login, require_dp_user
import logging

logger = logging.getLogger(__name__)

dp_bp = Blueprint('dp', __name__)

@dp_bp.route('/dp')
@require_login
def dp():
    """Página do Departamento Pessoal"""
    return render_template('dp.html')

