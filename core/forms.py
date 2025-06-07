from django import forms
from .models import Comment, BlogPost  # FlatPage çıkarıldı çünkü Django'nun kendi modelini kullanacağız
from tinymce.widgets import TinyMCE  # type: ignore
from django.contrib.flatpages.models import FlatPage  # Django'nun kendi FlatPage modelini içe aktarıyoruz
from captcha.fields import CaptchaField #type: ignore
from django.utils.translation import gettext_lazy as _




class CommentForm(forms.ModelForm):
    subscribe_newsletter = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Subscribe to newsletter'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    captcha = CaptchaField()  # captcha'yı burada form alanı olarak ekliyoruz

    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']  # SADECE modeldeki alanlar!
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Your name')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Your email')}),
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': _('Your comment')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['captcha'].label = _('Security Code')
        
class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'  # veya slug'ı açıkça ekle: ['title', 'slug', ...]
        widgets = {
            'content': TinyMCE(attrs={
                'cols': 80, 
                'rows': 30,
                'plugins': 'link image code',
                'toolbar': 'undo redo | styleselect | bold italic | alignleft aligncenter alignright | link image | code',
            }),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }


class FlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = ['title', 'content', 'url']
