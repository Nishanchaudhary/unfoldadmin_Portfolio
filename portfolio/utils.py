from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.utils.translation import gettext as _

def generate_pdf_report(queryset, title):
    """Generate PDF report from queryset"""
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Table data
    data = []
    
    # Headers
    headers = ['ID', 'Name', 'Created At', 'Status']
    data.append(headers)
    
    # Rows
    for obj in queryset:
        row = [
            str(obj.id)[:8],
            str(obj)[:50],
            obj.created_at.strftime('%Y-%m-%d'),
            'Active' if hasattr(obj, 'is_active') and obj.is_active else 'Inactive'
        ]
        data.append(row)
    
    # Create table
    table = Table(data, colWidths=[1 * inch, 3 * inch, 1.5 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3748')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    
    # Footer
    elements.append(Spacer(1, 0.5 * inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', footer_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

def export_to_csv(queryset, fields, filename):
    """Export queryset to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow(fields)
    
    # Write data
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field, '')
            if callable(value):
                value = value()
            row.append(str(value))
        writer.writerow(row)
    
    return response

def get_chart_data(queryset, date_field, value_field):
    """Generate chart data from queryset"""
    from collections import defaultdict
    import json
    
    data = defaultdict(int)
    
    for obj in queryset:
        date = getattr(obj, date_field)
        if date:
            month_year = date.strftime('%Y-%m')
            value = getattr(obj, value_field, 1)
            data[month_year] += int(value)
    
    # Sort by date
    sorted_data = sorted(data.items())
    
    return {
        'labels': [item[0] for item in sorted_data],
        'data': [item[1] for item in sorted_data]
    }