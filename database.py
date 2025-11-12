# -*- coding: utf-8 -*-
"""
نموذج قاعدة البيانات لبوت إدارة التخطيط
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean, Date, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import config

Base = declarative_base()

# جدول ربط المشاريع بالخطط (علاقة many-to-many)
project_plan_association = Table('project_plan', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('plan_id', Integer, ForeignKey('plans.id'))
)

# جدول ربط البنود الشرائية بالمشاريع
purchase_project_association = Table('purchase_project', Base.metadata,
    Column('purchase_id', Integer, ForeignKey('purchases.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)


class User(Base):
    """جدول المستخدمين"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(200))
    department = Column(String(200))
    role = Column(String(50), default=config.UserRoles.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    
    # العلاقات
    created_plans = relationship('Plan', back_populates='creator')
    created_projects = relationship('Project', back_populates='creator')
    created_purchases = relationship('Purchase', back_populates='creator')
    updates = relationship('ProjectUpdate', back_populates='user')
    
    def __repr__(self):
        return f"<User {self.full_name} - {self.role}>"


class Plan(Base):
    """جدول الخطط التشغيلية والإستراتيجية"""
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    plan_type = Column(String(50), nullable=False)  # تشغيلية، إستراتيجية، سنوية
    department = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)  # ربع سنوي (1-4)
    description = Column(Text)
    objectives = Column(Text)  # الأهداف
    file_path = Column(String(500))  # مسار ملف الخطة
    status = Column(String(50), default='نشط')
    completion_percentage = Column(Float, default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)
    next_update_date = Column(Date)  # موعد التحديث القادم
    creator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # العلاقات
    creator = relationship('User', back_populates='created_plans')
    projects = relationship('Project', secondary=project_plan_association, back_populates='plans')
    updates = relationship('PlanUpdate', back_populates='plan')
    
    def __repr__(self):
        return f"<Plan {self.title} - {self.year}>"


class PlanUpdate(Base):
    """جدول تحديثات الخطط"""
    __tablename__ = 'plan_updates'
    
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans.id'))
    update_text = Column(Text, nullable=False)
    completion_percentage = Column(Float)
    update_date = Column(DateTime, default=datetime.now)
    
    plan = relationship('Plan', back_populates='updates')


class Project(Base):
    """جدول المشاريع"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    project_code = Column(String(50), unique=True)
    title = Column(String(300), nullable=False)
    purpose = Column(Text)  # الغرض
    goal = Column(Text)  # الغاية
    objectives = Column(Text)  # الأهداف
    description = Column(Text)
    department = Column(String(200), nullable=False)  # الجهة المعنية (المالك)
    status = Column(String(50), default=config.ProjectStatus.IDEA)
    current_phase = Column(String(200))  # المرحلة الحالية
    completion_percentage = Column(Float, default=0.0)
    budget = Column(Float)  # الميزانية
    start_date = Column(Date)
    expected_end_date = Column(Date)
    actual_end_date = Column(Date)
    creator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # العلاقات
    creator = relationship('User', back_populates='created_projects')
    plans = relationship('Plan', secondary=project_plan_association, back_populates='projects')
    purchases = relationship('Purchase', secondary=purchase_project_association, back_populates='projects')
    updates = relationship('ProjectUpdate', back_populates='project')
    
    def __repr__(self):
        return f"<Project {self.project_code} - {self.title}>"


class ProjectUpdate(Base):
    """جدول التحديثات والتقارير المرحلية للمشاريع"""
    __tablename__ = 'project_updates'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    update_text = Column(Text, nullable=False)
    completion_percentage = Column(Float)
    phase = Column(String(200))  # المرحلة
    file_path = Column(String(500))  # تقرير مرفق
    update_date = Column(DateTime, default=datetime.now)
    
    project = relationship('Project', back_populates='updates')
    user = relationship('User', back_populates='updates')


class Purchase(Base):
    """جدول البنود الشرائية"""
    __tablename__ = 'purchases'
    
    id = Column(Integer, primary_key=True)
    purchase_code = Column(String(50), unique=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    department = Column(String(200), nullable=False)
    status = Column(String(50), default=config.PurchaseStatus.REGISTERED)
    budget = Column(Float)
    approved_budget = Column(Float)
    committee = Column(String(200))  # اللجنة المعنية
    announcement_date = Column(Date)  # تاريخ الطرح
    award_date = Column(Date)  # تاريخ الترسية
    contractor = Column(String(300))  # المقاول المرسى عليه
    file_path = Column(String(500))
    creator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # العلاقات
    creator = relationship('User', back_populates='created_purchases')
    projects = relationship('Project', secondary=purchase_project_association, back_populates='purchases')
    reports = relationship('CommitteeReport', back_populates='purchase')
    
    def __repr__(self):
        return f"<Purchase {self.purchase_code} - {self.title}>"


class CommitteeReport(Base):
    """جدول تقارير اللجان"""
    __tablename__ = 'committee_reports'
    
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'))
    committee_name = Column(String(200), nullable=False)
    report_type = Column(String(100))  # نوع التقرير
    report_text = Column(Text)
    decision = Column(Text)  # القرار
    file_path = Column(String(500))
    report_date = Column(DateTime, default=datetime.now)
    
    purchase = relationship('Purchase', back_populates='reports')


class Notification(Base):
    """جدول التنبيهات"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(300))
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))  # خطة، مشروع، بند_شرائي
    related_id = Column(Integer)  # معرف الكيان المرتبط
    is_read = Column(Boolean, default=False)
    scheduled_date = Column(DateTime)  # موعد الإرسال
    sent_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


class SystemLog(Base):
    """جدول سجلات النظام"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(200), nullable=False)
    entity_type = Column(String(50))  # خطة، مشروع، بند
    entity_id = Column(Integer)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)


# إنشاء قاعدة البيانات
def init_database():
    """تهيئة قاعدة البيانات"""
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """الحصول على جلسة قاعدة البيانات"""
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    init_database()
    print("✅ تم إنشاء قاعدة البيانات بنجاح")
