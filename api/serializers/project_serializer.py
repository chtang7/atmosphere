from rest_framework import serializers
from .application_serializer import ApplicationSerializer
from core.query import only_current
from .instance_serializer import InstanceSerializer
from .volume_serializer import VolumeSerializer
from .get_context_user import get_context_user
from core.models.project import Project


class ProjectSerializer(serializers.ModelSerializer):
    #Edits to Writable fields..
    owner = serializers.SlugRelatedField(slug_field="name", read_only=True)
    # These fields are READ-ONLY!
    applications = serializers.SerializerMethodField('get_user_applications')
    instances = serializers.SerializerMethodField('get_user_instances')
    volumes = serializers.SerializerMethodField('get_user_volumes')

    def get_user_applications(self, project):
        return [ApplicationSerializer(
            item,
            context={'request': self.context.get('request')}).data for item in
            project.applications.filter(only_current())]

    def get_user_instances(self, project):
        return [InstanceSerializer(
            item,
            context={'request': self.context.get('request')}).data for item in
            project.instances.filter(only_current(),
                provider_machine__provider__active=True
                )]

    def get_user_volumes(self, project):
        return [VolumeSerializer(
            item,
            context={'request': self.context.get('request')}).data for item in
            project.volumes.filter(only_current(), provider__active=True)]

    def __init__(self, *args, **kwargs):
        user = get_context_user(self, kwargs)
        super(ProjectSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Project