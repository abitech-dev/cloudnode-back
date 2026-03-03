import json
import asyncio
import paramiko
import io
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import Server, TerminalSession

class SSHConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.server_id = self.scope['url_route']['kwargs']['server_id']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.ssh_client = None
        self.ssh_channel = None
        self.session_record = None
        self.read_task = None
        self.full_log = ""

        await self.accept()

        try:
            # Obtener el servidor y el usuario de la BD
            server = await sync_to_async(Server.objects.get)(id=self.server_id)
            server_user = await sync_to_async(server.users.get)(id=self.user_id)
            
            # Crear el registro de la sesión
            self.session_record = await sync_to_async(TerminalSession.objects.create)(
                server=server,
                user=server_user,
                status='active'
            )

            # Conectar SSH
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if server_user.auth_type == 'password':
                await sync_to_async(self.ssh_client.connect)(
                    hostname=server.ip,
                    port=server.port,
                    username=server_user.username,
                    password=server_user.password_encrypted,
                    timeout=10
                )
            elif server_user.auth_type == 'key':
                key_file = io.StringIO(server_user.private_key_encrypted)
                pkey = paramiko.RSAKey.from_private_key(key_file)
                await sync_to_async(self.ssh_client.connect)(
                    hostname=server.ip,
                    port=server.port,
                    username=server_user.username,
                    pkey=pkey,
                    timeout=10
                )

            # Abrir shell interactivo
            self.ssh_channel = self.ssh_client.invoke_shell(term='xterm')
            self.ssh_channel.setblocking(0) # No bloqueante

            # Iniciar tarea de lectura en segundo plano
            self.read_task = asyncio.create_task(self.read_from_ssh())

        except Exception as e:
            print(f"SSH Connection Error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'\r\n\x1b[31mConnection failed: {str(e)}\x1b[0m\r\n'
            }))
            if self.session_record:
                self.session_record.status = 'error'
                self.session_record.ended_at = timezone.now()
                await sync_to_async(self.session_record.save)()
            await self.close()

    async def disconnect(self, close_code):
        if self.read_task:
            self.read_task.cancel()
        
        if self.ssh_channel:
            self.ssh_channel.close()
            
        if self.ssh_client:
            self.ssh_client.close()

        if self.session_record:
            self.session_record.status = 'closed' if self.session_record.status == 'active' else self.session_record.status
            self.session_record.ended_at = timezone.now()
            # self.session_record.session_log = self.full_log # Omitido si no existe el campo
            await sync_to_async(self.session_record.save)()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if 'resize' in text_data_json:
            # Manejar redimensionamiento de la terminal
            cols = text_data_json['resize'].get('cols', 80)
            rows = text_data_json['resize'].get('rows', 24)
            if self.ssh_channel:
                self.ssh_channel.resize_pty(width=cols, height=rows)
            return

        command = text_data_json.get('command', '')
        
        if self.ssh_channel and self.ssh_channel.send_ready():
            self.ssh_channel.send(command)

    async def read_from_ssh(self):
        try:
            while True:
                if self.ssh_channel and self.ssh_channel.recv_ready():
                    data = self.ssh_channel.recv(1024).decode('utf-8', errors='replace')
                    if data:
                        self.full_log += data
                        await self.send(text_data=json.dumps({
                            'type': 'output',
                            'message': data
                        }))
                await asyncio.sleep(0.01) # Pequeña pausa para no saturar la CPU
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error reading from SSH: {e}")
