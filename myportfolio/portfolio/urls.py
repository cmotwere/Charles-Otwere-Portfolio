from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'portfolio'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('projects/', views.projects_view, name='projects'),
    path('projects/<slug:slug>/', views.project_detail_view, name='project_detail'),
    path('skills/', views.skills_view, name='skills'),
    path('contact/', views.contact_view, name='contact'),
    path('testimonials/', views.testimonials_view, name='testimonials'),
    path('education/', views.education_view, name='education'),
    path('certifications/', views.certifications_view, name='certifications'),
    path('experience/', views.work_experience_view, name='experience'),
    path('blog/', views.blog_view, name='blog'),
    path('blog/debug/', views.blog_debug_view, name='blog_debug'),
    path('blog/post/<slug:slug>/', views.blog_post_detail_view, name='blog_detail'),
    path('blog/category/<slug:slug>/', views.blog_category_view, name='blog_category'),
    path('download/<str:file_type>/<str:filename>/', views.track_file_download, name='track_download'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('social-share/<str:platform>/<int:project_id>/', views.social_share, name='social_share'),
    
    # Authentication URLs
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),
    path('auth/error/', views.auth_error_view, name='auth_error'),
    path('auth/social-demo/', views.social_demo_view, name='social_demo'),
    
    # API URLs
    path('api/v1/', include('portfolio.api_urls')),
    
    # Keep original portfolio URL for backward compatibility
    path('portfolio/', views.portfolio_view, name='portfolio_old'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)