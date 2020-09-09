from django.shortcuts import render
from blog.models import Post

def index(request):
    if len(Post.objects.all()) >= 3:
        posts = Post.objects.order_by('-created')[0:3]
    else:
        posts = Post.objects.order_by('-created')

    return render(
        request, 
        'main/index.html',
        {
            'posts': posts,
        }
    )