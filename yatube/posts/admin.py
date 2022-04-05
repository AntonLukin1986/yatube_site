from django.contrib import admin

from rest_framework.authtoken.models import TokenProxy

from posts.models import Comment, Follow, Group, Post, Like


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
        'image'
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.unregister(TokenProxy)  # убирает из админки токены
admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)


# То же, что и admin.site.register(Like)
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    pass
