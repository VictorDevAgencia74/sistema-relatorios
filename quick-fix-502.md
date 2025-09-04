# 🚨 Correção Rápida - Erro 502 Bad Gateway

## ⚡ Solução Imediata

Se você está enfrentando o erro **502 Bad Gateway** no seu VPS Ubuntu, execute estes comandos **na ordem exata**:

### 1. Conectar ao Servidor
```bash
ssh usuario@seu-servidor-ip
```

### 2. Verificar Status dos Serviços
```bash
# Verificar se Nginx está rodando
sudo systemctl status nginx

# Verificar se há algum processo Python rodando
ps aux | grep python
```

### 3. Parar Processos Python Antigos
```bash
# Parar todos os processos Python (se houver)
sudo pkill -f python
sudo pkill -f flask
```

### 4. Instalar Dependências
```bash
# Atualizar sistema
sudo apt update

# Instalar dependências necessárias
sudo apt install -y python3 python3-pip python3-venv nginx git

# Instalar Gunicorn globalmente (se necessário)
sudo pip3 install gunicorn
```

### 5. Configurar a Aplicação
```bash
# Navegar para o diretório da aplicação
cd /var/www/sistema-relatorios

# Se não existir, criar
sudo mkdir -p /var/www/sistema-relatorios
cd /var/www/sistema-relatorios

# Clonar ou atualizar o código
sudo git clone https://github.com/seu-usuario/sistema-relatorios.git . || sudo git pull

# Dar permissões corretas
sudo chown -R www-data:www-data /var/www/sistema-relatorios
```

### 6. Configurar Ambiente Virtual
```bash
# Criar ambiente virtual
sudo -u www-data python3 -m venv .venv

# Ativar e instalar dependências
sudo -u www-data .venv/bin/pip install --upgrade pip
sudo -u www-data .venv/bin/pip install -r requirements.txt
sudo -u www-data .venv/bin/pip install gunicorn
```

### 7. Configurar Nginx
```bash
# Criar configuração básica do Nginx
sudo tee /etc/nginx/sites-available/sistema-relatorios << 'EOF'
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
sudo ln -sf /etc/nginx/sites-available/sistema-relatorios /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 8. Configurar Variáveis de Ambiente
```bash
# Criar arquivo .env
sudo tee /var/www/sistema-relatorios/.env << 'EOF'
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_muito_segura_aqui_123456789
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anonima_do_supabase
SUPABASE_SERVICE_KEY=sua_chave_de_servico_do_supabase
EOF

# Dar permissões corretas
sudo chown www-data:www-data /var/www/sistema-relatorios/.env
sudo chmod 600 /var/www/sistema-relatorios/.env
```

### 9. Iniciar a Aplicação com Gunicorn
```bash
# Navegar para o diretório
cd /var/www/sistema-relatorios

# Iniciar Gunicorn
sudo -u www-data .venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 30 app:app
```

### 10. Testar se Funcionou
```bash
# Em outro terminal, testar
curl http://localhost

# Ou testar diretamente no navegador
# http://seu-ip-do-servidor
```

## 🔧 Se Ainda Não Funcionar

### Verificar Logs
```bash
# Logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Logs do sistema
sudo journalctl -f
```

### Verificar Portas
```bash
# Verificar se a porta 8000 está sendo usada
sudo netstat -tlnp | grep 8000

# Verificar se a porta 80 está sendo usada
sudo netstat -tlnp | grep 80
```

### Reiniciar Tudo
```bash
# Parar Gunicorn (Ctrl+C)
# Depois executar:
sudo systemctl restart nginx
sudo -u www-data /var/www/sistema-relatorios/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 30 app:app
```

## 🚀 Configuração Permanente (Systemd)

Para que a aplicação inicie automaticamente:

```bash
# Criar arquivo de serviço
sudo tee /etc/systemd/system/sistema-relatorios.service << 'EOF'
[Unit]
Description=Sistema de Relatórios
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/sistema-relatorios
Environment=PATH=/var/www/sistema-relatorios/.venv/bin
ExecStart=/var/www/sistema-relatorios/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 30 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable sistema-relatorios
sudo systemctl start sistema-relatorios

# Verificar status
sudo systemctl status sistema-relatorios
```

## ✅ Verificação Final

```bash
# Verificar se tudo está funcionando
sudo systemctl status nginx
sudo systemctl status sistema-relatorios
curl http://localhost

# Se tudo estiver OK, você verá a página da aplicação
```

---

**💡 Dica:** Se você seguir estes passos na ordem exata, o erro 502 Bad Gateway deve ser resolvido. O problema geralmente é que o Nginx não consegue se comunicar com a aplicação Flask/Gunicorn na porta 8000.
