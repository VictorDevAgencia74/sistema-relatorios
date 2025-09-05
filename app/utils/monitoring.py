import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import threading
import json

# Configurar logging para monitoramento
monitoring_logger = logging.getLogger('monitoring')
monitoring_logger.setLevel(logging.INFO)

class MetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        # Métricas Prometheus
        self.request_counter = Counter('http_requests_total', 'Total de requisições HTTP', ['method', 'endpoint', 'status'])
        self.request_duration = Histogram('http_request_duration_seconds', 'Duração das requisições HTTP', ['method', 'endpoint'])
        self.active_users = Gauge('active_users_total', 'Total de usuários ativos')
        self.relatorios_counter = Counter('relatorios_total', 'Total de relatórios criados', ['status', 'tipo'])
        self.file_uploads = Counter('file_uploads_total', 'Total de uploads de arquivos', ['type', 'size_bucket'])
        self.error_counter = Counter('errors_total', 'Total de erros', ['type', 'endpoint'])
        
        # Métricas customizadas
        self.custom_metrics = {
            'login_attempts': defaultdict(int),
            'api_calls': defaultdict(int),
            'storage_usage': defaultdict(float),
            'response_times': defaultdict(list),
            'user_sessions': defaultdict(datetime)
        }
        
        # Cache de métricas em tempo real
        self.real_time_metrics = {
            'requests_per_minute': deque(maxlen=60),
            'errors_per_minute': deque(maxlen=60),
            'active_sessions': 0,
            'last_request_time': None
        }
        
        # Thread para limpeza periódica
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_data, daemon=True)
        self._cleanup_thread.start()
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Registra uma requisição HTTP"""
        # Métricas Prometheus
        self.request_counter.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Métricas customizadas
        self.custom_metrics['api_calls'][f"{method} {endpoint}"] += 1
        
        # Métricas em tempo real
        current_time = datetime.now()
        self.real_time_metrics['requests_per_minute'].append(current_time)
        self.real_time_metrics['last_request_time'] = current_time
        
        # Log de requisições
        monitoring_logger.info(f"Request: {method} {endpoint} - Status: {status} - Duration: {duration:.3f}s")
    
    def record_error(self, error_type: str, endpoint: str, error_message: str):
        """Registra um erro"""
        # Métricas Prometheus
        self.error_counter.labels(type=error_type, endpoint=endpoint).inc()
        
        # Log de erros
        monitoring_logger.error(f"Error: {error_type} at {endpoint} - {error_message}")
        
        # Métricas em tempo real
        current_time = datetime.now()
        self.real_time_metrics['errors_per_minute'].append(current_time)
    
    def record_relatorio_creation(self, status: str, tipo: str):
        """Registra criação de relatório"""
        self.relatorios_counter.labels(status=status, tipo=tipo).inc()
        monitoring_logger.info(f"Relatório criado: Status={status}, Tipo={tipo}")
    
    def record_file_upload(self, file_type: str, size_bytes: int):
        """Registra upload de arquivo"""
        # Categoriza tamanho do arquivo
        if size_bytes < 1024*1024:  # < 1MB
            size_bucket = "small"
        elif size_bytes < 5*1024*1024:  # < 5MB
            size_bucket = "medium"
        else:  # >= 5MB
            size_bucket = "large"
        
        self.file_uploads.labels(type=file_type, size_bucket=size_bucket).inc()
        monitoring_logger.info(f"Arquivo enviado: Tipo={file_type}, Tamanho={size_bytes} bytes")
    
    def record_user_login(self, user_id: str, setor: str):
        """Registra login de usuário"""
        self.custom_metrics['login_attempts'][setor] += 1
        self.custom_metrics['user_sessions'][user_id] = datetime.now()
        self.active_users.inc()
        self.real_time_metrics['active_sessions'] += 1
        
        monitoring_logger.info(f"Usuário logado: ID={user_id}, Setor={setor}")
    
    def record_user_logout(self, user_id: str):
        """Registra logout de usuário"""
        if user_id in self.custom_metrics['user_sessions']:
            del self.custom_metrics['user_sessions'][user_id]
            self.active_users.dec()
            self.real_time_metrics['active_sessions'] = max(0, self.real_time_metrics['active_sessions'] - 1)
            
            monitoring_logger.info(f"Usuário deslogado: ID={user_id}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        current_time = datetime.now()
        
        # Calcula métricas em tempo real
        requests_last_minute = len([t for t in self.real_time_metrics['requests_per_minute'] 
                                  if current_time - t < timedelta(minutes=1)])
        errors_last_minute = len([t for t in self.real_time_metrics['errors_per_minute'] 
                                if current_time - t < timedelta(minutes=1)])
        
        # Calcula tempo médio de resposta
        avg_response_time = 0
        if self.custom_metrics['response_times']:
            all_times = []
            for times in self.custom_metrics['response_times'].values():
                all_times.extend(times)
            if all_times:
                avg_response_time = sum(all_times) / len(all_times)
        
        return {
            'timestamp': current_time.isoformat(),
            'real_time': {
                'requests_per_minute': requests_last_minute,
                'errors_per_minute': errors_last_minute,
                'active_sessions': self.real_time_metrics['active_sessions'],
                'last_request': self.real_time_metrics['last_request_time'].isoformat() if self.real_time_metrics['last_request_time'] else None
            },
            'totals': {
                'total_requests': sum(self.custom_metrics['api_calls'].values()),
                'total_errors': sum(self.custom_metrics['login_attempts'].values()),
                'total_logins': sum(self.custom_metrics['login_attempts'].values()),
                'active_users': len(self.custom_metrics['user_sessions'])
            },
            'performance': {
                'average_response_time': round(avg_response_time, 3),
                'uptime': self._get_uptime()
            },
            'storage': dict(self.custom_metrics['storage_usage'])
        }
    
    def _get_uptime(self) -> str:
        """Calcula tempo de atividade do sistema"""
        # Implementar cálculo de uptime baseado no primeiro request
        if self.real_time_metrics['last_request_time']:
            uptime = datetime.now() - self.real_time_metrics['last_request_time']
            return str(uptime).split('.')[0]  # Remove microssegundos
        return "N/A"
    
    def _cleanup_old_data(self):
        """Limpa dados antigos periodicamente"""
        while True:
            time.sleep(300)  # Executa a cada 5 minutos
            current_time = datetime.now()
            
            # Remove sessões antigas (mais de 24 horas)
            old_sessions = []
            for user_id, login_time in self.custom_metrics['user_sessions'].items():
                if current_time - login_time > timedelta(hours=24):
                    old_sessions.append(user_id)
            
            for user_id in old_sessions:
                del self.custom_metrics['user_sessions'][user_id]
                self.active_users.dec()
                self.real_time_metrics['active_sessions'] = max(0, self.real_time_metrics['active_sessions'] - 1)
            
            # Limpa métricas de tempo de resposta antigas
            for endpoint in list(self.custom_metrics['response_times'].keys()):
                self.custom_metrics['response_times'][endpoint] = [
                    t for t in self.custom_metrics['response_times'][endpoint]
                    if current_time - t < timedelta(hours=1)
                ]
            
            monitoring_logger.info(f"Cleanup executado: {len(old_sessions)} sessões antigas removidas")

class AlertManager:
    """Gerenciador de alertas do sistema"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alerts = []
        self.alert_thresholds = {
            'error_rate': 0.1,  # 10% de erros
            'response_time': 5.0,  # 5 segundos
            'concurrent_users': 100,  # 100 usuários simultâneos
            'storage_usage': 0.9  # 90% de uso
        }
        
        # Thread para verificação de alertas
        self._alert_thread = threading.Thread(target=self._check_alerts, daemon=True)
        self._alert_thread.start()
    
    def add_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """Adiciona um alerta"""
        alert = {
            'id': len(self.alerts) + 1,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        monitoring_logger.warning(f"ALERTA: {alert_type} - {message} (Severidade: {severity})")
        
        return alert
    
    def acknowledge_alert(self, alert_id: int):
        """Marca um alerta como reconhecido"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
                break
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos"""
        return [alert for alert in self.alerts if not alert.get('acknowledged', False)]
    
    def _check_alerts(self):
        """Verifica condições para alertas"""
        while True:
            time.sleep(60)  # Verifica a cada minuto
            
            try:
                metrics = self.metrics.get_metrics_summary()
                
                # Verifica taxa de erro
                if metrics['real_time']['errors_per_minute'] > 0 and metrics['real_time']['requests_per_minute'] > 0:
                    error_rate = metrics['real_time']['errors_per_minute'] / metrics['real_time']['requests_per_minute']
                    if error_rate > self.alert_thresholds['error_rate']:
                        self.add_alert(
                            'high_error_rate',
                            f'Taxa de erro alta: {error_rate:.2%}',
                            'critical'
                        )
                
                # Verifica tempo de resposta
                if metrics['performance']['average_response_time'] > self.alert_thresholds['response_time']:
                    self.add_alert(
                        'slow_response_time',
                        f'Tempo de resposta lento: {metrics["performance"]["average_response_time"]}s',
                        'warning'
                    )
                
                # Verifica usuários simultâneos
                if metrics['real_time']['active_sessions'] > self.alert_thresholds['concurrent_users']:
                    self.add_alert(
                        'high_concurrent_users',
                        f'Muitos usuários simultâneos: {metrics["real_time"]["active_sessions"]}',
                        'info'
                    )
                
                # Verifica uso de storage
                for storage_type, usage in metrics['storage'].items():
                    if usage > self.alert_thresholds['storage_usage']:
                        self.add_alert(
                            'high_storage_usage',
                            f'Uso alto de storage {storage_type}: {usage:.2%}',
                            'warning'
                        )
                        
            except Exception as e:
                monitoring_logger.error(f"Erro ao verificar alertas: {e}")

# Instância global do coletor de métricas
metrics_collector = MetricsCollector()
alert_manager = AlertManager(metrics_collector)

def get_metrics():
    """Retorna métricas no formato Prometheus"""
    return generate_latest(), CONTENT_TYPE_LATEST

def record_request_metrics(method: str, endpoint: str, status: int, duration: float):
    """Função helper para registrar métricas de requisição"""
    metrics_collector.record_request(method, endpoint, status, duration)

def record_error_metrics(error_type: str, endpoint: str, error_message: str):
    """Função helper para registrar métricas de erro"""
    metrics_collector.record_error(error_type, endpoint, error_message)
