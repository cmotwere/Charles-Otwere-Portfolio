from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify

class About(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200, blank=True)
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='about/', blank=True, null=True)
    resume_file = models.FileField(upload_to='resume/', blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Me"
        verbose_name_plural = "About Me"

    def __str__(self):
        title_part = self.title if self.title else "(No title)"
        return f"{self.name} - {title_part}"

class Skill(models.Model):
    SKILL_CATEGORIES = [
        ('programming', 'Programming Languages'),
        ('frontend', 'Frontend Technologies'),
        ('backend', 'Backend Technologies'),
        ('data', 'Data & Analytics'),
        ('tools', 'Tools & Frameworks'),
        ('cloud', 'Cloud & DevOps'),
        ('productivity', 'Productivity & Office Tools'),
        ('other', 'Other Skills'),
    ]
    
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    icon = models.CharField(max_length=100, blank=True, help_text="CSS class for icon (e.g., fab fa-python)")
    description = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Show on main portfolio page")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['category', '-proficiency', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_proficiency_display()})"

class Project(models.Model):
    PROJECT_TYPES = [
        ('web', 'Web Application'),
        ('mobile', 'Mobile App'),
        ('desktop', 'Desktop Application'),
        ('api', 'API/Backend'),
        ('ml', 'Machine Learning'),
        ('data', 'Data Analysis'),
        ('game', 'Game Development'),
        ('other', 'Other'),
    ]
    
    PROJECT_STATUS = [
        ('planning', 'Planning'),
        ('development', 'In Development'),
        ('completed', 'Completed'),
        ('maintenance', 'Maintenance'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of title")
    short_description = models.CharField(max_length=200, help_text="Brief description for cards")
    description = models.TextField(help_text="Detailed project description")
    image = models.ImageField(upload_to='portfolio_images/')
    gallery_images = models.JSONField(default=list, blank=True, help_text="List of additional image URLs")
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='completed')
    technologies_used = models.ManyToManyField(Skill, blank=True, help_text="Technologies used in this project")
    live_url = models.URLField(blank=True, help_text="Live demo URL")
    github_url = models.URLField(blank=True, help_text="GitHub repository URL")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False, help_text="Show on main portfolio page")
    is_personal = models.BooleanField(default=True, help_text="Personal project vs client work")
    team_size = models.PositiveIntegerField(default=1, help_text="Number of team members")
    my_role = models.CharField(max_length=100, blank=True, help_text="Your role in the project")
    challenges = models.TextField(blank=True, help_text="Challenges faced during development")
    learned = models.TextField(blank=True, help_text="What you learned from this project")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.status in ['planning', 'development']

    @property
    def duration_months(self):
        if self.end_date:
            delta = self.end_date - self.start_date
            return round(delta.days / 30.44)  # Average days per month
        return None


class Testimonial(models.Model):
    """Client/colleague testimonials and reviews"""
    TESTIMONIAL_TYPES = [
        ('client', 'Client Review'),
        ('colleague', 'Colleague Recommendation'),
        ('supervisor', 'Supervisor Recommendation'),
        ('peer', 'Peer Review'),
        ('other', 'Other'),
    ]
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    name = models.CharField(max_length=100, help_text="Name of the person giving testimonial")
    email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=150, help_text="Job title or position")
    company = models.CharField(max_length=150, blank=True, help_text="Company or organization")
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    testimonial_type = models.CharField(max_length=20, choices=TESTIMONIAL_TYPES, default='client')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    title = models.CharField(max_length=200, blank=True, help_text="Short title for the testimonial")
    content = models.TextField(help_text="The actual testimonial text")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True,
                               help_text="Associated project if any")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    website_url = models.URLField(blank=True, help_text="Personal/company website")
    is_featured = models.BooleanField(default=False, help_text="Show on main portfolio page")
    is_approved = models.BooleanField(default=True, help_text="Approved for display")
    date_given = models.DateField(help_text="Date the testimonial was given")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_given', '-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        title_part = self.title if self.title else "(No title)"
        return f"{self.name} - {title_part}"


