from django.db import models
from django.contrib.auth import get_user_model

from .constants import NAME_LENGTH


User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField('Опубликовано',
                                       default=True,
                                       help_text='Снимите галочку,'
                                                 ' чтобы скрыть публикацию.')
    created_at = models.DateTimeField(verbose_name='Добавлено',
                                      auto_now_add=True)

    class Meta:
        abstract = True


class Location(PublishedModel):
    name = models.CharField(verbose_name='Название места',
                            max_length=NAME_LENGTH,
                            null=True)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(PublishedModel):
    title = models.CharField(verbose_name='Заголовок',
                             max_length=NAME_LENGTH)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True,
                            verbose_name='Идентификатор',
                            help_text='Идентификатор страницы для URL; '
                                      'разрешены символы латиницы, цифры,'
                                      ' дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(PublishedModel):
    title = models.CharField(verbose_name='Заголовок',
                             max_length=NAME_LENGTH)
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(verbose_name='Дата и время публикации',
                                    help_text='Если установить дату '
                                              'и время в будущем — '
                                              'можно делать'
                                              ' отложенные публикации.')
    image = models.ImageField('Фото',
                              upload_to='Post_images',
                              null=True)
    author = models.ForeignKey(
        User,
        blank=True,
        related_name='posts',
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        Location,
        null=True,
        default=None,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        Category,
        null=True,
        related_name='posts',
        verbose_name='Категория',
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Добавлено',
                                      auto_now_add=True)

    class Meta:
        verbose_name = 'коментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ('created_at',)
