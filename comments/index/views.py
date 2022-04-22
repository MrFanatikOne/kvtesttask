from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import *


@require_http_methods(["GET"])
@csrf_exempt
def get_comments_lvl_3(request):
    body = request.body
    json_data = json.loads(body.decode())
    post_id = json_data['post_id']
    # Проверка на корректность id
    try:
        post_id = int(post_id)
    except:
        return JsonResponse({'status': 'fail'}, status=500)
    # Выгрузка комментариев к посту из бд до третьего уровня вложенности включительно
    post_comments = Comment.objects.all().filter(Post=post_id).filter(ReplyLevel__lte=2).order_by('ReplyLevel')
    collected_comments = []
    compare_comments = []
    for post_comment in post_comments:
        if post_comment.ReplyLevel == 0:
            compare_comments.append({
                'comment': {
                    'id': post_comment.Id,
                    'name': post_comment.Name,
                    'title': post_comment.Title,
                },
                'children': []
            })
        else:
            collected_comments.append({
                'id': post_comment.Id,
                'name': post_comment.Name,
                'title': post_comment.Title,
                'parent': post_comment.ParentComment.Id,
            })
    # Построение дерева комментариев
    for compare_comment in compare_comments:
        append_child(compare_comment, collected_comments)
    return JsonResponse(
        {
            'status': 'success',
            'comments': compare_comments,
        },
        status=200)


# Создание поста
@require_http_methods(["POST"])
@csrf_exempt
def create_post(request):
    body = request.body
    json_data = json.loads(body.decode())
    title = json_data['title']
    text = json_data['text']
    if title == '' or text == '':
        return JsonResponse({'status': 'fail'}, status=500)
    post = Post.objects.create(Title=title, Text=text)
    post.save()
    return JsonResponse({'status': 'success'}, status=200)


# Добавление комментарий к посту
@require_http_methods(["POST"])
@csrf_exempt
def add_comment(request):
    body = request.body
    json_data = json.loads(body.decode())
    title = json_data['title']
    name = json_data['name']
    post_id = json_data['post_id']
    # Проверка на корректность ввода id
    try:
        post_id = int(post_id)
    except:
        return JsonResponse({'status': 'fail'}, status=500)
    post = Post.objects.get(Id=post_id)
    comment = Comment.objects.create(
        Title=title,
        Name=name,
        ParentComment=None,
        Post=post,
        ReplyLevel=0
    )
    comment.save()
    return JsonResponse({'status': 'success'}, status=200)


@require_http_methods(["POST"])
@csrf_exempt
def reply_comment(request):
    body = request.body
    json_data = json.loads(body.decode())
    title = json_data['title']
    name = json_data['name']
    post_id = json_data['post_id']
    parent_comment_id = json_data['parent_comment_id']
    # Проверка на корректность ввода id
    try:
        parent_comment_id = int(parent_comment_id)
        post_id = int(post_id)
    except:
        return JsonResponse({'status': 'fail'}, status=500)
    parent_comment = Comment.objects.get(Id=parent_comment_id)
    post = Post.objects.get(Id=post_id)
    comment = Comment.objects.create(
        Title=title,
        Name=name,
        ParentComment=parent_comment,
        Post=post,
        ReplyLevel=parent_comment.ReplyLevel + 1,
        )
    comment.save()
    return JsonResponse({'status': 'success'}, status=200)


# Получение всех вложенных коментариев к коментарию третьего уровня
@require_http_methods(["GET"])
@csrf_exempt
def replies_of_comment(request):
    body = request.body
    json_data = json.loads(body.decode())
    comment_id = json_data['comment_id']
    post_id = json_data['post_id']
    # Проверка на корректный ввод id
    try:
        comment_id = int(comment_id)
        post_id = int(post_id)
    except:
        return JsonResponse({'status': 'fail'}, status=500)
    comment = Comment.objects.get(Id=comment_id)
    # Введенный коментарий не третьего уровня вложености
    if comment.ReplyLevel != 2:
        return JsonResponse({'status': 'fail'}, status=500)
    collected_comments = []
    # Сборка структуры комментария
    compare_comment = {
        'comment': {
            'id': comment.Id,
            'name': comment.Name,
            'title': comment.Title,
        },
        'children': []
    }
    # Выгрузка комментариев к посту из бд выше второго уровня вложености
    post_comments = Comment.objects.all().filter(Post=post_id).filter(ReplyLevel__gt=2)
    for post_comment in post_comments:
        collected_comments.append({
            'id': post_comment.Id,
            'name': post_comment.Name,
            'title': post_comment.Title,
            'parent': post_comment.ParentComment.Id,
        })
    # Вызов рекурсивной функции добавления комментариев
    append_child(compare_comment, collected_comments)
    return JsonResponse(
        {
            'status': 'success',
            'comment': compare_comment,
        },
        status=200)


# Создание древа комментарие
def append_child(comment, all_comments):
    # Перебор всех комментариев с добавлением всех детей текущему комментарию
    for temp_comment in all_comments:
        if temp_comment['parent'] == comment['comment']['id']:
            comment['children'].append({
                'comment': {
                    'id': temp_comment['id'],
                    'name': temp_comment['name'],
                    'title': temp_comment['title'],
                },
                'children': [

                ]
            })
    # Рекурсивный вызов функции добваления дочерних элементов дерева
    for temp_child_comment in comment['children']:
        append_child(temp_child_comment, all_comments)
