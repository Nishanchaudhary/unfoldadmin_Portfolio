from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    """Contact form"""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your Name'),
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your Email'),
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Subject'),
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Your Message'),
                'rows': 5,
            }),
        }
        labels = {
            'name': _('Name'),
            'email': _('Email'),
            'subject': _('Subject'),
            'message': _('Message'),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add any email validation here
        return email

class FilterForm(forms.Form):
    """Generic filter form"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search...'),
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_('Start date cannot be after end date'))
        
        return cleaned_data

class ImportForm(forms.Form):
    """Import form for CSV/Excel"""
    file = forms.FileField(
        label=_('File'),
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls',
        })
    )
    
    import_type = forms.ChoiceField(
        choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        })
    )