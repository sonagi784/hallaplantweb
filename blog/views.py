from django.shortcuts import redirect
from .models import Post, Category, Tag
from .forms import CommentForm
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs): # context에 다른 객체들을 넣어 보낼수있다
        context = super(PostList, self).get_context_data(**kwargs)
        # template에서 {{ category_list }} 와 {{ posts_without_category }} 사용 가능
        context['category_list'] = Category.objects.all() # 카테고리 객체들
        context['posts_without_category'] = Post.objects.filter(category=None).count() # 미분류 카테고리 객체의 갯수

        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm()

        return context

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title', 'content', 'head_image', 'category', 'tags',
    ]
    
    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(type(self), self).form_valid(form)
        else:
            return redirect('/blog/')

class PostUpdate(UpdateView):
    model = Post
    fields = [
        'title', 'content', 'head_image', 'category', 'tags',
    ]

class PostListByTag(ListView):
    
    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        tag = Tag.objects.get(slug=tag_slug)

        return tag.post_set.order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs): # context에 다른 객체들을 넣어 보낼수있다
        context = super(type(self), self).get_context_data(**kwargs)
        # template에서 {{ category_list }} 와 {{ posts_without_category }} 사용 가능
        context['category_list'] = Category.objects.all() # 카테고리 객체들
        context['posts_without_category'] = Post.objects.filter(category=None).count() # 미분류 카테고리 객체의 갯수
        tag_slug = self.kwargs['slug']
        context['tag'] = tag = Tag.objects.get(slug=tag_slug)

        return context

class PostListByCategory(ListView):
    
    def get_queryset(self):
        slug = self.kwargs['slug']
        
        if slug == '_none':
            category = None
        else:
            category = Category.objects.get(slug=slug)
        return Post.objects.filter(category=category).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        
        slug = self.kwargs['slug']

        if slug == '_none':
            context['category'] = '미분류'
        else:
            category = Category.objects.get(slug=slug)
            context['category'] = category

        return context

def new_comment(request, pk):
    post = Post.objects.get(pk=pk)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(comment.get_absolute_url())
    else:
        return redirect('/blog/')


