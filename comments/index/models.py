from django.db import models


class Post(models.Model):
    Id = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=255)
    Text = models.CharField(max_length=255)


class Comment(models.Model):
    Id = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    ParentComment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='child_comment')
    Post = models.ForeignKey('Post', on_delete=models.CASCADE)
    ReplyLevel = models.PositiveIntegerField()
