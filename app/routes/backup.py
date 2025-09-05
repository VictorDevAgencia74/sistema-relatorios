"""
Rotas de backup
"""
from flask import Blueprint, request, jsonify, send_file
from app.services.auth_service import require_login, require_admin
from app.services.backup_service import create_backup, get_backup_status, list_backups
import logging
import os

logger = logging.getLogger(__name__)

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/api/backup/criar', methods=['POST'])
@require_login
def criar_backup():
    """Cria backup do sistema"""
    try:
        backup_info = create_backup()
        return jsonify({'success': True, 'message': 'Backup criado com sucesso', 'backup': backup_info})
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao criar backup'}), 500

@backup_bp.route('/api/backup/status')
@require_login
def status_backup():
    """Verifica status do backup"""
    try:
        status = get_backup_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Erro ao verificar status do backup: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao verificar status'}), 500

@backup_bp.route('/api/backup/listar')
@require_login
def listar_backups():
    """Lista backups disponíveis"""
    try:
        backups = list_backups()
        return jsonify({'success': True, 'backups': backups})
    except Exception as e:
        logger.error(f"Erro ao listar backups: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao listar backups'}), 500

@backup_bp.route('/api/backup/download/<int:backup_id>')
@require_login
def download_backup(backup_id):
    """Download de backup"""
    try:
        backups = list_backups()
        backup = next((b for b in backups if b['id'] == backup_id), None)
        
        if not backup:
            return jsonify({'success': False, 'message': 'Backup não encontrado'}), 404
        
        file_path = backup['file_path']
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Arquivo de backup não encontrado'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{backup['name']}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Erro ao fazer download do backup: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao fazer download'}), 500

