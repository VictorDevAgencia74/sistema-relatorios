from flask import Flask, render_template, request, jsonify, session
from supabase import create_client, Client
import os
from datetime import datetime
import base64
from functools import wraps
from dotenv import load_dotenv
import logging
import traceback
import uuid
import re

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configuração do Supabase
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL ou SUPABASE_KEY não configurados")

supabase: Client = create_client(supabase_url, supabase_key)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorator para verificar autenticação
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Configurar storage do Supabase
def setup_storage():
    try:
        # Listar buckets existentes
        response = supabase.storage.list_buckets()
        buckets = response if isinstance(response, list) else getattr(response, 'buckets', [])
        bucket_names = [bucket['name'] if isinstance(bucket, dict) else bucket.name for bucket in buckets]
        
        if 'relatorios-fotos' not in bucket_names:
            # Criar bucket se não existir
            create_response = supabase.storage.create_bucket(
                'relatorios-fotos', 
                public=True
            )
            logger.info("Bucket 'relatorios-fotos' criado com sucesso")
        else:
            logger.info("Bucket 'relatorios-fotos' já existe")
            
    except Exception as e:
        logger.error(f"Erro ao configurar storage: {e}")
        print(f"Erro detalhado no storage: {traceback.format_exc()}")

# Executar configuração do storage
setup_storage()

# Middleware para logging de requests
@app.before_request
def log_request_info():
    logger.info(f'{request.method} {request.url}')
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = request.get_json()
            if data and 'fotos' in data and data['fotos']:
                logger.info(f'Recebidas {len(data["fotos"])} fotos')
        except:
            pass

# Handlers de erro
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno do servidor: {error}")
    return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Recurso não encontrado'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'message': 'Requisição inválida'}), 400

@app.route('/')
def index():
    if 'user' in session and session['user'].get('setor') == 'porteiro':
        return render_template('index.html')
    return render_template('login.html')

@app.route('/admin')
def admin():
    if 'user' not in session or session['user'].get('setor') != 'admin':
        return render_template('login.html')
    return render_template('admin.html')

@app.route('/dp')
def dp():
    if 'user' not in session or session['user'].get('setor') != 'dp':
        return render_template('login.html')
    return render_template('dp.html')

@app.route('/trafego')
def trafego():
    if 'user' not in session or session['user'].get('setor') != 'trafego':
        return render_template('login.html')
    return render_template('trafego.html')

@app.route('/api/check-auth')
def check_auth():
    if 'user' in session:
        return jsonify({'success': True, 'user': session['user']})
    else:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data or 'codigo' not in data or 'setor' not in data:
            return jsonify(
                {'success': False, 'message': 'Código e setor não fornecidos'}
            ), 400

        codigo = data.get('codigo')
        setor = data.get('setor')

        # Verificar se o usuário existe no setor correto
        if setor == 'porteiro':
            response = supabase.table('porteiros').select('*').eq(
                'codigo_acesso', codigo).eq('ativo', True).execute()
        elif setor == 'admin':
            response = supabase.table('administradores').select('*').eq(
                'codigo_acesso', codigo).eq('ativo', True).execute()
        elif setor == 'dp':
            response = supabase.table('dp_users').select('*').eq(
                'codigo_acesso', codigo).eq('ativo', True).execute()
        elif setor == 'trafego':
            response = supabase.table('trafego_users').select('*').eq(
                'codigo_acesso', codigo).eq('ativo', True).execute()
        else:
            return jsonify(
                {'success': False, 'message': 'Setor inválido'}
            ), 400

        if response.data:
            user_data = response.data[0]
            user_data['setor'] = setor
            session['user'] = user_data
            log_msg = f"Login bem-sucedido para usuário ID: {user_data['id']}"
            logger.info(log_msg)
            return jsonify({'success': True, 'user': user_data})
        else:
            logger.warning(f"Tentativa de login com código inválido: {codigo}")
            return jsonify(
                {'success': False, 'message': 'Código de acesso inválido'}
            )
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': 'Erro interno no servidor'}
        ), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify(
        {'success': True, 'message': 'Logout realizado com sucesso'}
    )

