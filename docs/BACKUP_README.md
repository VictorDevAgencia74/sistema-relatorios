# Sistema de Backup - Documentação

## Visão Geral

O sistema de backup foi implementado para proteger os dados e arquivos do sistema de relatórios. Ele cria backups automáticos e manuais de todos os componentes importantes do sistema. **As funcionalidades de backup estão disponíveis apenas via backend/API, não há mais interface web para backup.**

## Funcionalidades

### ✅ Backup Automático
- **Backup Diário**: Executado automaticamente às 2:00 da manhã
- **Backup Semanal**: Executado aos domingos às 3:00 da manhã
- **Configurável**: Pode ser ajustado no arquivo `backup.py`

### ✅ Backup Manual
- **API REST**: Endpoints para integração com outros sistemas
- **Python Direto**: Funções para uso programático
- **Logs Detalhados**: Registro de todas as operações

### ✅ Componentes do Backup
- **Banco de Dados**: Schemas SQL e estruturas
- **Arquivos Estáticos**: CSS, JavaScript, imagens
- **Configurações**: Requirements, variáveis de ambiente
- **Logs**: Arquivos de log do sistema

## Como Usar

### ⚠️ **IMPORTANTE**: Interface Web Removida

**A interface web para backup foi removida do frontend.** As funcionalidades de backup agora estão disponíveis apenas via:

1. **API REST** (recomendado para integrações)
2. **Python direto** (para scripts e automação)
3. **Backup automático** (executado em background)

### 1. API REST

#### Criar Backup
```bash
POST /api/backup/criar
Content-Type: application/json
Authorization: Required (apenas administradores)

{
  "tipo": "manual"
}
```

#### Ver Status
```bash
GET /api/backup/status
Authorization: Required (apenas administradores)
```

#### Listar Backups
```bash
GET /api/backup/listar
Authorization: Required (apenas administradores)
```

#### Download de Backup
```bash
GET /api/backup/download/{id}
Authorization: Required (apenas administradores)
```

### 2. Python Direto

```python
from backup import create_backup, get_backup_status, list_backups

# Criar backup
result = create_backup('manual')

# Ver status
status = get_backup_status()

# Listar backups
backups = list_backups()
```

### 3. Scripts de Automação

```python
#!/usr/bin/env python3
# backup_script.py

import schedule
import time
from backup import create_backup, get_backup_status

def backup_job():
    print("Executando backup programado...")
    result = create_backup('scheduled')
    if result['status'] == 'completed':
        print(f"Backup concluído: {result['name']}")
    else:
        print(f"Erro no backup: {result.get('error', 'Erro desconhecido')}")

# Agendar backup diário às 3:00
schedule.every().day.at("03:00").do(backup_job)

# Executar agendamentos
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Estrutura dos Backups

### Formato dos Arquivos
- **Arquivo ZIP**: Cada backup é compactado em um arquivo `.zip`
- **Nomenclatura**: `backup_YYYYMMDD_HHMMSS_tipo.zip`
- **Metadados**: Informações detalhadas em `backup_info.json`

### Conteúdo dos Backups
```
backup_20250831_215249_manual.zip
├── database/
│   ├── administradores.sql
│   ├── dp_users.sql
│   ├── porteiros.sql
│   ├── relatorios.sql
│   ├── tipos_relatorio.sql
│   └── trafego_users.sql
├── static/
│   ├── css/style.css
│   ├── images/logoAtl.jpeg
│   └── js/
│       ├── admin.js
│       ├── app.js
│       ├── dp.js
│       ├── login.js
│       └── trafego.js
├── config/
│   ├── requirements.txt
│   ├── env.example
│   └── .gitignore
└── backup_info.json
```

## Configurações

### Arquivo: `backup.py`

```python
class BackupManager:
    def __init__(self, backup_dir: str = "backups", max_backups: int = 30):
        # backup_dir: Diretório onde os backups são salvos
        # max_backups: Número máximo de backups mantidos
```

### Configurações de Backup
```python
self.backup_config = {
    'database': True,    # Backup do banco de dados
    'files': True,       # Backup de arquivos estáticos
    'logs': True,        # Backup de logs
    'config': True       # Backup de configurações
}
```

## Monitoramento

### Logs
- **Arquivo**: Logs do sistema
- **Nível**: INFO para operações normais, ERROR para problemas
- **Formato**: Timestamp + Operação + Status

### Histórico
- **Arquivo**: `backups/backup_history.json`
- **Conteúdo**: Lista completa de todos os backups
- **Informações**: ID, nome, tipo, timestamp, status, tamanho

## Manutenção

### Limpeza Automática
- **Configuração**: `max_backups = 30` (padrão)
- **Processo**: Remove automaticamente backups antigos
- **Critério**: Mantém os 30 backups mais recentes

### Limpeza Manual
```python
from backup import backup_manager

