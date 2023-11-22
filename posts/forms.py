from ckeditor.widgets import CKEditorWidget
from django import forms

from .models import Post, Category, Comment


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'is_published', 'date_scheduled']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_scheduled': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
        labels = {
            'is_published': 'Publish this post?',
            'date_scheduled': 'Schedule this post?',
        }
        help_texts = {
            'title': 'Your post title goes here.',
        }

    def clean(self):
        cleaned_data = super().clean()
        is_published = cleaned_data.get('is_published')
        date_scheduled = cleaned_data.get('date_scheduled')
        if is_published and date_scheduled:
            raise forms.ValidationError("You cannot set a post to be published and scheduled at the same time.")

        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 200:
            raise forms.ValidationError('Content must be at least 200 characters long.')
        return content


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'title': 'Your category title goes here.',
            'description': 'Shortly describe your category.'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 4:
            raise forms.ValidationError('Title must be at least 4 characters long.')
        return title


class CommentForm(forms.ModelForm):
    parent_comment = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Comment
        fields = ['content', 'parent_comment']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }
