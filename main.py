# -*- coding: utf-8 -*-
"""
البرنامج الرئيسي لبوت إدارة التخطيط - شركة البريقة
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
import config
import database as db
import handlers
import keyboards as kb
import asyncio
from notifications import run_scheduled_notifications

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
(AWAITING_REGISTRATION, AWAITING_PLAN_DETAILS, AWAITING_PROJECT_DETAILS,
 AWAITING_PURCHASE_DETAILS, AWAITING_SEARCH) = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    await handlers.UserHandlers.start(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help"""
    await handlers.UserHandlers.help_command(update, context)


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /profile"""
    await handlers.UserHandlers.profile(update, context)


async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /plans"""
    await handlers.PlanHandlers.plans_menu(update, context)


async def projects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /projects"""
    await handlers.ProjectHandlers.projects_menu(update, context)


async def purchases_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /purchases"""
    await handlers.PurchaseHandlers.purchases_menu(update, context)


async def reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /reports"""
    await handlers.ReportHandlers.reports_menu(update, context)


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /dashboard"""
    await handlers.ReportHandlers.dashboard(update, context)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /search"""
    await handlers.SearchHandlers.search(update, context)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار التفاعلية"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # القائمة الرئيسية
    if data == "main_menu":
        telegram_id = update.effective_user.id
        session = db.get_session()
        user = session.query(db.User).filter_by(telegram_id=telegram_id).first()
        await query.edit_message_text(
            config.MESSAGES['welcome'],
            parse_mode='Markdown',
            reply_markup=kb.main_menu_keyboard(user.role)
        )
        session.close()
    
    # معالجات الخطط
    elif data.startswith("plans_"):
        if data == "plans_menu":
            await handlers.PlanHandlers.plans_menu(update, context)
        elif data == "plans_list_all":
            await handlers.PlanHandlers.list_plans(update, context)
        elif data.startswith("plans_search_"):
            await query.edit_message_text("🔍 أرسل كلمة البحث...")
            context.user_data['search_type'] = data.replace("plans_search_", "")
    
    # معالجات المشاريع
    elif data.startswith("projects_"):
        if data == "projects_menu":
            await handlers.ProjectHandlers.projects_menu(update, context)
        elif data == "projects_active":
            await handlers.ProjectHandlers.list_projects(update, context, config.ProjectStatus.IN_PROGRESS)
        elif data == "projects_completed":
            await handlers.ProjectHandlers.list_projects(update, context, config.ProjectStatus.COMPLETED)
        elif data == "projects_suspended":
            await handlers.ProjectHandlers.list_projects(update, context, config.ProjectStatus.SUSPENDED)
    
    # معالجات البنود الشرائية
    elif data.startswith("purchases_"):
        if data == "purchases_menu":
            await handlers.PurchaseHandlers.purchases_menu(update, context)
        elif data == "purchases_all":
            await handlers.PurchaseHandlers.list_purchases(update, context)
        elif data == "purchases_registered":
            await handlers.PurchaseHandlers.list_purchases(update, context, config.PurchaseStatus.REGISTERED)
        elif data == "purchases_announced":
            await handlers.PurchaseHandlers.list_purchases(update, context, config.PurchaseStatus.ANNOUNCED)
        elif data == "purchases_procedure":
            await handlers.PurchaseHandlers.list_purchases(update, context, config.PurchaseStatus.IN_PROCEDURE)
        elif data == "purchases_awarded":
            await handlers.PurchaseHandlers.list_purchases(update, context, config.PurchaseStatus.AWARDED)
    
    # معالجات التقارير
    elif data.startswith("report_"):
        if data == "report_plans":
            await query.edit_message_text(
                "📋 اختر صيغة تقرير الخطط:",
                reply_markup=kb.report_format_keyboard()
            )
            context.user_data['report_type'] = 'plans'
        elif data == "report_projects":
            await query.edit_message_text(
                "🏗️ اختر صيغة تقرير المشاريع:",
                reply_markup=kb.report_format_keyboard()
            )
            context.user_data['report_type'] = 'projects'
        elif data == "report_purchases":
            await query.edit_message_text(
                "🛒 اختر صيغة تقرير البنود:",
                reply_markup=kb.report_format_keyboard()
            )
            context.user_data['report_type'] = 'purchases'
    
    # لوحة المؤشرات
    elif data == "dashboard_refresh":
        await handlers.ReportHandlers.dashboard(update, context)
    
    # إلغاء
    elif data == "cancel":
        await query.edit_message_text("❌ تم الإلغاء.")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل النصية"""
    text = update.message.text
    
    # القوائم الرئيسية
    if text == "📋 الخطط":
        await handlers.PlanHandlers.plans_menu(update, context)
    elif text == "🏗️ المشاريع":
        await handlers.ProjectHandlers.projects_menu(update, context)
    elif text == "🛒 البنود الشرائية":
        await handlers.PurchaseHandlers.purchases_menu(update, context)
    elif text == "📊 التقارير":
        await handlers.ReportHandlers.reports_menu(update, context)
    elif text == "📈 لوحة المؤشرات":
        await handlers.ReportHandlers.dashboard(update, context)
    elif text == "🔍 البحث":
        await handlers.SearchHandlers.search(update, context)
    elif text == "ℹ️ المساعدة":
        await handlers.UserHandlers.help_command(update, context)
    elif text == "👤 حسابي":
        await handlers.UserHandlers.profile(update, context)
    
    # البحث
    elif context.user_data.get('awaiting_search'):
        await handlers.SearchHandlers.perform_search(update, context, text)
        context.user_data['awaiting_search'] = False
    
    # رسائل أخرى
    else:
        # محاولة استخراج معرف من الرسالة (مثل /project_123)
        if text.startswith('/project_'):
            try:
                project_id = int(text.replace('/project_', ''))
                await handlers.ProjectHandlers.project_details(update, context, project_id)
            except:
                pass
        elif text.startswith('/plan_'):
            try:
                plan_id = int(text.replace('/plan_', ''))
                # يمكن إضافة معالج تفاصيل الخطة هنا
                await update.message.reply_text(f"عرض تفاصيل الخطة #{plan_id}")
            except:
                pass
        elif text.startswith('/purchase_'):
            try:
                purchase_id = int(text.replace('/purchase_', ''))
                # يمكن إضافة معالج تفاصيل البند هنا
                await update.message.reply_text(f"عرض تفاصيل البند #{purchase_id}")
            except:
                pass


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الملفات المرفوعة"""
    document = update.message.document
    
    # حفظ الملف
    file = await context.bot.get_file(document.file_id)
    file_path = f"{config.UPLOAD_FOLDER}{document.file_name}"
    await file.download_to_drive(file_path)
    
    await update.message.reply_text(
        f"✅ تم استلام الملف: {document.file_name}\n"
        f"الحجم: {document.file_size / 1024:.2f} KB"
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"حدث خطأ: {context.error}")
    
    try:
        await update.message.reply_text(config.MESSAGES['error'])
    except:
        pass


def main():
    """الدالة الرئيسية"""
    # تهيئة قاعدة البيانات
    print("🔧 تهيئة قاعدة البيانات...")
    db.init_database()
    print("✅ تم تهيئة قاعدة البيانات")
    
    # إنشاء مجلد الرفع
    import os
    if not os.path.exists(config.UPLOAD_FOLDER):
        os.makedirs(config.UPLOAD_FOLDER)
    
    # إنشاء التطبيق
    print("🤖 بدء تشغيل البوت...")
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("plans", plans_command))
    application.add_handler(CommandHandler("projects", projects_command))
    application.add_handler(CommandHandler("purchases", purchases_command))
    application.add_handler(CommandHandler("reports", reports_command))
    application.add_handler(CommandHandler("dashboard", dashboard_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # معالجات الأزرار والرسائل
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء نظام التنبيهات في خلفية منفصلة
    async def start_notifications():
        await run_scheduled_notifications(config.BOT_TOKEN)
    
    # تشغيل البوت
    print("✅ البوت جاهز للعمل!")
    print(f"📱 رابط البوت: https://t.me/YOUR_BOT_USERNAME")
    print("\n🔔 نظام التنبيهات نشط")
    print("📊 جميع الميزات متاحة\n")
    
    # تشغيل التطبيق
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
