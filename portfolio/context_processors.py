from django.utils.translation import gettext_lazy as _
from .models import Service, FAQ, About

def site_settings(request):
    """Add site-wide settings to context"""
    about = About.objects.filter(is_active=True).first()
    
    return {
        'site_title': 'Nishan Chaudhary - Django Developer',
        'site_description': 'Portfolio of Nishan Chaudhary, Django Web Developer',
        'site_author': 'Nishan Chaudhary',
        'current_year': 2024,
        'about': about,
    }

def navigation(request):
    """Generate navigation menu"""
    nav_items = [
        {
            'name': _('Home'),
            'url': '/',
            'icon': 'home',
        },
        {
            'name': _('About'),
            'url': '/about/',
            'icon': 'person',
        },
        {
            'name': _('Services'),
            'url': '/services/',
            'icon': 'business_center',
            'dropdown': Service.objects.filter(is_active=True).order_by('order')[:5]
        },
        {
            'name': _('Projects'),
            'url': '/projects/',
            'icon': 'folder',
        },
        {
            'name': _('Blog'),
            'url': '/blog/',
            'icon': 'article',
        },
        {
            'name': _('Gallery'),
            'url': '/gallery/',
            'icon': 'photo_library',
        },
        {
            'name': _('Testimonials'),
            'url': '/testimonials/',
            'icon': 'format_quote',
        },
        {
            'name': _('Certificates'),
            'url': '/certificates/',
            'icon': 'badge',
        },
        {
            'name': _('FAQ'),
            'url': '/faq/',
            'icon': 'help',
            'dropdown': FAQ.objects.filter(is_active=True).order_by('category', 'order')[:5]
        },
        {
            'name': _('Contact'),
            'url': '/contact/',
            'icon': 'mail',
        },
    ]
    
    return {
        'nav_items': nav_items,
        'current_path': request.path,
    }