@app.route('/api/tipos-relatorio')
def get_tipos_relatorio():
    try:
        response = supabase.table('tipos_relatorio').select('*').execute()
        return jsonify(response.data)
    except Exception as e:
        logger.error(f"Erro ao buscar tipos de relatório: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': 'Erro ao buscar tipos de relatório'}
        ), 500

@app.route('/api/porteiros')
def get_porteiros():
    try:
        response = supabase.table('porteiros').select(
            'id, nome, codigo_acesso').eq('ativo', True).execute()
        return jsonify(response.data)
    except Exception as e:
        logger.error(f"Erro ao buscar porteiros: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': 'Erro ao buscar porteiros'}
        ), 500

@app.route('/api/relatorios', methods=['GET'])
def get_relatorios():
    try:
        logger.info("Recebida requisição para /api/relatorios")
        
        # Implementar lógica de filtros
        tipo = request.args.get('tipo')
        porteiro = request.args.get('porteiro')
        status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        logger.info(f"Parámetros: page={page}, per_page={per_page}")

        # Query básica primeiro
        query = supabase.table('relatorios').select('*', count='exact')

        if tipo:
            query = query.eq('tipo_id', tipo)
        if porteiro:
            query = query.eq('porteiro_id', porteiro)
        if status:
            query = query.eq('status', status)
        if data_inicio and data_fim:
            try:
                data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d')
                data_fim_ajustada = data_fim_ajustada.replace(
                    hour=23, minute=59, second=59
                )
                query = query.gte('criado_em', data_inicio).lte(
                    'criado_em', data_fim_ajustada.isoformat()
                )
            except ValueError:
                return jsonify(
                    {'success': False, 'message': 'Formato de data inválido'}
                ), 400

        # Executar query
        logger.info("Executando query no Supabase...")
        response = query.order('criado_em', desc=True).execute()
        logger.info(
            f"Query executada. {len(response.data)} registros encontrados"
        )

        # Enriquecer dados com informações das outras tabelas
        relatorios_enriquecidos = []
        for relatorio in response.data:
            relatorio_data = relatorio.copy()
            
            # Buscar informações do porteiro
            if relatorio.get('porteiro_id'):
                try:
                    porteiro_response = supabase.table('porteiros').select(
                        'nome').eq('id', relatorio['porteiro_id']).execute()
                    if porteiro_response.data:
                        relatorio_data['porteiro_nome'] = (
                            porteiro_response.data[0]['nome']
                        )
                    else:
                        relatorio_data['porteiro_nome'] = 'N/A'
                except Exception as e:
                    error_msg = f"Erro ao buscar porteiro {relatorio['porteiro_id']}: {e}"
                    logger.error(error_msg)
                    relatorio_data['porteiro_nome'] = 'Erro'
            
            # Buscar informações do tipo
            if relatorio.get('tipo_id'):
                try:
                    tipo_response = supabase.table('tipos_relatorio').select(
                        'nome').eq('id', relatorio['tipo_id']).execute()
                    if tipo_response.data:
                        relatorio_data['tipo_nome'] = (
                            tipo_response.data[0]['nome']
                        )
                    else:
                        relatorio_data['tipo_nome'] = 'N/A'
                except Exception as e:
                    error_msg = f"Erro ao buscar tipo {relatorio['tipo_id']}: {e}"
                    logger.error(error_msg)
                    relatorio_data['tipo_nome'] = 'Erro'
            
            relatorios_enriquecidos.append(relatorio_data)

        # Paginação manual
        total_count = len(relatorios_enriquecidos)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = relatorios_enriquecidos[start:end]

        return jsonify({
            'data': paginated_data,
            'count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })
    except Exception as e:
        logger.error(f"Erro ao buscar relatórios: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': f'Erro ao buscar relatórios: {str(e)}'}
        ), 500

@app.route('/api/relatorios/<id>')
def get_relatorio(id):
    try:
        print(f"Buscando relatório com ID: {id} (tipo: {type(id).__name__})")
        response = supabase.table('relatorios').select('*').eq('id', id).execute()

        if response.data:
            relatorio = response.data[0]
            print(f"Relatório encontrado: {relatorio['id']}")

            # Enriquecer dados
            if relatorio.get('porteiro_id'):
                try:
                    porteiro_response = supabase.table('porteiros').select(
                        'nome').eq('id', relatorio['porteiro_id']).execute()
                    if porteiro_response.data:
                        relatorio['porteiro_nome'] = (
                            porteiro_response.data[0]['nome']
                        )
                    else:
                        relatorio['porteiro_nome'] = 'N/A'
                except Exception as e:
                    error_msg = f"Erro ao buscar porteiro {relatorio['porteiro_id']}: {e}"
                    logger.error(error_msg)
                    relatorio['porteiro_nome'] = 'Erro'

            if relatorio.get('tipo_id'):
                try:
                    tipo_response = supabase.table('tipos_relatorio').select(
                        'nome').eq('id', relatorio['tipo_id']).execute()
                    if tipo_response.data:
                        relatorio['tipo_nome'] = tipo_response.data[0]['nome']
                    else:
                        relatorio['tipo_nome'] = 'N/A'
                except Exception as e:
                    error_msg = f"Erro ao buscar tipo {relatorio['tipo_id']}: {e}"
                    logger.error(error_msg)
                    relatorio['tipo_nome'] = 'Erro'
            
            return jsonify(relatorio)
        else:
            print(f"Relatório não encontrado para ID: {id}")
            return jsonify({'error': 'Relatório não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar relatório {id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': 'Erro ao buscar relatório'}
        ), 500

@app.route('/api/relatorios', methods=['POST'])
@require_login
def criar_relatorio():
    try:
        data = request.json
        if not data:
            return jsonify(
                {'success': False, 'message': 'Dados não fornecidos'}
            ), 400

        # Validação básica
        if 'tipo_id' not in data:
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios não fornecidos'
            }), 400

        # Preparar dados do relatório
        relatorio_data = {
            'porteiro_id': session['user']['id'],
            'tipo_id': data['tipo_id'],
            'dados': data.get('dados', {}),
            'destinatario_whatsapp': data.get('destinatario_whatsapp', ''),
            'status': 'PENDENTE',
            'criado_em': datetime.now().isoformat()
        }

        # Processar fotos se existirem - FORMATO CORRETO
        fotos_dict = {}
        fotos_urls = []  # ✅ NOVO: Lista para retornar as URLs ao frontend
        
        if 'fotos' in data and data['fotos']:
            # Gerar UUID para a pasta (mesmo formato do exemplo)
            pasta_uuid = str(uuid.uuid4())
            timestamp = int(datetime.now().timestamp() * 1000)  # Timestamp em milissegundos
            
            for i, foto_data in enumerate(data['fotos']):
                try:
                    # Verificar se é uma string base64 válida
                    if not foto_data.get('base64', '').startswith('data:image/'):
                        logger.warning(f"Formato de foto inválido: {foto_data.get('base64', '')[:100]}...")
                        continue

                    # Decodificar a imagem base64
                    foto_base64 = foto_data.get('base64', '')
                    header, encoded = foto_base64.split(',', 1)
                    formato = header.split(';')[0].split('/')[1]

                    # Validar formato
                    if formato not in ['jpeg', 'jpg', 'png', 'gif']:
                        logger.warning(f"Formato de imagem não suportado: {formato}")
                        continue

                    dados_imagem = base64.b64decode(encoded)

                    # Nome do arquivo no formato CORRETO: timestamp_fotoN.ext
                    nome_arquivo = f"{timestamp}_foto{i+1}.{formato}"
                    caminho_completo = f"{pasta_uuid}/{nome_arquivo}"

                    # Fazer upload para o Supabase Storage
                    upload_response = supabase.storage.from_('relatorios-fotos').upload(
                        caminho_completo,
                        dados_imagem,
                        {"content-type": f"image/{formato}"}
                    )

                    if hasattr(upload_response, 'error') and upload_response.error:
                        logger.error(f"Erro no upload da foto {i}: {upload_response.error}")
                        continue

                    # Gerar URL pública no formato CORRETO (sem parâmetros)
                    public_url = f"https://{supabase_url.split('//')[-1]}/storage/v1/object/public/relatorios-fotos/{caminho_completo}"
                    
                    # Salvar no dicionário com chave FOTO1, FOTO2, ...
                    chave = f"FOTO{i+1}"
                    if public_url:
                        fotos_dict[chave] = public_url
                        
                        # ✅ NOVO: Adicionar à lista de URLs para retorno ao frontend
                        fotos_urls.append({
                            'url': public_url,
                            'indice': i + 1,
                            'placeholder': f"FOTO{i+1}",
                            'campoNome': foto_data.get('campoNome', ''),
                            'fileName': foto_data.get('fileName', '')
                        })
                        
                        logger.info(f"{chave}: {public_url}")
                    else:
                        logger.error(f"URL pública não encontrada para {caminho_completo}")

                except Exception as e:
                    logger.error(f"Erro ao processar foto {i}: {e}")
                    logger.error(traceback.format_exc())
                    continue

        if fotos_dict:
            relatorio_data['fotos'] = fotos_dict
            logger.info(f"URLs das fotos para salvar: {fotos_dict}")

        # Inserir no banco de dados
        response = supabase.table('relatorios').insert(relatorio_data).execute()

        if response.data:
            log_msg = (
                f"Relatório criado com sucesso: ID {response.data[0]['id']}"
            )
            logger.info(log_msg)
            
            # ✅ NOVO: Retornar as URLs das fotos no formato esperado pelo frontend
            return jsonify({
                'success': True, 
                'id': response.data[0]['id'],
                'fotos_salvas': len(fotos_dict),
                'fotosUrls': fotos_urls,  # ✅ Isso é o que o frontend precisa
                'message': 'Relatório criado com sucesso'
            })
        else:
            logger.error("Erro ao criar relatório no banco de dados")
            return jsonify(
                {'success': False, 'message': 'Erro ao criar relatório'}
            ), 500
            
    except Exception as e:
        logger.error(f"Erro ao criar relatório: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Erro interno ao criar relatório'
        }), 500
            
    except Exception as e:
        logger.error(f"Erro ao criar relatório: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Erro interno ao criar relatório'
        }), 500

