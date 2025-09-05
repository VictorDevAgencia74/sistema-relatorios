"""
Sistema de Relatórios - Aplicação Principal
"""

from flask import Flask
from config.settings import Config

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.relatorios import relatorios_bp
    from app.routes.admin import admin_bp
    from app.routes.dp import dp_bp
    from app.routes.trafego import trafego_bp
    from app.routes.backup import backup_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dp_bp)
    app.register_blueprint(trafego_bp)
    app.register_blueprint(backup_bp)
    
    return app
