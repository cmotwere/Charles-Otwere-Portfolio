from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import (
    Project, About, Skill, Testimonial, DownloadTracking, SocialMediaPost,
    Education, Certification, WorkExperience, BlogCategory, BlogPost, Event
)
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer, AboutSerializer,
    SkillSerializer, TestimonialSerializer, ContactMessageSerializer,
    PortfolioStatsSerializer, DownloadTrackingSerializer, SocialMediaPostSerializer,
    EducationSerializer, CertificationSerializer, WorkExperienceSerializer,
    BlogCategorySerializer, BlogPostListSerializer, BlogPostDetailSerializer,
    EventListSerializer, EventDetailSerializer
)
import os
import mimetypes
from django.utils import timezone


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Projects"""
    queryset = Project.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectListSerializer
    
    def get_queryset(self):
        queryset = Project.objects.all()
        project_type = self.request.query_params.get('type', None)
        status_param = self.request.query_params.get('status', None)
        featured = self.request.query_params.get('featured', None)
        
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
            
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured projects only"""
        featured_projects = self.queryset.filter(is_featured=True)
        serializer = ProjectListSerializer(featured_projects, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available project types"""
        types = [{'value': choice[0], 'label': choice[1]} for choice in Project.PROJECT_TYPES]
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def statuses(self, request):
        """Get available project statuses"""
        statuses = [{'value': choice[0], 'label': choice[1]} for choice in Project.PROJECT_STATUS]
        return Response(statuses)


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Skills"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Skill.objects.all()
        category = self.request.query_params.get('category', None)
        featured = self.request.query_params.get('featured', None)
        
        if category:
            queryset = queryset.filter(category=category)
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
            
        return queryset.order_by('category', '-proficiency', 'name')
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get available skill categories"""
        categories = [{'value': choice[0], 'label': choice[1]} for choice in Skill.SKILL_CATEGORIES]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured skills only"""
        featured_skills = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_skills, many=True)
        return Response(serializer.data)


class AboutViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for About information"""
    queryset = About.objects.all()
    serializer_class = AboutSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the main about information"""
        about = About.objects.first()
        if about:
            serializer = self.get_serializer(about)
            return Response(serializer.data)
        return Response({'detail': 'About information not found'}, status=404)


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Testimonials"""
    queryset = Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Testimonial.objects.filter(is_approved=True)
        featured = self.request.query_params.get('featured', None)
        testimonial_type = self.request.query_params.get('type', None)
        
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
        if testimonial_type:
            queryset = queryset.filter(testimonial_type=testimonial_type)
            
        return queryset.order_by('-date_given')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured testimonials only"""
        featured_testimonials = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_testimonials, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_message(request):
    """Handle contact form submissions"""
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Send email notification
        subject = f"Portfolio Contact: {data['subject']}"
        message = f"""
New contact form submission:

Name: {data['name']}
Email: {data['email']}
Phone: {data.get('phone', 'Not provided')}
Company: {data.get('company', 'Not provided')}

Subject: {data['subject']}

Message:
{data['message']}
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return Response({'message': 'Your message has been sent successfully!'}, 
                          status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to send message. Please try again later.'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_stats(request):
    """Get portfolio statistics"""
    stats = {
        'total_projects': Project.objects.count(),
        'completed_projects': Project.objects.filter(status='completed').count(),
        'ongoing_projects': Project.objects.filter(status__in=['planning', 'development']).count(),
        'total_skills': Skill.objects.count(),
        'featured_projects': Project.objects.filter(is_featured=True).count(),
        'total_testimonials': Testimonial.objects.filter(is_approved=True).count(),
        'total_downloads': DownloadTracking.objects.count(),
    }
    
    serializer = PortfolioStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_download(request, file_type, file_name):
    """Track file downloads"""
    # Get client IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Get user agent and referrer
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')
    
    # Create tracking record
    DownloadTracking.objects.create(
        file_name=file_name,
        file_type=file_type,
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer,
    )
    
    return Response({'message': 'Download tracked successfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_stats(request):
    """Get download statistics (admin only)"""
    stats = DownloadTracking.objects.values('file_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([AllowAny])
def social_media_posts(request):
    """Get public social media posts"""
    posts = SocialMediaPost.objects.filter(
        status='published'
    ).order_by('-published_time')[:10]
    
    serializer = SocialMediaPostSerializer(posts, many=True)
    return Response(serializer.data)


class EducationViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Education"""
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Education.objects.all()
        status_param = self.request.query_params.get('status', None)
        degree_type = self.request.query_params.get('degree_type', None)
        featured = self.request.query_params.get('featured', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if degree_type:
            queryset = queryset.filter(degree_type=degree_type)
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
            
        return queryset.order_by('-end_date', '-start_date')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured education only"""
        featured_education = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_education, many=True)
        return Response(serializer.data)


class CertificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Certifications"""
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Certification.objects.all()
        certification_type = self.request.query_params.get('type', None)
        status_param = self.request.query_params.get('status', None)
        featured = self.request.query_params.get('featured', None)
        
        if certification_type:
            queryset = queryset.filter(certification_type=certification_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
            
        return queryset.order_by('-issue_date')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured certifications only"""
        featured_certs = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_certs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get certifications expiring within 30 days"""
        from datetime import timedelta
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        expiring_certs = self.queryset.filter(
            status='active',
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gte=timezone.now().date()
        )
        serializer = self.get_serializer(expiring_certs, many=True)
        return Response(serializer.data)


class WorkExperienceViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Work Experience"""
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = WorkExperience.objects.all()
        employment_type = self.request.query_params.get('type', None)
        status_param = self.request.query_params.get('status', None)
        featured = self.request.query_params.get('featured', None)
        
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
            
        return queryset.order_by('-start_date', '-end_date')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured work experience only"""
        featured_work = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_work, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current positions"""
        current_work = self.queryset.filter(status='current')
        serializer = self.get_serializer(current_work, many=True)
        return Response(serializer.data)


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Blog Categories"""
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return BlogCategory.objects.all().order_by('name')


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Blog Posts"""
    queryset = BlogPost.objects.filter(status='published')  # Default queryset for router
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer
    
    def get_queryset(self):
        # Import helper function from views
        from .views import get_published_blog_posts
        queryset = get_published_blog_posts()
        
        # Apply filters
        category = self.request.query_params.get('category', None)
        content_type = self.request.query_params.get('type', None)
        featured = self.request.query_params.get('featured', None)
        tags = self.request.query_params.get('tags', None)
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')
        if tags:
            queryset = queryset.filter(tags__icontains=tags)
            
        return queryset.order_by('-published_date')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured blog posts only"""
        featured_posts = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent blog posts"""
        recent_posts = self.get_queryset()[:5]
        serializer = self.get_serializer(recent_posts, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment view count"""
        from .views import increment_blog_view_count
        instance = self.get_object()
        increment_blog_view_count(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Events"""
    queryset = Event.objects.prefetch_related('photos').order_by('-date')
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer

    def get_queryset(self):
        queryset = Event.objects.prefetch_related('photos').order_by('-date')
        category = self.request.query_params.get('category')
        featured = self.request.query_params.get('featured')

        if category:
            queryset = queryset.filter(category=category)
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == 'true')

        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_events = self.get_queryset().filter(is_featured=True)
        serializer = EventListSerializer(featured_events, many=True, context={'request': request})
        return Response(serializer.data)