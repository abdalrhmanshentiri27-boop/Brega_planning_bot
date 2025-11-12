# -*- coding: utf-8 -*-
"""
معالجات الأوامر والرسائل
"""

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
import database as db
import config
import keyboards as kb
from datetime import datetime
import reports


class UserHandlers:
    """معالجات المستخدمين"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البدء"""
        telegram_id = update.effective_user.id
        session = db.get_session()
        
        # البحث عن المستخدم
        user = session.query(db.User).filter_by(telegram_id=telegram_id).first()
        
        if not user:
            # مستخدم جديد - طلب التسجيل
            await update.message.reply_text(
                "🔐 *تسجيل مستخدم جديد*\n\n"
                "مرحباً بك في بوت إدارة التخطيط - شركة البريقة\n\n"
                "للتسجيل، يرجى إرسال معلوماتك بالتنسيق التالي:\n\n"
                "الاسم الكامل: [اسمك]\n"
                "الإدارة: [اسم الإدارة]\n"
                "رقم الهاتف: [رقم الهاتف]\n"
                "البريد الإلكتروني: [البريد]",
                parse_mode='Markdown'
            )
        else:
            # تحديث آخر تسجيل دخول
            user.last_login = datetime.now()
            session.commit()
            
            # عرض القائمة الرئيسية
            await update.message.reply_text(
                config.MESSAGES['welcome'],
                parse_mode='Markdown',
                reply_markup=kb.main_menu_keyboard(user.role)
            )
        
        session.close()
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        await update.message.reply_text(
            config.MESSAGES['help'],
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي"""
        telegram_id = update.effective_user.id
        session = db.get_session()
        user = session.query(db.User).filter_by(telegram_id=telegram_id).first()
        
        if user:
            profile_text = f"""
👤 *الملف الشخصي*

📛 الاسم: {user.full_name}
🏢 الإدارة: {user.department}
🔑 الصلاحية: {user.role}
📞 الهاتف: {user.phone or 'غير محدد'}
📧 البريد: {user.email or 'غير محدد'}
📅 تاريخ التسجيل: {user.created_at.strftime('%Y-%m-%d')}
🕐 آخر دخول: {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'الآن'}
            """
            
            await update.message.reply_text(profile_text, parse_mode='Markdown')
        
        session.close()


class PlanHandlers:
    """معالجات الخطط"""
    
    @staticmethod
    async def plans_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة الخطط"""
        query = update.callback_query if update.callback_query else None
        telegram_id = update.effective_user.id
        session = db.get_session()
        user = session.query(db.User).filter_by(telegram_id=telegram_id).first()
        
        can_add = user.role in [config.UserRoles.ADMIN, config.UserRoles.PLANNING_OFFICER, 
                                config.UserRoles.DEPARTMENT_OFFICER]
        
        message_text = "📋 *إدارة الخطط*\n\nاختر الإجراء المطلوب:"
        
        if query:
            await query.edit_message_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.plans_menu_keyboard(can_add)
            )
        else:
            await update.message.reply_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.plans_menu_keyboard(can_add)
            )
        
        session.close()
    
    @staticmethod
    async def list_plans(update: Update, context: ContextTypes.DEFAULT_TYPE, filter_type=None):
        """عرض قائمة الخطط"""
        query = update.callback_query
        session = db.get_session()
        
        # جلب الخطط
        plans_query = session.query(db.Plan)
        
        if filter_type:
            plans_query = plans_query.filter_by(plan_type=filter_type)
        
        plans = plans_query.order_by(db.Plan.year.desc()).limit(20).all()
        
        if plans:
            response = "📋 *قائمة الخطط*\n\n"
            for plan in plans:
                response += f"🔹 *{plan.title}*\n"
                response += f"   📂 الإدارة: {plan.department}\n"
                response += f"   📅 السنة: {plan.year}\n"
                response += f"   📊 نسبة الإنجاز: {plan.completion_percentage}%\n"
                response += f"   🔖 النوع: {plan.plan_type}\n"
                response += f"   /plan_{plan.id}\n\n"
        else:
            response = "❌ لا توجد خطط مسجلة حالياً."
        
        await query.edit_message_text(response, parse_mode='Markdown')
        session.close()


