from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib import messages
from .utils import generate_token
from .models import BlogPost, Profile, Category, Tag, Comment, Project
from .forms import CommentForm
import os
import requests
from dotenv import load_dotenv
from .models import NewsletterSubscription
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
import logging

logger = logging.getLogger(__name__)





load_dotenv()   
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
USERNAME = os.getenv("UNSPLASH_USERNAME")  # Örn: "melih"

def unsplash_my_photos(request):
    url = f"https://api.unsplash.com/users/{USERNAME}/photos"
    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "per_page": 9,
        "order_by": "latest"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    photos = []
    if isinstance(data, list):  # başarıyla fotoğraflar geldiğinde liste dönüyor
        for photo in data:
            photos.append(photo["urls"]["regular"])

    return render(request, "core/my_unsplash_photos.html", {
        "photos": photos,
    })


# Profil Görünümü
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'core/home.html', {'profile': profile})

# Anasayfa Görünümü
def home(request):
    post_list = BlogPost.objects.all().select_related('author').prefetch_related('categories', 'tags').order_by('-date_posted')
    paginator = Paginator(post_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    profile = Profile.objects.first()
    return render(request, 'core/home.html', {
        'posts': posts,
        'profile': profile
    })

# Yazı Detay Görünümü
# views.py'deki post_detail fonksiyonunu şu şekilde güncelleyin:
def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.filter(parent=None).order_by('-created_at')
    form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.author = request.user
            comment.save()

            if form.cleaned_data.get('subscribe_newsletter'):
                email = form.cleaned_data['email']
                
                # name alanı olmadan
                subscription, created = NewsletterSubscription.objects.get_or_create(
                    email=email,
                    defaults={
                        'is_active': True,
                        'is_verified': True,
                        'subscription_source': 'comment_form',
                        'token': generate_token(),  # Token üreten bir fonksiyon
                    }
                )

                # Mail gönder
                subject = "Aboneliğiniz Aktif!"
                html_message = render_to_string('core/emails/newsletter_confirmation_success.html', {
                    'unsubscribe_link': request.build_absolute_uri(
                        reverse('core:newsletter_unsubscribe', kwargs={'token': subscription.token})
                    )
                })
                send_mail(subject, strip_tags(html_message), settings.DEFAULT_FROM_EMAIL, [email], html_message=html_message)

            return redirect('core:post_detail', slug=post.slug)

    return render(request, 'core/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })
def send_newsletter(post):
    if post.status != 'published':
        return

    active_subscribers = NewsletterSubscription.objects.filter(
        is_active=True,
        is_verified=True
    )

    site_url = getattr(settings, 'SITE_URL', 'http://enmelih.com')
    subject = _("New Blog Post: {}").format(post.title)

    for subscriber in active_subscribers:
        unsubscribe_link = f"{site_url}{reverse('core:newsletter_unsubscribe', kwargs={'token': subscriber.token})}"
        html_content = render_to_string('core/emails/new_post_notification.html', {
            'post': post,
            'unsubscribe_link': unsubscribe_link
        })
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
# Newsletter Abonelik Onayı
        
def newsletter_unsubscribe(request, token):
    subscription = get_object_or_404(NewsletterSubscription, token=token)
    subscription.is_active = False
    subscription.save()
    return render(request, 'core/emails/newsletter_unsubscribed.html', {'email': subscription.email})
    
@login_required
def add_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('core:post_detail', slug=slug)
    else:
        form = CommentForm()
    return render(request, 'core/add_comment.html', {
        'form': form,
        'post': post
    })

# Yorum Düzenleme
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        raise PermissionDenied("Bu yorumu düzenleme yetkiniz yok.")
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('core:post_detail', slug=comment.post.slug)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'core/edit_comment.html', {'form': form})

# Yorum Silme
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        raise PermissionDenied("Bu yorumu silme yetkiniz yok.")
    if request.method == 'POST':
        comment.delete()
        return redirect('core:post_detail', slug=comment.post.slug)
    return render(request, 'core/confirm_delete.html', {'comment': comment})

# Yazar Profili
def author_profile(request, username):
    author = get_object_or_404(Profile, user__username=username)
    posts = BlogPost.objects.filter(author=author.user).order_by('-date_posted')
    return render(request, 'core/author_profile.html', {
        'author': author,
        'posts': posts
    })

# Arama
def search(request):
    query = request.GET.get('q')
    if query:
        results = BlogPost.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().order_by('-date_posted')
    else:
        results = BlogPost.objects.none()
    return render(request, 'core/search_results.html', {'results': results, 'query': query})

# Admin Giriş
def admin_login_view(request):
    account_locked = False
    if account_locked:
        return render(request, 'admin/lockout.html')
    return render(request, 'admin/login.html')

# Kategori Yazıları
def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(categories=category).order_by('-date_posted')
    return render(request, 'core/category_posts.html', {
        'category': category,
        'posts': posts
    })

# Etiket Yazıları
def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(tags=tag).order_by('-date_posted')
    return render(request, 'core/tag_posts.html', {
        'tag': tag,
        'posts': posts
    })

# Tüm Blog Yazıları
def blog_posts(request):
    posts = BlogPost.objects.all().order_by('-date_posted')
    return render(request, 'core/blog_posts.html', {'posts': posts})


def projects(request):
    projects = Project.objects.all().order_by('-created_at')  # veya '-start_date'
    return render(request, 'core/projects.html', {'projects': projects})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'core/project_detail.html', {'project': project})

def subscribe_newsletter(request):
    if request.method == 'POST':
        if request.POST.get('website'):  # Bu alan doldurulduysa bot olabilir
            messages.error(request, "Bot tespiti: Form gönderilemedi.")
            return redirect('core:home')
        name = request.POST.get('name')
        email = request.POST.get('email')
        privacy_check = request.POST.get('privacy_check') == 'on'

        if not privacy_check:
            messages.error(request, 'Gizlilik politikasını kabul etmelisiniz.')
            return redirect('core:home')

        # Abonelik işlemi
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'is_active': True,
                'is_verified': True,
                'subscription_source': 'homepage_form',
                'token': generate_token(),
            }
        )

        # Mail gönder
        subject = "Bülten Aboneliğiniz Aktif!"
        html_message = render_to_string('core/emails/newsletter_confirmation_success.html', {
            'unsubscribe_link': request.build_absolute_uri(
                reverse('core:newsletter_unsubscribe', kwargs={'token': subscription.token})
            )
        })
        send_mail(
            subject, 
            strip_tags(html_message), 
            settings.DEFAULT_FROM_EMAIL, 
            [email], 
            html_message=html_message
        )

        messages.success(request, 'Bültenimize başarıyla abone oldunuz! Teşekkür ederiz.')
        return redirect('core:home')
    

    return redirect('core:home')
