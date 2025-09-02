# Sistema de Números de OS (Ordem de Serviço)

## Visão Geral

Este sistema resolve o problema dos IDs UUID muito longos das ocorrências, implementando um campo `numero_os` mais amigável e fácil de referenciar.

## Formato do Número de OS

O número de OS segue o padrão: **OS-YYYY-NNNNNN**

- **OS**: Prefixo fixo "Ordem de Serviço"
- **YYYY**: Ano atual (ex: 2024)
- **NNNNNN**: Número sequencial com 6 dígitos (ex: 000001)

**Exemplos:**
- `OS-2024-000001`
- `OS-2024-000002`
- `OS-2024-000123`

## Funcionalidades Implementadas

### 1. Geração Automática
- ✅ Números são gerados automaticamente ao criar novos relatórios
- ✅ Sequência única e incremental por ano
- ✅ Trigger automático no banco de dados

### 2. Busca e Filtros
- ✅ Buscar relatório por número de OS: `/api/relatorios/numero/OS-2024-000001`
- ✅ Filtrar listagens por número de OS
- ✅ Incluído em estatísticas e exportações

### 3. Compatibilidade
- ✅ Mantém o ID UUID original
- ✅ Não quebra funcionalidades existentes
- ✅ Campo opcional (pode ser NULL)

## Como Implementar

### Passo 1: Executar o Script de Configuração

```bash
python setup_numero_os.py
```

O script irá:
- Adicionar o campo `numero_os` na tabela
- Criar sequência e trigger automático
- Atualizar registros existentes
- Verificar se tudo está funcionando

### Passo 2: Verificar Configuração

O script verifica automaticamente se a configuração foi bem-sucedida.

### Passo 3: Testar Funcionalidade

Crie um novo relatório e verifique se o número de OS foi gerado automaticamente.

## APIs Atualizadas

### Listar Relatórios
```http
GET /api/relatorios?numero_os=OS-2024-000001
```

### Buscar por Número de OS
```http
GET /api/relatorios/numero/OS-2024-000001
```

### Estatísticas
```http
GET /api/estatisticas?numero_os=OS-2024-000001
```

### Exportação HTML
```http
GET /api/exportar/html?numero_os=OS-2024-000001
```

## Estrutura do Banco de Dados

### Nova Coluna
```sql
ALTER TABLE public.relatorios 
ADD COLUMN numero_os VARCHAR(20) UNIQUE;
```

### Índice para Performance
```sql
CREATE INDEX idx_relatorios_numero_os ON public.relatorios(numero_os);
```

### Sequência Automática
```sql
CREATE SEQUENCE public.relatorios_numero_os_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 999999
    CACHE 1;
```

### Trigger Automático
```sql
CREATE TRIGGER trigger_gerar_numero_os
    BEFORE INSERT ON public.relatorios
    FOR EACH ROW
    EXECUTE FUNCTION gerar_numero_os();
```

## Vantagens

1. **Facilidade de Referência**: Números curtos e memoráveis
2. **Organização por Ano**: Separação clara por período
3. **Sequência Única**: Nunca duplica números
4. **Busca Rápida**: Índice otimizado para performance
5. **Compatibilidade**: Não afeta sistema existente

## Casos de Uso

### Para Porteiros
- Referenciar ocorrências por número simples
- Comunicar números de OS para outros setores
- Acompanhar status por número amigável

### Para DP
- Buscar ocorrências específicas rapidamente
- Referenciar em documentos e comunicações
- Organizar trabalho por número de OS

### Para Tráfego
- Identificar ocorrências para cobrança
- Acompanhar status por número de referência
- Comunicar com motoristas e clientes

### Para Administradores
- Relatórios mais organizados
- Filtros mais eficientes
- Melhor rastreabilidade

## Troubleshooting

### Erro: "Campo numero_os não existe"
Execute o script de configuração:
```bash
python setup_numero_os.py
```

### Erro: "Permissão negada"
Verifique se você tem privilégios de administrador no Supabase.

### Números não estão sendo gerados
Verifique se o trigger foi criado corretamente:
```sql
SELECT * FROM information_schema.triggers 
WHERE trigger_name = 'trigger_gerar_numero_os';
```

### Sequência não está funcionando
Verifique se a sequência existe:
```sql
SELECT * FROM public.relatorios_numero_os_seq;
```

## Manutenção

### Reset da Sequência (se necessário)
```sql
ALTER SEQUENCE public.relatorios_numero_os_seq RESTART WITH 1;
```

### Limpeza de Números (se necessário)
```sql
UPDATE public.relatorios SET numero_os = NULL WHERE numero_os LIKE 'OS-2024-%';
```

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs da aplicação
2. Execute o script de verificação
3. Consulte a documentação do Supabase
4. Entre em contato com o suporte técnico

