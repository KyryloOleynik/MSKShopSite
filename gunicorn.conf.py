bind = "0.0.0.0:8000"  # Слушаем порт 8000 на всех интерфейсах
workers = 3
worker_class = "sync"
accesslog = "/www/wwwroot/msk52.shop/SmartZamovProj/access.log"
errorlog = "/www/wwwroot/msk52.shop/SmartZamovProj/error.log"
loglevel = "info"