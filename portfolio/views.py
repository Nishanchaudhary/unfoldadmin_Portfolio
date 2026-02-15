from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import get_language
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page

from .models import (
    About, Service, Project, Blog, Gallery, 
    Testimonial, Certificate, Skill, ContactMessage, FAQ
)
from .forms import ContactForm
from .utils import generate_pdf_report

import json
from datetime import datetime

@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    """Home page view"""
    about = About.objects.filter(is_active=True).first()
    services = Service.objects.filter(is_active=True).order_by('order')[:6]
    projects = Project.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:4]
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:5]
    skills = Skill.objects.filter(is_active=True).order_by('category', 'order')
    blog = Blog.objects.filter(is_published=True).order_by('-published_date')[:3]
    faq = FAQ.objects.filter(is_active=True).order_by('category', 'order')[:5]
    gallery_items = Gallery.objects.filter(is_active=True).order_by('-created_at')[:8]
    certificate = Certificate.objects.filter(is_active=True).order_by('-issue_date')[:3]

    for post in blog:
        if post.tags:
            post.first_tag = post.tags.split(',')[0]
        else:
            post.first_tag = 'General'
    
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    context = {
        'about': about,
        'services': services,
        'featured_projects': projects,
        'testimonials': testimonials,
        'skills': skills,
        'skills_by_category': skills_by_category,
        'blog_posts': blog,
        'current_language': get_language(),
        'faq': faq,
        'gallery_items': gallery_items,
        'certificates': certificate,
    }
    return render(request, 'portfolio/home.html', context)

def about(request):
    """About page view"""
    about_info = About.objects.filter(is_active=True).first()
    certificates = Certificate.objects.filter(is_active=True).order_by('-issue_date')
    skills = Skill.objects.filter(is_active=True).order_by('category', 'order')
    
    context = {
        'about': about_info,
        'certificates': certificates,
        'skills': skills,
    }
    return render(request, 'portfolio/about.html', context)

def services(request):
    """Services page view"""
    services = Service.objects.filter(is_active=True).order_by('order')
    
    # Pagination
    paginator = Paginator(services, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'portfolio/services.html', context)

def project_list(request):
    """Project listing with filtering and pagination"""
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    
    # Filtering
    project_type = request.GET.get('type')
    search_query = request.GET.get('search')
    
    if project_type:
        projects = projects.filter(project_type=project_type)
    
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(technologies__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(projects, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'project_types': Project.PROJECT_TYPE_CHOICES,
        'selected_type': project_type,
        'search_query': search_query or '',
    }
    return render(request, 'portfolio/projects.html', context)

def project_detail(request, id):  # Changed from slug to id
    """Project detail view"""
    project = get_object_or_404(Project, id=id, is_active=True)  # Changed to use id
    
    # Get 3 related projects
    related_projects = Project.objects.filter(
        is_active=True,
        project_type=project.project_type
    ).exclude(id=project.id).order_by('-created_at')[:3]  # Changed from slug to id
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'portfolio/project_detail.html', context)


def blog_list(request):
    """Blog listing with filtering and pagination"""
    blogs = Blog.objects.filter(is_published=True).order_by('-published_date')
    
    # Filtering
    category = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique tags
    all_tags = set()
    for blog in blogs:
        tags = [tag.strip() for tag in blog.tags.split(',') if tag.strip()]
        all_tags.update(tags)
    
    context = {
        'blogs': page_obj,
        'page_obj': page_obj,
        'all_tags': sorted(all_tags),
        'search_query': search_query or '',
    }
    return render(request, 'portfolio/blog.html', context)

def blog_detail(request, slug):
    """Blog detail view"""
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
    
    # Increment view count
    blog.views += 1
    blog.save()
    
    # Get related blogs
    related_blogs = Blog.objects.filter(
        is_published=True
    ).exclude(id=blog.id).order_by('-published_date')[:3]
    
    context = {
        'blog': blog,
        'related_blogs': related_blogs,
    }
    return render(request, 'portfolio/blog_detail.html', context)

def gallery(request):
    """Gallery view with filtering"""
    gallery_items = Gallery.objects.filter(is_active=True).order_by('-created_at')
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        gallery_items = gallery_items.filter(category=category)
    
    # Pagination
    paginator = Paginator(gallery_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'gallery_items': page_obj,
        'page_obj': page_obj,
        'categories': Gallery.CATEGORY_CHOICES,
        'selected_category': category,
    }
    return render(request, 'portfolio/gallery.html', context)

def testimonials(request):
    """Testimonials view"""
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(testimonials, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'testimonials': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'portfolio/testimonials.html', context)

def certificates(request):
    """Certificates view"""
    certificates = Certificate.objects.filter(is_active=True).order_by('-issue_date')
    
    context = {
        'certificates': certificates,
    }
    return render(request, 'portfolio/certificates.html', context)

def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.ip_address = request.META.get('REMOTE_ADDR')
            contact_message.user_agent = request.META.get('HTTP_USER_AGENT', '')
            contact_message.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your message! I will get back to you soon.'
                })
            return render(request, 'portfolio/contact_success.html')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'portfolio/contact.html', context)

def faq_list(request):
    """FAQ view grouped by category"""
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    # Group FAQs by category
    faqs_by_category = {}
    for faq in faqs:
        if faq.category not in faqs_by_category:
            faqs_by_category[faq.category] = []
        faqs_by_category[faq.category].append(faq)
    
    context = {
        'faqs_by_category': faqs_by_category,
        'categories': FAQ.CATEGORY_CHOICES,
    }
    return render(request, 'portfolio/faq.html', context)

def download_resume(request):
    """Download resume view"""
    about = About.objects.filter(is_active=True).first()
    if about and about.resume:
        response = HttpResponse(about.resume.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{about.full_name}_Resume.pdf"'
        return response
    return HttpResponse("Resume not available", status=404)

def export_projects_pdf(request):
    """Export projects as PDF"""
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    
    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="projects_portfolio.pdf"'
    
    pdf_buffer = generate_pdf_report(projects, 'Projects Portfolio')
    response.write(pdf_buffer.getvalue())
    
    return response

# API Views for AJAX
@require_http_methods(["GET"])
def api_projects(request):
    """API endpoint for projects"""
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 9))
    paginator = Paginator(projects, per_page)
    
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    
    data = {
        'projects': [
            {
                'id': str(p.id),
                'title': p.title,
                'description': str(p.description.html) if hasattr(p.description, 'html') else str(p.description),
                'project_type': p.get_project_type_display(),
                'technologies': p.technologies,
                'github_url': p.github_url,
                'live_url': p.live_url,
                'featured_image': p.featured_image.url if p.featured_image else None,
                'start_date': p.start_date.strftime('%Y-%m-%d'),
                'end_date': p.end_date.strftime('%Y-%m-%d') if p.end_date else None,
            }
            for p in page_obj
        ],
        'pagination': {
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    }
    
    return JsonResponse(data)