class DownloadTracking(models.Model):
    """Track downloads of resume and other files"""
    DOWNLOAD_TYPES = [
        ('resume', 'Resume/CV'),
        ('portfolio', 'Portfolio PDF'),
        ('certificate', 'Certificate'),
        ('other', 'Other Document'),
    ]
    
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=DOWNLOAD_TYPES)
    download_date = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, help_text="Detected location")
    
    class Meta:
        ordering = ['-download_date']
        verbose_name = "Download Tracking"
        verbose_name_plural = "Download Tracking"
    
    def __str__(self):
        return f"{self.file_name} - {self.download_date.strftime('%Y-%m-%d %H:%M')}"


class SocialMediaPost(models.Model):
    """Track and manage social media posts about projects"""
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('github', 'GitHub'),
        ('reddit', 'Reddit'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=280, blank=True)
    content = models.TextField(help_text="Post content/caption")
    hashtags = models.CharField(max_length=500, blank=True, help_text="Comma-separated hashtags")
    media_url = models.URLField(blank=True, null=True, help_text="Image/video URL")
    post_url = models.URLField(blank=True, null=True, help_text="URL of published post")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField(blank=True, null=True)
    published_time = models.DateTimeField(blank=True, null=True)
    likes_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Social Media Post"
        verbose_name_plural = "Social Media Posts"
    
    def __str__(self):
        title_part = self.title[:50] if self.title else "(No title)"
        return f"{self.platform.title()} - {title_part}"


class Education(models.Model):
    """Educational background and qualifications"""
    DEGREE_TYPES = [
        ('highschool', 'High School Diploma'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctorate', 'Doctorate/PhD'),
        ('certificate', 'Certificate Program'),
        ('bootcamp', 'Coding Bootcamp'),
        ('online', 'Online Course'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('deferred', 'Deferred'),
        ('dropped', 'Dropped'),
    ]
    
    institution = models.CharField(max_length=200, help_text="School, university, or institution name")
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES)
    program_name = models.CharField(max_length=200, help_text="Degree title or program name")
    field_of_study = models.CharField(max_length=150, blank=True, help_text="Major, specialization, or field")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Expected or actual graduation date")
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, help_text="Grade Point Average")
    description = models.TextField(blank=True, help_text="Additional details, achievements, or coursework")
    location = models.CharField(max_length=150, blank=True, help_text="City, State/Country")
    website_url = models.URLField(blank=True, help_text="Institution website")
    is_featured = models.BooleanField(default=False, help_text="Show prominently on main pages")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        verbose_name = "Education"
        verbose_name_plural = "Education"
    
    def __str__(self):
        return f"{self.degree_type.title()} in {self.program_name} - {self.institution}"
    
    @property
    def duration_years(self):
        if self.end_date:
            delta = self.end_date - self.start_date
            return round(delta.days / 365.25, 1)
        return None
    
    @property
    def is_current(self):
        return self.status == 'in_progress'


