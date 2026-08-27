def twitter_coming_soon(request):
    return render(request, 'coming_soon.html')
import logging
from django.shortcuts import render, get_object_or_404, redirect

logger = logging.getLogger(__name__)
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django import forms
import os
import time
import requests
from .models import (
    Project, About, Skill, Testimonial, DownloadTracking, SocialMediaPost,
    Education, Certification, WorkExperience, BlogCategory, BlogPost,
    Event
)

# Blog helper functions to reduce repetition
def get_published_blog_posts():
    """Get published blog posts with optimized queries"""
    return BlogPost.objects.filter(status='published').select_related('category').prefetch_related('related_projects')

def increment_blog_view_count(blog_post):
    """Centralized view count incrementing"""
    if blog_post.status == 'published':
        blog_post.view_count += 1
        blog_post.save(update_fields=['view_count'])

def get_blog_context_data(posts=None, **extra_context):
    """Common context data for blog views"""
    if posts is None:
        posts = get_published_blog_posts()
    
    # Get all categories for filters
    all_categories = BlogCategory.objects.all()

    context = {
        'posts': posts,
        'categories': all_categories,  # For filters dropdown
        'featured_posts': posts.filter(is_featured=True)[:3] if posts else [],
        'recent_posts': posts[:10] if posts else [],
    }
    context.update(extra_context)
    return context


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username or Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class UserProfileForm(forms.ModelForm):
    """User profile editing form"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

def home_view(request):
    """Main portfolio home page"""
    about = About.objects.first()
    featured_projects = Project.objects.filter(is_featured=True)[:6]
    featured_skills = Skill.objects.filter(is_featured=True)
    featured_events = Event.objects.filter(is_featured=True).prefetch_related('photos')[:4]

    context = {
        'about': about,
        'featured_projects': featured_projects,
        'featured_skills': featured_skills,
        'featured_events': featured_events,
    }
    return render(request, 'portfolio/home.html', context)

def about_view(request):
    """Detailed about me page"""
    about = About.objects.first()
    all_skills = Skill.objects.all().order_by('category', '-proficiency')
    
    # Group skills by category
    skills_by_category = {}
    for skill in all_skills:
        category = skill.get_category_display()
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)
    
    context = {
        'about': about,
        'skills_by_category': skills_by_category,
    }
    return render(request, 'portfolio/about.html', context)

def privacy_policy_view(request):
    """Privacy policy page"""
    about = About.objects.first()
    context = {
        'about': about,
        'turnstile_configured': bool(getattr(settings, 'TURNSTILE_SITE_KEY', '')),
    }
    return render(request, 'portfolio/privacy_policy.html', context)

def projects_view(request):
    """All projects page with filtering"""
    project_type = request.GET.get('type')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    projects = Project.objects.all()
    
    if project_type:
        projects = projects.filter(project_type=project_type)
    if status:
        projects = projects.filter(status=status)
    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(technologies_used__name__icontains=search)
        ).distinct()

    projects = projects.order_by('-start_date')

    # Get filter options
    project_types = Project.PROJECT_TYPES
    project_statuses = Project.PROJECT_STATUS
    
    context = {
        'projects': projects,
        'project_types': project_types,
        'project_statuses': project_statuses,
        'current_type': project_type,
        'current_status': status,
        'search_query': search,
    }
    return render(request, 'portfolio/projects.html', context)

def project_detail_view(request, slug):
    """Individual project detail page"""
    project = get_object_or_404(Project, slug=slug)
    related_projects = Project.objects.filter(
        project_type=project.project_type
    ).exclude(id=project.id)[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'portfolio/project_detail.html', context)

def skills_view(request):
    """Skills and technologies page"""
    category = request.GET.get('category')
    
    skills = Skill.objects.all()
    if category:
        skills = skills.filter(category=category)
    
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        cat = skill.get_category_display()
        if cat not in skills_by_category:
            skills_by_category[cat] = []
        skills_by_category[cat].append(skill)
    
    categories = Skill.SKILL_CATEGORIES
    
    context = {
        'skills_by_category': skills_by_category,
        'categories': categories,
        'current_category': category,
    }
    return render(request, 'portfolio/skills.html', context)

CONTACT_RATE_LIMIT_MAX = 5
CONTACT_RATE_LIMIT_WINDOW = 3600  # seconds
CONTACT_MIN_FILL_TIME = 3  # seconds — submissions faster than this are treated as bots


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _verify_turnstile(token, remote_ip):
    if not settings.TURNSTILE_SECRET_KEY:
        return True
    if not token:
        return False
    try:
        resp = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={
                'secret': settings.TURNSTILE_SECRET_KEY,
                'response': token,
                'remoteip': remote_ip,
            },
            timeout=5,
        )
        return resp.json().get('success', False)
    except requests.RequestException as e:
        logger.error("Turnstile verification request failed: %s", e)
        return False


def contact_view(request):
    """Contact information page"""
    about = About.objects.first()

    if request.method == 'POST':
        # Honeypot check — bots fill this field; silently discard their submission
        if request.POST.get('hp_url', ''):
            return redirect('portfolio:contact')

        ip = _client_ip(request)
        rl_key = f'contact_rl:{ip}'
        attempts = cache.get(rl_key, 0)
        if attempts >= CONTACT_RATE_LIMIT_MAX:
            messages.error(request, 'Too many submissions. Please try again later.')
            return redirect('portfolio:contact')
        cache.set(rl_key, attempts + 1, CONTACT_RATE_LIMIT_WINDOW)

        # Time-trap — bots that submit immediately after the page loads are silently dropped
        try:
            form_ts = float(request.POST.get('form_ts', '0'))
        except ValueError:
            form_ts = 0
        if time.time() - form_ts < CONTACT_MIN_FILL_TIME:
            return redirect('portfolio:contact')

        if not _verify_turnstile(request.POST.get('cf-turnstile-response', ''), ip):
            messages.error(request, 'Verification failed. Please try again.')
            return redirect('portfolio:contact')

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            try:
                recipient = [about.email] if about and about.email else [settings.DEFAULT_FROM_EMAIL]
                send_mail(
                    subject=f"[Portfolio Contact] {subject}",
                    message=f"From: {name} <{email}>\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient,
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent! I'll get back to you soon.")
            except Exception as e:
                logger.error("Contact form send_mail failed: %s", e, exc_info=True)
                messages.error(request, 'There was an error sending your message. Please try again or contact me directly via email.')
        else:
            messages.error(request, 'Please fill in all required fields.')

        return redirect('portfolio:contact')

    context = {
        'about': about,
        'turnstile_site_key': settings.TURNSTILE_SITE_KEY,
        'form_ts': time.time(),
    }
    return render(request, 'portfolio/contact.html', context)

# Keep the original view for backward compatibility
def portfolio_view(request):
    """Original portfolio view - redirects to home"""
    return home_view(request)


def testimonials_view(request):
    """Testimonials page"""
    testimonials = Testimonial.objects.filter(is_approved=True)
    
    # Filter by type if specified
    testimonial_type = request.GET.get('type')
    if testimonial_type:
        testimonials = testimonials.filter(testimonial_type=testimonial_type)
    
    context = {
        'testimonials': testimonials,
        'testimonial_types': Testimonial.TESTIMONIAL_TYPES,
        'current_type': testimonial_type,
    }
    return render(request, 'portfolio/testimonials.html', context)


def track_file_download(request, file_type, filename):
    """Track file downloads and serve the file"""
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
        file_name=filename,
        file_type=file_type,
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer,
    )
    
    # Serve the file
    file_path = os.path.join(settings.MEDIA_ROOT, file_type, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read())
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    else:
        raise Http404("File not found")


def toggle_theme(request):
    """Toggle between light and dark theme"""
    current_theme = request.session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    request.session['theme'] = new_theme
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'theme': new_theme})
    
    # Redirect back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', '/'))


def social_share(request, platform, project_id):
    """Generate social media sharing URLs"""
    project = get_object_or_404(Project, id=project_id)
    
    # Get current site URL
    current_site = request.get_host()
    project_url = f"http://{current_site}/projects/{project.slug}/"
    
    share_urls = {
        'twitter': f"https://twitter.com/intent/tweet?text={project.title}&url={project_url}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={project_url}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={project_url}",
        'reddit': f"https://reddit.com/submit?url={project_url}&title={project.title}",
    }
    
    if platform in share_urls:
        # Track the social share attempt
        SocialMediaPost.objects.create(
            platform=platform,
            project=project,
            title=f"Shared {project.title}",
            content=f"Check out my project: {project.title}",
            post_url=share_urls[platform],
            status='published',
            published_time=timezone.now()
        )
        return redirect(share_urls[platform])
    
    return redirect('portfolio:project_detail', slug=project.slug)


# Authentication Views
def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('portfolio:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'portfolio:home')
                return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    context = {'form': form}
    return render(request, 'portfolio/auth/login.html', context)


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('portfolio:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('portfolio:login')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'portfolio/auth/register.html', context)


def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        username = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'You have been logged out. Thanks for visiting, {username}!')
    return redirect('portfolio:home')


@login_required
def profile_view(request):
    """User profile management"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('portfolio:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get connected social providers
    connected_providers = list(request.user.social_auth.values_list('provider', flat=True))
    
    context = {
        'form': form,
        'user': request.user,
        'connected_providers': connected_providers,
    }
    return render(request, 'portfolio/auth/profile.html', context)


