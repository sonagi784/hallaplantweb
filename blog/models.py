from django.db import models
from django.contrib.auth.models import User

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

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    created = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.title) + ' :: ' + str(self.author)

    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)
