from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """
    Форма для создания и редактирования объекта модели Post.
    """

    class Meta:
        model = Post
        fields = ['content']


class CommentForm(forms.ModelForm):
    """
    Форма для создания и редактирования объекта модели Comment.
    """

    class Meta:
        model = Comment
        fields = ['content']
