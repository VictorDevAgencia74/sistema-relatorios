# Documentação da API - Sistema de Relatórios

## Visão Geral

Esta documentação descreve todos os endpoints da API do Sistema de Relatórios, incluindo parâmetros, respostas e exemplos de uso.

## Base URL

```
http://localhost:5000
```

## Autenticação

O sistema utiliza autenticação baseada em sessão. Todas as rotas protegidas requerem que o usuário esteja autenticado.

## Endpoints

### 1. Autenticação

#### POST /api/login
Realiza login do usuário.

**Parâmetros:**
```json
{
  "codigo": "string",
  "setor": "string"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "nome": "string",
    "codigo_acesso": "string",
    "setor": "string",
    "ativo": true
  }
}
```

**Resposta de Erro (400/401):**
```json
{
  "success": false,
  "message": "string"
}
```

#### POST /api/logout
Realiza logout do usuário.

**Resposta (200):**
```json
{
  "success": true,
  "message": "Logout realizado com sucesso"
}
```

#### GET /api/check-auth
Verifica se o usuário está autenticado.

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "nome": "string",
    "setor": "string"
  }
}
```

**Resposta de Erro (401):**
```json
{
  "success": false,
  "message": "Não autenticado"
}
```

### 2. Tipos de Relatório

#### GET /api/tipos-relatorio
Lista todos os tipos de relatório disponíveis.

**Resposta (200):**
```json
[
  {
    "id": 1,
    "nome": "string",
    "template": "string",
    "campos": {},
    "destinatario_whatsapp": "string"
  }
]
```

#### POST /api/tipos-relatorio
Cria um novo tipo de relatório (apenas admin).

**Parâmetros:**
```json
{
  "nome": "string",
  "template": "string",
  "campos": {},
  "destinatario_whatsapp": "string"
}
```

#### PUT /api/tipos-relatorio/{id}
Atualiza um tipo de relatório (apenas admin).

#### DELETE /api/tipos-relatorio/{id}
Remove um tipo de relatório (apenas admin).

### 3. Usuários

#### GET /api/porteiros
Lista todos os porteiros ativos.

**Resposta (200):**
```json
[
  {
    "id": "uuid",
    "nome": "string",
    "codigo_acesso": "string"
  }
]
```

#### GET /api/administradores
Lista todos os administradores (apenas admin).

#### GET /api/dp-users
Lista usuários do DP (apenas admin).

#### GET /api/trafego-users
Lista usuários do tráfego (apenas admin).

### 4. Relatórios

#### POST /api/relatorios
Cria um novo relatório (apenas porteiros).

**Parâmetros:**
```json
{
  "tipo_id": 1,
  "dados": {},
  "destinatario_whatsapp": "string",
  "fotos": ["string"],
  "motorista": "string",
  "valor": 0.00
}
```

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "relatorio": {
    "id": "uuid",
    "status": "PENDENTE",
    "criado_em": "datetime"
  }
}
```

#### GET /api/relatorios
Lista relatórios com filtros (apenas admin/DP/tráfego).

**Parâmetros de Query:**
- `status`: Filtro por status
- `tipo_id`: Filtro por tipo
- `porteiro_id`: Filtro por porteiro
- `data_inicio`: Data de início
- `data_fim`: Data de fim
- `limit`: Limite de resultados
- `offset`: Offset para paginação

#### GET /api/relatorios/{id}
Obtém detalhes de um relatório específico.

#### PUT /api/relatorios/{id}
Atualiza um relatório (apenas DP/tráfego).

**Parâmetros:**
```json
{
  "status": "string",
  "motorista": "string",
  "valor": 0.00,
  "documentos": {}
}
```

#### DELETE /api/relatorios/{id}
Remove um relatório (apenas admin).

### 5. Upload de Arquivos

#### POST /api/upload
Faz upload de arquivos (fotos/documentos).

**Parâmetros:**
- `file`: Arquivo a ser enviado
- `tipo`: Tipo do arquivo (foto/documento)

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "url": "string",
  "filename": "string",
  "size": 0
}
```

### 6. Estatísticas

#### GET /api/stats/relatorios
Estatísticas de relatórios (apenas admin).

**Resposta (200):**
```json
{
  "total": 0,
  "por_status": {},
  "por_tipo": {},
  "por_mes": {}
}
```

#### GET /api/stats/usuarios
Estatísticas de usuários (apenas admin).

### 7. Monitoramento

#### GET /metrics
Métricas do sistema no formato Prometheus.

#### GET /api/health
Status de saúde da aplicação.

**Resposta (200):**
```json
{
  "status": "healthy",
  "timestamp": "datetime",
  "version": "string",
  "uptime": "string"
}
```

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Parâmetros inválidos
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Acesso negado
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

## Tratamento de Erros

Todos os endpoints retornam erros no seguinte formato:

```json
{
  "success": false,
  "message": "Descrição do erro",
  "error_code": "CODIGO_ERRO",
  "details": {}
}
```

## Rate Limiting

- **Login**: Máximo 5 tentativas por 30 minutos
- **Upload**: Máximo 10 arquivos por minuto
- **API**: Máximo 100 requisições por minuto por IP

## Validação de Dados

### Relatórios
- `tipo_id`: Deve ser um ID válido de tipo de relatório
- `dados`: Objeto JSON válido
- `destinatario_whatsapp`: Formato 55DDD999999999
- `valor`: Número positivo (opcional)

### Usuários
- `nome`: 2-100 caracteres
- `codigo_acesso`: 4-20 caracteres alfanuméricos
- `setor`: Um dos valores: porteiro, admin, dp, trafego

### Arquivos
- **Tipos permitidos**: jpg, jpeg, png, gif, pdf, doc, docx
- **Tamanho máximo**: 10MB
- **Nomes**: Apenas caracteres seguros

## Exemplos de Uso

### Criar Relatório
```bash
curl -X POST http://localhost:5000/api/relatorios \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "tipo_id": 1,
    "dados": {
      "descricao": "Ocorrência na portaria",
      "local": "Entrada principal"
    },
    "destinatario_whatsapp": "5511999999999"
  }'
```

### Upload de Foto
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Cookie: session=..." \
  -F "file=@foto.jpg" \
  -F "tipo=foto"
```

### Listar Relatórios
```bash
curl -X GET "http://localhost:5000/api/relatorios?status=PENDENTE&limit=10" \
  -H "Cookie: session=..."
```

## Segurança

- Todas as entradas são sanitizadas
- Validação de tipos e formatos
- Proteção contra XSS e SQL injection
- Sessões com timeout configurável
- Logs de auditoria para todas as operações

## Suporte

Para suporte técnico ou dúvidas sobre a API:
- Abra uma issue no GitHub
- Consulte a documentação
- Entre em contato com a equipe de desenvolvimento