@app.route('/api/relatorios/<id>/status', methods=['PUT'])
def atualizar_status(id):
    try:
        data = request.json
        if not data or 'status' not in data:
            return jsonify(
                {'success': False, 'message': 'Status não fornecido'}
            ), 400

        novo_status = data.get('status')

        # Validar status
        if novo_status not in ['PENDENTE', 'EM_DP', 'EM_TRAFEGO', 'COBRADO']:
            return jsonify(
                {'success': False, 'message': 'Status inválido'}
            ), 400

        # Adicionar dados adicionais se necessário
        update_data = {'status': novo_status}
        
        if 'valor' in data:
            update_data['valor'] = data['valor']
        if 'motorista' in data:
            update_data['motorista'] = data['motorista']
        if 'documentos' in data:
            update_data['documentos'] = data['documentos']

        response = supabase.table('relatorios').update(
            update_data).eq('id', id).execute()

        if response.data:
            log_msg = f"Status do relatório {id} atualizado para {novo_status}"
            logger.info(log_msg)
            return jsonify({'success': True})
        else:
            return jsonify(
                {'success': False, 'message': 'Relatório não encontrado'}
            ), 404
    except Exception as e:
        logger.error(f"Erro ao atualizar status do relatório {id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': 'Erro ao atualizar status'}
        ), 500

