from rest_framework import serializers
from core.models import Project
from core.models.group import get_user_group
from django.contrib.auth.models import AnonymousUser


class ProjectsField(serializers.WritableField):
    def to_native(self, project_mgr):
        request_user = self.root.request_user
        if type(request_user) == AnonymousUser:
            return None
        try:
            group = get_user_group(request_user.username)
            projects = project_mgr.filter(owner=group)
            # Modifications to how 'project' should be displayed here:
            return [p.id for p in projects]
        except Project.DoesNotExist:
            return None

    def field_from_native(self, data, files, field_name, into):
        value = data.get(field_name)
        if value is None:
            return
        related_obj = self.root.object
        user = self.root.request_user
        group = get_user_group(user.username)
        # Retrieve the New Project(s)
        if type(value) == list:
            new_projects = value
        else:
            new_projects = [value, ]

        # Remove related_obj from Old Project(s)
        old_projects = related_obj.get_projects(user)
        for old_proj in old_projects:
            related_obj.projects.remove(old_proj)

        # Add Project(s) to related_obj
        for project_id in new_projects:
            # Retrieve/Create the New Project
            #TODO: When projects can be shared,
            #change the qualifier here.
            new_project = Project.objects.get(id=project_id, owner=group)
            # Assign related_obj to New Project
            if not related_obj.projects.filter(id=project_id):
                related_obj.projects.add(new_project)
        # Modifications to how 'project' should be displayed here:
        into[field_name] = new_projects