class Certification(models.Model):
    """Professional certifications and credentials"""
    CERTIFICATION_TYPES = [
        ('technical', 'Technical Certification'),
        ('professional', 'Professional Certification'),
        ('vendor', 'Vendor Certification'),
        ('industry', 'Industry Certification'),
        ('academic', 'Academic Certification'),
        ('online', 'Online Course Certificate'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('in_progress', 'In Progress'),
    ]
    
    name = models.CharField(max_length=200, help_text="Certification name")
    issuing_organization = models.CharField(max_length=200, help_text="Organization that issued the certificate")
    certification_type = models.CharField(max_length=20, choices=CERTIFICATION_TYPES, default='technical')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    credential_id = models.CharField(max_length=100, blank=True, help_text="Certificate or badge ID")
    issue_date = models.DateField(help_text="Date certification was earned")
    expiry_date = models.DateField(blank=True, null=True, help_text="Expiration date if applicable")
    description = models.TextField(blank=True, help_text="Skills or knowledge gained")
    verification_url = models.URLField(blank=True, help_text="Link to verify credential")
    badge_image = models.ImageField(upload_to='certifications/', blank=True, null=True, help_text="Digital badge or certificate image")
    skills_gained = models.ManyToManyField(Skill, blank=True, help_text="Skills related to this certification")
    is_featured = models.BooleanField(default=False, help_text="Show on main portfolio page")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
    
    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False
    
    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            days_until_expiry = (self.expiry_date - timezone.now().date()).days
            return 0 < days_until_expiry <= 30
        return False


class WorkExperience(models.Model):
    """Professional work experience and career history"""
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('volunteer', 'Volunteer'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('current', 'Current Position'),
        ('completed', 'Past Position'),
    ]
    
    job_title = models.CharField(max_length=150, help_text="Position title")
    company_name = models.CharField(max_length=200, help_text="Company or organization name")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='current')
    start_date = models.DateField(help_text="Employment start date")
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank if current position")
    location = models.CharField(max_length=150, help_text="City, State/Country or 'Remote'")
    company_description = models.TextField(blank=True, help_text="Brief company overview")
    job_description = models.TextField(help_text="Role overview and key responsibilities")
    key_achievements = models.TextField(blank=True, help_text="Major accomplishments and achievements")
    technologies_used = models.ManyToManyField(Skill, blank=True, help_text="Technologies and skills used")
    company_website = models.URLField(blank=True, help_text="Company website URL")
    company_logo = models.ImageField(upload_to='companies/', blank=True, null=True, help_text="Company logo")
    reference_contact = models.CharField(max_length=200, blank=True, help_text="Reference contact information")
    is_featured = models.BooleanField(default=False, help_text="Show on main portfolio page")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date', '-end_date']
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experience"
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"
    
    @property
    def duration_months(self):
        end = self.end_date or timezone.now().date()
        delta = end - self.start_date
        return round(delta.days / 30.44)  # Average days per month
    
    @property
    def duration_display(self):
        months = self.duration_months
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''}"
        years = months // 12
        remaining_months = months % 12
        if remaining_months == 0:
            return f"{years} year{'s' if years != 1 else ''}"
        return f"{years} year{'s' if years != 1 else ''}, {remaining_months} month{'s' if remaining_months != 1 else ''}"
    
    @property
    def is_current_position(self):
        return self.status == 'current'


class BlogCategory(models.Model):
    """Categories for blog posts"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code for category badge")
    icon = models.CharField(max_length=100, blank=True, help_text="CSS class for icon (e.g., fas fa-code)")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Blog posts and articles for thought leadership"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    CONTENT_TYPES = [
        ('tutorial', 'Tutorial'),
        ('case_study', 'Case Study'),
        ('opinion', 'Opinion Piece'),
        ('technical', 'Technical Article'),
        ('industry', 'Industry Insights'),
        ('personal', 'Personal Experience'),
        ('news', 'News & Updates'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200, blank=True, help_text="Blog post title (auto-generated if empty)")
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True, help_text="Brief description for previews (optional)")
    content = models.TextField(blank=True, help_text="Full blog post content (supports Markdown)")
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='technical')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    reading_time = models.PositiveIntegerField(default=5, help_text="Estimated reading time in minutes")
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    related_projects = models.ManyToManyField(Project, blank=True, help_text="Related portfolio projects")
    seo_title = models.CharField(max_length=200, blank=True, help_text="SEO optimized title")
    meta_description = models.CharField(max_length=300, blank=True, help_text="Meta description for SEO")
    is_featured = models.BooleanField(default=False, help_text="Featured post on blog homepage")
    published_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        elif not self.slug:
            # Generate a default slug if no title provided
            self.slug = f"blog-post-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        if not self.seo_title and self.title:
            self.seo_title = self.title
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title or f"Untitled Post - {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_tags_as_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_date and self.published_date <= timezone.now()