@app.route('/api/estatisticas')
def get_estatisticas():
    try:
        # Implementar lógica de estatísticas
        tipo = request.args.get('tipo')
        porteiro = request.args.get('porteiro')
        status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        query = supabase.table('relatorios').select('*', count='exact')

        if tipo:
            query = query.eq('tipo_id', tipo)
        if porteiro:
            query = query.eq('porteiro_id', porteiro)
        if status:
            query = query.eq('status', status)
        if data_inicio and data_fim:
            try:
                data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d')
                data_fim_ajustada = data_fim_ajustada.replace(
                    hour=23, minute=59, second=59
                )
                query = query.gte('criado_em', data_inicio).lte(
                    'criado_em', data_fim_ajustada.isoformat()
                )
            except ValueError:
                return jsonify(
                    {'success': False, 'message': 'Formato de data inválido'}
                ), 400

        response = query.execute()
        total = response.count or 0

        # Contagem por status
        status_query = supabase.table('relatorios').select('status')

        if tipo:
            status_query = status_query.eq('tipo_id', tipo)
        if porteiro:
            status_query = status_query.eq('porteiro_id', porteiro)
        if data_inicio and data_fim:
            try:
                data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d')
                data_fim_ajustada = data_fim_ajustada.replace(
                    hour=23, minute=59, second=59
                )
                status_query = status_query.gte(
                    'criado_em', data_inicio
                ).lte('criado_em', data_fim_ajustada.isoformat())
            except ValueError:
                return jsonify(
                    {'success': False, 'message': 'Formato de data inválido'}
                ), 400

        status_response = status_query.execute()

        estatisticas_status = {
            'PENDENTE': 0,
            'EM_DP': 0,
            'EM_TRAFEGO': 0,
            'COBRADO': 0
        }
        for relatorio in status_response.data:
            status = relatorio.get('status', 'PENDENTE')
            estatisticas_status[status] = (
                estatisticas_status.get(status, 0) + 1
            )

        return jsonify({
            'total': total,
            'por_status': estatisticas_status
        })
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': 'Erro ao buscar estatísticas'}
        ), 500

