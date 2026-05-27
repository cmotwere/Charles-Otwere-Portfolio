from django.contrib import admin
from django.utils import timezone
from .models import (
    Project, About, Skill, Testimonial, DownloadTracking, SocialMediaPost,
    Education, Certification, WorkExperience, BlogCategory, BlogPost,
    Event, EventPhoto
)

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'email', 'created_at']
    fields = [
        'name', 'title', 'bio', 'profile_image', 'resume_file',
        'email', 'phone', 'location',
        'linkedin_url', 'github_url', 'twitter_url', 'website_url'
    ]

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'years_experience', 'is_featured']
    list_filter = ['category', 'proficiency', 'is_featured']
    search_fields = ['name', 'description']
    ordering = ['category', '-proficiency', 'name']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'project_type', 'status', 'is_featured', 'start_date', 'created_at']
    list_filter = ['project_type', 'status', 'is_featured', 'is_personal']
    search_fields = ['title', 'description', 'technologies_used__name']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['technologies_used']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'image')
        }),
        ('Project Details', {
            'fields': ('project_type', 'status', 'technologies_used', 'start_date', 'end_date')
        }),
        ('Links', {
            'fields': ('live_url', 'github_url')
        }),
        ('Team & Role', {
            'fields': ('is_personal', 'team_size', 'my_role'),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('challenges', 'learned', 'gallery_images'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        })
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'testimonial_type', 'rating', 'is_featured', 'is_approved', 'date_given']
    list_filter = ['testimonial_type', 'rating', 'is_featured', 'is_approved', 'date_given']
    search_fields = ['name', 'company', 'position', 'title', 'content']
    ordering = ['-date_given']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'position', 'company', 'avatar')
        }),
        ('Testimonial Details', {
            'fields': ('testimonial_type', 'rating', 'title', 'content', 'project', 'date_given')
        }),
        ('Links', {
            'fields': ('linkedin_url', 'website_url')
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_approved')
        })
    )


@admin.register(DownloadTracking)
class DownloadTrackingAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'download_date', 'ip_address', 'location']
    list_filter = ['file_type', 'download_date']
    search_fields = ['file_name', 'ip_address', 'location']
    ordering = ['-download_date']
    readonly_fields = ['download_date', 'ip_address', 'user_agent', 'referrer']
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Read-only


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'status', 'published_time', 'likes_count', 'shares_count']
    list_filter = ['platform', 'status', 'published_time']
    search_fields = ['title', 'content', 'hashtags']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('platform', 'project', 'title', 'content', 'hashtags')
        }),
        ('Media & Links', {
            'fields': ('media_url', 'post_url')
        }),
        ('Scheduling', {
            'fields': ('status', 'scheduled_time', 'published_time')
        }),
        ('Engagement Stats', {
            'fields': ('likes_count', 'shares_count', 'comments_count'),
            'classes': ('collapse',)
        })
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'institution', 'degree_type', 'status', 'end_date', 'is_featured']
    list_filter = ['degree_type', 'status', 'is_featured', 'end_date']
    search_fields = ['institution', 'program_name', 'field_of_study', 'location']
    ordering = ['-end_date', '-start_date']
    
    fieldsets = (
        ('Education Details', {
            'fields': ('institution', 'degree_type', 'program_name', 'field_of_study', 'status')
        }),
        ('Dates & Duration', {
            'fields': ('start_date', 'end_date')
        }),
        ('Performance & Details', {
            'fields': ('gpa', 'description')
        }),
        ('Location & Links', {
            'fields': ('location', 'website_url')
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        })
    )


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuing_organization', 'certification_type', 'status', 'issue_date', 'expiry_date', 'is_featured']
    list_filter = ['certification_type', 'status', 'is_featured', 'issue_date', 'expiry_date']
    search_fields = ['name', 'issuing_organization', 'credential_id', 'description']
    ordering = ['-issue_date']
    filter_horizontal = ['skills_gained']
    
    fieldsets = (
        ('Certification Details', {
            'fields': ('name', 'issuing_organization', 'certification_type', 'status')
        }),
        ('Credential Information', {
            'fields': ('credential_id', 'issue_date', 'expiry_date')
        }),
        ('Content & Verification', {
            'fields': ('description', 'verification_url', 'badge_image')
        }),
        ('Skills & Relations', {
            'fields': ('skills_gained',)
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('skills_gained')


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'employment_type', 'status', 'start_date', 'end_date', 'is_featured']
    list_filter = ['employment_type', 'status', 'is_featured', 'start_date']
    search_fields = ['job_title', 'company_name', 'location', 'job_description']
    ordering = ['-start_date', '-end_date']
    filter_horizontal = ['technologies_used']
    
    fieldsets = (
        ('Position Details', {
            'fields': ('job_title', 'company_name', 'employment_type', 'status')
        }),
        ('Dates & Location', {
            'fields': ('start_date', 'end_date', 'location')
        }),
        ('Company Information', {
            'fields': ('company_description', 'company_website', 'company_logo')
        }),
        ('Role Description', {
            'fields': ('job_description', 'key_achievements')
        }),
        ('Skills & Technologies', {
            'fields': ('technologies_used',)
        }),
        ('Reference & Display', {
            'fields': ('reference_contact', 'is_featured')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('technologies_used')


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    fieldsets = (
        ('Category Details', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Styling', {
            'fields': ('color', 'icon')
        })
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'status', 'published_date', 'view_count', 'is_featured']
    list_filter = ['status', 'content_type', 'category', 'is_featured', 'published_date', 'created_at']
    search_fields = ['title', 'content', 'excerpt', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['related_projects']
    date_hierarchy = 'published_date'
    ordering = ['-published_date', '-created_at']
    
    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image'),
            'description': 'REQUIRED: Fill in Title and Content. Excerpt is recommended for previews. Status must be "Published" to show on website.'
        }),
        ('Categorization', {
            'fields': ('category', 'content_type', 'tags')
        }),
        ('Publishing', {
            'fields': ('status', 'published_date')
        }),
        ('SEO & Metadata', {
            'fields': ('seo_title', 'meta_description', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Relations & Stats', {
            'fields': ('related_projects', 'view_count', 'like_count'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category').prefetch_related('related_projects')

    def save_model(self, request, obj, form, change):

        # Ensure title is set if not provided
        if not obj.title:
            obj.title = f"Untitled Post - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Auto-publish if content is provided and no status set
        if obj.content and obj.status == 'draft':
            obj.status = 'published'
            
        if obj.status == 'published' and not obj.published_date:
            obj.published_date = timezone.now()
        super().save_model(request, obj, form, change)


class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 3
    fields = ['image', 'caption', 'order']
    ordering = ['order']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date', 'location', 'photo_count', 'is_featured']
    list_filter = ['category', 'is_featured', 'date']
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'
    ordering = ['-date']
    inlines = [EventPhotoInline]

    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'slug', 'category', 'date', 'location')
        }),
        ('Content', {
            'fields': ('description', 'cover_image')
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        }),
    )

    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'
