# Configuração do Gunicorn para produção
import multiprocessing
import os

# Configurações básicas
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Configurações de logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configurações de processo
daemon = False
pidfile = "/var/run/gunicorn/sistema-relatorios.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Configurações de ambiente
raw_env = [
    'FLASK_ENV=production',
    'FLASK_APP=app.py'
]

# Configurações de SSL (se necessário)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

def when_ready(server):
    server.log.info("Servidor Gunicorn iniciado e pronto para receber conexões")

def worker_int(worker):
    worker.log.info("Worker recebeu SIGINT ou SIGQUIT")

def pre_fork(server, worker):
    server.log.info("Worker %s será iniciado", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker %s foi iniciado", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker %s foi inicializado", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker %s foi abortado", worker.pid)