def auth_error_view(request):
    """Social authentication error handler"""
    return render(request, 'portfolio/auth/error.html')


def social_demo_view(request):
    """Demo page showing social authentication integration"""
    return render(request, 'portfolio/social_demo.html')


def education_view(request):
    """Education and academic background page"""
    education = Education.objects.all().order_by('-start_date', '-end_date')
    featured_education = education.filter(is_featured=True)
    
    # Group education by degree type for better organization
    education_by_type = {}
    for edu in education:
        if edu.degree_type not in education_by_type:
            education_by_type[edu.degree_type] = []
        education_by_type[edu.degree_type].append(edu)
    
    context = {
        'education': education,
        'featured_education': featured_education,
        'education_by_type': education_by_type,
    }
    return render(request, 'portfolio/education.html', context)


def certifications_view(request):
    """Certifications and credentials page"""
    certifications = Certification.objects.select_related().prefetch_related('skills_gained')
    active_certs = certifications.filter(status='active').order_by('-issue_date')
    featured_certs = certifications.filter(is_featured=True)
    
    # Get expiring certifications (within 60 days)
    from datetime import timedelta
    sixty_days_from_now = timezone.now().date() + timedelta(days=60)
    expiring_certs = active_certs.filter(
        expiry_date__lte=sixty_days_from_now,
        expiry_date__gte=timezone.now().date()
    )
    
    context = {
        'certifications': certifications,
        'active_certs': active_certs,
        'featured_certs': featured_certs,
        'expiring_certs': expiring_certs,
    }
    return render(request, 'portfolio/certifications.html', context)


