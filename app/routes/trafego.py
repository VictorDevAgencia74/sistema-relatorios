"""
Rotas de Tráfego
"""
from flask import Blueprint, render_template, request, jsonify
from app.services.auth_service import require_login, require_trafego_user
import logging

logger = logging.getLogger(__name__)

trafego_bp = Blueprint('trafego', __name__)

@trafego_bp.route('/trafego')
@require_login
def trafego():
    """Página de Tráfego"""
    return render_template('trafego.html')

