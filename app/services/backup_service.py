import os
import json
import shutil
import zipfile
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import schedule
import time
import threading
from pathlib import Path

# Configurar logging para backup
backup_logger = logging.getLogger('backup')
backup_logger.setLevel(logging.INFO)

class BackupManager:
    """Gerenciador de backup automático do sistema"""
    
    def __init__(self, backup_dir: str = "backups", max_backups: int = 30):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurações de backup
        self.backup_config = {
            'database': True,
            'files': True,
            'logs': True,
            'config': True
        }
        
        # Histórico de backups
        self.backup_history_file = self.backup_dir / "backup_history.json"
        self.backup_history = self._load_backup_history()
        
        # Configurar backup automático
        self._setup_automated_backup()
        
        backup_logger.info(f"Backup Manager inicializado. Diretório: {self.backup_dir}")
    
    def _load_backup_history(self) -> List[Dict[str, Any]]:
        """Carrega histórico de backups"""
        if self.backup_history_file.exists():
            try:
                with open(self.backup_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                backup_logger.error(f"Erro ao carregar histórico de backup: {e}")
                return []
        return []
    
    def _save_backup_history(self):
        """Salva histórico de backups"""
        try:
            with open(self.backup_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            backup_logger.error(f"Erro ao salvar histórico de backup: {e}")
    
    def create_backup(self, backup_type: str = "manual") -> Dict[str, Any]:
        """Cria um novo backup"""
        timestamp = datetime.now()
        backup_name = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}_{backup_type}"
        backup_path = self.backup_dir / backup_name
        
        try:
            backup_path.mkdir(exist_ok=True)
            
            backup_info = {
                'id': len(self.backup_history) + 1,
                'name': backup_name,
                'type': backup_type,
                'timestamp': timestamp.isoformat(),
                'status': 'in_progress',
                'files': [],
                'size': 0,
                'error': None
            }
            
            # Backup do banco de dados (schema)
            if self.backup_config['database']:
                self._backup_database(backup_path, backup_info)
            
            # Backup de arquivos estáticos
            if self.backup_config['files']:
                self._backup_static_files(backup_path, backup_info)
            
            # Backup de logs
            if self.backup_config['logs']:
                self._backup_logs(backup_path, backup_info)
            
            # Backup de configurações
            if self.backup_config['config']:
                self._backup_config(backup_path, backup_info)
            
            # Criar arquivo de metadados
            self._create_backup_metadata(backup_path, backup_info)
            
            # Compactar backup
            zip_path = self._compress_backup(backup_path, backup_info)
            
            # Limpar diretório temporário
            shutil.rmtree(backup_path)
            
            # Atualizar informações do backup
            backup_info['status'] = 'completed'
            backup_info['zip_path'] = str(zip_path)
            backup_info['size'] = zip_path.stat().st_size
            
            # Adicionar ao histórico
            self.backup_history.append(backup_info)
            self._save_backup_history()
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            backup_logger.info(f"Backup criado com sucesso: {backup_name}")
            return backup_info
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            backup_logger.error(f"Erro ao criar backup {backup_name}: {e}")
            
            # Limpar diretório em caso de erro
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            return backup_info
    
    def _backup_database(self, backup_path: Path, backup_info: Dict[str, Any]):
        """Backup do banco de dados (schema)"""
        try:
            db_backup_dir = backup_path / "database"
            db_backup_dir.mkdir(exist_ok=True)
            
            # Copiar arquivos de schema
            schema_dir = Path("database/schema")
            if schema_dir.exists():
                for schema_file in schema_dir.glob("*.sql"):
                    dest_file = db_backup_dir / schema_file.name
                    shutil.copy2(schema_file, dest_file)
                    backup_info['files'].append(f"database/{schema_file.name}")
            
            backup_logger.info("Backup do banco de dados concluído")
            
        except Exception as e:
            backup_logger.error(f"Erro no backup do banco de dados: {e}")
            raise
    
    def _backup_static_files(self, backup_path: Path, backup_info: Dict[str, Any]):
        """Backup de arquivos estáticos"""
        try:
            static_backup_dir = backup_path / "static"
            static_backup_dir.mkdir(exist_ok=True)
            
            # Copiar arquivos estáticos
            static_dir = Path("static")
            if static_dir.exists():
                for item in static_dir.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(static_dir)
                        dest_path = static_backup_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                        backup_info['files'].append(f"static/{rel_path}")
            
            backup_logger.info("Backup de arquivos estáticos concluído")
            
        except Exception as e:
            backup_logger.error(f"Erro no backup de arquivos estáticos: {e}")
            raise
    
    def _backup_logs(self, backup_path: Path, backup_info: Dict[str, Any]):
        """Backup de logs"""
        try:
            logs_backup_dir = backup_path / "logs"
            logs_backup_dir.mkdir(exist_ok=True)
            
            # Copiar logs existentes
            log_files = list(Path(".").glob("*.log"))
            for log_file in log_files:
                dest_file = logs_backup_dir / log_file.name
                shutil.copy2(log_file, dest_file)
                backup_info['files'].append(f"logs/{log_file.name}")
            
            backup_logger.info("Backup de logs concluído")
            
        except Exception as e:
            backup_logger.error(f"Erro no backup de logs: {e}")
            raise
    
    def _backup_config(self, backup_path: Path, backup_info: Dict[str, Any]):
        """Backup de configurações"""
        try:
            config_backup_dir = backup_path / "config"
            config_backup_dir.mkdir(exist_ok=True)
            
            # Copiar arquivos de configuração
            config_files = [
                "requirements.txt",
                "env.example",
                ".gitignore"
            ]
            
            for config_file in config_files:
                if Path(config_file).exists():
                    dest_file = config_backup_dir / config_file
                    shutil.copy2(config_file, dest_file)
                    backup_info['files'].append(f"config/{config_file}")
            
            backup_logger.info("Backup de configurações concluído")
            
        except Exception as e:
            backup_logger.error(f"Erro no backup de configurações: {e}")
            raise
    
    def _create_backup_metadata(self, backup_path: Path, backup_info: Dict[str, Any]):
        """Cria arquivo de metadados do backup"""
        try:
            metadata_file = backup_path / "backup_info.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            backup_info['files'].append("backup_info.json")
            
        except Exception as e:
            backup_logger.error(f"Erro ao criar metadados do backup: {e}")
            raise
    
    def _compress_backup(self, backup_path: Path, backup_info: Dict[str, Any]) -> Path:
        """Compacta o backup em arquivo ZIP"""
        try:
            zip_path = self.backup_dir / f"{backup_path.name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for item in backup_path.rglob("*"):
                    if item.is_file():
                        arcname = item.relative_to(backup_path)
                        zipf.write(item, arcname)
            
            backup_logger.info(f"Backup compactado: {zip_path}")
            return zip_path
            
        except Exception as e:
            backup_logger.error(f"Erro ao compactar backup: {e}")
            raise
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado no limite configurado"""
        try:
            if len(self.backup_history) <= self.max_backups:
                return
            
            # Ordena por timestamp e remove os mais antigos
            sorted_backups = sorted(
                self.backup_history, 
                key=lambda x: x['timestamp']
            )
            
            backups_to_remove = sorted_backups[:-self.max_backups]
            
            for backup in backups_to_remove:
                try:
                    # Remove arquivo ZIP
                    if 'zip_path' in backup and Path(backup['zip_path']).exists():
                        Path(backup['zip_path']).unlink()
                        backup_logger.info(f"Backup removido: {backup['zip_path']}")
                    
                    # Remove do histórico
                    self.backup_history.remove(backup)
                    
                except Exception as e:
                    backup_logger.error(f"Erro ao remover backup {backup['name']}: {e}")
            
            self._save_backup_history()
            backup_logger.info(f"Cleanup concluído: {len(backups_to_remove)} backups removidos")
            
        except Exception as e:
            backup_logger.error(f"Erro no cleanup de backups: {e}")
    
    def restore_backup(self, backup_id: int) -> Dict[str, Any]:
        """Restaura um backup específico"""
        try:
            # Encontrar backup no histórico
            backup = next((b for b in self.backup_history if b['id'] == backup_id), None)
            if not backup:
                raise ValueError(f"Backup com ID {backup_id} não encontrado")
            
            if backup['status'] != 'completed':
                raise ValueError(f"Backup {backup['name']} não está completo")
            
            zip_path = Path(backup['zip_path'])
            if not zip_path.exists():
                raise ValueError(f"Arquivo de backup não encontrado: {zip_path}")
            
            # Criar diretório temporário para restauração
            restore_dir = self.backup_dir / f"restore_{backup['name']}"
            restore_dir.mkdir(exist_ok=True)
            
            # Extrair backup
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(restore_dir)
            
            # Ler metadados
            metadata_file = restore_dir / "backup_info.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            backup_logger.info(f"Backup {backup['name']} extraído para restauração")
            
            return {
                'success': True,
                'backup': backup,
                'restore_path': str(restore_dir),
                'metadata': metadata
            }
            
        except Exception as e:
            backup_logger.error(f"Erro ao restaurar backup {backup_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Retorna status dos backups"""
        try:
            total_size = sum(b.get('size', 0) for b in self.backup_history if b['status'] == 'completed')
            
            return {
                'total_backups': len(self.backup_history),
                'completed_backups': len([b for b in self.backup_history if b['status'] == 'completed']),
                'failed_backups': len([b for b in self.backup_history if b['status'] == 'failed']),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'max_backups': self.max_backups,
                'backup_dir': str(self.backup_dir),
                'last_backup': self.backup_history[-1] if self.backup_history else None
            }
            
        except Exception as e:
            backup_logger.error(f"Erro ao obter status dos backups: {e}")
            return {'error': str(e)}
    
    def _setup_automated_backup(self):
        """Configura backup automático"""
        try:
            # Backup diário às 2:00 da manhã
            schedule.every().day.at("02:00").do(self.create_backup, "automated")
            
            # Backup semanal aos domingos às 3:00
            schedule.every().sunday.at("03:00").do(self.create_backup, "weekly")
            
            # Thread para executar agendamentos
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Verifica a cada minuto
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            backup_logger.info("Backup automático configurado")
            
        except Exception as e:
            backup_logger.error(f"Erro ao configurar backup automático: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista todos os backups"""
        return self.backup_history.copy()
    
    def delete_backup(self, backup_id: int) -> bool:
        """Remove um backup específico"""
        try:
            backup = next((b for b in self.backup_history if b['id'] == backup_id), None)
            if not backup:
                return False
            
            # Remove arquivo ZIP
            if 'zip_path' in backup and Path(backup['zip_path']).exists():
                Path(backup['zip_path']).unlink()
            
            # Remove do histórico
            self.backup_history.remove(backup)
            self._save_backup_history()
            
            backup_logger.info(f"Backup {backup['name']} removido")
            return True
            
        except Exception as e:
            backup_logger.error(f"Erro ao remover backup {backup_id}: {e}")
            return False

# Instância global do gerenciador de backup
backup_manager = BackupManager()

def create_backup(backup_type: str = "manual") -> Dict[str, Any]:
    """Função helper para criar backup"""
    return backup_manager.create_backup(backup_type)

def get_backup_status() -> Dict[str, Any]:
    """Função helper para obter status dos backups"""
    return backup_manager.get_backup_status()

def list_backups() -> List[Dict[str, Any]]:
    """Função helper para listar backups"""
    return backup_manager.list_backups()
