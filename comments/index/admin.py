from django.contrib import admin
from .models import *


@admin.register(Post)
class AdminPost(admin.ModelAdmin):
    list_display = ('Id', 'Title')


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    list_display = ('Id', 'Title', 'ParentComment', 'Post')