def work_experience_view(request):
    """Work experience and career timeline page"""
    work_experience = WorkExperience.objects.prefetch_related('technologies_used').order_by('-start_date', '-end_date')
    current_positions = work_experience.filter(status='current')
    featured_experience = work_experience.filter(is_featured=True)
    
    # Calculate total experience years
    total_months = sum([exp.duration_months for exp in work_experience])
    total_years = round(total_months / 12, 1)
    
    context = {
        'work_experience': work_experience,
        'current_positions': current_positions,
        'featured_experience': featured_experience,
        'total_years': total_years,
    }
    return render(request, 'portfolio/work_experience.html', context)


def blog_view(request):
    """Blog and articles listing page"""
    # Show all posts for debugging, or just published ones in production
    if request.GET.get('debug') == 'true':
        posts = BlogPost.objects.all().select_related('category').order_by('-created_at')
        messages.info(request, 'Debug mode: Showing all blog posts regardless of status')
    else:
        posts = get_published_blog_posts().order_by('-published_date')
    
    # Apply filters
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
        current_category = get_object_or_404(BlogCategory, slug=category_slug)
    
    content_type = request.GET.get('type')
    if content_type:
        posts = posts.filter(content_type=content_type)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    context = get_blog_context_data(
        posts=posts,
        current_category=current_category,
        search_query=search_query,
    )
    return render(request, 'portfolio/blog.html', context)


