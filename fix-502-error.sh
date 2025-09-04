#!/bin/bash

# Script para diagnosticar e corrigir erro 502 Bad Gateway
# Uso: ./fix-502-error.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log "Iniciando diagnóstico do erro 502 Bad Gateway..."

# 1. Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Este script deve ser executado como root (use sudo)"
    exit 1
fi

# 2. Verificar status do Nginx
log "Verificando status do Nginx..."
if systemctl is-active --quiet nginx; then
    success "Nginx está rodando"
else
    error "Nginx não está rodando"
    log "Iniciando Nginx..."
    systemctl start nginx
fi

# 3. Verificar configuração do Nginx
log "Verificando configuração do Nginx..."
if nginx -t; then
    success "Configuração do Nginx está OK"
else
    error "Configuração do Nginx com erro"
    log "Mostrando erros de configuração:"
    nginx -t
    exit 1
fi

# 4. Verificar se o serviço da aplicação está rodando
log "Verificando status do serviço da aplicação..."
if systemctl is-active --quiet sistema-relatorios; then
    success "Serviço da aplicação está rodando"
else
    error "Serviço da aplicação não está rodando"
    log "Tentando iniciar o serviço..."
    systemctl start sistema-relatorios
    sleep 5
    
    if systemctl is-active --quiet sistema-relatorios; then
        success "Serviço iniciado com sucesso"
    else
        error "Falha ao iniciar o serviço"
        log "Status do serviço:"
        systemctl status sistema-relatorios --no-pager
        exit 1
    fi
fi

# 5. Verificar se a porta 8000 está sendo usada
log "Verificando se a porta 8000 está sendo usada..."
if netstat -tlnp | grep -q ":8000"; then
    success "Porta 8000 está sendo usada"
    log "Processo usando a porta 8000:"
    netstat -tlnp | grep ":8000"
else
    error "Porta 8000 não está sendo usada"
    log "Verificando logs do serviço para entender o problema..."
    journalctl -u sistema-relatorios -n 20 --no-pager
    exit 1
fi

# 6. Testar conectividade local
log "Testando conectividade local na porta 8000..."
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health | grep -q "200"; then
    success "Aplicação responde na porta 8000"
else
    error "Aplicação não responde na porta 8000"
    log "Tentando conectar na porta 8000:"
    curl -v http://127.0.0.1:8000/health || true
    exit 1
fi

# 7. Verificar logs do Nginx
log "Verificando logs do Nginx..."
if [ -f /var/log/nginx/sistema-relatorios.error.log ]; then
    log "Últimas linhas do log de erro do Nginx:"
    tail -10 /var/log/nginx/sistema-relatorios.error.log
else
    warning "Log de erro do Nginx não encontrado"
fi

# 8. Verificar logs do Gunicorn
log "Verificando logs do Gunicorn..."
if [ -f /var/log/gunicorn/error.log ]; then
    log "Últimas linhas do log de erro do Gunicorn:"
    tail -10 /var/log/gunicorn/error.log
else
    warning "Log de erro do Gunicorn não encontrado"
fi

# 9. Verificar permissões
log "Verificando permissões..."
APP_DIR="/var/www/sistema-relatorios"
if [ -d "$APP_DIR" ]; then
    log "Permissões do diretório da aplicação:"
    ls -la "$APP_DIR"
    
    # Corrigir permissões se necessário
    log "Corrigindo permissões..."
    chown -R www-data:www-data "$APP_DIR"
    chmod -R 755 "$APP_DIR"
    success "Permissões corrigidas"
else
    error "Diretório da aplicação não encontrado: $APP_DIR"
    exit 1
fi

# 10. Verificar arquivo de configuração do Nginx
log "Verificando configuração do Nginx para a aplicação..."
if [ -f /etc/nginx/sites-available/sistema-relatorios ]; then
    log "Configuração do Nginx encontrada"
    log "Verificando se o proxy_pass está correto..."
    if grep -q "proxy_pass http://127.0.0.1:8000" /etc/nginx/sites-available/sistema-relatorios; then
        success "Configuração do proxy está correta"
    else
        error "Configuração do proxy está incorreta"
        log "Configuração atual:"
        grep -A 5 -B 5 "proxy_pass" /etc/nginx/sites-available/sistema-relatorios || true
    fi
else
    error "Arquivo de configuração do Nginx não encontrado"
    log "Criando configuração básica..."
    
    cat > /etc/nginx/sites-available/sistema-relatorios << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/sistema-relatorios/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Habilitar site
    ln -sf /etc/nginx/sites-available/sistema-relatorios /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Testar e recarregar
    nginx -t && systemctl reload nginx
    success "Configuração básica do Nginx criada"
fi

# 11. Reiniciar serviços
log "Reiniciando serviços..."
systemctl restart sistema-relatorios
sleep 5
systemctl restart nginx
sleep 2

# 12. Verificar se o problema foi resolvido
log "Verificando se o problema foi resolvido..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    success "Problema resolvido! Aplicação está respondendo corretamente"
else
    error "Problema ainda persiste"
    log "Testando conectividade:"
    curl -v http://localhost/ || true
    exit 1
fi

# 13. Mostrar status final
log "Status final dos serviços:"
echo "=== Status do Gunicorn ==="
systemctl status sistema-relatorios --no-pager

echo -e "\n=== Status do Nginx ==="
systemctl status nginx --no-pager

echo -e "\n=== Portas em uso ==="
netstat -tlnp | grep -E ':(80|443|8000)'

success "Diagnóstico concluído!"