@app.route('/api/exportar/html')
def exportar_html():
    try:
        # Implementar lógica de exportação HTML
        tipo = request.args.get('tipo')
        porteiro = request.args.get('porteiro')
        status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        query = supabase.table('relatorios').select('*')

        if tipo:
            query = query.eq('tipo_id', tipo)
        if porteiro:
            query = query.eq('porteiro_id', porteiro)
        if status:
            query = query.eq('status', status)
        if data_inicio and data_fim:
            try:
                data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d')
                data_fim_ajustada = data_fim_ajustada.replace(
                    hour=23, minute=59, second=59
                )
                query = query.gte('criado_em', data_inicio).lte(
                    'criado_em', data_fim_ajustada.isoformat()
                )
            except ValueError:
                return jsonify(
                    {'success': False, 'message': 'Formato de data inválido'}
                ), 400

        query = query.order('criado_em', desc=True)
        response = query.execute()

        # Enriquecer dados para o template
        relatorios_enriquecidos = []
        for relatorio in response.data:
            relatorio_data = relatorio.copy()
            
            if relatorio.get('porteiro_id'):
                porteiro_response = supabase.table('porteiros').select(
                    'nome').eq('id', relatorio['porteiro_id']).execute()
                if porteiro_response.data:
                    relatorio_data['porteiro_nome'] = (
                        porteiro_response.data[0]['nome']
                    )
                else:
                    relatorio_data['porteiro_nome'] = 'N/A'
            
            if relatorio.get('tipo_id'):
                tipo_response = supabase.table('tipos_relatorio').select(
                    'nome').eq('id', relatorio['tipo_id']).execute()
                if tipo_response.data:
                    relatorio_data['tipo_nome'] = tipo_response.data[0]['nome']
                else:
                    relatorio_data['tipo_nome'] = 'N/A'
            
            relatorios_enriquecidos.append(relatorio_data)

        # Gerar HTML
        html_content = render_template(
            'export_template.html', relatorios=relatorios_enriquecidos
        )
        return html_content
    except Exception as e:
        logger.error(f"Erro ao exportar relatórios: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {'success': False, 'message': 'Erro ao exportar relatórios'}
        ), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
