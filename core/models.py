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
from django.core.validators import MinLengthValidator, MaxLengthValidator
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
from django.utils import timezone

User = get_user_model()


class BaseModel(models.Model):
    """
    Abstract base model with common fields and methods
    """
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name=_("Category Name"),
        help_text=_("Maximum 50 characters")
    )
    slug = models.SlugField(
        unique=True, 
        max_length=60, 
        allow_unicode=True,
        editable=True
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Optional category description")
    )
    color = models.CharField(
        max_length=7, 
        default='#4F46E5',
        verbose_name=_("Color Code"),
        help_text=_("Hex color code for UI display")
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon"),
        help_text=_("Icon class name (e.g., 'fa-code')")
    )

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name:
            raise ValidationError(_("Category name cannot be empty"))
        if len(self.name) > 50:
            raise ValidationError(_("Category name cannot exceed 50 characters"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

class Tag(BaseModel):
    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name=_("Tag Name")
    )
    slug = models.SlugField(
        unique=True, 
        max_length=60, 
        allow_unicode=True,
        editable=True
    )
    color = models.CharField(
        max_length=7, 
        default='#10B981',
        verbose_name=_("Color Code")
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']

class BlogPost(BaseModel):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )

    title = models.CharField(
        max_length=200,
        verbose_name=_("Title"),
        validators=[
            MinLengthValidator(10, _("Title must be at least 10 characters")),
            MaxLengthValidator(200, _("Title cannot exceed 200 characters"))
        ]
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
    )
    content = tinymce_models.HTMLField(verbose_name=_("Content"))
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        verbose_name=_("Excerpt"),
        help_text=_("Short description (important for SEO)")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name=_("Author")
    )
    date_posted = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Publication Date")
    )
    image = CloudinaryField(
        'image',
        folder='blog/featured_images',
        blank=True,
        null=True,
        help_text=_("Optimal size: 1200x630 pixels")
    )
    image_alt = models.CharField(
        max_length=125,
        blank=True,
        verbose_name=_("Image Alt Text"),
        help_text=_("Description of image for accessibility")
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("Status")
    )
    categories = models.ManyToManyField(
        Category,
        through='BlogPostCategory',
        related_name='blog_posts',
        verbose_name=_("Categories")
    )
    tags = models.ManyToManyField(
        Tag,
        through='BlogPostTag',
        related_name='blog_posts',
        verbose_name=_("Tags")
    )
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=_("Meta Title"),
        help_text=_("SEO title (max 60 characters)")
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("Meta Description"),
        help_text=_("SEO description (max 160 characters)")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured Post")
    )
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("View Count")
    )   

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:post_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Calculate estimated reading time in minutes"""
        cleaned_content = strip_tags(self.content)
        cleaned_content = ' '.join(cleaned_content.split())
        word_count = len(cleaned_content.split())
        return max(1, round(word_count / 200))  # Assuming 200 words per minute
    
    def category_list(self):
        return ", ".join([cat.name for cat in self.categories.all()])

    def clean(self):
        if not self.title:
            raise ValidationError(_("Title cannot be empty"))
        if self.meta_title and len(self.meta_title) > 60:
            raise ValidationError(_("Meta title cannot exceed 60 characters"))
        if self.meta_description and len(self.meta_description) > 160:
            raise ValidationError(_("Meta description cannot exceed 160 characters"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['view_count']),
        ]

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
        verbose_name=_("Primary Category")
    )

    class Meta:
        verbose_name = _("Blog Post Category")
        verbose_name_plural = _("Blog Post Categories")
        unique_together = ('blog_post', 'category')

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
        verbose_name = _("Blog Post Tag")
        verbose_name_plural = _("Blog Post Tags")
        unique_together = ('blog_post', 'tag')

class Comment(BaseModel):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True) 
    email = models.EmailField(blank=True)
    content = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_("Parent Comment")
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Approved")
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_("IP Address")
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("User Agent")
    )

    def __str__(self):
        author_name = self.author.get_full_name() if self.author else self.name
        return f"{author_name} - {self.post.title}"

   
    def clean(self):
        if not self.author and (not self.name or not self.email):
            raise ValidationError("Misafir yorumları için ad ve email gereklidir")

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_approved']),
            models.Index(fields=['post']),
        ]

# NewsletterSubscription modelini güncelleyin
class NewsletterSubscription(BaseModel):
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    token = models.CharField(max_length=64, unique=True, verbose_name=_("Verification Token"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Verified"))
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Subscription Date"))
    subscription_source = models.CharField(
        max_length=50,
        default='website_form',
        choices=(
            ('comment_form', _('Comment Form')),
            ('website_form', _('Website Form')),
            ('api', _('API')),
        ),
        verbose_name=_("Subscription Source")
    )

    def __str__(self):
        return self.email

    def generate_token(self):
        """Güvenli bir token oluşturur"""
        import secrets
        self.token = secrets.token_hex(32)

    def get_name(self):
        """Email'den isim kısmını çıkarır (opsiyonel)"""
        return self.email.split('@')[0]

    def save(self, *args, **kwargs):
        if not self.token:
            self.generate_token()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Newsletter Subscription")
        verbose_name_plural = _("Newsletter Subscriptions")
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
        ]
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_("User")
    )
    profile_picture = CloudinaryField(
        'image',
        folder='profiles',
        blank=True,
        null=True,
        help_text=_("Upload a profile picture")
    )
    bio = tinymce_models.HTMLField(
        blank=True,
        null=True,
        verbose_name=_("Bio")
    )
    website = models.URLField(
        blank=True,
        verbose_name=_("Website")
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Location")
    )
    social_github = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("GitHub")
    )
    social_twitter = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Twitter")
    )
    social_linkedin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("LinkedIn")
    )
    social_instagram = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Instagram")
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated")
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

