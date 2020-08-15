from django.contrib import admin
from .models import Post, Category

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}  # Category의 name으로 slug를 자동생성 -> admin.site.register

admin.site.register(Post)
admin.site.register(Category, CategoryAdmin)
