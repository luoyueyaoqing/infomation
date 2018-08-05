from django.contrib import admin
from .models import Article, User, ArticleColumn, Comment


admin.site.register(User)
admin.site.register(ArticleColumn)
admin.site.register(Article)
admin.site.register(Comment)
