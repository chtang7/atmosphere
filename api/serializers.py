# from django.contrib.auth.models import AnonymousUser
# from core.models.application import Application, ApplicationScore, ApplicationBookmark, ApplicationThreshold
# from core.models.credential import Credential
# from core.models.group import get_user_group
# from core.models.group import Group
# from core.models.group import IdentityMembership
# from core.models.identity import Identity
# from core.models.instance import Instance
# from core.models.instance import InstanceStatusHistory
# from core.models.machine import ProviderMachine
# from core.models.machine_request import MachineRequest
# from core.models.machine_export import MachineExport
# from core.models.maintenance import MaintenanceRecord
# from core.models.profile import UserProfile
# from core.models.project import Project
# from core.models.provider import ProviderType, Provider
# from core.models.size import Size
# from core.models.step import Step
# from core.models.tag import Tag, find_or_create_tag
# from core.models.user import AtmosphereUser
# from core.models.volume import Volume
# from core.query import only_current
# from rest_framework import serializers
# from rest_framework import pagination
# from threepio import logger


# Useful Serializer methods


# def get_projects_for_obj(serializer, related_obj):
#     """
#     Using <>Serializer.request_user, find the projects
#     the related object is a member of
#     """
#     if not serializer.request_user:
#         return None
#     projects = related_obj.get_projects(serializer.request_user)
#     return [p.id for p in projects]


# # Custom Fields


# class NewThresholdField(serializers.WritableField):
#
#     def to_native(self, threshold_dict):
#         return threshold_dict
#
#     def field_from_native(self, data, files, field_name, into):
#         value = data.get(field_name)
#         if value is None:
#             return
#         memory = value.get('memory',0)
#         disk = value.get('disk',0)
#         machine_request = self.root.object
#         machine_request.new_machine_memory_min = memory
#         machine_request.new_machine_storage_min = disk
#         into[field_name] = value


# class AppBookmarkField(serializers.WritableField):
#
#     def to_native(self, bookmark_mgr):
#         request_user = self.root.request_user
#         if type(request_user) == AnonymousUser:
#             return False
#         try:
#             bookmark_mgr.get(user=request_user)
#             return True
#         except ApplicationBookmark.DoesNotExist:
#             return False
#
#     def field_from_native(self, data, files, field_name, into):
#         value = data.get(field_name)
#         if value is None:
#             return
#         app = self.root.object
#         user = self.root.request_user
#         if value:
#             ApplicationBookmark.objects.\
#                 get_or_create(application=app, user=user)
#             result = True
#         else:
#             ApplicationBookmark.objects\
#                                .filter(application=app, user=user).delete()
#             result = False
#         into[field_name] = result


# class IdentityRelatedField(serializers.RelatedField):
#
#     def to_native(self, identity):
#         quota_dict = identity.get_quota_dict()
#         return {
#             "id": identity.id,
#             "provider": identity.provider.location,
#             "provider_id": identity.provider.id,
#             "quota": quota_dict,
#         }
#
#     def field_from_native(self, data, files, field_name, into):
#         value = data.get(field_name)
#         if value is None:
#             return
#         try:
#             into[field_name] = Identity.objects.get(id=value)
#         except Identity.DoesNotExist:
#             into[field_name] = None


# class InstanceRelatedField(serializers.RelatedField):
#     def to_native(self, instance_alias):
#         instance = Instance.objects.get(provider_alias=instance_alias)
#         return instance.provider_alias
#
#     def field_from_native(self, data, files, field_name, into):
#         value = data.get(field_name)
#         if value is None:
#             return
#         try:
#             into["instance"] = Instance.objects.get(provider_alias=value)
#             into[field_name] = Instance.objects.get(
#                 provider_alias=value).provider_alias
#         except Instance.DoesNotExist:
#             into[field_name] = None


# # Serializers
# class AccountSerializer(serializers.Serializer):
#     pass
#     #Define fields here
#     #TODO: Define a spec that we expect from list_users across all providers


