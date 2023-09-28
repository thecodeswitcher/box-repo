from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from box.models import Repo, RepoAccess, Box, BoxMedia

class BoxSerializer(serializers.ModelSerializer):
    """Serializer for the Box Model"""

    class Meta:
        model = Box
        fields = "__all__"

class BoxMediaSerializer(serializers.ModelSerializer):
    """Serializer for the BoxMedia Model"""
    class Meta:
        model = BoxMedia
        fields = ("id", "box_id", "user_id","file_name", "s3_bucket_file_path")



class RepoSerializer(serializers.ModelSerializer):
    """Serializer for the Repo Model"""
    boxes_list = serializers.SerializerMethodField('_get_boxes')
    def _get_boxes(self, obj):
         serializer = BoxSerializer(obj.boxes_list, many=True)
         return serializer.data

    class Meta:
        model = Repo
        fields = ("id", "repo_name", "user_id","boxes_list")
        read_only_fields = ["user"]

class RepoAccessSerializer(serializers.ModelSerializer):
    """Serializer for the RepoAccess Model"""

    class Meta:
        model = RepoAccess
        fields = "__all__"

