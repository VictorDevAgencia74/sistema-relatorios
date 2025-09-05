import re
import bleach
import hashlib
import secrets
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging

# Configurar logging para segurança
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

class SecurityManager:
    """Gerenciador de segurança do sistema"""
    
    def __init__(self):
        # Configurações de segurança
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_timeout = timedelta(hours=8)
        
        # Cache de tentativas de login
        self.login_attempts = {}
        self.locked_accounts = {}
        
        # Configurações de sanitização
        self.allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3'
        ]
        self.allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title']
        }
        
        # Padrões de validação
        self.validation_patterns = {
            'whatsapp': r'^55\d{11}$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
            'cpf': r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            'cnpj': r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'
        }
    
    def sanitize_input(self, data: Any, input_type: str = 'text') -> Any:
        """Sanitiza entrada de dados"""
        try:
            if data is None:
                return None
            
            if isinstance(data, str):
                return self._sanitize_string(data, input_type)
            elif isinstance(data, dict):
                return self._sanitize_dict(data)
            elif isinstance(data, list):
                return self._sanitize_list(data)
            else:
                return data
                
        except Exception as e:
            security_logger.error(f"Erro ao sanitizar entrada: {e}")
            return None
    
    def _sanitize_string(self, text: str, input_type: str) -> str:
        """Sanitiza string baseado no tipo"""
        if not text:
            return text
        
        # Remove caracteres perigosos
        dangerous_chars = ['<script>', 'javascript:', 'vbscript:', 'onload', 'onerror']
        for char in dangerous_chars:
            text = text.replace(char.lower(), '').replace(char.upper(), '')
        
        if input_type == 'html':
            # Permite HTML limitado
            text = bleach.clean(
                text,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True
            )
        elif input_type == 'filename':
            # Sanitiza nome de arquivo
            text = re.sub(r'[<>:"/\\|?*]', '_', text)
            text = text.strip()
        else:
            # Sanitização padrão (remove HTML)
            text = bleach.clean(text, tags=[], strip=True)
        
        return text.strip()
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza dicionário"""
        sanitized = {}
        for key, value in data.items():
            sanitized_key = self._sanitize_string(str(key), 'text')
            sanitized[sanitized_key] = self.sanitize_input(value)
        return sanitized
    
    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitiza lista"""
        return [self.sanitize_input(item) for item in data]
    
    def validate_input(self, data: Any, validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Valida entrada de dados"""
        errors = []
        warnings = []
        
        try:
            for field, rules in validation_rules.items():
                if field not in data:
                    if rules.get('required', False):
                        errors.append(f"Campo '{field}' é obrigatório")
                    continue
                
                value = data[field]
                
                # Validação de tipo
                if 'type' in rules:
                    if not self._validate_type(value, rules['type']):
                        errors.append(f"Campo '{field}' deve ser do tipo {rules['type']}")
                
                # Validação de tamanho
                if 'min_length' in rules and isinstance(value, str):
                    if len(value) < rules['min_length']:
                        errors.append(f"Campo '{field}' deve ter pelo menos {rules['min_length']} caracteres")
                
                if 'max_length' in rules and isinstance(value, str):
                    if len(value) > rules['max_length']:
                        errors.append(f"Campo '{field}' deve ter no máximo {rules['max_length']} caracteres")
                
                # Validação de padrão
                if 'pattern' in rules and isinstance(value, str):
                    if not re.match(rules['pattern'], value):
                        errors.append(f"Campo '{field}' não está no formato correto")
                
                # Validação de valores permitidos
                if 'allowed_values' in rules:
                    if value not in rules['allowed_values']:
                        errors.append(f"Campo '{field}' deve ser um dos seguintes: {', '.join(rules['allowed_values'])}")
                
                # Validação customizada
                if 'custom_validator' in rules:
                    custom_result = rules['custom_validator'](value)
                    if not custom_result['valid']:
                        errors.append(f"Campo '{field}': {custom_result['message']}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            security_logger.error(f"Erro na validação: {e}")
            return {
                'valid': False,
                'errors': [f"Erro interno na validação: {e}"],
                'warnings': []
            }
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Valida tipo de dado"""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'integer':
            return isinstance(value, int)
        elif expected_type == 'float':
            return isinstance(value, (int, float))
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'email':
            return isinstance(value, str) and re.match(self.validation_patterns['email'], value)
        elif expected_type == 'whatsapp':
            return isinstance(value, str) and re.match(self.validation_patterns['whatsapp'], value)
        elif expected_type == 'phone':
            return isinstance(value, str) and re.match(self.validation_patterns['phone'], value)
        elif expected_type == 'cpf':
            return isinstance(value, str) and re.match(self.validation_patterns['cpf'], value)
        elif expected_type == 'cnpj':
            return isinstance(value, str) and re.match(self.validation_patterns['cnpj'], value)
        else:
            return True
    
    def check_login_attempts(self, identifier: str) -> Dict[str, Any]:
        """Verifica tentativas de login"""
        current_time = datetime.now()
        
        # Verifica se a conta está bloqueada
        if identifier in self.locked_accounts:
            lockout_time = self.locked_accounts[identifier]
            if current_time < lockout_time:
                remaining_time = lockout_time - current_time
                return {
                    'locked': True,
                    'remaining_time': str(remaining_time).split('.')[0],
                    'attempts': 0
                }
            else:
                # Remove bloqueio expirado
                del self.locked_accounts[identifier]
                if identifier in self.login_attempts:
                    del self.login_attempts[identifier]
        
        # Retorna tentativas atuais
        attempts = self.login_attempts.get(identifier, 0)
        return {
            'locked': False,
            'remaining_time': None,
            'attempts': attempts
        }
    
    def record_login_attempt(self, identifier: str, success: bool):
        """Registra tentativa de login"""
        current_time = datetime.now()
        
        if success:
            # Reset de tentativas em caso de sucesso
            if identifier in self.login_attempts:
                del self.login_attempts[identifier]
            if identifier in self.locked_accounts:
                del self.locked_accounts[identifier]
        else:
            # Incrementa tentativas
            current_attempts = self.login_attempts.get(identifier, 0) + 1
            self.login_attempts[identifier] = current_attempts
            
            # Bloqueia conta se exceder limite
            if current_attempts >= self.max_login_attempts:
                lockout_time = current_time + self.lockout_duration
                self.locked_accounts[identifier] = lockout_time
                security_logger.warning(f"Conta bloqueada: {identifier} por {self.lockout_duration}")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Gera token seguro"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str) -> str:
        """Gera hash seguro de senha"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica senha hash"""
        try:
            salt, hash_hex = hashed.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False
    
    def validate_session(self, session_data: Dict[str, Any]) -> bool:
        """Valida sessão de usuário"""
        if not session_data or 'user' not in session_data:
            return False
        
        # Verifica timeout da sessão
        if 'created_at' in session_data:
            try:
                created_at = datetime.fromisoformat(session_data['created_at'])
                if datetime.now() - created_at > self.session_timeout:
                    return False
            except Exception:
                return False
        
        return True
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None):
        """Registra evento de segurança"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'ip_address': details.get('ip_address', 'unknown'),
            'user_agent': details.get('user_agent', 'unknown')
        }
        
        security_logger.info(f"SECURITY_EVENT: {event_type} - {log_entry}")
        
        # Aqui você pode implementar armazenamento em banco de dados
        # ou envio para sistema de monitoramento externo

# Instância global do gerenciador de segurança
security_manager = SecurityManager()

def sanitize_input(data: Any, input_type: str = 'text') -> Any:
    """Função helper para sanitização"""
    return security_manager.sanitize_input(data, input_type)

def validate_input(data: Any, validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Função helper para validação"""
    return security_manager.validate_input(data, validation_rules)

def check_login_attempts(identifier: str) -> Dict[str, Any]:
    """Função helper para verificar tentativas de login"""
    return security_manager.check_login_attempts(identifier)

def record_login_attempt(identifier: str, success: bool):
    """Função helper para registrar tentativa de login"""
    security_manager.record_login_attempt(identifier, success)