# class ApplicationSerializer(serializers.ModelSerializer):
#     """
#     test maybe something
#     """
#     #Read-Only Fields
#     uuid = serializers.CharField(read_only=True)
#     icon = serializers.CharField(read_only=True, source='icon_url')
#     created_by = serializers.SlugRelatedField(slug_field='username',
#                                               source='created_by',
#                                               read_only=True)
#     #scores = serializers.Field(source='get_scores')
#     uuid_hash = serializers.CharField(read_only=True, source='hash_uuid')
#     #Writeable Fields
#     name = serializers.CharField(source='name')
#     tags = serializers.CharField(source='tags.all')
#     description = serializers.CharField(source='description')
#     start_date = serializers.CharField(source='start_date')
#     end_date = serializers.CharField(source='end_date',
#                                      required=False, read_only=True)
#     private = serializers.BooleanField(source='private')
#     featured = serializers.BooleanField(source='featured')
#     machines = serializers.SerializerMethodField('get_machines')
#     is_bookmarked = AppBookmarkField(source="bookmarks.all")
#     threshold = serializers.RelatedField(read_only=True, source="threshold")
#     projects = ProjectsField()
#
#     def get_machines(self, application):
#         machines = application._current_machines(request_user=self.request_user)
#         return [{"start_date": pm.start_date,
#                  "end_date": pm.end_date,
#                  "alias": pm.identifier,
#                  "version": pm.version,
#                  "provider": pm.provider.id} for pm in machines]
#
#
#     def __init__(self, *args, **kwargs):
#         user = get_context_user(self, kwargs)
#         self.request_user = user
#         super(ApplicationSerializer, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = Application


# class PaginatedApplicationSerializer(pagination.PaginationSerializer):
#     """
#     Serializes page objects of Instance querysets.
#     """
#
#     def __init__(self, *args, **kwargs):
#         user = get_context_user(self, kwargs)
#         self.request_user = user
#         super(PaginatedApplicationSerializer, self).__init__(*args, **kwargs)
#
#     class Meta:
#         object_serializer_class = ApplicationSerializer


# class ApplicationBookmarkSerializer(serializers.ModelSerializer):
#     """
#     """
#     #TODO:Need to validate provider/identity membership on id change
#     type = serializers.SerializerMethodField('get_bookmark_type')
#     alias = serializers.SerializerMethodField('get_bookmark_alias')
#
#     def get_bookmark_type(self, bookmark_obj):
#         return "Application"
#
#     def get_bookmark_alias(self, bookmark_obj):
#         return bookmark_obj.application.uuid
#
#     class Meta:
#         model = ApplicationBookmark
#         fields = ('type', 'alias')


# class ApplicationScoreSerializer(serializers.ModelSerializer):
#     """
#     """
#     #TODO:Need to validate provider/identity membership on id change
#     username = serializers.CharField(read_only=True, source='user.username')
#     application = serializers.CharField(read_only=True,
#                                         source='application.name')
#     vote = serializers.CharField(read_only=True, source='get_vote_name')
#
#     class Meta:
#         model = ApplicationScore
#         fields = ('username', "application", "vote")


# class CredentialSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Credential
#         exclude = ('identity',)


# class InstanceHistorySerializer(serializers.ModelSerializer):
#     #R/O Fields first!
#     alias = serializers.CharField(read_only=True, source='provider_alias')
#     alias_hash = serializers.CharField(read_only=True, source='hash_alias')
#     created_by = serializers.SlugRelatedField(slug_field='username',
#                                               source='created_by',
#                                               read_only=True)
#     size_alias = serializers.CharField(read_only=True, source='esh_size')
#     machine_alias = serializers.CharField(read_only=True, source='esh_machine')
#     machine_name = serializers.CharField(read_only=True,
#                                          source='esh_machine_name')
#     machine_alias_hash = serializers.CharField(read_only=True,
#                                                source='hash_machine_alias')
#     ip_address = serializers.CharField(read_only=True)
#     start_date = serializers.DateTimeField(read_only=True)
#     end_date = serializers.DateTimeField(read_only=True)
#     provider = serializers.CharField(read_only=True, source='provider_name')
#     #Writeable fields
#     name = serializers.CharField()
#     tags = TagRelatedField(slug_field='name', source='tags', many=True)
#
#     class Meta:
#         model = Instance
#         exclude = ('id', 'provider_machine', 'provider_alias',
#                    'shell', 'vnc', 'created_by_identity')


# class PaginatedInstanceHistorySerializer(pagination.PaginationSerializer):
#     """
#     Serializes page objects of Instance querysets.
#     """
#     class Meta:
#         object_serializer_class = InstanceHistorySerializer


# class PaginatedInstanceSerializer(pagination.PaginationSerializer):
#     """
#     Serializes page objects of Instance querysets.
#     """
#     class Meta:
#         object_serializer_class = InstanceSerializer


# class MachineExportSerializer(serializers.ModelSerializer):
#     """
#     """
#     name = serializers.CharField(source='export_name')
#     instance = serializers.SlugRelatedField(slug_field='provider_alias')
#     status = serializers.CharField(default="pending")
#     disk_format = serializers.CharField(source='export_format')
#     owner = serializers.SlugRelatedField(slug_field='username',
#                                          source='export_owner')
#     file = serializers.CharField(read_only=True, default="",
#                                  required=False, source='export_file')
#
#     class Meta:
#         model = MachineExport
#         fields = ('id', 'instance', 'status', 'name',
#                   'owner', 'disk_format', 'file')


