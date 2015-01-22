from core.models import Instance
from rest_framework import serializers
from .identity_summary_serializer import IdentitySummarySerializer
from .user_serializer import UserSerializer


class InstanceSerializer(serializers.ModelSerializer):
    identity = IdentitySummarySerializer(source='created_by_identity')
    user = UserSerializer(source='created_by')

    class Meta:
        model = Instance
        fields = ('id', 'name', 'ip_address', 'shell', 'vnc', 'start_date', 'identity', 'user')
