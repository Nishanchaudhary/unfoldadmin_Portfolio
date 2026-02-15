from django.urls import path
from . import views
from django.conf.urls.i18n import i18n_patterns

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<uuid:id>/', views.project_detail, name='project_detail'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('certificates/', views.certificates, name='certificates'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq_list, name='faq_list'),
    path('download/resume/', views.download_resume, name='download_resume'),
    path('export/projects/pdf/', views.export_projects_pdf, name='export_projects_pdf'),
]