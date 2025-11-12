# -*- coding: utf-8 -*-
"""
نظام توليد التقارير
"""

from datetime import datetime, timedelta
from sqlalchemy import func
import database as db
import config
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from io import BytesIO


class ReportGenerator:
    """مولد التقارير"""
    
    def __init__(self):
        self.session = db.get_session()
        # تسجيل خط عربي (يحتاج ملف خط)
        # pdfmetrics.registerFont(TTFont('Arabic', 'path/to/arabic/font.ttf'))
    
    def generate_plans_report(self, year=None, department=None, format='PDF'):
        """تقرير الخطط"""
        query = self.session.query(db.Plan)
        
        if year:
            query = query.filter_by(year=year)
        if department:
            query = query.filter_by(department=department)
        
        plans = query.all()
        
        if format == 'PDF':
            return self._generate_plans_pdf(plans)
        else:
            return self._generate_plans_excel(plans)
    
    def generate_projects_report(self, status=None, department=None, format='PDF'):
        """تقرير المشاريع"""
        query = self.session.query(db.Project)
        
        if status:
            query = query.filter_by(status=status)
        if department:
            query = query.filter_by(department=department)
        
        projects = query.all()
        
        if format == 'PDF':
            return self._generate_projects_pdf(projects)
        else:
            return self._generate_projects_excel(projects)
    
    def generate_purchases_report(self, status=None, format='PDF'):
        """تقرير البنود الشرائية"""
        query = self.session.query(db.Purchase)
        
        if status:
            query = query.filter_by(status=status)
        
        purchases = query.all()
        
        if format == 'PDF':
            return self._generate_purchases_pdf(purchases)
        else:
            return self._generate_purchases_excel(purchases)
    
    def generate_monthly_report(self, year, month, format='PDF'):
        """التقرير الشهري الشامل"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # جمع البيانات
        plans = self.session.query(db.Plan).filter(
            db.Plan.created_at >= start_date,
            db.Plan.created_at < end_date
        ).all()
        
        projects = self.session.query(db.Project).filter(
            db.Project.created_at >= start_date,
            db.Project.created_at < end_date
        ).all()
        
        purchases = self.session.query(db.Purchase).filter(
            db.Purchase.created_at >= start_date,
            db.Purchase.created_at < end_date
        ).all()
        
        if format == 'PDF':
            return self._generate_monthly_pdf(plans, projects, purchases, year, month)
        else:
            return self._generate_monthly_excel(plans, projects, purchases, year, month)
    
    def generate_comprehensive_report(self, format='PDF'):
        """التقرير الشامل"""
        # إحصائيات عامة
        stats = {
            'total_plans': self.session.query(db.Plan).count(),
            'active_plans': self.session.query(db.Plan).filter_by(status='نشط').count(),
            'total_projects': self.session.query(db.Project).count(),
            'active_projects': self.session.query(db.Project).filter_by(
                status=config.ProjectStatus.IN_PROGRESS
            ).count(),
            'completed_projects': self.session.query(db.Project).filter_by(
                status=config.ProjectStatus.COMPLETED
            ).count(),
            'total_purchases': self.session.query(db.Purchase).count(),
            'awarded_purchases': self.session.query(db.Purchase).filter_by(
                status=config.PurchaseStatus.AWARDED
            ).count(),
        }
        
        # متوسط نسب الإنجاز
        stats['avg_plan_progress'] = self.session.query(
            func.avg(db.Plan.completion_percentage)
        ).scalar() or 0
        
        stats['avg_project_progress'] = self.session.query(
            func.avg(db.Project.completion_percentage)
        ).scalar() or 0
        
        if format == 'PDF':
            return self._generate_comprehensive_pdf(stats)
        else:
            return self._generate_comprehensive_excel(stats)
    
    # دوال توليد PDF
    
    def _generate_plans_pdf(self, plans):
        """توليد PDF للخطط"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # العنوان
        title = Paragraph("تقرير الخطط", getSampleStyleSheet()['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # البيانات
        data = [['العنوان', 'النوع', 'الإدارة', 'السنة', 'نسبة الإنجاز']]
        for plan in plans:
            data.append([
                plan.title[:30],
                plan.plan_type,
                plan.department,
                str(plan.year),
                f"{plan.completion_percentage}%"
            ])
        
        # إنشاء الجدول
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    def _generate_projects_pdf(self, projects):
        """توليد PDF للمشاريع"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        
        title = Paragraph("تقرير المشاريع", getSampleStyleSheet()['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        data = [['الكود', 'العنوان', 'الإدارة', 'الحالة', 'نسبة الإنجاز', 'الميزانية']]
        for project in projects:
            data.append([
                project.project_code or '-',
                project.title[:40],
                project.department,
                project.status,
                f"{project.completion_percentage}%",
                str(project.budget) if project.budget else '-'
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    def _generate_purchases_pdf(self, purchases):
        """توليد PDF للبنود الشرائية"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        
        title = Paragraph("تقرير البنود الشرائية", getSampleStyleSheet()['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        data = [['الكود', 'العنوان', 'الإدارة', 'الحالة', 'الميزانية', 'اللجنة']]
        for purchase in purchases:
            data.append([
                purchase.purchase_code or '-',
                purchase.title[:40],
                purchase.department,
                purchase.status,
                str(purchase.budget) if purchase.budget else '-',
                purchase.committee or '-'
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    def _generate_comprehensive_pdf(self, stats):
        """التقرير الشامل PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        title = Paragraph("التقرير الشامل - إدارة التخطيط", getSampleStyleSheet()['Title'])
        elements.append(title)
        elements.append(Spacer(1, 1*cm))
        
        # إحصائيات
        data = [
            ['المؤشر', 'القيمة'],
            ['إجمالي الخطط', str(stats['total_plans'])],
            ['الخطط النشطة', str(stats['active_plans'])],
            ['متوسط إنجاز الخطط', f"{stats['avg_plan_progress']:.1f}%"],
            ['إجمالي المشاريع', str(stats['total_projects'])],
            ['المشاريع النشطة', str(stats['active_projects'])],
            ['المشاريع المكتملة', str(stats['completed_projects'])],
            ['متوسط إنجاز المشاريع', f"{stats['avg_project_progress']:.1f}%"],
            ['إجمالي البنود الشرائية', str(stats['total_purchases'])],
            ['البنود المرساة', str(stats['awarded_purchases'])],
        ]
        
        table = Table(data, colWidths=[12*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    # دوال توليد Excel
    
    def _generate_plans_excel(self, plans):
        """توليد Excel للخطط"""
        data = []
        for plan in plans:
            data.append({
                'العنوان': plan.title,
                'النوع': plan.plan_type,
                'الإدارة': plan.department,
                'السنة': plan.year,
                'نسبة الإنجاز': plan.completion_percentage,
                'تاريخ البدء': plan.start_date,
                'تاريخ الانتهاء': plan.end_date,
                'الحالة': plan.status
            })
        
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer
    
    def _generate_projects_excel(self, projects):
        """توليد Excel للمشاريع"""
        data = []
        for project in projects:
            data.append({
                'الكود': project.project_code,
                'العنوان': project.title,
                'الإدارة': project.department,
                'الحالة': project.status,
                'المرحلة': project.current_phase,
                'نسبة الإنجاز': project.completion_percentage,
                'الميزانية': project.budget,
                'تاريخ البدء': project.start_date,
                'تاريخ الانتهاء المتوقع': project.expected_end_date
            })
        
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer
    
    def _generate_purchases_excel(self, purchases):
        """توليد Excel للبنود الشرائية"""
        data = []
        for purchase in purchases:
            data.append({
                'الكود': purchase.purchase_code,
                'العنوان': purchase.title,
                'الإدارة': purchase.department,
                'الحالة': purchase.status,
                'الميزانية': purchase.budget,
                'الميزانية المعتمدة': purchase.approved_budget,
                'اللجنة': purchase.committee,
                'تاريخ الطرح': purchase.announcement_date,
                'تاريخ الترسية': purchase.award_date,
                'المقاول': purchase.contractor
            })
        
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer
    
    def _generate_monthly_excel(self, plans, projects, purchases, year, month):
        """التقرير الشهري Excel"""
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # ورقة الخطط
            plans_data = [{'العنوان': p.title, 'النوع': p.plan_type, 'الإدارة': p.department} for p in plans]
            pd.DataFrame(plans_data).to_excel(writer, sheet_name='الخطط', index=False)
            
            # ورقة المشاريع
            projects_data = [{'العنوان': p.title, 'الحالة': p.status, 'الإدارة': p.department} for p in projects]
            pd.DataFrame(projects_data).to_excel(writer, sheet_name='المشاريع', index=False)
            
            # ورقة البنود
            purchases_data = [{'العنوان': p.title, 'الحالة': p.status, 'الإدارة': p.department} for p in purchases]
            pd.DataFrame(purchases_data).to_excel(writer, sheet_name='البنود الشرائية', index=False)
        
        buffer.seek(0)
        return buffer
    
    def _generate_monthly_pdf(self, plans, projects, purchases, year, month):
        """التقرير الشهري PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        title = Paragraph(f"التقرير الشهري - {year}/{month}", getSampleStyleSheet()['Title'])
        elements.append(title)
        elements.append(Spacer(1, 1*cm))
        
        # ملخص
        summary = Paragraph(f"""
        <b>ملخص التقرير:</b><br/>
        • الخطط الجديدة: {len(plans)}<br/>
        • المشاريع الجديدة: {len(projects)}<br/>
        • البنود الشرائية الجديدة: {len(purchases)}
        """, getSampleStyleSheet()['Normal'])
        elements.append(summary)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _generate_comprehensive_excel(self, stats):
        """التقرير الشامل Excel"""
        data = {
            'المؤشر': [
                'إجمالي الخطط', 'الخطط النشطة', 'متوسط إنجاز الخطط',
                'إجمالي المشاريع', 'المشاريع النشطة', 'المشاريع المكتملة',
                'متوسط إنجاز المشاريع', 'إجمالي البنود', 'البنود المرساة'
            ],
            'القيمة': [
                stats['total_plans'], stats['active_plans'], f"{stats['avg_plan_progress']:.1f}%",
                stats['total_projects'], stats['active_projects'], stats['completed_projects'],
                f"{stats['avg_project_progress']:.1f}%", stats['total_purchases'], stats['awarded_purchases']
            ]
        }
        
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer
    
    def __del__(self):
        self.session.close()
