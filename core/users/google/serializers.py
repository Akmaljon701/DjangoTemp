from rest_framework import serializers
from core.users import models as users_models


class GoogleGetUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = users_models.User
        fields = (
            'id',
            'full_name',
            'phone',
            'email',
            'date_of_birth',
            'device_tokens',
            'created_at',
        )


class GoogleCallBackInputSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    error = serializers.CharField(required=False)
    state = serializers.CharField(required=True)


class GoogleCallBackResponseSerializer(serializers.Serializer):
    id_token_decoded = serializers.CharField(max_length=100)
    access_token = serializers.CharField(max_length=200)
    user = GoogleGetUserSerializer()
    is_new_user = serializers.BooleanField()