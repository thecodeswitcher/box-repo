from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from box.models import Repo

class RepoSerializer(serializers.ModelSerializer):
    """Serializer for the Repo Model"""

    class Meta:
        model = Repo
        fields = "__all__"
        read_only_fields = ["user"]