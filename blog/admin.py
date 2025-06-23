from django.contrib import admin
from .models import BlogPost, Category, Tag, Comment, BlogImage

admin.site.register(BlogPost)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(BlogImage)