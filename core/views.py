from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from .models import BlogPost, Profile, Category, Tag, Comment, Project
from .forms import CommentForm
import os
import requests
from dotenv import load_dotenv

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
def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    related_posts = BlogPost.objects.filter(
        categories__in=post.categories.all()
    ).exclude(id=post.id).distinct()[:3]
    comments = post.comments.filter(parent=None).order_by('-created_at')
    form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                content=form.cleaned_data['content'],
                post=post,
                author=request.user if request.user.is_authenticated else None
            )
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            return redirect('core:post_detail', slug=post.slug)

    return render(request, 'core/post_detail.html', {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'form': form,
        'request_user': request.user,
    })

# Yorum Ekleme (opsiyonel ayrı görünüm)
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
    projects = Project.objects.all().order_by('-date_posted')
    return render(request, 'core/projects.html', {'projects': projects})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'core/project_detail.html', {'project': project})
