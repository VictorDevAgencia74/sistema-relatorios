# Sistema de Relatórios - Controle de Ocorrências para Portaria

Sistema completo de controle de ocorrências para portaria com telas administrativas e fluxo de usuários integrado.

## 🚀 Funcionalidades

- **Sistema de Autenticação** por código de acesso por setor
- **Criação de Relatórios** com formulários dinâmicos
- **Upload de Fotos** integrado ao Supabase Storage
- **Fluxo de Aprovação** com estados controlados
- **Integração WhatsApp** para notificações automáticas
- **Dashboard Administrativo** completo
- **Interface Responsiva** para todos os dispositivos

## 🏗️ Arquitetura

- **Backend**: Flask 2.3.3 (Python)
- **Banco de Dados**: Supabase (PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript + Bootstrap 5.3
- **Storage**: Supabase Storage para arquivos
- **Autenticação**: Sistema de sessões baseado em códigos

## 📋 Pré-requisitos

- Python 3.8+
- Conta no Supabase
- Navegador web moderno

## ⚙️ Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd sistema-relatorios
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. **Configure o banco de dados**
   - Execute os scripts SQL em `database/schema/` no seu projeto Supabase
   - Configure as tabelas necessárias

6. **Execute o sistema**
   ```bash
   python app.py
   ```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `SECRET_KEY` | Chave secreta para sessões Flask | ✅ |
| `SUPABASE_URL` | URL do seu projeto Supabase | ✅ |
| `SUPABASE_KEY` | Chave anônima do Supabase | ✅ |
| `FLASK_ENV` | Ambiente de execução | ❌ |
| `LOG_LEVEL` | Nível de logging | ❌ |

### Estrutura do Banco de Dados

O sistema utiliza as seguintes tabelas principais:

- **relatorios**: Relatórios de ocorrências
- **tipos_relatorio**: Templates de relatórios
- **porteiros**: Usuários porteiros
- **administradores**: Usuários administrativos
- **dp_users**: Usuários do departamento pessoal
- **trafego_users**: Usuários do setor de tráfego
- **arquivos_relatorio**: Arquivos anexados aos relatórios

## 👥 Usuários e Permissões

### Porteiros
- Criação e envio de relatórios
- Upload de fotos
- Visualização de histórico

### Administradores
- Gestão completa do sistema
- Criação de tipos de relatório
- Gestão de usuários
- Relatórios e estatísticas

### DP (Departamento Pessoal)
- Aprovação de relatórios
- Processamento de ocorrências
- Gestão de documentos

### Tráfego
- Gestão de relatórios de tráfego
- Aprovação de solicitações
- Controle de veículos

## 🔄 Fluxo de Trabalho

1. **Porteiro** cria relatório com fotos
2. **Sistema** envia notificação WhatsApp
3. **DP** aprova e processa
4. **Tráfego** gerencia se aplicável
5. **Sistema** marca como finalizado

## 📱 Interface

- **Login**: Autenticação por setor e código
- **Porteiro**: Formulários dinâmicos para relatórios
- **Admin**: Dashboard completo com gestão
- **DP**: Interface de aprovação e processamento
- **Tráfego**: Gestão específica de tráfego

## 🧪 Testes

Para executar os testes:

```bash
python -m pytest tests/
```

## 📊 Monitoramento

O sistema inclui:
- Logging completo de todas as operações
- Tratamento de erros abrangente
- Métricas de uso (em desenvolvimento)

## 🔒 Segurança

- Autenticação por sessão
- Controle de acesso por setor
- Validação de entrada
- Sanitização de dados
- Headers de segurança

## 🚀 Deploy

### Produção
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
python app.py
```

### Docker (em desenvolvimento)
```bash
docker build -t sistema-relatorios .
docker run -p 5000:5000 sistema-relatorios
```

## 📝 Logs

Os logs são salvos em:
- Console (desenvolvimento)
- Arquivo (produção)
- Nível configurável via `LOG_LEVEL`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte técnico:
- Abra uma issue no GitHub
- Consulte a documentação
- Entre em contato com a equipe de desenvolvimento

## 🔄 Changelog

### v1.0.0
- Sistema base completo
- Autenticação por setor
- Gestão de relatórios
- Upload de fotos
- Integração WhatsApp
- Dashboard administrativo
