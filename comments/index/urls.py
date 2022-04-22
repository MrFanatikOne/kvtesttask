from .views import *
from django.urls import path

urlpatterns = [
    path('get_comments_lvl_3/',  get_comments_lvl_3),
    path('create_post/',  create_post),
    path('add_comment/',  add_comment),
    path('reply_comment/',  reply_comment),
    path('replies_of_comment/',  replies_of_comment),
]