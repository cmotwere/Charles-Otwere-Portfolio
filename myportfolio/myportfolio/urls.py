"""
URL configuration for myportfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from portfolio.views import twitter_coming_soon

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('i18n/', include('django.conf.urls.i18n')),
    
    # PWA files
    path('manifest.json', TemplateView.as_view(
        template_name='portfolio/manifest.json',
        content_type='application/json',
    ), name='manifest'),
    path('sw.js', TemplateView.as_view(
        template_name='portfolio/sw.js',
        content_type='application/javascript',
    ), name='service-worker'),
    
    # API endpoints (not translated)
    path('api/', include('portfolio.api_urls')),
    path('auth/login/twitter/', twitter_coming_soon, name='twitter_coming_soon'),
]
    # removed duplicate import

# Add i18n patterns for translated URLs
urlpatterns += i18n_patterns(
    path('', include('portfolio.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