class ProjectHandlers:
    """معالجات المشاريع"""
    
    @staticmethod
    async def projects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة المشاريع"""
        query = update.callback_query if update.callback_query else None
        telegram_id = update.effective_user.id
        session = db.get_session()
        user = session.query(db.User).filter_by(telegram_id=telegram_id).first()
        
        can_add = user.role in [config.UserRoles.ADMIN, config.UserRoles.PLANNING_OFFICER]
        
        message_text = "🏗️ *إدارة المشاريع*\n\nاختر الإجراء المطلوب:"
        
        if query:
            await query.edit_message_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.projects_menu_keyboard(can_add)
            )
        else:
            await update.message.reply_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.projects_menu_keyboard(can_add)
            )
        
        session.close()
    
    @staticmethod
    async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE, status_filter=None):
        """عرض قائمة المشاريع"""
        query = update.callback_query
        session = db.get_session()
        
        projects_query = session.query(db.Project)
        
        if status_filter:
            projects_query = projects_query.filter_by(status=status_filter)
        
        projects = projects_query.order_by(db.Project.created_at.desc()).limit(20).all()
        
        if projects:
            response = "🏗️ *قائمة المشاريع*\n\n"
            for project in projects:
                response += f"🔹 *{project.title}*\n"
                response += f"   🏢 الإدارة: {project.department}\n"
                response += f"   📊 الحالة: {project.status}\n"
                response += f"   📈 نسبة الإنجاز: {project.completion_percentage}%\n"
                if project.project_code:
                    response += f"   🔢 الكود: {project.project_code}\n"
                response += f"   /project_{project.id}\n\n"
        else:
            response = "❌ لا توجد مشاريع مسجلة."
        
        await query.edit_message_text(response, parse_mode='Markdown')
        session.close()
    
    @staticmethod
    async def project_details(update: Update, context: ContextTypes.DEFAULT_TYPE, project_id: int):
        """عرض تفاصيل المشروع"""
        session = db.get_session()
        project = session.query(db.Project).filter_by(id=project_id).first()
        
        if project:
            details = f"""
🏗️ *تفاصيل المشروع*

📌 *العنوان:* {project.title}
🔢 *الكود:* {project.project_code or 'غير محدد'}

🎯 *الغاية:* {project.goal or 'غير محدد'}
📝 *الغرض:* {project.purpose or 'غير محدد'}
🎯 *الأهداف:*
{project.objectives or 'غير محدد'}

🏢 *الجهة المعنية:* {project.department}
📊 *الحالة:* {project.status}
🔄 *المرحلة الحالية:* {project.current_phase or 'غير محدد'}
📈 *نسبة الإنجاز:* {project.completion_percentage}%

💰 *الميزانية:* {project.budget if project.budget else 'غير محدد'}
📅 *تاريخ البدء:* {project.start_date if project.start_date else 'غير محدد'}
📅 *تاريخ الانتهاء المتوقع:* {project.expected_end_date if project.expected_end_date else 'غير محدد'}
            """
            
            telegram_id = update.effective_user.id
            user = session.query(db.User).filter_by(telegram_id=telegram_id).first()
            can_edit = user.role in [config.UserRoles.ADMIN, config.UserRoles.PLANNING_OFFICER]
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    details,
                    parse_mode='Markdown',
                    reply_markup=kb.project_details_keyboard(project_id, can_edit)
                )
            else:
                await update.message.reply_text(
                    details,
                    parse_mode='Markdown',
                    reply_markup=kb.project_details_keyboard(project_id, can_edit)
                )
        else:
            await update.message.reply_text("❌ المشروع غير موجود.")
        
        session.close()


class PurchaseHandlers:
    """معالجات البنود الشرائية"""
    
    @staticmethod
    async def purchases_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة البنود الشرائية"""
        query = update.callback_query if update.callback_query else None
        telegram_id = update.effective_user.id
        session = db.get_session()
        user = session.query(db.User).filter_by(telegram_id=telegram_id).first()
        
        can_add = user.role in [config.UserRoles.ADMIN, config.UserRoles.PLANNING_OFFICER,
                                config.UserRoles.COMMITTEE_MEMBER]
        
        message_text = "🛒 *إدارة البنود الشرائية*\n\nاختر الإجراء المطلوب:"
        
        if query:
            await query.edit_message_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.purchases_menu_keyboard(can_add)
            )
        else:
            await update.message.reply_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.purchases_menu_keyboard(can_add)
            )
        
        session.close()
    
    @staticmethod
    async def list_purchases(update: Update, context: ContextTypes.DEFAULT_TYPE, status_filter=None):
        """عرض البنود الشرائية"""
        query = update.callback_query
        session = db.get_session()
        
        purchases_query = session.query(db.Purchase)
        
        if status_filter:
            purchases_query = purchases_query.filter_by(status=status_filter)
        
        purchases = purchases_query.order_by(db.Purchase.created_at.desc()).limit(20).all()
        
        if purchases:
            response = "🛒 *قائمة البنود الشرائية*\n\n"
            for purchase in purchases:
                response += f"🔹 *{purchase.title}*\n"
                response += f"   🏢 الإدارة: {purchase.department}\n"
                response += f"   📊 الحالة: {purchase.status}\n"
                if purchase.purchase_code:
                    response += f"   🔢 الكود: {purchase.purchase_code}\n"
                if purchase.budget:
                    response += f"   💰 الميزانية: {purchase.budget}\n"
                response += f"   /purchase_{purchase.id}\n\n"
        else:
            response = "❌ لا توجد بنود شرائية مسجلة."
        
        await query.edit_message_text(response, parse_mode='Markdown')
        session.close()


