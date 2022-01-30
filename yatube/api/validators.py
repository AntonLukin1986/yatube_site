from rest_framework import serializers


def vlidate_user_is_not_author(attrs):
    user = attrs['user']
    following = attrs['author']
    if user == following:
        raise serializers.ValidationError(
            'Нельзя подписаться на самого себя!'
        )
