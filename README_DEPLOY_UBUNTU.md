# 🚀 Deploy no Ubuntu VPS - Sistema de Relatórios

## ⚡ Solução Rápida para Erro 502 Bad Gateway

Se você está enfrentando o erro **502 Bad Gateway**, execute estes comandos no seu servidor Ubuntu:

```bash
# 1. Conectar ao servidor via SSH
ssh usuario@seu-servidor-ip

# 2. Baixar e executar o script de correção
wget https://raw.githubusercontent.com/seu-usuario/sistema-relatorios/main/fix-502-error.sh
chmod +x fix-502-error.sh
sudo ./fix-502-error.sh
```

## 📋 Passo a Passo Completo

### 1. Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Instalar Node.js (opcional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs
```

### 2. Clonar o Projeto

```bash
# Clonar repositório
sudo git clone https://github.com/seu-usuario/sistema-relatorios.git /var/www/sistema-relatorios

# Dar permissões corretas
sudo chown -R www-data:www-data /var/www/sistema-relatorios
sudo chmod +x /var/www/sistema-relatorios/deploy.sh
```

### 3. Configurar Variáveis de Ambiente

```bash
# Entrar no diretório
cd /var/www/sistema-relatorios

# Copiar arquivo de ambiente
sudo cp env.production .env

# Editar configurações (IMPORTANTE!)
sudo nano .env
```

**Configure estas variáveis no arquivo `.env`:**

```env
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anonima_do_supabase
SUPABASE_SERVICE_KEY=sua_chave_de_servico_do_supabase
```

### 4. Executar Deploy Automatizado

```bash
# Instalar dependências e configurar sistema
sudo ./deploy.sh install

# Fazer deploy da aplicação
sudo ./deploy.sh deploy
```

### 5. Verificar se Está Funcionando

```bash
# Verificar status
sudo ./deploy.sh status

# Testar acesso
curl http://localhost
```

## 🔧 Configuração Manual (Se o Deploy Automatizado Falhar)

### 1. Configurar Gunicorn

```bash
# Instalar Gunicorn
cd /var/www/sistema-relatorios
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install -r requirements.txt
sudo -u www-data .venv/bin/pip install gunicorn

# Criar diretórios de log
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

### 2. Configurar Nginx

```bash
# Copiar configuração
sudo cp nginx-sistema-relatorios.conf /etc/nginx/sites-available/sistema-relatorios

# Habilitar site
sudo ln -s /etc/nginx/sites-available/sistema-relatorios /etc/nginx/sites-enabled/

# Remover site padrão
sudo rm -f /etc/nginx/sites-enabled/default

# Testar e recarregar
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Configurar Systemd

```bash
# Copiar arquivo de serviço
sudo cp sistema-relatorios.service /etc/systemd/system/

# Recarregar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable sistema-relatorios
sudo systemctl start sistema-relatorios
```

## 🔍 Diagnóstico de Problemas

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

# Logs do Gunicorn
sudo tail -f /var/log/gunicorn/error.log
```

### Comandos de Troubleshooting

```bash
# Reiniciar tudo
sudo ./deploy.sh restart

# Ver status completo
sudo ./deploy.sh status

# Ver logs em tempo real
sudo ./deploy.sh logs

# Fazer rollback
sudo ./deploy.sh rollback
```

## 🚨 Soluções para Erros Comuns

### Erro 502 Bad Gateway

```bash
# 1. Verificar se o Gunicorn está rodando
sudo systemctl status sistema-relatorios

# 2. Se não estiver, iniciar
sudo systemctl start sistema-relatorios

# 3. Verificar logs
sudo journalctl -u sistema-relatorios -n 50

# 4. Verificar se a porta 8000 está aberta
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

# Se houver erro, verificar sintaxe
sudo nginx -T
```

## 🔒 Configuração de SSL (HTTPS)

### Usando Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado (substitua pelo seu domínio)
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Testar renovação automática
sudo certbot renew --dry-run
```

## 📊 Monitoramento

### Configurar Logs Rotativos

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

Se ainda tiver problemas:

1. **Execute o script de diagnóstico:**
   ```bash
   sudo ./fix-502-error.sh
   ```

2. **Verifique os logs:**
   ```bash
   sudo ./deploy.sh logs
   ```

3. **Verifique o status:**
   ```bash
   sudo ./deploy.sh status
   ```

4. **Consulte a documentação completa:**
   ```bash
   cat DEPLOY_GUIDE.md
   ```

## 📝 Checklist de Deploy

- [ ] Servidor Ubuntu atualizado
- [ ] Dependências instaladas
- [ ] Projeto clonado
- [ ] Variáveis de ambiente configuradas
- [ ] Gunicorn configurado e rodando
- [ ] Nginx configurado e rodando
- [ ] Serviço systemd configurado
- [ ] Aplicação acessível via HTTP
- [ ] SSL configurado (opcional)
- [ ] Backup automático configurado (opcional)
- [ ] Monitoramento configurado (opcional)

## 🎯 Próximos Passos

Após o deploy bem-sucedido:

1. **Configure um domínio** (se ainda não tiver)
2. **Configure SSL/HTTPS** para segurança
3. **Configure backup automático** para proteção dos dados
4. **Configure monitoramento** para acompanhar a saúde da aplicação
5. **Teste todas as funcionalidades** para garantir que tudo está funcionando

---

**💡 Dica:** Se você está enfrentando o erro 502 Bad Gateway, execute primeiro o script `fix-502-error.sh` que irá diagnosticar e corrigir automaticamente os problemas mais comuns.
