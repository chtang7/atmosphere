from core.models import Application
from rest_framework import serializers
from .get_context_user import get_context_user

class ApplicationSerializer(serializers.ModelSerializer):
    """
    test maybe something
    """
    #Read-Only Fields
    uuid = serializers.CharField(read_only=True)
    icon = serializers.CharField(read_only=True, source='icon_url')
    created_by = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    #scores = serializers.Field(source='get_scores')
    uuid_hash = serializers.CharField(read_only=True, source='hash_uuid')
    #Writeable Fields
    name = serializers.CharField()
    tags = serializers.StringRelatedField(many=True)
    description = serializers.CharField()
    start_date = serializers.CharField()
    end_date = serializers.CharField(
        required=False,
        read_only=True
    )
    private = serializers.BooleanField()
    featured = serializers.BooleanField()
    machines = serializers.SerializerMethodField()
    # is_bookmarked = AppBookmarkField(source="bookmarks.all")
    threshold = serializers.RelatedField(read_only=True)
    # projects = ProjectsField()

    def get_machines(self, application):
        machines = application._current_machines(request_user=self.request_user)
        return [{
            "start_date": pm.start_date,
            "end_date": pm.end_date,
            "alias": pm.identifier,
            # "version": pm.version,
            "provider": pm.provider.id
        } for pm in machines]

    def __init__(self, *args, **kwargs):
        user = get_context_user(self, kwargs)
        self.request_user = user
        super(ApplicationSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Application
        # fields = ('id', 'name', 'description', 'user')