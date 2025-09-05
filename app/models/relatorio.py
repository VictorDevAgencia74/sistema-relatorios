from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class UserBase(BaseModel):
    """Modelo base para usuários"""
    nome: str = Field(..., min_length=2, max_length=100)
    codigo_acesso: str = Field(..., min_length=4, max_length=20)
    ativo: bool = True

class Porteiro(UserBase):
    """Modelo para porteiros"""
    id: Optional[str] = None
    setor: str = "porteiro"
    
    @validator('codigo_acesso')
    def validate_codigo_acesso(cls, v):
        if not v.isalnum():
            raise ValueError('Código de acesso deve conter apenas letras e números')
        return v

class Admin(UserBase):
    """Modelo para administradores"""
    id: Optional[str] = None
    setor: str = "admin"

class DPUser(UserBase):
    """Modelo para usuários do DP"""
    id: Optional[str] = None
    setor: str = "dp"

class TrafegoUser(UserBase):
    """Modelo para usuários do tráfego"""
    id: Optional[str] = None
    setor: str = "trafego"

class TipoRelatorio(BaseModel):
    """Modelo para tipos de relatório"""
    id: Optional[int] = None
    nome: str = Field(..., min_length=2, max_length=100)
    template: str = Field(..., min_length=10)
    campos: Dict[str, Any] = Field(..., description="Campos do formulário")
    destinatario_whatsapp: Optional[str] = None
    
    @validator('destinatario_whatsapp')
    def validate_whatsapp(cls, v):
        if v is not None:
            if not re.match(r'^55\d{11}$', v):
                raise ValueError('Número de WhatsApp deve estar no formato 55DDD999999999')
        return v

class Relatorio(BaseModel):
    """Modelo para relatórios"""
    id: Optional[str] = None
    porteiro_id: str = Field(..., description="ID do porteiro")
    tipo_id: int = Field(..., description="ID do tipo de relatório")
    dados: Dict[str, Any] = Field(..., description="Dados do relatório")
    destinatario_whatsapp: str = Field(..., description="Número de WhatsApp do destinatário")
    fotos: Optional[List[str]] = Field(default=[], description="Lista de URLs das fotos")
    status: str = Field(default="PENDENTE", description="Status do relatório")
    motorista: Optional[str] = Field(None, max_length=100)
    valor: Optional[float] = Field(None, ge=0, description="Valor em reais")
    documentos: Optional[Dict[str, Any]] = Field(default={}, description="Documentos anexados")
    criado_em: Optional[datetime] = None
    enviado_em: Optional[datetime] = None
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['PENDENTE', 'EM_DP', 'EM_TRAFEGO', 'COBRADO', 'FINALIZADA']
        if v not in valid_statuses:
            raise ValueError(f'Status deve ser um dos seguintes: {", ".join(valid_statuses)}')
        return v
    
    @validator('destinatario_whatsapp')
    def validate_whatsapp(cls, v):
        if not re.match(r'^55\d{11}$', v):
            raise ValueError('Número de WhatsApp deve estar no formato 55DDD999999999')
        return v
    
    @validator('valor')
    def validate_valor(cls, v):
        if v is not None and v < 0:
            raise ValueError('Valor não pode ser negativo')
        return v

class LoginRequest(BaseModel):
    """Modelo para requisições de login"""
    codigo: str = Field(..., min_length=4, max_length=20)
    setor: str = Field(..., description="Setor do usuário")
    
    @validator('setor')
    def validate_setor(cls, v):
        valid_setores = ['porteiro', 'admin', 'dp', 'trafego']
        if v not in valid_setores:
            raise ValueError(f'Setor deve ser um dos seguintes: {", ".join(valid_setores)}')
        return v

class FileUpload(BaseModel):
    """Modelo para upload de arquivos"""
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    size: int = Field(..., gt=0, le=10*1024*1024, description="Tamanho em bytes (máx 10MB)")
    
    @validator('filename')
    def validate_filename(cls, v):
        # Remove caracteres perigosos do nome do arquivo
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f'Nome do arquivo não pode conter o caractere: {char}')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'application/pdf', 'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        if v not in allowed_types:
            raise ValueError(f'Tipo de arquivo não permitido. Tipos permitidos: {", ".join(allowed_types)}')
        return v

class RelatorioUpdate(BaseModel):
    """Modelo para atualizações de relatórios"""
    status: Optional[str] = None
    motorista: Optional[str] = None
    valor: Optional[float] = None
    documentos: Optional[Dict[str, Any]] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['PENDENTE', 'EM_DP', 'EM_TRAFEGO', 'COBRADO', 'FINALIZADA']
            if v not in valid_statuses:
                raise ValueError(f'Status deve ser um dos seguintes: {", ".join(valid_statuses)}')
        return v
    
    @validator('valor')
    def validate_valor(cls, v):
        if v is not None and v < 0:
            raise ValueError('Valor não pode ser negativo')
        return v

class SearchFilters(BaseModel):
    """Modelo para filtros de busca"""
    status: Optional[str] = None
    tipo_id: Optional[int] = None
    porteiro_id: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['PENDENTE', 'EM_DP', 'EM_TRAFEGO', 'COBRADO', 'FINALIZADA']
            if v not in valid_statuses:
                raise ValueError(f'Status deve ser um dos seguintes: {", ".join(valid_statuses)}')
        return v

class APIResponse(BaseModel):
    """Modelo para respostas da API"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Mensagem não pode estar vazia')
        return v.strip()

class ErrorResponse(APIResponse):
    """Modelo para respostas de erro"""
    success: bool = False
    error_code: str = Field(..., description="Código do erro")
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(APIResponse):
    """Modelo para respostas de sucesso"""
    success: bool = True
