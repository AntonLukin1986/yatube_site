from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.validators import vlidate_user_is_not_author
from posts.models import Comment, Follow, Group, Like, Post, User


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Post
        exclude = ('created',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        exclude = ('created',)
        read_only_fields = ('post',)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        exclude = ('id',)
        validators = [
            vlidate_user_is_not_author,
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого автора!'
            )
        ]

    # Встроенный валидатор поля (дублирует vlidate_user_is_not_author)
    def validate_author(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return value


class CurrentPostDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return get_object_or_404(
            Post,
            id=serializer_field.context['view'].kwargs['post_id']
        )


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.HiddenField(default=CurrentPostDefault())

    class Meta:
        model = Like
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Like.objects.all(),
                fields=['user', 'post'],
                message='Вы уже оценили этот пост!'
            )
        ]

    def validate_post(self, value):
        if value.author == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя ставить лайк собственному посту!'
            )
        return value