class ReportHandlers:
    """معالجات التقارير"""
    
    @staticmethod
    async def reports_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة التقارير"""
        query = update.callback_query if update.callback_query else None
        message_text = "📊 *التقارير والإحصائيات*\n\nاختر نوع التقرير:"
        
        if query:
            await query.edit_message_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.reports_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=kb.reports_menu_keyboard()
            )
    
    @staticmethod
    async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لوحة المؤشرات"""
        session = db.get_session()
        
        # إحصائيات المشاريع
        total_projects = session.query(db.Project).count()
        active_projects = session.query(db.Project).filter_by(status=config.ProjectStatus.IN_PROGRESS).count()
        completed_projects = session.query(db.Project).filter_by(status=config.ProjectStatus.COMPLETED).count()
        
        # إحصائيات الخطط
        total_plans = session.query(db.Plan).count()
        active_plans = session.query(db.Plan).filter_by(status='نشط').count()
        
        # إحصائيات البنود
        total_purchases = session.query(db.Purchase).count()
        awarded_purchases = session.query(db.Purchase).filter_by(status=config.PurchaseStatus.AWARDED).count()
        
        # حساب متوسط نسبة الإنجاز
        from sqlalchemy import func
        avg_project_progress = session.query(func.avg(db.Project.completion_percentage)).scalar() or 0
        avg_plan_progress = session.query(func.avg(db.Plan.completion_percentage)).scalar() or 0
        
        dashboard_text = f"""
📈 *لوحة المؤشرات الرئيسية*
_آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}_

🏗️ *المشاريع:*
   • إجمالي المشاريع: {total_projects}
   • المشاريع النشطة: {active_projects}
   • المشاريع المكتملة: {completed_projects}
   • متوسط نسبة الإنجاز: {avg_project_progress:.1f}%

📋 *الخطط:*
   • إجمالي الخطط: {total_plans}
   • الخطط النشطة: {active_plans}
   • متوسط نسبة الإنجاز: {avg_plan_progress:.1f}%

🛒 *البنود الشرائية:*
   • إجمالي البنود: {total_purchases}
   • البنود المرساة: {awarded_purchases}
   • نسبة الترسية: {(awarded_purchases/total_purchases*100) if total_purchases > 0 else 0:.1f}%
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                dashboard_text,
                parse_mode='Markdown',
                reply_markup=kb.dashboard_keyboard()
            )
        else:
            await update.message.reply_text(
                dashboard_text,
                parse_mode='Markdown',
                reply_markup=kb.dashboard_keyboard()
            )
        
        session.close()


class SearchHandlers:
    """معالجات البحث"""
    
    @staticmethod
    async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """البحث العام"""
        await update.message.reply_text(
            "🔍 *البحث*\n\n"
            "أرسل كلمة البحث للبحث في:\n"
            "• الخطط\n"
            "• المشاريع\n"
            "• البنود الشرائية",
            parse_mode='Markdown'
        )
        context.user_data['awaiting_search'] = True
    
    @staticmethod
    async def perform_search(update: Update, context: ContextTypes.DEFAULT_TYPE, query_text: str):
        """تنفيذ البحث"""
        session = db.get_session()
        search_term = f"%{query_text}%"
        
        # البحث في المشاريع
        projects = session.query(db.Project).filter(
            (db.Project.title.like(search_term)) |
            (db.Project.description.like(search_term))
        ).limit(5).all()
        
        # البحث في الخطط
        plans = session.query(db.Plan).filter(
            (db.Plan.title.like(search_term)) |
            (db.Plan.description.like(search_term))
        ).limit(5).all()
        
        # البحث في البنود
        purchases = session.query(db.Purchase).filter(
            (db.Purchase.title.like(search_term)) |
            (db.Purchase.description.like(search_term))
        ).limit(5).all()
        
        response = f"🔍 *نتائج البحث عن:* {query_text}\n\n"
        
        if projects:
            response += "🏗️ *المشاريع:*\n"
            for p in projects:
                response += f"  • {p.title} - /project_{p.id}\n"
            response += "\n"
        
        if plans:
            response += "📋 *الخطط:*\n"
            for p in plans:
                response += f"  • {p.title} - /plan_{p.id}\n"
            response += "\n"
        
        if purchases:
            response += "🛒 *البنود الشرائية:*\n"
            for p in purchases:
                response += f"  • {p.title} - /purchase_{p.id}\n"
        
        if not (projects or plans or purchases):
            response += "❌ لم يتم العثور على نتائج."
        
        await update.message.reply_text(response, parse_mode='Markdown')
        session.close()
