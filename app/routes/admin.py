"""
Rotas de administração
"""
from flask import Blueprint, render_template, request, jsonify
from app.services.auth_service import require_login, require_admin
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@require_login
def admin():
    """Página de administração"""
    return render_template('admin.html')

