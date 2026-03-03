# Guía de Despliegue Backend Django + Channels en CloudPanel (VPS)

Esta guía detalla paso a paso cómo desplegar una aplicación Django con soporte para WebSockets (Channels/Daphne) en un VPS gestionado con CloudPanel.

## Paso 1: Preparación del Servidor (Usuario Root)

Conéctate vía SSH como `root`.

1. **Instalar Redis (Requerido para WebSockets):**
   ```bash
   sudo apt update
   sudo apt install redis-server -y
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   
   # Validar instalación (Debe responder PONG)
   redis-cli ping
   ```

2. **Instalar Dependencias del Sistema para Python y MySQL:**
   Es crucial instalar estas librerías para evitar errores al compilar `mysqlclient` y crear entornos virtuales.
   *(Ajusta `python3.12` a tu versión de Python si es diferente)*.
   ```bash
   sudo apt install -y python3.12-venv python3.12-dev default-libmysqlclient-dev build-essential pkg-config
   ```

## Paso 2: Crear el Sitio en CloudPanel

1. Entra a CloudPanel -> **Sites** -> **Add Site**.
2. Selecciona **Create a Python Site**.
3. **Domain Name:** `api.tudominio.com` (o el que uses).
4. **Python Version:** Python 3.12 (o superior).
5. **App Port:** Anota el puerto que te asigna (ej. `8091`).

## Paso 3: Configurar Código y Entorno (Usuario del Sitio)

Conéctate vía SSH con el usuario del sitio creado (ej. `uat-cloudnode` o el que hayas puesto).

1. **Clonar repositorio o subir archivos:**
   Borra la carpeta vacía y clona tu repo (o usa la función Git de CloudPanel).
   *(Asegúrate de estar en `htdocs/api.tudominio.com`)*.

2. **Crear e Instalar Entorno Virtual:**
   ```bash
   cd htdocs/api.tudominio.com
   
   # Crear entorno virtual
   python3.12 -m venv venv
   
   # Activar
   source venv/bin/activate
   
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Instalar servidores de producción (si no están en requirements.txt)
   pip install gunicorn uvicorn daphne mysqlclient
   ```

3. **Configurar Variables de Entorno (`.env`):**
   Crea un archivo `.env` en la raíz del proyecto:
   ```env
   # Base de Datos (Datos de CloudPanel -> Databases)
   DB_NAME=cloudnode_db
   DB_USER=cloudnode_user
   DB_PASSWORD=tu_password
   DB_HOST=127.0.0.1
   DB_PORT=3306

   # Django
   SECRET_KEY=tu_clave_secreta_super_larga
   DEBUG=False
   ALLOWED_HOSTS=api.tudominio.com

   # Redis para Channels (WebSockets)
   CHANNEL_LAYER_REDIS=True
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379

   # CORS (Dominios permitidos del Frontend)
   CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app
   ```

4. **Configurar Gunicorn + Uvicorn:**
   Crea un archivo `gunicorn_config.py` en la raíz del proyecto para forzar el uso de Uvicorn (WebSockets) y escuchar en el puerto correcto.
   
   ```python
   import multiprocessing

   # Reemplaza 8091 con el puerto que CloudPanel asignó en la pestaña Settings
   bind = "127.0.0.1:8091"
   
   # CRUCIAL: Usar UvicornWorker para WebSockets
   worker_class = "uvicorn.workers.UvicornWorker"
   
   workers = multiprocessing.cpu_count() * 2 + 1
   
   # Logs a stdout/stderr para que CloudPanel los capture
   accesslog = "-"
   errorlog = "-"
   loglevel = "info"
   ```

## Paso 4: Base de Datos y Estáticos

Ejecuta las tareas de Django usando la ruta absoluta al Python del entorno virtual para evitar errores.

```bash
# 1. Migraciones
./venv/bin/python manage.py migrate

# 2. Recolectar archivos estáticos (CSS/JS admin)
./venv/bin/python manage.py collectstatic --noinput

# 3. Crear superusuario (Opcional)
./venv/bin/python manage.py createsuperuser
```

## Paso 5: Ejecución del Servidor

En CloudPanel, los sitios Python básicos no siempre permiten cambiar el comando de inicio en la interfaz.

### Opción A: Ejecución Manual (Prueba Rápida/Temporal)
```bash
# Ejecutar en segundo plano
nohup ./venv/bin/gunicorn -c gunicorn_config.py config.asgi:application &
```

### Opción B: Servicio Systemd (Recomendado/Permanente)
Como usuario `root`, crea un servicio: `/etc/systemd/system/misitio.service`

```ini
[Unit]
Description=Gunicorn instance to serve cloudnode
After=network.target

[Service]
User=nombre_usuario_sitio
Group=nombre_usuario_sitio
WorkingDirectory=/home/nombre_usuario_sitio/htdocs/api.tudominio.com
Environment="PATH=/home/nombre_usuario_sitio/htdocs/api.tudominio.com/venv/bin"
ExecStart=/home/nombre_usuario_sitio/htdocs/api.tudominio.com/venv/bin/gunicorn -c gunicorn_config.py config.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego activar:
```bash
sudo systemctl daemon-reload
sudo systemctl start misitio
sudo systemctl enable misitio
```

## Paso 6: Configurar Nginx (Reverse Proxy)

En CloudPanel -> Pestaña **Vhost**, reemplaza el bloque `location /` por esto para soportar WebSockets y servir estáticos correctamente:

```nginx
  # 1. Servir Estáticos del Admin
  location /static/ {
    alias /home/usuario_sitio/htdocs/api.tudominio.com/staticfiles/;
    expires max;
    access_log off;
    add_header Cache-Control "public, max-age=31536000, immutable";
  }

  # 2. Proxy a la App (HTTP + WebSockets)
  location / {
    # Puerto asignado en CloudPanel (debe coincidir con gunicorn_config.py)
    proxy_pass http://127.0.0.1:8091; 
    
    proxy_http_version 1.1;
    
    # Headers estándar
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Server $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $host;

    # --- WEBSOCKETS ---
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # Timeouts largos para SSH
    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
  }
```

Guarda y ¡Listo! Tu backend debería estar operativo con WebSockets funcionando.
