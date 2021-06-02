# from django.shortcuts import render
# from blog.models import Post

# def index(request):
#     if len(Post.objects.all()) >= 3:
#         posts = Post.objects.order_by('-created')[0:3]
#     else:
#         posts = Post.objects.order_by('-created')

#     return render(
#         request, 
#         'main/index.html',
#         {
#             'post_preview': posts,
#         }
#     )

from blog.models import Post
from django.views.generic.base import TemplateView

class PreviewList(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, *, object_list=None, **kwargs): # context에 다른 객체들을 넣어 보낼수있다
        context = super(PreviewList, self).get_context_data(**kwargs)
        context['post_preview'] = Post.objects.order_by('-created')[:3] # 카테고리 객체들

        return context
