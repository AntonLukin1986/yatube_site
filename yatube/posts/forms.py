from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
                    'text': 'Текст поста',
                    'group': 'Сообщество'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Сообщество, к которому будет относиться пост'
        }
