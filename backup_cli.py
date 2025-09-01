#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de linha de comando para o sistema de backup
Uso: python backup_cli.py [comando] [opções]
"""

import sys
import json
from datetime import datetime
from backup import create_backup, get_backup_status, list_backups

def print_help():
    """Mostra ajuda do script"""
    print("""
Sistema de Backup - Linha de Comando
====================================

Uso: python backup_cli.py [comando]

Comandos disponíveis:
  status          - Mostra status dos backups
  list            - Lista todos os backups
  create [tipo]   - Cria um novo backup (tipo: manual, automated, weekly)
  info [id]       - Mostra informações detalhadas de um backup
  help            - Mostra esta ajuda

Exemplos:
  python backup_cli.py status
  python backup_cli.py create manual
  python backup_cli.py list
  python backup_cli.py info 1
""")

def print_status():
    """Mostra status dos backups"""
    try:
        status = get_backup_status()
        print("\n📊 STATUS DO SISTEMA DE BACKUP")
        print("=" * 40)
        print(f"Total de backups: {status['total_backups']}")
        print(f"Concluídos: {status['completed_backups']}")
        print(f"Falharam: {status['failed_backups']}")
        print(f"Espaço total: {status['total_size_mb']:.2f} MB")
        print(f"Diretório: {status['backup_dir']}")
        
        if status['last_backup']:
            last = status['last_backup']
            last_time = datetime.fromisoformat(last['timestamp'])
            print(f"\n🕒 Último backup:")
            print(f"   Nome: {last['name']}")
            print(f"   Tipo: {last['type']}")
            print(f"   Data: {last_time.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   Status: {last['status']}")
            print(f"   Tamanho: {last.get('size', 0) / 1024:.1f} KB")
        else:
            print("\n❌ Nenhum backup encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao obter status: {e}")

def print_list():
    """Lista todos os backups"""
    try:
        backups = list_backups()
        if not backups:
            print("\n❌ Nenhum backup encontrado")
            return
            
        print(f"\n📋 LISTA DE BACKUPS ({len(backups)} total)")
        print("=" * 60)
        print(f"{'ID':<3} {'Nome':<30} {'Tipo':<10} {'Data/Hora':<20} {'Status':<10} {'Tamanho':<10}")
        print("-" * 60)
        
        for backup in backups:
            timestamp = datetime.fromisoformat(backup['timestamp'])
            size_kb = backup.get('size', 0) / 1024
            status_icon = "✅" if backup['status'] == 'completed' else "❌" if backup['status'] == 'failed' else "⏳"
            
            print(f"{backup['id']:<3} {backup['name']:<30} {backup['type']:<10} {timestamp.strftime('%d/%m/%Y %H:%M'):<20} {status_icon} {backup['status']:<8} {size_kb:.1f} KB")
            
    except Exception as e:
        print(f"❌ Erro ao listar backups: {e}")

def create_new_backup(backup_type="manual"):
    """Cria um novo backup"""
    try:
        print(f"\n🔄 Criando backup do tipo '{backup_type}'...")
        result = create_backup(backup_type)
        
        if result['status'] == 'completed':
            print("✅ Backup criado com sucesso!")
            print(f"   Nome: {result['name']}")
            print(f"   ID: {result['id']}")
            print(f"   Tamanho: {result.get('size', 0) / 1024:.1f} KB")
            print(f"   Arquivo: {result.get('zip_path', 'N/A')}")
        else:
            print(f"❌ Erro ao criar backup: {result.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")

def print_backup_info(backup_id):
    """Mostra informações detalhadas de um backup"""
    try:
        backup_id = int(backup_id)
        backups = list_backups()
        backup = next((b for b in backups if b['id'] == backup_id), None)
        
        if not backup:
            print(f"❌ Backup com ID {backup_id} não encontrado")
            return
            
        print(f"\n📋 INFORMAÇÕES DO BACKUP #{backup_id}")
        print("=" * 50)
        print(f"Nome: {backup['name']}")
        print(f"Tipo: {backup['type']}")
        print(f"Status: {backup['status']}")
        
        timestamp = datetime.fromisoformat(backup['timestamp'])
        print(f"Data/Hora: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        
        if backup.get('size'):
            print(f"Tamanho: {backup['size'] / 1024:.1f} KB")
            
        if backup.get('zip_path'):
            print(f"Arquivo: {backup['zip_path']}")
            
        if backup.get('files'):
            print(f"\nArquivos incluídos ({len(backup['files'])}):")
            for file in backup['files'][:10]:  # Mostra apenas os primeiros 10
                print(f"  • {file}")
            if len(backup['files']) > 10:
                print(f"  ... e mais {len(backup['files']) - 10} arquivos")
                
        if backup.get('error'):
            print(f"\n❌ Erro: {backup['error']}")
            
    except ValueError:
        print("❌ ID do backup deve ser um número")
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print_help()
        return
        
    command = sys.argv[1].lower()
    
    if command == "help":
        print_help()
    elif command == "status":
        print_status()
    elif command == "list":
        print_list()
    elif command == "create":
        backup_type = sys.argv[2] if len(sys.argv) > 2 else "manual"
        create_new_backup(backup_type)
    elif command == "info":
        if len(sys.argv) < 3:
            print("❌ Uso: python backup_cli.py info [id]")
            return
        print_backup_info(sys.argv[2])
    else:
        print(f"❌ Comando desconhecido: {command}")
        print_help()

if __name__ == "__main__":
    main()

