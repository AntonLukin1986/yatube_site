from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Уникальный идентификатор страницы', unique=True)
    description = models.TextField('Краткое описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Сообщество',
        help_text='Cообщество для поста'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return (
            f'Автор: {self.author.username}. '
            f'Дата: {self.pub_date}. '
            f'Сообщество: {self.group}. '
            f'Пост: {self.text[:15]}.'
        )
