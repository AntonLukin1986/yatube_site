from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        help_texts = {
                'text': ('Текст нового поста'),
                'group': ('Сообщество, к которому будет относиться пост')
        }
        labels = {
                'text': ('Текст поста'),
                'group': ('Сообщество')
        }
