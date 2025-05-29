from django.urls import path
from . import views
from .views import unsplash_my_photos

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('unsplash/', unsplash_my_photos, name='unsplash_photos'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('author/<str:username>/', views.author_profile, name='author_profile'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('blog/', views.blog_posts, name='blog_posts'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/', views.projects, name='projects'),   # <- Bu satır gerekli!

]
