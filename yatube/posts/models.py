from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Уникальный идентификатор страницы', unique=True)
    description = models.TextField('Краткое описание')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField('Текст поста', help_text='Текст нового поста')
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
        help_text='Сообщество, к которому будет относиться пост'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        help_text='Добавить изображение'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return (
            f'Автор: {self.author.username}. '
            f'Дата: {self.created}. '
            f'Сообщество: {self.group}. '
            f'Пост: {self.text[:15]}.'
        )


class Comment(CreatedModel):
    text = models.TextField('Комментарий', help_text='Содержание комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )

    class Meta(CreatedModel.Meta):
        ordering = ('created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (
            f'Автор: {self.author.username}. '
            f'Создан: {self.created}. '
            f'Содержание: {self.text[:15]}. '
            f'Пост: {self.post.id}.'
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        # ограничение вносится на уровне БД:
        constraints = (
            # сочетание user и author должно быть уникальным:
            models.UniqueConstraint(
                fields=['user', 'author'], name='user_author_unique'
            ),
            # проверка может быть назначена только для полей одной модели!
            # user не может быть author:
            models.CheckConstraint(
                check=~(models.Q(user=models.F('author'))),
                name='user_is_not_author'
            )
        )

    def __str__(self):
        return (
            f'{self.user.username} подписан на {self.author.username}.'
        )


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='made_like',
        verbose_name='Поставил лайк'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Оценённый пост'
    )

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'post'], name='user_post_like_unique'
            ),
        )

    def __str__(self):
        return (
            f'{self.user.username} оценил пост: {self.post.text[:15]}.'
        )
