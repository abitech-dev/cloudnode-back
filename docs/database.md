# Database

## Resumen
- Base de datos: MySQL
- App principal: servers
- Modelos: Server, ServerUser, TerminalSession
- Campos clave: created_at, updated_at, deleted_at
- Soft delete: usa deleted_at, no borra fisicamente

## Como funciona
- created_at: se crea una sola vez
- updated_at: se actualiza en cada save
- deleted_at: null = activo, con fecha = eliminado
- objects: solo activos
- all_objects: incluye eliminados

## Comandos basicos
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver migraciones
python manage.py showmigrations
```

## Reset de datos
```bash
# Borra todos los datos y vuelve a crear tablas (pide confirmacion)
python manage.py flush

# Lo mismo sin preguntar
python manage.py flush --noinput
```

## Migrar desde cero (manual)
```bash
# Deshacer migraciones de una app
python manage.py migrate servers zero --fake

# Aplicar migraciones otra vez
python manage.py migrate servers
```

## Soft delete en la consola
```python
from servers.models import Server

# Eliminar suave
s = Server.objects.first()
if s:
    s.soft_delete()

# Ver activos
Server.objects.all()

# Ver todos
Server.all_objects.all()
```
