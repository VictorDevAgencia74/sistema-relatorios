# Guia de Deploy - Sistema de Relatórios

Este guia explica como fazer o deploy da aplicação Sistema de Relatórios em um servidor VPS Ubuntu com Nginx.

## 📋 Pré-requisitos

- Servidor VPS Ubuntu 20.04+ ou 22.04+
- Acesso root ou sudo
- Domínio configurado (opcional, mas recomendado)
- Certificado SSL (opcional, mas recomendado)

## 🚀 Instalação Rápida

### 1. Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Instalar Node.js (para build de assets, se necessário)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs
```

### 2. Clonar e Configurar a Aplicação

```bash
# Clonar repositório
sudo git clone https://github.com/seu-usuario/sistema-relatorios.git /var/www/sistema-relatorios

# Dar permissões corretas
sudo chown -R www-data:www-data /var/www/sistema-relatorios
sudo chmod +x /var/www/sistema-relatorios/deploy.sh
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cd /var/www/sistema-relatorios
sudo cp env.production .env

# Editar configurações
sudo nano .env
```

**Configurações importantes no arquivo `.env`:**

```env
# Configurações da aplicação
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_super_segura_aqui_123456789

# Configurações do Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anonima_do_supabase
SUPABASE_SERVICE_KEY=sua_chave_de_servico_do_supabase
```

### 4. Executar Deploy Automatizado

```bash
# Executar script de deploy
cd /var/www/sistema-relatorios
sudo ./deploy.sh install
sudo ./deploy.sh deploy
```

## 🔧 Configuração Manual (Alternativa)

Se preferir configurar manualmente:

### 1. Configurar Gunicorn

```bash
# Instalar Gunicorn
sudo -u www-data /var/www/sistema-relatorios/.venv/bin/pip install gunicorn

# Copiar configuração
sudo cp gunicorn.conf.py /var/www/sistema-relatorios/

# Criar diretórios de log
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

### 2. Configurar Nginx

```bash
# Copiar configuração do Nginx
sudo cp nginx-sistema-relatorios.conf /etc/nginx/sites-available/sistema-relatorios

# Habilitar site
sudo ln -s /etc/nginx/sites-available/sistema-relatorios /etc/nginx/sites-enabled/

# Remover site padrão
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 3. Configurar Systemd

```bash
# Copiar arquivo de serviço
sudo cp sistema-relatorios.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar serviço
sudo systemctl enable sistema-relatorios
sudo systemctl start sistema-relatorios
```

## 🔍 Verificação e Troubleshooting

### Verificar Status dos Serviços

```bash
# Status do Gunicorn
sudo systemctl status sistema-relatorios

# Status do Nginx
sudo systemctl status nginx

# Verificar portas
sudo netstat -tlnp | grep -E ':(80|443|8000)'
```

### Verificar Logs

```bash
# Logs do Gunicorn
sudo journalctl -u sistema-relatorios -f

# Logs do Nginx
sudo tail -f /var/log/nginx/sistema-relatorios.error.log
sudo tail -f /var/log/nginx/sistema-relatorios.access.log

# Logs do Gunicorn
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/gunicorn/access.log
```

### Comandos Úteis

```bash
# Reiniciar serviços
sudo ./deploy.sh restart

# Ver status completo
sudo ./deploy.sh status

# Ver logs em tempo real
sudo ./deploy.sh logs

# Fazer rollback
sudo ./deploy.sh rollback
```

## 🔒 Configuração de SSL (HTTPS)

### Usando Certbot (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Testar renovação automática
sudo certbot renew --dry-run
```

### Configuração Manual

1. Edite o arquivo `/etc/nginx/sites-available/sistema-relatorios`
2. Descomente a seção HTTPS
3. Configure os caminhos dos certificados SSL
4. Reinicie o Nginx: `sudo systemctl restart nginx`

## 📊 Monitoramento

### Configurar Logrotate

```bash
# Criar configuração de logrotate
sudo tee /etc/logrotate.d/sistema-relatorios << EOF
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload sistema-relatorios
    endscript
}
EOF
```

### Configurar Backup Automático

```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar linha para backup diário às 2h
0 2 * * * /var/www/sistema-relatorios/backup.py --auto
```

## 🚨 Troubleshooting Comum

### Erro 502 Bad Gateway

```bash
# Verificar se o Gunicorn está rodando
sudo systemctl status sistema-relatorios

# Verificar logs
sudo journalctl -u sistema-relatorios -n 50

# Verificar se a porta 8000 está aberta
sudo netstat -tlnp | grep 8000
```

### Erro de Permissão

```bash
# Corrigir permissões
sudo chown -R www-data:www-data /var/www/sistema-relatorios
sudo chmod -R 755 /var/www/sistema-relatorios
```

### Erro de Dependências

```bash
# Reinstalar dependências
cd /var/www/sistema-relatorios
sudo -u www-data .venv/bin/pip install -r requirements.txt
```

### Erro de Configuração do Nginx

```bash
# Testar configuração
sudo nginx -t

# Verificar sintaxe
sudo nginx -T
```

## 📈 Otimizações de Performance

### Configurar Cache do Nginx

Adicione ao arquivo de configuração do Nginx:

```nginx
# Cache para arquivos estáticos
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

### Configurar Compressão

Adicione ao arquivo de configuração do Nginx:

```nginx
# Compressão gzip
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### Configurar Rate Limiting

Adicione ao arquivo de configuração do Nginx:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://127.0.0.1:8000;
}

location /login {
    limit_req zone=login burst=5 nodelay;
    proxy_pass http://127.0.0.1:8000;
}
```

## 🔄 Atualizações

### Deploy de Atualizações

```bash
# Fazer pull das atualizações
cd /var/www/sistema-relatorios
sudo git pull origin main

# Executar deploy
sudo ./deploy.sh deploy
```

### Rollback

```bash
# Fazer rollback para versão anterior
sudo ./deploy.sh rollback
```

## 📞 Suporte

Em caso de problemas:

1. Verifique os logs: `sudo ./deploy.sh logs`
2. Verifique o status: `sudo ./deploy.sh status`
3. Consulte a documentação do projeto
4. Abra uma issue no repositório

## 📝 Notas Importantes

- **Nunca** execute a aplicação como root em produção
- **Sempre** use HTTPS em produção
- **Configure** backups automáticos
- **Monitore** os logs regularmente
- **Mantenha** o sistema atualizado
- **Teste** as atualizações em ambiente de desenvolvimento primeiro
