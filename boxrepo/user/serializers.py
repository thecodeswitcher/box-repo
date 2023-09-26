from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from user.models import Account

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User Object"""

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {
                                     "write_only": True
                                    #  , "min_length": 8
                                    }
                       }
    
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    username = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), username=username, password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for the Account Model"""

    class Meta:
        model = Account
        fields = "__all__"

    def create(self, validated_data):
        return Account.objects.create(**validated_data)