# class MachineRequestSerializer(serializers.ModelSerializer):
#     """
#     """
#     instance = serializers.SlugRelatedField(slug_field='provider_alias')
#     status = serializers.CharField(default="pending")
#     parent_machine = serializers.SlugRelatedField(slug_field='identifier',
#                                                   read_only=True)
#
#     sys = serializers.CharField(default="", source='iplant_sys_files',
#                                 required=False)
#     software = serializers.CharField(default="No software listed",
#                                      source='installed_software',
#                                      required=False)
#     exclude_files = serializers.CharField(default="", required=False)
#     shared_with = serializers.CharField(source="access_list", required=False)
#
#     name = serializers.CharField(source='new_machine_name')
#     provider = serializers.PrimaryKeyRelatedField(
#         source='new_machine_provider')
#     owner = serializers.SlugRelatedField(slug_field='username',
#                                          source='new_machine_owner')
#     vis = serializers.CharField(source='new_machine_visibility')
#     description = serializers.CharField(source='new_machine_description',
#                                         required=False)
#     tags = serializers.CharField(source='new_machine_tags', required=False)
#     threshold = NewThresholdField(source='new_machine_threshold')
#     new_machine = serializers.SlugRelatedField(slug_field='identifier',
#                                                required=False)
#
#     class Meta:
#         model = MachineRequest
#         fields = ('id', 'instance', 'status', 'name', 'owner', 'provider',
#                   'vis', 'description', 'tags', 'sys', 'software', 'threshold',
#                   'shared_with', 'new_machine')


# class AtmoUserSerializer(serializers.ModelSerializer):
#     selected_identity = IdentityRelatedField(source='select_identity')
#
#     def validate_selected_identity(self, attrs, source):
#         """
#         Check that profile is an identitymember & providermember
#         Returns the dict of attrs
#         """
#         #Short-circut if source (identity) not in attrs
#         logger.debug(attrs)
#         logger.debug(source)
#         if 'selected_identity' not in attrs:
#             return attrs
#         user = self.object.user
#         logger.info("Validating identity for %s" % user)
#         selected_identity = attrs['selected_identity']
#         logger.debug(selected_identity)
#         groups = user.group_set.all()
#         for g in groups:
#             for id_member in g.identitymembership_set.all():
#                 if id_member.identity == selected_identity:
#                     logger.info("Saving new identity:%s" % selected_identity)
#                     user.selected_identity = selected_identity
#                     user.save()
#                     return attrs
#         raise serializers.ValidationError("User is not a member of"
#                                           "selected_identity: %s"
#                                           % selected_identity)
#
#     class Meta:
#         model = AtmosphereUser
#         exclude = ('id', 'password')


# class ProfileSerializer(serializers.ModelSerializer):
#     """
#     """
#     #TODO:Need to validate provider/identity membership on id change
#     username = serializers.CharField(read_only=True, source='user.username')
#     email = serializers.CharField(read_only=True, source='user.email')
#     groups = serializers.CharField(read_only=True, source='user.groups.all')
#     is_staff = serializers.BooleanField(source='user.is_staff')
#     is_superuser = serializers.BooleanField(source='user.is_superuser')
#     selected_identity = IdentityRelatedField(source='user.select_identity')
#
#     class Meta:
#         model = UserProfile
#         exclude = ('id',)


# class ProviderMachineSerializer(serializers.ModelSerializer):
#     #R/O Fields first!
#     alias = serializers.CharField(read_only=True, source='identifier')
#     alias_hash = serializers.CharField(read_only=True, source='hash_alias')
#     created_by = serializers.CharField(
#         read_only=True, source='application.created_by.username')
#     icon = serializers.CharField(read_only=True, source='icon_url')
#     private = serializers.CharField(
#         read_only=True, source='application.private')
#     architecture = serializers.CharField(read_only=True,
#                                          source='esh_architecture')
#     ownerid = serializers.CharField(read_only=True, source='esh_ownerid')
#     state = serializers.CharField(read_only=True, source='esh_state')
#     scores = serializers.SerializerMethodField('get_scores')
#     #Writeable fields
#     name = serializers.CharField(source='application.name')
#     tags = serializers.CharField(source='application.tags.all')
#     description = serializers.CharField(source='application.description')
#     start_date = serializers.CharField(source='start_date')
#     end_date = serializers.CharField(source='end_date',
#                                      required=False, read_only=True)
#     featured = serializers.BooleanField(source='application.featured')
#     version = serializers.CharField(source='version')
#
#     def __init__(self, *args, **kwargs):
#         self.request_user = kwargs.pop('request_user', None)
#         super(ProviderMachineSerializer, self).__init__(*args, **kwargs)
#
#     def get_scores(self, pm):
#         app = pm.application
#         scores = app.get_scores()
#         update_dict = {
#             "has_voted": False,
#             "vote_cast": None}
#         if not self.request_user:
#             scores.update(update_dict)
#             return scores
#         last_vote = ApplicationScore.last_vote(app, self.request_user)
#         if last_vote:
#             update_dict["has_voted"] = True
#             update_dict["vote_cast"] = last_vote.get_vote_name()
#         scores.update(update_dict)
#         return scores
#
#     class Meta:
#         model = ProviderMachine
#         exclude = ('id', 'provider', 'application', 'identity')


