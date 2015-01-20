from rest_framework import serializers
from core.models.identity import Identity


class IdentityRelatedField(serializers.RelatedField):

    def to_native(self, identity):
        quota_dict = identity.get_quota_dict()
        return {
            "id": identity.id,
            "provider": identity.provider.location,
            "provider_id": identity.provider.id,
            "quota": quota_dict,
        }

    def field_from_native(self, data, files, field_name, into):
        value = data.get(field_name)
        if value is None:
            return
        try:
            into[field_name] = Identity.objects.get(id=value)
        except Identity.DoesNotExist:
            into[field_name] = None