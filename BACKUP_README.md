# Sistema de Backup - Documentação

## Visão Geral

O sistema de backup foi implementado para proteger os dados e arquivos do sistema de relatórios. Ele cria backups automáticos e manuais de todos os componentes importantes do sistema.

## Funcionalidades

### ✅ Backup Automático
- **Backup Diário**: Executado automaticamente às 2:00 da manhã
- **Backup Semanal**: Executado aos domingos às 3:00 da manhã
- **Configurável**: Pode ser ajustado no arquivo `backup.py`

### ✅ Backup Manual
- **Interface Web**: Botões na página de administração
- **API REST**: Endpoints para integração com outros sistemas
- **Logs Detalhados**: Registro de todas as operações

### ✅ Componentes do Backup
- **Banco de Dados**: Schemas SQL e estruturas
- **Arquivos Estáticos**: CSS, JavaScript, imagens
- **Configurações**: Requirements, variáveis de ambiente
- **Logs**: Arquivos de log do sistema

## Como Usar

### 1. Interface Web (Recomendado)

1. **Acesse a página de administração** (`/admin`)
2. **Faça login como administrador**
3. **Use os botões na seção "Sistema de Backup":**
   - **Criar Backup**: Cria um novo backup manual
   - **Status**: Mostra estatísticas do sistema
   - **Listar Backups**: Abre modal com histórico completo

### 2. API REST

#### Criar Backup
```bash
POST /api/backup/criar
Content-Type: application/json

{
  "tipo": "manual"
}
```

#### Ver Status
```bash
GET /api/backup/status
```

#### Listar Backups
```bash
GET /api/backup/listar
```

#### Download de Backup
```bash
GET /api/backup/download/{id}
```

### 3. Python Direto

```python
from backup import create_backup, get_backup_status, list_backups

# Criar backup
result = create_backup('manual')

# Ver status
status = get_backup_status()

# Listar backups
backups = list_backups()
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

## Suporte

Para problemas ou dúvidas sobre o sistema de backup:

1. **Verificar logs** do sistema
2. **Consultar** este documento
3. **Testar** funcionalidades básicas
4. **Contatar** equipe de desenvolvimento

---

**Última atualização**: Agosto 2025  
**Versão**: 1.0  
**Autor**: Sistema de Relatórios
