from django import forms
from .models import Post , Category ,Comment
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor_uploader.fields import RichTextUploadingField
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from operator import is_not
from functools import partial
# Register your models here.

def min_length_3_validator(value):
    if len(value) < 3:
        raise forms.ValidationError('3글자 이상 입력해 주세요.')

class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['title','body','category']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.exclude(parent__isnull=True)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']