# class PaginatedProviderMachineSerializer(pagination.PaginationSerializer):
#     """
#     Serializes page objects of ProviderMachine querysets.
#     """
#     class Meta:
#         object_serializer_class = ProviderMachineSerializer


# class GroupSerializer(serializers.ModelSerializer):
#     identities = serializers.SerializerMethodField('get_identities')
#
#     class Meta:
#         model = Group
#         exclude = ('id', 'providers')
#
#     def get_identities(self, group):
#         identities = group.identities.all()
#         return map(lambda i:
#                    {"id": i.id, "provider_id": i.provider_id},
#                    identities)


# class VolumeSerializer(serializers.ModelSerializer):
#     status = serializers.CharField(read_only=True, source='esh_status')
#     attach_data = serializers.Field(source='esh_attach_data')
#     #metadata = serializers.Field(source='esh_metadata')
#     mount_location = serializers.Field(source='mount_location')
#     identity = CleanedIdentitySerializer(source="created_by_identity")
#     projects = ProjectsField()
#
#     def __init__(self, *args, **kwargs):
#         user = get_context_user(self, kwargs)
#         self.request_user = user
#         super(VolumeSerializer, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = Volume
#         exclude = ('id', 'created_by_identity', 'end_date')


# class NoProjectSerializer(serializers.ModelSerializer):
#     applications = serializers.SerializerMethodField('get_user_applications')
#     instances = serializers.SerializerMethodField('get_user_instances')
#     volumes = serializers.SerializerMethodField('get_user_volumes')
#
#     def get_user_applications(self, atmo_user):
#         return [ApplicationSerializer(
#             item,
#             context={'request': self.context.get('request')}).data for item in
#             atmo_user.application_set.filter(only_current(), projects=None)]
#
#     def get_user_instances(self, atmo_user):
#         return [InstanceSerializer(
#             item,
#             context={'request': self.context.get('request')}).data for item in
#             atmo_user.instance_set.filter(only_current(),
#                 provider_machine__provider__active=True,
#                 projects=None)]
#
#     def get_user_volumes(self, atmo_user):
#         return [VolumeSerializer(
#             item,
#             context={'request': self.context.get('request')}).data for item in
#             atmo_user.volume_set.filter(only_current(),
#                 provider__active=True, projects=None)]
#     class Meta:
#         model = AtmosphereUser
#         fields = ('applications', 'instances', 'volumes')


# class ProviderSizeSerializer(serializers.ModelSerializer):
#     occupancy = serializers.CharField(read_only=True, source='esh_occupancy')
#     total = serializers.CharField(read_only=True, source='esh_total')
#     remaining = serializers.CharField(read_only=True, source='esh_remaining')
#     active = serializers.BooleanField(read_only=True, source="active")
#
#     class Meta:
#         model = Size
#         exclude = ('id', 'start_date', 'end_date')


# class StepSerializer(serializers.ModelSerializer):
#     alias = serializers.CharField(read_only=True, source='alias')
#     name = serializers.CharField()
#     script = serializers.CharField()
#     exit_code = serializers.IntegerField(read_only=True,
#                                          source='exit_code')
#     instance_alias = InstanceRelatedField(source='instance.provider_alias')
#     created_by = serializers.SlugRelatedField(slug_field='username',
#                                               source='created_by',
#                                               read_only=True)
#     start_date = serializers.DateTimeField(read_only=True)
#     end_date = serializers.DateTimeField(read_only=True)
#
#     class Meta:
#         model = Step
#         exclude = ('id', 'instance', 'created_by_identity')


# class ProviderTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProviderType


# class InstanceStatusHistorySerializer(serializers.ModelSerializer):
#     instance = serializers.SlugRelatedField(slug_field='provider_alias')
#     size = serializers.SlugRelatedField(slug_field='alias')
#
#     class Meta:
#         model = InstanceStatusHistory
