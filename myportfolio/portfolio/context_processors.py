from django.conf import settings
from .models import About


def theme_context(request):
    """Context processor for theme and global template variables"""
    
    # Get theme from session or default to light
    current_theme = request.session.get('theme', 'light')
    
    # Get main about information  
    about = About.objects.first()
    
    # PWA manifest data
    pwa_data = {
        'app_name': getattr(settings, 'PWA_APP_NAME', 'Charles Otwere Portfolio'),
        'app_description': getattr(settings, 'PWA_APP_DESCRIPTION', 'Professional portfolio'),
        'theme_color': getattr(settings, 'PWA_APP_THEME_COLOR', '#3b82f6'),
        'background_color': getattr(settings, 'PWA_APP_BACKGROUND_COLOR', '#ffffff'),
    }
    
    # Social media links for sharing
    social_share = {
        'twitter_share_url': 'https://twitter.com/intent/tweet',
        'linkedin_share_url': 'https://www.linkedin.com/sharing/share-offsite/',
        'facebook_share_url': 'https://www.facebook.com/sharer/sharer.php',
    }
    
    return {
        'current_theme': current_theme,
        'global_about': about,
        'pwa_data': pwa_data,
        'social_share': social_share,
        'available_languages': getattr(settings, 'LANGUAGES', []),
    }