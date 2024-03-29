from django.shortcuts import get_object_or_404

from rest_framework import mixins, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import AuthorOrReadOnly, OwnerOrReadOnly
from api.serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, LikeSerializer,
    PostSerializer
)
from posts.models import Group, Like, Post


class ListCreateDeleteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin, viewsets.GenericViewSet,
                              mixins.DestroyModelMixin):
    pass


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        return self.get_current_post().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            post=self.get_current_post()
        )

    def get_current_post(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))


class FollowViewSet(ListCreateDeleteViewSet):
    serializer_class = FollowSerializer
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('^following__username',)

    def get_queryset(self):
        return self.request.user.follower

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class APILike(APIView):
    def post(self, request, post_id):
        serializer = LikeSerializer(
            context={'request': request, 'view': self}, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        like = get_object_or_404(Like, post=post_id)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
