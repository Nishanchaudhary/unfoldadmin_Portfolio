# portfolio/admin.py

from django.contrib import admin
from django.db import models
from django.core.validators import EMPTY_VALUES
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone

from unfold.admin import ModelAdmin
from unfold.paginator import InfinitePaginator
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter, RangeNumericFilter, FieldTextFilter
from unfold.contrib.forms.widgets import WysiwygWidget, ArrayWidget
from unfold.contrib.filters.admin import TextFilter

from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import csv
from io import BytesIO
import html

from .models import (
    About, Service, Project, Blog, Gallery, 
    Testimonial, Certificate, Skill, ContactMessage, FAQ
)

# PDF Export Mixin
class PDFExportMixin:
    """Mixin to add PDF export functionality"""
    
    def export_as_pdf(self, request, queryset):
        """Export selected items as PDF"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="export.pdf"'
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Add title
        title = Paragraph(f"{self.model._meta.verbose_name_plural} Export", styles['Title'])
        elements.append(title)
        
        # Prepare data
        data = [['ID', 'Name', 'Created At']]
        for obj in queryset:
            data.append([
                str(obj.id)[:8],
                str(obj),
                obj.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(obj, 'created_at') else 'N/A'
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    
    export_as_pdf.short_description = _("Export selected items as PDF")

# Custom Filters
class CreatedDateRangeFilter(RangeDateFilter):
    title = _('Created Date Range')
    parameter_name = 'created_at'

class UpdatedDateRangeFilter(RangeDateFilter):
    title = _('Updated Date Range')
    parameter_name = 'updated_at'

class ProficiencyRangeFilter(RangeNumericFilter):
    title = _('Proficiency Range')
    parameter_name = 'proficiency'

class CustomTextFilter(TextFilter):
    title = _("Custom Search")
    parameter_name = "custom_query"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(full_name__icontains=self.value())
        return queryset

# Resource classes for import-export
class AboutResource(resources.ModelResource):
    class Meta:
        model = About
        fields = ('id', 'full_name', 'title', 'email', 'phone', 'github_url')
        export_order = fields

class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service
        fields = ('id', 'title', 'icon', 'order', 'is_active')
        export_order = fields

class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project
        fields = ('id', 'title', 'project_type', 'technologies', 'is_featured', 'is_active')
        export_order = fields

# Admin Classes with Unfold Configuration
@admin.register(About)
class AboutAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    resource_class = AboutResource
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    list_filter_sheet = True
    list_fullwidth = False
    list_horizontal_scrollbar_top = True
    list_disable_select_all = False
    compressed_fields = True
    warn_unsaved_form = True
    change_form_show_cancel_button = True
    
    list_display = ('full_name', 'title', 'email', 'is_active', 'created_at')
    list_filter = [
        "is_active",
        ("created_at", CreatedDateRangeFilter),
        ("full_name", FieldTextFilter),
    ]
    search_fields = ('full_name', 'title', 'email', 'bio')
    list_per_page = 20
    
    actions = ['export_as_pdf']
    
    fieldsets = (
        (_('Personal Information'), {
            'fields': ('full_name', 'title', 'profile_image', 'bio')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone', 'address')
        }),
        (_('Social Links'), {
            'fields': ('github_url', 'linkedin_url', 'twitter_url')
        }),
        (_('Documents'), {
            'fields': ('resume',)
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }
    
    readonly_preprocess_fields = {
        "bio": "html.unescape",
    }

@admin.register(Service)
class ServiceAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    resource_class = ServiceResource
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('title', 'icon', 'order', 'is_active', 'created_at')
    list_filter = [
        "is_active",
        ("created_at", CreatedDateRangeFilter),
        ("title", FieldTextFilter),
    ]
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    list_per_page = 20
    
    fieldsets = (
        (_('Service Details'), {
            'fields': ('title', 'icon', 'description', 'order')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(Project)
class ProjectAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    resource_class = ProjectResource
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('title', 'project_type', 'is_featured', 'is_active', 'start_date', 'created_at')
    list_filter = [
        "project_type",
        "is_featured", 
        "is_active",
        ("created_at", CreatedDateRangeFilter),
        ("title", FieldTextFilter),
    ]
    search_fields = ('title', 'description', 'technologies')
    list_per_page = 20
    
    fieldsets = (
        (_('Project Details'), {
            'fields': ('title', 'project_type', 'description', 'technologies')
        }),
        (_('Links & Media'), {
            'fields': ('github_url', 'live_url', 'featured_image')
        }),
        (_('Timeline'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Status'), {
            'fields': ('is_featured', 'is_active')
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(Blog)
class BlogAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('title', 'author', 'is_published', 'published_date', 'views', 'created_at')
    list_filter = [
        "is_published",
        "author",
        ("created_at", CreatedDateRangeFilter),
        ("title", FieldTextFilter),
    ]
    search_fields = ('title', 'content', 'tags', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    
    fieldsets = (
        (_('Blog Content'), {
            'fields': ('title', 'slug', 'excerpt', 'content', 'tags')
        }),
        (_('Media'), {
            'fields': ('featured_image',)
        }),
        (_('Publication'), {
            'fields': ('author', 'is_published', 'published_date')
        }),
        (_('Statistics'), {
            'fields': ('views',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if obj.is_published and not obj.published_date:
            obj.published_date = timezone.now()
        super().save_model(request, obj, form, change)
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(Gallery)
class GalleryAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('title', 'category', 'image_preview', 'is_active', 'created_at')
    list_filter = [
        "category",
        "is_active",
        ("created_at", CreatedDateRangeFilter),
        ("title", FieldTextFilter),
    ]
    search_fields = ('title', 'description')
    list_per_page = 20
    
    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = _("Preview")
    
    fieldsets = (
        (_('Gallery Item'), {
            'fields': ('title', 'category', 'image', 'description')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(Testimonial)
class TestimonialAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('client_name', 'company', 'rating', 'is_featured', 'is_active', 'created_at')
    list_filter = [
        "is_featured",
        "is_active",
        "rating",
        ("created_at", CreatedDateRangeFilter),
        ("client_name", FieldTextFilter),
    ]
    search_fields = ('client_name', 'company', 'content')
    list_per_page = 20
    
    fieldsets = (
        (_('Client Information'), {
            'fields': ('client_name', 'client_title', 'company', 'client_image')
        }),
        (_('Testimonial'), {
            'fields': ('content', 'rating')
        }),
        (_('Status'), {
            'fields': ('is_featured', 'is_active')
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(Certificate)
class CertificateAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('name', 'issuer', 'image', 'issue_date', 'is_active', 'created_at')
    list_filter = [
        "issuer",
        "is_active",
        ("created_at", CreatedDateRangeFilter),
        ("name", FieldTextFilter),
    ]
    search_fields = ('name', 'issuer', 'skills', 'credential_id')
    list_per_page = 20
    
    fieldsets = (
        (_('Certificate Details'), {
            'fields': ('name', 'issuer', 'certificate_url', 'credential_id')
        }),
        (_('Image'), {  # Add this new fieldset for image
            'fields': ('image',)
        }),
        (_('Dates'), {
            'fields': ('issue_date', 'expiry_date')
        }),
        (_('Skills'), {
            'fields': ('skills',)
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }
    
    # Optional: Add a method to display image thumbnail in list view
    def image(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" style="width: 50px; height: 30px; object-fit: cover;" />')
        return "No Image"
    image.short_description = _('Certificate Image')

@admin.register(Skill)
class SkillAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('name', 'category', 'proficiency', 'years_of_experience', 'is_active', 'order')
    list_filter = [
        "category",
        "is_active",
        ("proficiency", ProficiencyRangeFilter),
        ("name", FieldTextFilter),
    ]
    search_fields = ('name', 'icon')
    list_editable = ('proficiency', 'order', 'is_active')
    list_per_page = 20
    
    fieldsets = (
        (_('Skill Details'), {
            'fields': ('name', 'category', 'icon')
        }),
        (_('Proficiency'), {
            'fields': ('proficiency', 'years_of_experience')
        }),
        (_('Display'), {
            'fields': ('order', 'is_active')
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(ContactMessage)
class ContactMessageAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = [
        "status",
        ("created_at", CreatedDateRangeFilter),
        ("name", FieldTextFilter),
        ("email", FieldTextFilter),
    ]
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('ip_address', 'user_agent', 'created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        (_('Message Details'), {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Metadata'), {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'export_as_pdf']
    
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    mark_as_read.short_description = _("Mark selected messages as read")
    
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_as_replied.short_description = _("Mark selected messages as replied")
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(FAQ)
class FAQAdmin(PDFExportMixin, ImportExportModelAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_filter_submit = True
    
    list_display = ('question', 'category', 'order', 'is_active', 'created_at')
    list_filter = [
        "category",
        "is_active",
        ("created_at", CreatedDateRangeFilter),
        ("question", FieldTextFilter),
    ]
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')
    list_per_page = 20
    
    fieldsets = (
        (_('FAQ Content'), {
            'fields': ('question', 'answer', 'category')
        }),
        (_('Display'), {
            'fields': ('order', 'is_active')
        }),
    )
    
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }
    
    readonly_preprocess_fields = {
        "answer": lambda content: content.strip(),
    }