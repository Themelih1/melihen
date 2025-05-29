from django import forms
from .models import Comment, BlogPost  # FlatPage çıkarıldı çünkü Django'nun kendi modelini kullanacağız
from tinymce.widgets import TinyMCE  # type: ignore
from django.contrib.flatpages.models import FlatPage  # Django'nun kendi FlatPage modelini içe aktarıyoruz
from captcha.fields import CaptchaField #type: ignore



class CommentForm(forms.ModelForm):
    """Form for adding comments."""
    
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'})
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        label="Comment",
        required=True
    )
    captcha = CaptchaField(label='Güvenlik Kodu')   

    parent_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Comment
        fields = ['first_name', 'last_name', 'content', 'captcha', 'parent_id']


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'  # '__all__' özel bir değer olarak kullanılmalı
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
        }


class FlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = ['title', 'content', 'url']
