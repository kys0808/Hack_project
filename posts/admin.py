from django.contrib import admin
from .models import Post, Category,Comment
from django import forms

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)

