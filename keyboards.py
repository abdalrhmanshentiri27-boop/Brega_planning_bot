# -*- coding: utf-8 -*-
"""
لوحات المفاتيح التفاعلية للبوت
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard(user_role):
    """القائمة الرئيسية حسب صلاحيات المستخدم"""
    keyboard = [
        [KeyboardButton("📋 الخطط"), KeyboardButton("🏗️ المشاريع")],
        [KeyboardButton("🛒 البنود الشرائية"), KeyboardButton("📊 التقارير")],
        [KeyboardButton("🔍 البحث"), KeyboardButton("📈 لوحة المؤشرات")],
    ]
    
    # إضافة خيارات الإدارة للمسؤولين
    if user_role in ["إدارة_عليا", "موظف_تخطيط"]:
        keyboard.append([KeyboardButton("👥 إدارة المستخدمين"), KeyboardButton("⚙️ الإعدادات")])
    
    keyboard.append([KeyboardButton("ℹ️ المساعدة"), KeyboardButton("👤 حسابي")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def plans_menu_keyboard(can_add=True):
    """قائمة إدارة الخطط"""
    keyboard = [
        [InlineKeyboardButton("📋 عرض جميع الخطط", callback_data="plans_list_all")],
        [InlineKeyboardButton("🔍 البحث حسب الإدارة", callback_data="plans_search_dept"),
         InlineKeyboardButton("🔍 البحث حسب السنة", callback_data="plans_search_year")],
        [InlineKeyboardButton("📑 البحث حسب النوع", callback_data="plans_search_type")],
    ]
    
    if can_add:
        keyboard.append([InlineKeyboardButton("➕ إضافة خطة جديدة", callback_data="plans_add")])
    
    keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def projects_menu_keyboard(can_add=True):
    """قائمة إدارة المشاريع"""
    keyboard = [
        [InlineKeyboardButton("🏗️ المشاريع النشطة", callback_data="projects_active")],
        [InlineKeyboardButton("✅ المشاريع المكتملة", callback_data="projects_completed"),
         InlineKeyboardButton("⏸️ المشاريع المعلقة", callback_data="projects_suspended")],
        [InlineKeyboardButton("📊 حسب الإدارة", callback_data="projects_by_dept"),
         InlineKeyboardButton("📈 حسب نسبة الإنجاز", callback_data="projects_by_progress")],
    ]
    
    if can_add:
        keyboard.append([InlineKeyboardButton("➕ مشروع جديد", callback_data="projects_add")])
    
    keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def project_details_keyboard(project_id, can_edit=False):
    """تفاصيل المشروع مع خيارات التحكم"""
    keyboard = [
        [InlineKeyboardButton("📊 عرض التحديثات", callback_data=f"project_updates_{project_id}")],
        [InlineKeyboardButton("📎 الخطط المرتبطة", callback_data=f"project_plans_{project_id}"),
         InlineKeyboardButton("🛒 البنود المرتبطة", callback_data=f"project_purchases_{project_id}")],
    ]
    
    if can_edit:
        keyboard.append([
            InlineKeyboardButton("✏️ تحديث التقدم", callback_data=f"project_update_{project_id}"),
            InlineKeyboardButton("🔗 ربط بخطة", callback_data=f"project_link_plan_{project_id}")
        ])
        keyboard.append([InlineKeyboardButton("⚙️ تعديل المشروع", callback_data=f"project_edit_{project_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="projects_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def purchases_menu_keyboard(can_add=True):
    """قائمة إدارة البنود الشرائية"""
    keyboard = [
        [InlineKeyboardButton("🛒 جميع البنود", callback_data="purchases_all")],
        [InlineKeyboardButton("📝 مسجل", callback_data="purchases_registered"),
         InlineKeyboardButton("📢 تم الطرح", callback_data="purchases_announced")],
        [InlineKeyboardButton("⚖️ قيد الإجراء", callback_data="purchases_procedure"),
         InlineKeyboardButton("✅ تم الترسية", callback_data="purchases_awarded")],
        [InlineKeyboardButton("🔍 البحث", callback_data="purchases_search")],
    ]
    
    if can_add:
        keyboard.append([InlineKeyboardButton("➕ بند جديد", callback_data="purchases_add")])
    
    keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def purchase_details_keyboard(purchase_id, can_edit=False):
    """تفاصيل البند الشرائي"""
    keyboard = [
        [InlineKeyboardButton("📋 تقارير اللجان", callback_data=f"purchase_reports_{purchase_id}")],
        [InlineKeyboardButton("🏗️ المشاريع المرتبطة", callback_data=f"purchase_projects_{purchase_id}")],
    ]
    
    if can_edit:
        keyboard.append([
            InlineKeyboardButton("📝 تحديث الحالة", callback_data=f"purchase_status_{purchase_id}"),
            InlineKeyboardButton("🔗 ربط بمشروع", callback_data=f"purchase_link_{purchase_id}")
        ])
        keyboard.append([
            InlineKeyboardButton("📄 إضافة تقرير لجنة", callback_data=f"purchase_report_add_{purchase_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="purchases_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def reports_menu_keyboard():
    """قائمة التقارير"""
    keyboard = [
        [InlineKeyboardButton("📊 تقرير الخطط", callback_data="report_plans"),
         InlineKeyboardButton("🏗️ تقرير المشاريع", callback_data="report_projects")],
        [InlineKeyboardButton("🛒 تقرير البنود", callback_data="report_purchases"),
         InlineKeyboardButton("📈 تقرير شامل", callback_data="report_comprehensive")],
        [InlineKeyboardButton("📅 تقرير شهري", callback_data="report_monthly"),
         InlineKeyboardButton("📆 تقرير ربع سنوي", callback_data="report_quarterly")],
        [InlineKeyboardButton("📄 تقرير سنوي", callback_data="report_annual")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def report_format_keyboard():
    """اختيار صيغة التقرير"""
    keyboard = [
        [InlineKeyboardButton("📕 PDF", callback_data="format_pdf"),
         InlineKeyboardButton("📗 Excel", callback_data="format_excel")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="reports_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def dashboard_keyboard():
    """لوحة المؤشرات"""
    keyboard = [
        [InlineKeyboardButton("🔄 تحديث البيانات", callback_data="dashboard_refresh")],
        [InlineKeyboardButton("📊 تفاصيل المشاريع", callback_data="dashboard_projects"),
         InlineKeyboardButton("📋 تفاصيل الخطط", callback_data="dashboard_plans")],
        [InlineKeyboardButton("🛒 تفاصيل البنود", callback_data="dashboard_purchases")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def users_management_keyboard():
    """إدارة المستخدمين"""
    keyboard = [
        [InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="users_list")],
        [InlineKeyboardButton("➕ إضافة مستخدم", callback_data="users_add"),
         InlineKeyboardButton("🔍 البحث", callback_data="users_search")],
        [InlineKeyboardButton("🔑 إدارة الصلاحيات", callback_data="users_permissions")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def user_details_keyboard(user_id):
    """تفاصيل المستخدم"""
    keyboard = [
        [InlineKeyboardButton("✏️ تعديل الصلاحيات", callback_data=f"user_edit_role_{user_id}")],
        [InlineKeyboardButton("🔒 تعطيل", callback_data=f"user_deactivate_{user_id}"),
         InlineKeyboardButton("🔓 تفعيل", callback_data=f"user_activate_{user_id}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="users_list")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def role_selection_keyboard():
    """اختيار الصلاحية"""
    keyboard = [
        [InlineKeyboardButton("👔 إدارة عليا", callback_data="role_admin")],
        [InlineKeyboardButton("📊 موظف تخطيط", callback_data="role_planning")],
        [InlineKeyboardButton("👨‍💼 موظف إدارة", callback_data="role_department")],
        [InlineKeyboardButton("🤝 عضو لجنة", callback_data="role_committee")],
        [InlineKeyboardButton("👁️ مشاهد", callback_data="role_viewer")],
        [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def plan_type_keyboard():
    """اختيار نوع الخطة"""
    keyboard = [
        [InlineKeyboardButton("⚙️ تشغيلية", callback_data="plantype_operational")],
        [InlineKeyboardButton("🎯 إستراتيجية", callback_data="plantype_strategic")],
        [InlineKeyboardButton("📅 سنوية", callback_data="plantype_annual")],
        [InlineKeyboardButton("📆 ربع سنوية", callback_data="plantype_quarterly")],
        [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def project_status_keyboard():
    """اختيار حالة المشروع"""
    keyboard = [
        [InlineKeyboardButton("💡 فكرة", callback_data="status_idea")],
        [InlineKeyboardButton("📝 تخطيط", callback_data="status_planning")],
        [InlineKeyboardButton("✅ معتمد", callback_data="status_approved")],
        [InlineKeyboardButton("🔄 قيد التنفيذ", callback_data="status_in_progress")],
        [InlineKeyboardButton("✔️ مكتمل", callback_data="status_completed")],
        [InlineKeyboardButton("⏸️ معلق", callback_data="status_suspended")],
        [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def purchase_status_keyboard():
    """اختيار حالة البند الشرائي"""
    keyboard = [
        [InlineKeyboardButton("📝 مسجل", callback_data="pstatus_registered")],
        [InlineKeyboardButton("📢 تم الطرح", callback_data="pstatus_announced")],
        [InlineKeyboardButton("⚖️ قيد الإجراء", callback_data="pstatus_in_procedure")],
        [InlineKeyboardButton("✅ تم الترسية", callback_data="pstatus_awarded")],
        [InlineKeyboardButton("📄 تم التعاقد", callback_data="pstatus_contracted")],
        [InlineKeyboardButton("❌ ملغي", callback_data="pstatus_cancelled")],
        [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def confirmation_keyboard(action_id):
    """لوحة التأكيد"""
    keyboard = [
        [InlineKeyboardButton("✅ تأكيد", callback_data=f"confirm_{action_id}"),
         InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard():
    """زر الإلغاء"""
    keyboard = [
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)
