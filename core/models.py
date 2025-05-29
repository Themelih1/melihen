from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from tinymce import models as tinymce_models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinLengthValidator

User = get_user_model()

# Profil resmi için dosya yolu oluşturma
def user_directory_path(instance, filename):
    return f'profile_pics/user_{instance.user.id}/{timezone.now().strftime("%Y/%m/%d")}/{filename}'

def blog_image_path(instance, filename):
    return f'blog/{timezone.now().strftime("%Y/%m/%d")}/{filename}'

def project_image_path(instance, filename):
    return f'projects/{timezone.now().strftime("%Y/%m/%d")}/{filename}'

# Kategori Modeli
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True, max_length=60, allow_unicode=True)
    description = models.TextField(blank=True, verbose_name="Açıklama")
    color = models.CharField(max_length=7, default='#4F46E5', verbose_name="Renk Kodu")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['name']

# Etiket Modeli
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Etiket Adı")
    slug = models.SlugField(unique=True, max_length=60, allow_unicode=True)
    color = models.CharField(max_length=7, default='#10B981', verbose_name="Renk Kodu")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Etiket"
        verbose_name_plural = "Etiketler"
        ordering = ['name']

# Blog Gönderisi Modeli
class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Taslak'),
        ('published', 'Yayınlandı'),
        ('archived', 'Arşivlendi'),
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Başlık",
        validators=[MinLengthValidator(10)]
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        allow_unicode=True,
        verbose_name="URL Uzantısı"
    )
    content = tinymce_models.HTMLField(verbose_name="İçerik")
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        verbose_name="Özet",
        help_text="Kısa açıklama (SEO için önemli)"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name="Yazar"
    )
    date_posted = models.DateTimeField(
        default=timezone.now,
        verbose_name="Yayınlanma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )
    image = models.ImageField(
        upload_to=blog_image_path,
        blank=True,
        null=True,
        verbose_name="Kapak Görseli"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Durum"
    )
    categories = models.ManyToManyField(
        Category,
        through='BlogPostCategory',
        related_name='blog_posts',
        verbose_name="Kategoriler"
    )
    tags = models.ManyToManyField(
        Tag,
        through='BlogPostTag',
        related_name='blog_posts',
        verbose_name="Etiketler"
    )
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Meta Başlık",
        help_text="SEO için başlık (max 60 karakter)"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta Açıklama",
        help_text="SEO için açıklama (max 160 karakter)"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        cleaned_content = strip_tags(self.content)
        cleaned_content = ' '.join(cleaned_content.split())
        word_count = len(cleaned_content.split())
        return max(1, round(word_count / 200))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Blog Gönderisi"
        verbose_name_plural = "Blog Gönderileri"
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]

# Blog Gönderisi ve Kategori Ara Modeli
class BlogPostCategory(models.Model):
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='post_categories'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category_posts'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Birincil Kategori"
    )

    class Meta:
        verbose_name = "Blog Gönderisi Kategorisi"
        verbose_name_plural = "Blog Gönderisi Kategorileri"
        unique_together = ('blog_post', 'category')

# Blog Gönderisi ve Etiket Ara Modeli
class BlogPostTag(models.Model):
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='post_tags'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_posts'
    )

    class Meta:
        verbose_name = "Blog Gönderisi Etiketi"
        verbose_name_plural = "Blog Gönderisi Etiketleri"
        unique_together = ('blog_post', 'tag')

# Yorum Modeli
class Comment(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Gönderi"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Yazar"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Ad Soyad",
        blank=True
    )
    email = models.EmailField(
        verbose_name="E-posta",
        blank=True
    )
    content = models.TextField(
        verbose_name="Yorum"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Üst Yorum"
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Onaylandı"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP Adresi"
    )

    def __str__(self):
        author_name = self.author.get_full_name() if self.author else self.name
        return f"{author_name} - {self.post.title}"

    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"
        ordering = ['-created_at']

# Bülten Abonesi Modeli
class NewsletterSubscriber(models.Model):
    email = models.EmailField(
        unique=True,
        verbose_name="E-posta"
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Abonelik Tarihi"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif Abonelik"
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Doğrulama Tokenı"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="E-posta Doğrulandı"
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Bülten Abonesi"
        verbose_name_plural = "Bülten Aboneleri"
        ordering = ['-subscribed_at']

# Profil Modeli
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_picture = models.ImageField(
        upload_to=user_directory_path,
        default='profile_pics/default_profile.jpg',
        verbose_name="Profil Resmi"
    )
    bio = tinymce_models.HTMLField(
        blank=True,
        null=True,
        verbose_name="Hakkımda"
    )
    website = models.URLField(
        blank=True,
        verbose_name="Web Sitesi"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Konum"
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )
    social_github = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="GitHub"
    )
    social_twitter = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Twitter"
    )
    social_linkedin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="LinkedIn"
    )

    def __str__(self):
        return f"{self.user.username} Profili"

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profiller"

# Proje Modeli
class Project(models.Model):
    PROJECT_STATUS = (
        ('ongoing', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('planned', 'Planlanıyor'),
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Proje Başlığı",
        validators=[MinLengthValidator(10)]
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        allow_unicode=True,
        verbose_name="URL Uzantısı"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Yazar"
    )
    description = tinymce_models.HTMLField(
        verbose_name="Açıklama"
    )
    short_description = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Kısa Açıklama"
    )
    image = models.ImageField(
        upload_to=project_image_path,
        blank=True,
        null=True,
        verbose_name="Kapak Görseli"
    )
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Proje Linki"
    )
    repository_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Depo Linki (GitHub vb.)"
    )
    technologies = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Teknolojiler"
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="projects",
        verbose_name="Etiketler"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Öne Çıkarılan"
    )
    status = models.CharField(
        max_length=10,
        choices=PROJECT_STATUS,
        default='completed',
        verbose_name="Durum"
    )
    date_posted = models.DateTimeField(
        default=timezone.now,
        verbose_name="Oluşturulma Tarihi"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Başlangıç Tarihi"
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Bitiş Tarihi"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:project_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_technologies_list(self):
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',')]
        return []

    class Meta:
        verbose_name = "Proje"
        verbose_name_plural = "Projeler"
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured']),
        ]

# Sinyaller
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()