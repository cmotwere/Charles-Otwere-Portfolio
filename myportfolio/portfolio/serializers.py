from rest_framework import serializers
from .models import (
    Project, About, Skill, Testimonial, DownloadTracking, SocialMediaPost,
    Education, Certification, WorkExperience, BlogCategory, BlogPost
)


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model"""
    class Meta:
        model = Skill
        fields = '__all__'


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project lists"""
    technologies_used = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'short_description', 'image',
            'project_type', 'status', 'technologies_used', 'start_date',
            'end_date', 'is_featured', 'live_url', 'github_url'
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual projects"""
    technologies_used = SkillSerializer(many=True, read_only=True)
    duration_days = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = '__all__'


class AboutSerializer(serializers.ModelSerializer):
    """Serializer for About model"""
    class Meta:
        model = About
        exclude = ['created_at', 'updated_at']


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for Testimonial model"""
    project = ProjectListSerializer(read_only=True)
    
    class Meta:
        model = Testimonial
        fields = '__all__'


class DownloadTrackingSerializer(serializers.ModelSerializer):
    """Serializer for Download tracking"""
    class Meta:
        model = DownloadTracking
        fields = '__all__'
        read_only_fields = ['download_date', 'ip_address', 'user_agent', 'referrer']


class SocialMediaPostSerializer(serializers.ModelSerializer):
    """Serializer for Social Media Posts"""
    project = ProjectListSerializer(read_only=True)
    
    class Meta:
        model = SocialMediaPost
        fields = '__all__'


class ContactMessageSerializer(serializers.Serializer):
    """Serializer for contact form messages"""
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_message(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value


class PortfolioStatsSerializer(serializers.Serializer):
    """Serializer for portfolio statistics"""
    total_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    ongoing_projects = serializers.IntegerField()
    total_skills = serializers.IntegerField()
    featured_projects = serializers.IntegerField()
    total_testimonials = serializers.IntegerField()
    total_downloads = serializers.IntegerField()


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for Education model"""
    duration_years = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    
    class Meta:
        model = Education
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    """Serializer for Certification model"""
    skills_gained = SkillSerializer(many=True, read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    
    class Meta:
        model = Certification
        fields = '__all__'


class WorkExperienceSerializer(serializers.ModelSerializer):
    """Serializer for Work Experience model"""
    technologies_used = SkillSerializer(many=True, read_only=True)
    duration_months = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()
    is_current_position = serializers.ReadOnlyField()
    
    class Meta:
        model = WorkExperience
        fields = '__all__'


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for Blog Category model"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCategory
        fields = '__all__'
    
    def get_post_count(self, obj):
        return obj.blogpost_set.filter(status='published').count()


class BlogPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for blog post lists"""
    category = BlogCategorySerializer(read_only=True)
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image', 'category',
            'content_type', 'status', 'tags_list', 'reading_time',
            'view_count', 'like_count', 'is_featured', 'published_date'
        ]
    
    def get_tags_list(self, obj):
        return obj.get_tags_as_list()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual blog posts"""
    category = BlogCategorySerializer(read_only=True)
    related_projects = ProjectListSerializer(many=True, read_only=True)
    tags_list = serializers.SerializerMethodField()
    is_published = serializers.ReadOnlyField()
    
    class Meta:
        model = BlogPost
        fields = '__all__'
    
    def get_tags_list(self, obj):
        return obj.get_tags_as_list()