class Project(BaseModel):
    STATUS_CHOICES = (
        ('ongoing', _('Ongoing')),
        ('completed', _('Completed')),
        ('planned', _('Planned')),
    )

    title = models.CharField(
        max_length=200,
        verbose_name=_("Project Title"),
        validators=[MinLengthValidator(10)]
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        allow_unicode=True,
        verbose_name=_("URL Slug"),
        editable=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name=_("Author")
    )
    description = tinymce_models.HTMLField(
        verbose_name=_("Description")
    )
    short_description = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_("Short Description")
    )
    image = CloudinaryField(
        'image',
        folder='projects/featured',
        blank=True,
        null=True,
        help_text=_("Upload a project image")
    )
    image_alt = models.CharField(
        max_length=125,
        blank=True,
        verbose_name=_("Image Alt Text")
    )
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Project URL")
    )
    repository_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Repository URL")
    )
    technologies = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_("Technologies"),
        help_text=_("Comma-separated list of technologies used")
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="projects",
        verbose_name=_("Tags")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured Project")
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='completed',
        verbose_name=_("Status")
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("End Date")
    )
    client = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Client")
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:project_detail", kwargs={"slug": self.slug})

    def get_technologies_list(self):
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',')]
        return []

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

class Meta:
    verbose_name = _("Project")
    verbose_name_plural = _("Projects")
    ordering = ['-start_date']
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['is_featured']),
        models.Index(fields=['status']),
    ]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

def blog_image_path(instance, filename):
    """Blog gönderileri için resim yolu"""
    date_path = timezone.now().strftime('%Y/%m/%d')
    return os.path.join('blog_images', date_path, filename)

def user_directory_path(instance, filename):
    """Kullanıcı profili resimleri için yol"""
    return os.path.join('profile_pics', str(instance.user.id), filename)

def project_image_path(instance, filename):
    """Proje resimleri için yol"""
    return os.path.join('project_images', str(instance.id), filename)

