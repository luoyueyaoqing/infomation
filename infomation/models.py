from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    IDENTITY = (
        ('Normal', 'Normal'),
        ('Redact', 'Redact'),
        ('Manage', 'Manage')
    )
    ATTITUDE = (
        (-1, '反对'),
        (0, ''),
        (1, '赞成')
    )
    attitude = models.IntegerField(choices=ATTITUDE, default=0)
    identity = models.CharField(choices=IDENTITY, default='Normal', max_length=6)

    def __str__(self):
        return self.username


class ArticleColumn(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title


class Article(models.Model):
    '''
    author, title, content, create_time, support_num, read_num, garde_num, column
    '''
    title = models.CharField(max_length=64)
    content = models.TextField()
    create_time = models.DateTimeField(default=timezone.now)
    support_num = models.IntegerField(default=0)
    read_num = models.IntegerField(default=1)
    garde_num = models.IntegerField(default=0)
    author = models.ForeignKey(to=User, related_name='articles')
    column = models.ForeignKey(to=ArticleColumn, related_name='column_articles')

    def comment_this(self, user: User, content: str):
        comment = Comment.objects.create(article=self, user=user, content=content)
        return comment

    def __str__(self):
        return self.title


class Comment(models.Model):
    '''
    user, content, create_time, article
    '''
    content = models.TextField()
    create_time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(to=User, related_name='all_comments')
    article = models.ForeignKey(to=Article, related_name='comments')

    def __str__(self):
        return self.content