
Paso 1
Instalar en servidor root
sudo apt update
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

Validar
redis-cli ping

Resultado PONG Ok

Paso 2
Crear el Sitio en CloudPanel


Paso 3: Subir tu Código
Subir arcivo o clonar


Paso 4: Configurar Entorno en CloudPanel
# Base de Datos (Usa los datos que CloudPanel te dio al crear la DB)
DB_NAME=nombre_de_tu_db
DB_USER=usuario_de_tu_db
DB_PASSWORD=password_de_tu_db
DB_HOST=127.0.0.1
DB_PORT=3306

# Seguridad
SECRET_KEY=inventa_una_clave_larga_y_segura_aqui
DEBUG=False
ALLOWED_HOSTS=api.tudominio.com # Reemplaza con tu dominio real

# Redis (Importante para WebSockets)
CHANNEL_LAYER_REDIS=True
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# CORS (Importante para que tu frontend en Vercel se conecte)
CORS_ALLOWED_ORIGINS=https://tu-frontend-en-vercel.app

Paso 5: Instalar Dependencias
Instalar en root
apt update
apt install python3.12-venv -y

Instlar python dev
apt update
apt install python3.12-dev -y

previo validacion: python3 --version

En usario de web
python3 -m venv venv
source venv/bin/activate

Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

Como root instalar
apt install default-libmysqlclient-dev pkg-config -y

Instalar librerías:
pip install -r requirements.txt
pip install gunicorn daphne mysqlclient

Migrar base de datos:
/home/uat-cloudnode/htdocs/cloudnode.abitech.dev/venv/bin/python3 manage.py migrate

Recolectar estáticos:
/home/uat-cloudnode/htdocs/cloudnode.abitech.dev/venv/bin/python3 manage.py collectstatic --noinput
