from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from django_quill.fields import QuillField
from django.utils.text import slugify
import uuid

class About(models.Model):
    """Model for storing personal information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(_("Full Name"), max_length=200)
    title = models.CharField(_("Title"), max_length=200)
    bio = QuillField(_("Biography"))
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    address = models.TextField(_("Address"), blank=True)
    github_url = models.URLField(_("GitHub URL"))
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    twitter_url = models.URLField(_("Twitter URL"), blank=True)
    profile_image = models.ImageField(_("Profile Image"), upload_to='profile/', blank=True)
    resume = models.FileField(_("Resume"), upload_to='resumes/', blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("About")
        verbose_name_plural = _("About")
    
    def __str__(self):
        return self.full_name

class Service(models.Model):
    """Model for services offered"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=200)
    description = QuillField(_("Description"))
    icon = models.CharField(_("Icon"), max_length=50, help_text="FontAwesome icon class")
    order = models.IntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title

class Project(models.Model):
    """Model for portfolio projects"""
    PROJECT_TYPE_CHOICES = [
        ('web', _('Web Development')),
        ('mobile', _('Mobile App')),
        ('desktop', _('Desktop Application')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=200)
    description = QuillField(_("Description"))
    project_type = models.CharField(_("Project Type"), max_length=50, choices=PROJECT_TYPE_CHOICES)
    technologies = models.TextField(_("Technologies Used"), help_text="Comma separated list")
    github_url = models.URLField(_("GitHub URL"), blank=True)
    live_url = models.URLField(_("Live URL"), blank=True)
    featured_image = models.ImageField(_("Featured Image"), upload_to='projects/')
    is_featured = models.BooleanField(_("Featured"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title 

class Blog(models.Model):
    """Model for blog posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True)
    content = QuillField(_("Content"))
    excerpt = models.TextField(_("Excerpt"), max_length=500)
    featured_image = models.ImageField(_("Featured Image"), upload_to='blogs/')
    author = models.CharField(_("Author"), max_length=100, default="Nishan Chaudhary")
    is_published = models.BooleanField(_("Published"), default=False)
    published_date = models.DateTimeField(_("Published Date"), null=True, blank=True)
    views = models.IntegerField(_("Views"), default=0)
    tags = models.CharField(_("Tags"), max_length=500, help_text="Comma separated tags")
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ['-published_date', '-created_at']
    
    def __str__(self):
        return self.title

class Gallery(models.Model):
    """Model for image gallery"""
    CATEGORY_CHOICES = [
        ('project', _('Project')),
        ('personal', _('Personal')),
        ('certificate', _('Certificate')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=200)
    image = models.ImageField(_("Image"), upload_to='gallery/')
    category = models.CharField(_("Category"), max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Gallery Item")
        verbose_name_plural = _("Gallery Items")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Testimonial(models.Model):
    """Model for client testimonials"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_name = models.CharField(_("Client Name"), max_length=200)
    client_title = models.CharField(_("Client Title"), max_length=200)
    company = models.CharField(_("Company"), max_length=200, blank=True)
    content = QuillField(_("Testimonial Content"))
    client_image = models.ImageField(_("Client Image"), upload_to='testimonials/', blank=True)
    rating = models.IntegerField(_("Rating"), choices=[(i, i) for i in range(1, 6)])
    is_featured = models.BooleanField(_("Featured"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.client_name} - {self.company}"

class Certificate(models.Model):
    """Model for certificates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Certificate Name"), max_length=200)
    issuer = models.CharField(_("Issuer"), max_length=200)
    issue_date = models.DateField(_("Issue Date"))
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    certificate_url = models.URLField(_("Certificate URL"))
    credential_id = models.CharField(_("Credential ID"), max_length=100, blank=True)
    image = models.ImageField(_("Certificate Image"), upload_to='certificates/', null=True, blank=True)
    skills = models.TextField(_("Skills Covered"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        ordering = ['-issue_date']
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    """Model for technical skills"""
    SKILL_CATEGORY_CHOICES = [
        ('frontend', _('Frontend')),
        ('backend', _('Backend')),
        ('database', _('Database')),
        ('devops', _('DevOps')),
        ('tools', _('Tools')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Skill Name"), max_length=100)
    category = models.CharField(_("Category"), max_length=50, choices=SKILL_CATEGORY_CHOICES)
    proficiency = models.IntegerField(_("Proficiency"), help_text="Percentage (0-100)")
    years_of_experience = models.DecimalField(_("Years of Experience"), max_digits=3, decimal_places=1, default=0)
    icon = models.CharField(_("Icon"), max_length=50, help_text="FontAwesome icon class", blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    order = models.IntegerField(_("Order"), default=0)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    """Model for contact form messages"""
    STATUS_CHOICES = [
        ('new', _('New')),
        ('read', _('Read')),
        ('replied', _('Replied')),
        ('archived', _('Archived')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=200)
    email = models.EmailField(_("Email"))
    subject = models.CharField(_("Subject"), max_length=200)
    message = models.TextField(_("Message"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(_("IP Address"), blank=True, null=True)
    user_agent = models.TextField(_("User Agent"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class FAQ(models.Model):
    """Model for Frequently Asked Questions"""
    CATEGORY_CHOICES = [
        ('general', _('General')),
        ('technical', _('Technical')),
        ('services', _('Services')),
        ('pricing', _('Pricing')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(_("Question"), max_length=500)
    answer = QuillField(_("Answer"))
    category = models.CharField(_("Category"), max_length=50, choices=CATEGORY_CHOICES)
    order = models.IntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ['category', 'order']
    
    def __str__(self):
        return self.question[:100]