from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    """Manager que excluye registros eliminados por defecto"""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Server(models.Model):
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255)
    port = models.IntegerField(default=22)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager para incluir eliminados

    def soft_delete(self):
        """Eliminación suave"""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaurar registro eliminado"""
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"{self.name} ({self.ip})"

class ServerUser(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='users')
    username = models.CharField(max_length=255)
    auth_type = models.CharField(max_length=50, default='password', choices=[('password', 'Password'), ('key', 'Private Key')])
    password_encrypted = models.TextField(blank=True, null=True)
    private_key_encrypted = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self):
        """Eliminación suave"""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaurar registro eliminado"""
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"{self.username} @ {self.server.name}"

class TerminalSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('error', 'Error'),
    ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='sessions')
    user = models.ForeignKey(ServerUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    session_log = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self):
        """Eliminación suave"""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaurar registro eliminado"""
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"Session {self.id} - {self.server.name} ({self.status})"

