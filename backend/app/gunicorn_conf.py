# backend/app/gunicorn_conf.py

import multiprocessing
import os

# Server socket
bind = ["0.0.0.0:5555", "0.0.0.0:5556"]
backlog = 2048

# Worker processes
# Odporúčaný počet workerov: (2 * cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "api-centrum"