def blog_debug_view(request):
    """Debug view to show all blog posts with detailed information"""
    from django.http import HttpResponse
    
    posts = BlogPost.objects.all().order_by('-created_at')
    
    html = """
    <html>
    <head><title>Blog Debug Information</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .post { border: 1px solid #ccc; margin: 10px 0; padding: 15px; }
        .published { background-color: #d4edda; }
        .draft { background-color: #f8d7da; }
        .empty-content { color: red; font-weight: bold; }
    </style>
    </head>
    <body>
    <h1>Blog Posts Debug Information</h1>
    <p><strong>Total blog posts:</strong> {}</p>
    """.format(posts.count())
    
    for post in posts:
        status_class = 'published' if post.status == 'published' else 'draft'
        content_warning = '' if post.content else '<span class="empty-content">⚠️ NO CONTENT</span>'
        
        html += f"""
        <div class="post {status_class}">
            <h3>📝 {post.title or 'Untitled Post'}</h3>
            <p><strong>Slug:</strong> {post.slug}</p>
            <p><strong>Status:</strong> {post.status} {content_warning}</p>
            <p><strong>Created:</strong> {post.created_at}</p>
            <p><strong>Published:</strong> {post.published_date or 'Not published'}</p>
            <p><strong>Excerpt:</strong> "{post.excerpt or 'No excerpt'}"</p>
            <p><strong>Content Length:</strong> {len(post.content or '')} characters</p>
            {f'<p><strong>Content Preview:</strong> {post.content[:200]}...</p>' if post.content else '<p><strong>Content:</strong> Empty</p>'}
            <p><strong>Admin Link:</strong> <a href="/admin/portfolio/blogpost/{post.id}/change/">Edit in Admin</a></p>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return HttpResponse(html)


def blog_post_detail_view(request, slug):
    """Individual blog post detail page"""
    # First try to find published posts
    try:
        post = get_published_blog_posts().get(slug=slug)
    except BlogPost.DoesNotExist:
        # If no published post found, try any status (for debugging/preview)
        post = get_object_or_404(
            BlogPost.objects.select_related('category').prefetch_related('related_projects'),
            slug=slug
        )
        
        # Add a warning message for non-published posts
        if post.status != 'published':
            messages.warning(request, f'This blog post has status "{post.get_status_display()}" and may not be fully ready.')
    
    # Increment view count
    increment_blog_view_count(post)
    
    # Get related posts (same category)
    related_posts = get_published_blog_posts().exclude(id=post.id)
    if post.category:
        related_posts = related_posts.filter(category=post.category)
    related_posts = related_posts.order_by('-published_date')[:4]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'portfolio/blog_detail.html', context)


def blog_category_view(request, slug):
    """Blog posts by category"""
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = get_published_blog_posts().filter(category=category).order_by('-published_date')

    context = get_blog_context_data(
        posts=posts,
        category=category,
        current_category=category,
    )
    return render(request, 'portfolio/blog_category.html', context)


def events_view(request):
    """Events gallery listing page"""
    category = request.GET.get('category')

    events = Event.objects.prefetch_related('photos').order_by('-date')

    if category:
        events = events.filter(category=category)

    context = {
        'events': events,
        'event_categories': Event.EVENT_CATEGORIES,
        'current_category': category,
    }
    return render(request, 'portfolio/events.html', context)


def event_detail_view(request, slug):
    """Single event detail with photo gallery"""
    event = get_object_or_404(Event.objects.prefetch_related('photos'), slug=slug)
    photos = event.photos.all()

    context = {
        'event': event,
        'photos': photos,
    }
    return render(request, 'portfolio/event_detail.html', context)
