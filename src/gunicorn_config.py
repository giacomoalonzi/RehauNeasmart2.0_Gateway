#!/usr/bin/env python3
"""
Gunicorn configuration for Rehau Neasmart Gateway.
Production-ready WSGI server configuration.
"""

import multiprocessing
import os

# Server socket
bind = os.environ.get('NEASMART_API_BIND', '0.0.0.0:5001')
backlog = 2048

# Worker processes
workers = int(os.environ.get('NEASMART_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Try to use gevent, fallback to sync if not available
try:
    import gevent
    worker_class = 'gevent'  # Async worker for better performance
    worker_connections = 1000
except ImportError:
    print("WARNING: gevent not available, using sync worker class")
    worker_class = 'sync'  # Fallback to sync workers
    worker_connections = None

timeout = 30
keepalive = 2

# Worker recycling
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many seconds
max_worker_restart_time = 3600

# Server mechanics
daemon = False
pidfile = '/tmp/neasmart-gateway.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.environ.get('NEASMART_LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'neasmart-gateway'

# Server hooks
def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called just prior to forking the worker subprocess."""
    pass

def pre_exec(server):
    """Called just prior to forking off a secondary master process."""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

# StatsD integration (optional)
statsd_host = os.environ.get('STATSD_HOST')
if statsd_host:
    statsd_prefix = 'neasmart.gateway'
    
# SSL/TLS (optional)
keyfile = os.environ.get('NEASMART_SSL_KEY')
certfile = os.environ.get('NEASMART_SSL_CERT')
ssl_version = 2  # TLS
cert_reqs = 0
ca_certs = None
ciphers = 'TLSv1.2' 