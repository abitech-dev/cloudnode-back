# API

Guia rapida para consumir la API desde el frontend. Incluye rutas publicas, parametros y respuestas esperadas.

## Base URL
- Produccion y local: `/api/`

## Recursos
### Servers
Ruta base: `/api/servers/`

- `GET /api/servers/`
  - Lista servidores con usuarios anidados.
- `POST /api/servers/`
  - Crea un servidor.
- `GET /api/servers/{id}/`
  - Detalle de un servidor.
- `PUT /api/servers/{id}/`
  - Actualiza completo.
- `PATCH /api/servers/{id}/`
  - Actualiza parcial.
- `DELETE /api/servers/{id}/`
  - Elimina de forma suave (soft delete).

Campos que devuelve en Server:
- `id`, `name`, `ip`, `port`, `created_at`
- `users` (lista de usuarios)
- `last_used_at`, `total_sessions`, `average_session_time`

Ejemplo crear servidor:
```bash
POST /api/servers/
{
  "name": "Servidor 1",
  "ip": "10.0.0.1",
  "port": 22
}
```

### Historial de sesiones por servidor
- `GET /api/servers/{id}/history/`
  - Devuelve sesiones del servidor.

Campos en cada sesion:
- `id`, `server`, `user`, `username`
- `started_at`, `ended_at`, `status`, `duration`

### Server Users
Ruta base: `/api/server-users/`

- `GET /api/server-users/`
  - Lista todos los usuarios.
- `GET /api/server-users/?server_id={id}`
  - Lista usuarios de un server.
- `POST /api/server-users/`
  - Crea usuario.
- `GET /api/server-users/{id}/`
  - Detalle.
- `PUT /api/server-users/{id}/`
  - Actualiza completo.
- `PATCH /api/server-users/{id}/`
  - Actualiza parcial.
- `DELETE /api/server-users/{id}/`
  - Elimina de forma suave (soft delete).

Campos para crear usuario:
- `server` (id del servidor)
- `username`
- `auth_type` = `password` o `key`
- `password_encrypted` (si usas password)
- `private_key_encrypted` (si usas key)

Notas rapidas:
- `password_encrypted` y `private_key_encrypted` son write-only.
- Los deletes son suaves (soft delete).
