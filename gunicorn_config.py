import multiprocessing

bind = "127.0.0.1:8091"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "-"
errorlog = "-"
loglevel = "info"