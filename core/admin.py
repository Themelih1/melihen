from django.contrib import admin
from django import forms
from django.utils.html import format_html
from tinymce.widgets import TinyMCE
from .models import BlogPost, Category, Tag, Comment, NewsletterSubscriber, Profile, Project, BlogPostCategory, BlogPostTag

# TinyMCE için özel formlar
class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
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

class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'bio': TinyMCE(attrs={
                'cols': 80, 
                'rows': 20,
                'toolbar': 'undo redo | bold italic | link',
            }),
        }

class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'description': TinyMCE(attrs={
                'cols': 80,
                'rows': 30,
                'plugins': 'code',
                'toolbar': 'undo redo | styleselect | bold italic | code',
            }),
            'short_description': forms.Textarea(attrs={'rows': 3}),
        }

# Inline Admin Sınıfları
class BlogPostCategoryInline(admin.TabularInline):
    model = BlogPostCategory
    extra = 1
    raw_id_fields = ('category',)

class BlogPostTagInline(admin.TabularInline):
    model = BlogPostTag
    extra = 1
    raw_id_fields = ('tag',)

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('author', 'name', 'email', 'content', 'is_approved', 'created_at')

# Admin Sınıfları
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm
    inlines = [BlogPostCategoryInline, BlogPostTagInline]
    list_display = ('title', 'author', 'status', 'date_posted', 'reading_time', 'get_categories', 'comment_count')
    list_filter = ('status', 'date_posted', 'categories', 'tags')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'date_posted'
    readonly_fields = ('reading_time', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('İçerik', {
            'fields': ('image', 'content', 'excerpt')
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description'),
        }),
        ('Tarihler', {
            'classes': ('collapse',),
            'fields': ('date_posted', 'updated_at', 'reading_time'),
        }),
    )

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'Kategoriler'

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Yorumlar'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ('user', 'get_full_name', 'website', 'updated')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'bio')
    list_filter = ('updated',)
    readonly_fields = ('profile_picture_preview', 'updated')
    fieldsets = (
        (None, {
            'fields': ('user', 'profile_picture', 'profile_picture_preview')
        }),
        ('Bilgiler', {
            'fields': ('bio', 'website', 'location')
        }),
        ('Sosyal Medya', {
            'fields': ('social_github', 'social_twitter', 'social_linkedin')
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Ad Soyad'

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.profile_picture.url)
        return "-"
    profile_picture_preview.short_description = 'Profil Resmi Önizleme'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('color_preview',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Görünüm', {
            'fields': ('color', 'color_preview')
        }),
        ('Diğer', {
            'fields': ('description',)
        }),
    )

    def color_preview(self, obj):
        if obj.color:
            return format_html('<div style="width: 20px; height: 20px; background-color: {};"></div>', obj.color)
        return "-"
    color_preview.short_description = 'Renk Önizleme'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('color_preview', 'post_count', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'color', 'color_preview')
        }),
        ('İstatistikler', {
            'fields': ('post_count', 'created_at')
        }),
    )

    def color_preview(self, obj):
        if obj.color:
            return format_html('<div style="width: 20px; height: 20px; background-color: {};"></div>', obj.color)
        return "-"
    color_preview.short_description = 'Renk Önizleme'

    def post_count(self, obj):
        return obj.blog_posts.count()
    post_count.short_description = 'Gönderi Sayısı'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_author_name', 'get_post_title', 'content_preview', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'name')
    list_editable = ('is_approved',)
    list_select_related = ('author', 'post')
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    fieldsets = (
        (None, {
            'fields': ('post', 'author', 'name', 'email')
        }),
        ('Yorum', {
            'fields': ('content', 'is_approved')
        }),
        ('Meta', {
            'fields': ('parent', 'ip_address')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else obj.name
    get_author_name.short_description = 'Yazar'

    def get_post_title(self, obj):
        return obj.post.title
    get_post_title.short_description = 'Gönderi'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Yorum'

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_verified', 'subscribed_at')
    list_filter = ('is_active', 'is_verified', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'token')
    fieldsets = (
        (None, {
            'fields': ('email', 'is_active', 'is_verified')
        }),
        ('Meta', {
            'fields': ('token', 'subscribed_at')
        }),
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('title', 'author', 'status', 'is_featured', 'date_posted', 'technologies_preview')
    list_filter = ('status', 'is_featured', 'tags', 'date_posted')
    search_fields = ('title', 'description', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author', 'tags')
    readonly_fields = ('last_updated', 'technologies_list')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'status', 'is_featured')
        }),
        ('İçerik', {
            'fields': ('image', 'short_description', 'description')
        }),
        ('Teknolojiler', {
            'fields': ('technologies', 'technologies_list', 'tags')
        }),
        ('Bağlantılar', {
            'fields': ('url', 'repository_url')
        }),
        ('Tarihler', {
            'fields': ('start_date', 'end_date', 'date_posted', 'last_updated')
        }),
    )

    def technologies_preview(self, obj):
        return ", ".join(obj.get_technologies_list()[:3]) + ('...' if len(obj.get_technologies_list()) > 3 else '')
    technologies_preview.short_description = 'Teknolojiler'

    def technologies_list(self, obj):
        return format_html("<br>".join(obj.get_technologies_list()))
    technologies_list.short_description = 'Teknoloji Listesi'