# Remover backup específico
backup_manager.delete_backup(backup_id)

# Verificar espaço usado
status = backup_manager.get_backup_status()
print(f"Espaço total: {status['total_size_mb']} MB")
```

## Solução de Problemas

### Problema: Pasta de backups vazia
**Solução**: Verificar se o sistema está sendo executado e se há permissões de escrita

### Problema: Backup falha
**Solução**: Verificar logs e arquivos de configuração

### Problema: Erro de permissão
**Solução**: Verificar permissões de escrita na pasta de backups

### Problema: API retorna erro 403
**Solução**: Verificar se o usuário tem privilégios de administrador

## Segurança

### Acesso
- **Apenas Administradores**: Todas as operações de backup requerem privilégios de admin
- **Autenticação**: Verificação de sessão em todas as rotas
- **Logs**: Registro de todas as operações para auditoria

### Dados
- **Compactação**: Backups são compactados para economizar espaço
- **Validação**: Verificação de integridade dos arquivos
- **Isolamento**: Backups são armazenados em diretório separado

## Backup Automático

### Agendamento
```python
def _setup_automated_backup(self):
    # Backup diário às 2:00 da manhã
    schedule.every().day.at("02:00").do(self.create_backup, "automated")
    
    # Backup semanal aos domingos às 3:00
    schedule.every().sunday.at("03:00").do(self.create_backup, "weekly")
```

### Thread de Execução
- **Processo**: Executa em background
- **Verificação**: A cada minuto
- **Logs**: Registra todas as execuções automáticas

## Restauração

### Função de Restauração
```python
from backup import backup_manager

# Restaurar backup específico
result = backup_manager.restore_backup(backup_id)

if result['success']:
    print(f"Backup restaurado em: {result['restore_path']}")
else:
    print(f"Erro: {result['error']}")
```

### Processo de Restauração
1. **Seleção**: Escolher backup pelo ID
2. **Validação**: Verificar integridade
3. **Extração**: Descompactar arquivos
4. **Metadados**: Ler informações do backup
5. **Disponibilização**: Arquivos prontos para uso

## Integração com Outros Sistemas

### Webhook para Backup
```python
import requests

def notify_backup_complete(backup_info):
    webhook_url = "https://seu-sistema.com/webhook/backup"
    payload = {
        "event": "backup_completed",
        "backup_id": backup_info['id'],
        "backup_name": backup_info['name'],
        "timestamp": backup_info['timestamp'],
        "size_mb": backup_info['size'] / (1024 * 1024)
    }
    
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        print("Notificação enviada com sucesso")
    else:
        print(f"Erro ao enviar notificação: {response.status_code}")
```

### Monitoramento Externo
```python
# Verificar status periodicamente
import time
from backup import get_backup_status

def monitor_backup_system():
    while True:
        status = get_backup_status()
        
        # Alertar se não há backups recentes
        if status['last_backup']:
            last_backup_time = datetime.fromisoformat(status['last_backup']['timestamp'])
            days_since_backup = (datetime.now() - last_backup_time).days
            
            if days_since_backup > 2:
                print(f"ALERTA: Último backup há {days_since_backup} dias!")
        
        time.sleep(3600)  # Verificar a cada hora
```

## Recomendações

### Frequência
- **Desenvolvimento**: Backup manual antes de mudanças importantes
- **Produção**: Manter backups automáticos ativos
- **Testes**: Verificar restauração periodicamente

### Armazenamento
- **Local**: Pasta `backups/` no servidor
- **Externo**: Considerar backup em nuvem ou servidor remoto
- **Retenção**: Ajustar `max_backups` conforme necessidade

### Monitoramento
- **Logs**: Verificar regularmente os logs de backup
- **Espaço**: Monitorar uso de disco
- **Testes**: Testar restauração periodicamente
- **API**: Monitorar endpoints de backup para falhas

### Automação
- **Scripts**: Criar scripts para backup programado
- **Webhooks**: Configurar notificações automáticas
- **Monitoramento**: Implementar verificação de saúde do sistema

## Suporte

Para problemas ou dúvidas sobre o sistema de backup:

1. **Verificar logs** do sistema
2. **Consultar** este documento
3. **Testar** funcionalidades via API
4. **Verificar** autenticação e permissões
5. **Contatar** equipe de desenvolvimento

---

**Última atualização**: Agosto 2025  
**Versão**: 2.0 (Frontend removido)  
**Autor**: Sistema de Relatórios  
**Nota**: Interface web removida - backup disponível apenas via API e Python
