from rest_framework import serializers
from .models import Server, ServerUser, TerminalSession

class ServerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerUser
        fields = '__all__'
        extra_kwargs = {
            'password_encrypted': {'write_only': True},
            'private_key_encrypted': {'write_only': True}
        }

class ServerSerializer(serializers.ModelSerializer):
    users = ServerUserSerializer(many=True, read_only=True)
    last_used_at = serializers.SerializerMethodField()
    total_sessions = serializers.SerializerMethodField()
    average_session_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Server
        fields = ['id', 'name', 'ip', 'port', 'created_at', 'users', 'last_used_at', 'total_sessions', 'average_session_time']

    def get_last_used_at(self, obj):
        last_session = obj.sessions.order_by('-started_at').first()
        if last_session:
            return last_session.started_at
        return None

    def get_total_sessions(self, obj):
        return obj.sessions.count()

    def get_average_session_time(self, obj):
        completed_sessions = obj.sessions.filter(ended_at__isnull=False, started_at__isnull=False)
        if not completed_sessions.exists():
            return "N/A"
        
        total_seconds = sum((s.ended_at - s.started_at).total_seconds() for s in completed_sessions)
        avg_seconds = total_seconds / completed_sessions.count()
        
        minutes = int(avg_seconds // 60)
        seconds = int(avg_seconds % 60)
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

class TerminalSessionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TerminalSession
        fields = ['id', 'server', 'user', 'username', 'started_at', 'ended_at', 'status', 'duration']

    def get_duration(self, obj):
        if obj.ended_at and obj.started_at:
            diff = obj.ended_at - obj.started_at
            minutes = diff.total_seconds() // 60
            seconds = diff.total_seconds() % 60
            if int(minutes) > 0:
                return f"{int(minutes)}m {int(seconds)}s"
            return f"{int(seconds)}s"
        return "Ongoing"
