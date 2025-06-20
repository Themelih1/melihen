# Generated by Django 5.1.6 on 2025-05-31 19:44

import cloudinary.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import tinymce.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('token', models.CharField(max_length=64, unique=True, verbose_name='Verification Token')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Email Verified')),
                ('subscribed_at', models.DateTimeField(auto_now_add=True, verbose_name='Subscription Date')),
            ],
            options={
                'verbose_name': 'Newsletter Subscriber',
                'verbose_name_plural': 'Newsletter Subscribers',
                'ordering': ['-subscribed_at'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Tag Name')),
                ('slug', models.SlugField(allow_unicode=True, max_length=60, unique=True)),
                ('color', models.CharField(default='#10B981', max_length=7, verbose_name='Color Code')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('title', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(10, 'Title must be at least 10 characters'), django.core.validators.MaxLengthValidator(200, 'Title cannot exceed 200 characters')], verbose_name='Title')),
                ('slug', models.SlugField(allow_unicode=True, max_length=255, unique=True, verbose_name='URL Slug')),
                ('content', tinymce.models.HTMLField(verbose_name='Content')),
                ('excerpt', models.TextField(blank=True, help_text='Short description (important for SEO)', max_length=300, verbose_name='Excerpt')),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Publication Date')),
                ('image', cloudinary.models.CloudinaryField(blank=True, help_text='Optimal size: 1200x630 pixels', max_length=255, null=True, verbose_name='image')),
                ('image_alt', models.CharField(blank=True, help_text='Description of image for accessibility', max_length=125, verbose_name='Image Alt Text')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=10, verbose_name='Status')),
                ('meta_title', models.CharField(blank=True, help_text='SEO title (max 60 characters)', max_length=60, verbose_name='Meta Title')),
                ('meta_description', models.CharField(blank=True, help_text='SEO description (max 160 characters)', max_length=160, verbose_name='Meta Description')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Featured Post')),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='View Count')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
            ],
            options={
                'verbose_name': 'Blog Post',
                'verbose_name_plural': 'Blog Posts',
                'ordering': ['-date_posted'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('name', models.CharField(help_text='Maximum 50 characters', max_length=50, unique=True, verbose_name='Category Name')),
                ('slug', models.SlugField(allow_unicode=True, max_length=60, unique=True)),
                ('description', models.TextField(blank=True, help_text='Optional category description', verbose_name='Description')),
                ('color', models.CharField(default='#4F46E5', help_text='Hex color code for UI display', max_length=7, verbose_name='Color Code')),
                ('icon', models.CharField(blank=True, help_text="Icon class name (e.g., 'fa-code')", max_length=50, verbose_name='Icon')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['slug'], name='core_catego_slug_a504e5_idx'), models.Index(fields=['is_active'], name='core_catego_is_acti_26a709_idx')],
            },
        ),
        migrations.CreateModel(
            name='BlogPostCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_primary', models.BooleanField(default=False, verbose_name='Primary Category')),
                ('blog_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_categories', to='core.blogpost')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_posts', to='core.category')),
            ],
            options={
                'verbose_name': 'Blog Post Category',
                'verbose_name_plural': 'Blog Post Categories',
                'unique_together': {('blog_post', 'category')},
            },
        ),
        migrations.AddField(
            model_name='blogpost',
            name='categories',
            field=models.ManyToManyField(related_name='blog_posts', through='core.BlogPostCategory', to='core.category', verbose_name='Categories'),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', cloudinary.models.CloudinaryField(blank=True, help_text='Upload a profile picture', max_length=255, null=True, verbose_name='image')),
                ('bio', tinymce.models.HTMLField(blank=True, null=True, verbose_name='Bio')),
                ('website', models.URLField(blank=True, verbose_name='Website')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='Location')),
                ('social_github', models.CharField(blank=True, max_length=100, verbose_name='GitHub')),
                ('social_twitter', models.CharField(blank=True, max_length=100, verbose_name='Twitter')),
                ('social_linkedin', models.CharField(blank=True, max_length=100, verbose_name='LinkedIn')),
                ('social_instagram', models.CharField(blank=True, max_length=100, verbose_name='Instagram')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('title', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(10)], verbose_name='Project Title')),
                ('slug', models.SlugField(allow_unicode=True, max_length=255, unique=True, verbose_name='URL Slug')),
                ('description', tinymce.models.HTMLField(verbose_name='Description')),
                ('short_description', models.CharField(blank=True, max_length=250, verbose_name='Short Description')),
                ('image', cloudinary.models.CloudinaryField(blank=True, help_text='Upload a project image', max_length=255, null=True, verbose_name='image')),
                ('image_alt', models.CharField(blank=True, max_length=125, verbose_name='Image Alt Text')),
                ('url', models.URLField(blank=True, null=True, verbose_name='Project URL')),
                ('repository_url', models.URLField(blank=True, null=True, verbose_name='Repository URL')),
                ('technologies', models.CharField(blank=True, help_text='Comma-separated list of technologies used', max_length=250, verbose_name='Technologies')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Featured Project')),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('planned', 'Planned')], default='completed', max_length=10, verbose_name='Status')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('client', models.CharField(blank=True, max_length=100, verbose_name='Client')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('tags', models.ManyToManyField(blank=True, related_name='projects', to='core.tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BlogPostTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blog_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_tags', to='core.blogpost')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_posts', to='core.tag')),
            ],
            options={
                'verbose_name': 'Blog Post Tag',
                'verbose_name_plural': 'Blog Post Tags',
                'unique_together': {('blog_post', 'tag')},
            },
        ),
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=models.ManyToManyField(related_name='blog_posts', through='core.BlogPostTag', to='core.tag', verbose_name='Tags'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='Full Name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('content', models.TextField(validators=[django.core.validators.MinLengthValidator(10, 'Comment must be at least 10 characters')], verbose_name='Comment')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Approved')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')),
                ('user_agent', models.CharField(blank=True, max_length=255, verbose_name='User Agent')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='core.comment', verbose_name='Parent Comment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.blogpost', verbose_name='Post')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['is_approved'], name='core_commen_is_appr_a7c29f_idx'), models.Index(fields=['post'], name='core_commen_post_id_6aa857_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['slug'], name='core_blogpo_slug_36a1f7_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['status'], name='core_blogpo_status_032da8_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['is_featured'], name='core_blogpo_is_feat_7f8ebf_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['view_count'], name='core_blogpo_view_co_4a7c3a_idx'),
        ),
    ]
