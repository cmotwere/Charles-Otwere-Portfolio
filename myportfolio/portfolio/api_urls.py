from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create router
router = DefaultRouter()
router.register(r'projects', api_views.ProjectViewSet)
router.register(r'skills', api_views.SkillViewSet)
router.register(r'about', api_views.AboutViewSet)
router.register(r'testimonials', api_views.TestimonialViewSet)
router.register(r'education', api_views.EducationViewSet)
router.register(r'certifications', api_views.CertificationViewSet)
router.register(r'work-experience', api_views.WorkExperienceViewSet)
router.register(r'blog-categories', api_views.BlogCategoryViewSet)
router.register(r'blog-posts', api_views.BlogPostViewSet, basename='blogpost')
router.register(r'events', api_views.EventViewSet, basename='event')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('contact/', api_views.contact_message, name='api-contact'),
    path('stats/', api_views.portfolio_stats, name='api-stats'),
    path('downloads/<str:file_type>/<str:file_name>/', api_views.track_download, name='api-track-download'),
    path('download-stats/', api_views.download_stats, name='api-download-stats'),
    path('social-posts/', api_views.social_media_posts, name='api-social-posts'),
]