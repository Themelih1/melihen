from django.urls import path
from django.views.generic import TemplateView
from . import views
from .views import unsplash_my_photos


app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('unsplash/', unsplash_my_photos, name='unsplash_photos'),
    path('post/<str:slug>/', views.post_detail, name='post_detail'),
    path('author/<str:username>/', views.author_profile, name='author_profile'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('blog/', views.blog_posts, name='blog_posts'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/', views.projects, name='projects'),   # <- Bu satır gerekli!
    path('newsletter/unsubscribe/<str:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('gizlilik-politikasi/', TemplateView.as_view(template_name='core/emails/gizlilik-politikasi.html'), name='gizlilik'),
    path('abone-ol/', views.subscribe_newsletter, name='subscribe_newsletter'),
]


