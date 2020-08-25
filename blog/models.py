from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(blank=True)
    
    slug = models.SlugField(unique=True, allow_unicode=True) # 다양한 문자들을 유니코드로 변환가능

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/category/{}/'.format(self.slug) # slug > pk와 비슷한, url을 만들기위한 각 카테고리별 이름

    class Meta:
        verbose_name_plural = 'categories'

class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/tag/{}/'.format(self.slug)
    
    

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return str(self.title) + ' :: ' + str(self.author)

    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)

    def get_markdown_content(self):
        return markdown(self.content)
    
    def get_update_url(self):
        return self.get_absolute_url() + 'update/'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = MarkdownxField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_markdown_content(self):
        return markdown(self.text)

    def get_absolute_url(self):
        return self.post.get_absolute_url() + '#comment-id-{}'.format(self.pk)

