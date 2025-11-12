# -*- coding: utf-8 -*-
"""
نظام التنبيهات والإشعارات
"""

from datetime import datetime, timedelta
from telegram import Bot
import database as db
import config
import asyncio


class NotificationManager:
    """مدير التنبيهات"""
    
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.session = db.get_session()
    
    async def check_plan_deadlines(self):
        """فحص مواعيد تحديث الخطط"""
        today = datetime.now().date()
        
        for days_before in config.NOTIFICATION_DAYS_BEFORE:
            target_date = today + timedelta(days=days_before)
            
            # البحث عن الخطط التي موعد تحديثها قريب
            plans = self.session.query(db.Plan).filter(
                db.Plan.next_update_date == target_date,
                db.Plan.status == 'نشط'
            ).all()
            
            for plan in plans:
                await self._send_plan_reminder(plan, days_before)
    
    async def check_project_milestones(self):
        """فحص المراحل المهمة للمشاريع"""
        today = datetime.now().date()
        
        # المشاريع التي تقترب من موعد الانتهاء
        projects = self.session.query(db.Project).filter(
            db.Project.expected_end_date.isnot(None),
            db.Project.status == config.ProjectStatus.IN_PROGRESS
        ).all()
        
        for project in projects:
            days_remaining = (project.expected_end_date - today).days
            
            if days_remaining in config.NOTIFICATION_DAYS_BEFORE:
                await self._send_project_deadline_reminder(project, days_remaining)
            
            # تنبيه إذا كان المشروع متأخر
            if days_remaining < 0 and project.completion_percentage < 100:
                await self._send_project_overdue_alert(project, abs(days_remaining))
    
    async def check_purchase_status(self):
        """فحص حالة البنود الشرائية"""
        # البنود التي في حالة "قيد الإجراء" لأكثر من 30 يوم
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        purchases = self.session.query(db.Purchase).filter(
            db.Purchase.status == config.PurchaseStatus.IN_PROCEDURE,
            db.Purchase.updated_at < thirty_days_ago
        ).all()
        
        for purchase in purchases:
            await self._send_purchase_delay_alert(purchase)
    
    async def send_monthly_reports(self):
        """إرسال التقارير الشهرية التلقائية"""
        # الحصول على المستخدمين الإداريين
        admins = self.session.query(db.User).filter(
            db.User.role == config.UserRoles.ADMIN,
            db.User.is_active == True
        ).all()
        
        for admin in admins:
            await self._send_monthly_summary(admin)
    
    async def _send_plan_reminder(self, plan, days_before):
        """إرسال تذكير بموعد تحديث الخطة"""
        message = f"""
⏰ *تذكير: تحديث الخطة*

📋 الخطة: {plan.title}
🏢 الإدارة: {plan.department}
📅 موعد التحديث: {plan.next_update_date.strftime('%Y-%m-%d')}
⏳ المتبقي: {days_before} يوم

يرجى تحديث حالة الخطة وإدخال نسبة الإنجاز.
        """
        
        # إرسال للمسؤولين عن الإدارة
        users = self.session.query(db.User).filter(
            db.User.department == plan.department,
            db.User.is_active == True
        ).all()
        
        for user in users:
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
                # حفظ في قاعدة البيانات
                notification = db.Notification(
                    user_id=user.id,
                    title='تذكير تحديث خطة',
                    message=message,
                    notification_type='خطة',
                    related_id=plan.id,
                    sent_date=datetime.now()
                )
                self.session.add(notification)
            except Exception as e:
                print(f"خطأ في إرسال التنبيه: {e}")
        
        self.session.commit()
    
    async def _send_project_deadline_reminder(self, project, days_remaining):
        """تذكير بموعد انتهاء المشروع"""
        message = f"""
⏰ *تنبيه: اقتراب موعد انتهاء المشروع*

🏗️ المشروع: {project.title}
🏢 الإدارة: {project.department}
📅 موعد الانتهاء: {project.expected_end_date.strftime('%Y-%m-%d')}
⏳ المتبقي: {days_remaining} يوم
📊 نسبة الإنجاز الحالية: {project.completion_percentage}%

{self._get_progress_emoji(project.completion_percentage, days_remaining)}
        """
        
        # إرسال للمسؤولين
        users = self.session.query(db.User).filter(
            db.User.department == project.department,
            db.User.role.in_([config.UserRoles.ADMIN, config.UserRoles.PLANNING_OFFICER]),
            db.User.is_active == True
        ).all()
        
        for user in users:
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال التنبيه: {e}")
    
    async def _send_project_overdue_alert(self, project, days_overdue):
        """تنبيه بتأخر المشروع"""
        message = f"""
🚨 *تنبيه: مشروع متأخر*

🏗️ المشروع: {project.title}
🏢 الإدارة: {project.department}
📅 كان من المفترض الانتهاء في: {project.expected_end_date.strftime('%Y-%m-%d')}
⏰ متأخر بـ: {days_overdue} يوم
📊 نسبة الإنجاز: {project.completion_percentage}%

⚠️ يرجى اتخاذ الإجراءات اللازمة.
        """
        
        # إرسال للإدارة العليا
        admins = self.session.query(db.User).filter(
            db.User.role == config.UserRoles.ADMIN,
            db.User.is_active == True
        ).all()
        
        for admin in admins:
            try:
                await self.bot.send_message(
                    chat_id=admin.telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال التنبيه: {e}")
    
    async def _send_purchase_delay_alert(self, purchase):
        """تنبيه بتأخر البند الشرائي"""
        days_in_procedure = (datetime.now() - purchase.updated_at).days
        
        message = f"""
⚠️ *تنبيه: بند شرائي متأخر*

🛒 البند: {purchase.title}
🏢 الإدارة: {purchase.department}
📊 الحالة: {purchase.status}
⏰ مدة البقاء في الحالة: {days_in_procedure} يوم

يرجى متابعة الإجراءات.
        """
        
        # إرسال لأعضاء اللجنة والإدارة
        users = self.session.query(db.User).filter(
            db.User.role.in_([
                config.UserRoles.ADMIN,
                config.UserRoles.COMMITTEE_MEMBER,
                config.UserRoles.PLANNING_OFFICER
            ]),
            db.User.is_active == True
        ).all()
        
        for user in users:
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال التنبيه: {e}")
    
    async def _send_monthly_summary(self, admin):
        """إرسال الملخص الشهري"""
        from sqlalchemy import func
        
        # إحصائيات الشهر الحالي
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        
        new_plans = self.session.query(db.Plan).filter(
            db.Plan.created_at >= start_of_month
        ).count()
        
        new_projects = self.session.query(db.Project).filter(
            db.Project.created_at >= start_of_month
        ).count()
        
        new_purchases = self.session.query(db.Purchase).filter(
            db.Purchase.created_at >= start_of_month
        ).count()
        
        completed_projects = self.session.query(db.Project).filter(
            db.Project.status == config.ProjectStatus.COMPLETED,
            db.Project.actual_end_date >= start_of_month
        ).count()
        
        message = f"""
📊 *الملخص الشهري - {datetime.now().strftime('%B %Y')}*

📋 *الخطط:*
   • خطط جديدة: {new_plans}

🏗️ *المشاريع:*
   • مشاريع جديدة: {new_projects}
   • مشاريع مكتملة: {completed_projects}

🛒 *البنود الشرائية:*
   • بنود جديدة: {new_purchases}

استخدم /reports للحصول على تقارير تفصيلية.
        """
        
        try:
            await self.bot.send_message(
                chat_id=admin.telegram_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"خطأ في إرسال الملخص الشهري: {e}")
    
    def _get_progress_emoji(self, completion, days_remaining):
        """الحصول على رمز تعبيري بناءً على التقدم"""
        if completion >= 90:
            return "✅ المشروع يسير بشكل ممتاز!"
        elif completion >= 70:
            return "👍 التقدم جيد، استمروا!"
        elif completion >= 50 and days_remaining > 7:
            return "⚠️ يرجى تسريع وتيرة العمل"
        else:
            return "🚨 يحتاج إلى تدخل عاجل!"
    
    async def create_custom_notification(self, user_id, title, message, notification_type, related_id=None):
        """إنشاء تنبيه مخصص"""
        user = self.session.query(db.User).filter_by(id=user_id).first()
        
        if user:
            notification = db.Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                related_id=related_id,
                sent_date=datetime.now()
            )
            self.session.add(notification)
            self.session.commit()
            
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"*{title}*\n\n{message}",
                    parse_mode='Markdown'
                )
                return True
            except Exception as e:
                print(f"خطأ في إرسال التنبيه المخصص: {e}")
                return False
        return False
    
    def __del__(self):
        self.session.close()


async def run_scheduled_notifications(bot_token):
    """تشغيل التنبيهات المجدولة"""
    manager = NotificationManager(bot_token)
    
    while True:
        try:
            # فحص يومي
            await manager.check_plan_deadlines()
            await manager.check_project_milestones()
            await manager.check_purchase_status()
            
            # فحص التقارير الشهرية (اليوم الأول من الشهر)
            if datetime.now().day == config.AUTO_REPORT_DAY:
                await manager.send_monthly_reports()
            
            # انتظار 24 ساعة
            await asyncio.sleep(86400)
        except Exception as e:
            print(f"خطأ في نظام التنبيهات: {e}")
            await asyncio.sleep(3600)  # إعادة المحاولة بعد ساعة
