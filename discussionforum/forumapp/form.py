from django.forms import ModelForm
from .models import Post,Category
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class PostForm(ModelForm):
    content = forms.CharField(label="Post Content", widget=forms.Textarea)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Category")
    post_img = forms.ImageField(label="Post Image", required=False)
    is_new_thread = forms.BooleanField(label="Create new thread", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get('user')
        if not user or not user.is_authenticated:
            self.fields['is_new_thread'].widget.attrs['disabled'] = True
        elif not user.has_perm('forum.create_thread'):
            self.fields['is_new_thread'].widget.attrs['disabled'] = True

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'thread', 'post_img', 'is_new_thread']

class UpdateForm(forms.ModelForm):
    content = forms.CharField(label="Post Content", widget=forms.Textarea)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Category")
    post_img = forms.ImageField(label="Post Image", required=False)
    class Meta:
        model = Post
        fields = ['content', 'category', 'post_img']
