#!/bin/bash

# Script de deploy para Sistema de Relatórios
# Uso: ./deploy.sh [ambiente]
# Exemplo: ./deploy.sh production

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
APP_NAME="sistema-relatorios"
APP_DIR="/var/www/$APP_NAME"
SERVICE_NAME="sistema-relatorios"
NGINX_SITE="sistema-relatorios"
BACKUP_DIR="/var/backups/$APP_NAME"

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

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Este script deve ser executado como root (use sudo)"
    exit 1
fi

# Função para instalar dependências do sistema
install_system_dependencies() {
    log "Instalando dependências do sistema..."
    
    apt update
    apt install -y python3 python3-pip python3-venv nginx postgresql-client git curl
    
    # Instalar Node.js (se necessário para build de assets)
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    
    success "Dependências do sistema instaladas"
}

# Função para criar estrutura de diretórios
create_directories() {
    log "Criando estrutura de diretórios..."
    
    mkdir -p $APP_DIR
    mkdir -p /var/log/gunicorn
    mkdir -p /var/run/gunicorn
    mkdir -p $BACKUP_DIR
    
    # Definir permissões
    chown -R www-data:www-data $APP_DIR
    chown -R www-data:www-data /var/log/gunicorn
    chown -R www-data:www-data /var/run/gunicorn
    
    success "Estrutura de diretórios criada"
}

# Função para configurar ambiente virtual
setup_virtualenv() {
    log "Configurando ambiente virtual..."
    
    cd $APP_DIR
    
    # Criar ambiente virtual se não existir
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    # Ativar ambiente virtual e instalar dependências
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    
    success "Ambiente virtual configurado"
}

# Função para configurar Nginx
setup_nginx() {
    log "Configurando Nginx..."
    
    # Copiar configuração do Nginx
    cp nginx-sistema-relatorios.conf /etc/nginx/sites-available/$NGINX_SITE
    
    # Criar link simbólico se não existir
    if [ ! -L /etc/nginx/sites-enabled/$NGINX_SITE ]; then
        ln -s /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
    fi
    
    # Remover site padrão se existir
    if [ -L /etc/nginx/sites-enabled/default ]; then
        rm /etc/nginx/sites-enabled/default
    fi
    
    # Testar configuração do Nginx
    nginx -t
    
    # Recarregar Nginx
    systemctl reload nginx
    
    success "Nginx configurado"
}

# Função para configurar systemd
setup_systemd() {
    log "Configurando serviço systemd..."
    
    # Copiar arquivo de serviço
    cp sistema-relatorios.service /etc/systemd/system/
    
    # Recarregar systemd
    systemctl daemon-reload
    
    # Habilitar serviço
    systemctl enable $SERVICE_NAME
    
    success "Serviço systemd configurado"
}

# Função para fazer backup
backup_app() {
    log "Fazendo backup da aplicação..."
    
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    if [ -d $APP_DIR ]; then
        tar -czf $BACKUP_FILE -C /var/www $APP_NAME
        success "Backup criado: $BACKUP_FILE"
    else
        warning "Diretório da aplicação não encontrado, pulando backup"
    fi
}

# Função para deploy da aplicação
deploy_app() {
    log "Fazendo deploy da aplicação..."
    
    # Parar serviço se estiver rodando
    if systemctl is-active --quiet $SERVICE_NAME; then
        log "Parando serviço..."
        systemctl stop $SERVICE_NAME
    fi
    
    # Fazer backup
    backup_app
    
    # Copiar arquivos da aplicação
    log "Copiando arquivos da aplicação..."
    cp -r . $APP_DIR/
    
    # Configurar permissões
    chown -R www-data:www-data $APP_DIR
    chmod +x $APP_DIR/deploy.sh
    
    # Configurar arquivo de ambiente
    if [ -f "env.production" ]; then
        cp env.production $APP_DIR/.env
        chown www-data:www-data $APP_DIR/.env
        chmod 600 $APP_DIR/.env
    fi
    
    # Configurar ambiente virtual
    setup_virtualenv
    
    # Iniciar serviço
    log "Iniciando serviço..."
    systemctl start $SERVICE_NAME
    
    # Verificar status
    sleep 5
    if systemctl is-active --quiet $SERVICE_NAME; then
        success "Serviço iniciado com sucesso"
    else
        error "Falha ao iniciar serviço"
        systemctl status $SERVICE_NAME
        exit 1
    fi
}

# Função para verificar status
check_status() {
    log "Verificando status dos serviços..."
    
    echo "=== Status do Gunicorn ==="
    systemctl status $SERVICE_NAME --no-pager
    
    echo -e "\n=== Status do Nginx ==="
    systemctl status nginx --no-pager
    
    echo -e "\n=== Portas em uso ==="
    netstat -tlnp | grep -E ':(80|443|8000)'
    
    echo -e "\n=== Logs recentes do Gunicorn ==="
    journalctl -u $SERVICE_NAME -n 20 --no-pager
}

# Função para mostrar logs
show_logs() {
    log "Mostrando logs do serviço..."
    journalctl -u $SERVICE_NAME -f
}

# Função para restart
restart_services() {
    log "Reiniciando serviços..."
    
    systemctl restart $SERVICE_NAME
    systemctl restart nginx
    
    success "Serviços reiniciados"
}

# Função para rollback
rollback() {
    log "Fazendo rollback..."
    
    # Parar serviço
    systemctl stop $SERVICE_NAME
    
    # Encontrar último backup
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/backup_*.tar.gz | head -n1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restaurando backup: $LATEST_BACKUP"
        tar -xzf $LATEST_BACKUP -C /var/www/
        chown -R www-data:www-data $APP_DIR
        
        # Iniciar serviço
        systemctl start $SERVICE_NAME
        success "Rollback concluído"
    else
        error "Nenhum backup encontrado para rollback"
        exit 1
    fi
}

# Menu principal
case "${1:-deploy}" in
    "install")
        install_system_dependencies
        create_directories
        setup_nginx
        setup_systemd
        success "Instalação concluída!"
        ;;
    "deploy")
        deploy_app
        success "Deploy concluído!"
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs
        ;;
    "restart")
        restart_services
        ;;
    "rollback")
        rollback
        ;;
    *)
        echo "Uso: $0 {install|deploy|status|logs|restart|rollback}"
        echo ""
        echo "Comandos disponíveis:"
        echo "  install  - Instalar dependências e configurar sistema"
        echo "  deploy   - Fazer deploy da aplicação"
        echo "  status   - Verificar status dos serviços"
        echo "  logs     - Mostrar logs em tempo real"
        echo "  restart  - Reiniciar serviços"
        echo "  rollback - Fazer rollback para versão anterior"
        exit 1
        ;;
esac
