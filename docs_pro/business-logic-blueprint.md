# Business Logic Blueprint

## Prehľad
Tento blueprint definuje business logiku pre API Centrum Backend systém vrátane billingu, notifikácií, audit logov a iných podnikových procesov.

## Ciele
- Implementovať komplexný billing systém
- Vytvoriť notifikačný systém
- Nastaviť audit logovanie
- Implementovať business rules a validácie
- Vytvoriť reporting a analytics

## 1. Billing System

### 1.1 Billing models
```python
# app/billing/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from enum import Enum as PyEnum
from decimal import Decimal
from app.db import Base

class BillingPeriod(PyEnum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class PaymentStatus(PyEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class InvoiceStatus(PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class SubscriptionStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class PlanType(PyEnum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(500))
    plan_type = Column(Enum(PlanType), default=PlanType.FREE)
    price = Column(Float, default=0.0)
    billing_period = Column(Enum(BillingPeriod), default=BillingPeriod.MONTHLY)
    
    # Limits
    max_domains = Column(Integer, default=5)
    max_ssl_certificates = Column(Integer, default=5)
    max_users = Column(Integer, default=1)
    max_api_calls = Column(Integer, default=1000)
    
    # Features
    has_priority_support = Column(Boolean, default=False)
    has_custom_domains = Column(Boolean, default=False)
    has_advanced_analytics = Column(Boolean, default=False)
    has_sso = Column(Boolean, default=False)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    billing_period = Column(Enum(BillingPeriod))
    
    # Billing info
    next_billing_date = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String(50))  # stripe, paypal, bank_transfer
    
    # Usage tracking
    current_period_start = Column(DateTime, default=datetime.utcnow)
    current_period_end = Column(DateTime)
    domains_used = Column(Integer, default=0)
    ssl_certificates_used = Column(Integer, default=0)
    api_calls_used = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan")
    invoices = relationship("Invoice", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    
    invoice_number = Column(String(50), unique=True)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    total_amount = Column(Float)
    currency = Column(String(3), default="EUR")
    
    # Dates
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    paid_date = Column(DateTime, nullable=True)
    
    # Line items
    description = Column(String(200))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)
    
    # Metadata
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    
    amount = Column(Float)
    currency = Column(String(3), default="EUR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment details
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    payment_reference = Column(String(100))
    
    # Metadata
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    
    # Usage metrics
    domains_count = Column(Integer, default=0)
    ssl_certificates_count = Column(Integer, default=0)
    api_calls_count = Column(Integer, default=0)
    storage_used = Column(Float, default=0.0)  # in MB
    
    # Time period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    subscription = relationship("Subscription")
```

### 1.2 Billing service
```python
# app/billing/services.py
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.billing.models import (
    Plan, Subscription, Invoice, Payment, UsageRecord,
    SubscriptionStatus, InvoiceStatus, PaymentStatus, BillingPeriod
)
from app.models import User
from app.crud import CRUDUser
from app.core.config import settings

class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_user = CRUDUser()
    
    def get_plan_by_type(self, plan_type: str) -> Optional[Plan]:
        """Get plan by type"""
        return self.db.query(Plan).filter(
            Plan.plan_type == plan_type,
            Plan.is_active == True
        ).first()
    
    def get_all_plans(self) -> List[Plan]:
        """Get all active plans"""
        return self.db.query(Plan).filter(Plan.is_active == True).all()
    
    def create_subscription(self, user_id: int, plan_type: str, 
                          billing_period: str = "monthly",
                          auto_renew: bool = True) -> Subscription:
        """Create new subscription"""
        plan = self.get_plan_by_type(plan_type)
        if not plan:
            raise ValueError(f"Plan {plan_type} not found")
        
        # Calculate end date based on billing period
        start_date = datetime.utcnow()
        if billing_period == "monthly":
            end_date = start_date + timedelta(days=30)
        elif billing_period == "quarterly":
            end_date = start_date + timedelta(days=90)
        elif billing_period == "yearly":
            end_date = start_date + timedelta(days=365)
        else:
            raise ValueError("Invalid billing period")
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            billing_period=billing_period,
            next_billing_date=end_date,
            auto_renew=auto_renew,
            current_period_start=start_date,
            current_period_end=end_date
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        # Create initial invoice
        self.create_invoice(subscription)
        
        return subscription
    
    def update_subscription(self, subscription_id: int, plan_type: str = None,
                          auto_renew: bool = None) -> Subscription:
        """Update subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        if plan_type:
            plan = self.get_plan_by_type(plan_type)
            if not plan:
                raise ValueError(f"Plan {plan_type} not found")
            subscription.plan_id = plan.id
        
        if auto_renew is not None:
            subscription.auto_renew = auto_renew
        
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def cancel_subscription(self, subscription_id: int, immediate: bool = False) -> bool:
        """Cancel subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        if immediate:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.end_date = datetime.utcnow()
        else:
            subscription.status = SubscriptionStatus.CANCELLED
            # Keep until end of current period
        
        self.db.commit()
        return True
    
    def create_invoice(self, subscription: Subscription) -> Invoice:
        """Create invoice for subscription"""
        plan = subscription.plan
        amount = plan.price
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{subscription.id}"
        
        # Calculate due date (7 days from issue)
        due_date = datetime.utcnow() + timedelta(days=7)
        
        invoice = Invoice(
            subscription_id=subscription.id,
            invoice_number=invoice_number,
            status=InvoiceStatus.SENT,
            total_amount=amount,
            currency="EUR",
            due_date=due_date,
            description=f"Subscription for {plan.name} plan",
            quantity=1,
            unit_price=amount
        )
        
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def process_payment(self, invoice_id: int, payment_method: str,
                       transaction_id: str) -> Payment:
        """Process payment for invoice"""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        
        if invoice.status != InvoiceStatus.SENT:
            raise ValueError("Invoice is not in sent status")
        
        # Create payment record
        payment = Payment(
            invoice_id=invoice.id,
            subscription_id=invoice.subscription_id,
            amount=invoice.total_amount,
            currency=invoice.currency,
            status=PaymentStatus.PAID,
            payment_method=payment_method,
            transaction_id=transaction_id,
            payment_reference=f"REF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            processed_at=datetime.utcnow()
        )
        
        # Update invoice status
        invoice.status = InvoiceStatus.PAID
        invoice.paid_date = datetime.utcnow()
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        # Extend subscription
        self.extend_subscription(invoice.subscription)
        
        return payment
    
    def extend_subscription(self, subscription: Subscription):
        """Extend subscription period"""
        plan = subscription.plan
        
        # Calculate new end date
        if subscription.billing_period == BillingPeriod.MONTHLY:
            extension = timedelta(days=30)
        elif subscription.billing_period == BillingPeriod.QUARTERLY:
            extension = timedelta(days=90)
        elif subscription.billing_period == BillingPeriod.YEARLY:
            extension = timedelta(days=365)
        else:
            extension = timedelta(days=30)
        
        subscription.end_date = subscription.end_date + extension
        subscription.next_billing_date = subscription.end_date
        subscription.current_period_start = subscription.current_period_end
        subscription.current_period_end = subscription.end_date
        
        self.db.commit()
    
    def check_usage_limits(self, user_id: int) -> Dict[str, Any]:
        """Check current usage against limits"""
        user = self.crud_user.get(self.db, user_id)
        if not user.subscription:
            return {"allowed": False, "reason": "No active subscription"}
        
        plan = user.subscription.plan
        subscription = user.subscription
        
        # Get current usage
        usage = {
            "domains_used": subscription.domains_used,
            "ssl_certificates_used": subscription.ssl_certificates_used,
            "api_calls_used": subscription.api_calls_used,
            "limits": {
                "max_domains": plan.max_domains,
                "max_ssl_certificates": plan.max_ssl_certificates,
                "max_api_calls": plan.max_api_calls
            }
        }
        
        # Check limits
        limits_exceeded = []
        
        if usage["domains_used"] >= plan.max_domains:
            limits_exceeded.append("domains")
        
        if usage["ssl_certificates_used"] >= plan.max_ssl_certificates:
            limits_exceeded.append("ssl_certificates")
        
        if usage["api_calls_used"] >= plan.max_api_calls:
            limits_exceeded.append("api_calls")
        
        usage["limits_exceeded"] = limits_exceeded
        usage["allowed"] = len(limits_exceeded) == 0
        
        return usage
    
    def record_usage(self, user_id: int, usage_type: str, amount: int = 1):
        """Record usage for a user"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        if not subscription:
            return
        
        # Update subscription usage
        if usage_type == "domain":
            subscription.domains_used += amount
        elif usage_type == "ssl":
            subscription.ssl_certificates_used += amount
        elif usage_type == "api_call":
            subscription.api_calls_used += amount
        
        # Create usage record
        usage_record = UsageRecord(
            user_id=user_id,
            subscription_id=subscription.id,
            domains_count=subscription.domains_used,
            ssl_certificates_count=subscription.ssl_certificates_used,
            api_calls_count=subscription.api_calls_used,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end
        )
        
        self.db.add(usage_record)
        self.db.commit()
    
    def get_billing_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get billing history for user"""
        invoices = self.db.query(Invoice).join(Subscription).filter(
            Subscription.user_id == user_id
        ).order_by(Invoice.created_at.desc()).limit(limit).all()
        
        history = []
        for invoice in invoices:
            history.append({
                "invoice_number": invoice.invoice_number,
                "amount": invoice.total_amount,
                "currency": invoice.currency,
                "status": invoice.status.value,
                "issue_date": invoice.issue_date,
                "due_date": invoice.due_date,
                "paid_date": invoice.paid_date,
                "plan_name": invoice.subscription.plan.name
            })
        
        return history
    
    def get_overdue_invoices(self) -> List[Invoice]:
        """Get all overdue invoices"""
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        return self.db.query(Invoice).filter(
            and_(
                Invoice.status == InvoiceStatus.SENT,
                Invoice.due_date < cutoff_date
            )
        ).all()
    
    def send_payment_reminders(self):
        """Send payment reminders for overdue invoices"""
        overdue_invoices = self.get_overdue_invoices()
        
        for invoice in overdue_invoices:
            # Send notification (implement based on notification system)
            print(f"Sending reminder for invoice {invoice.invoice_number}")
```

## 2. Notification System

### 2.1 Notification models
```python
# app/notifications/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.db import Base

class NotificationType(PyEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class NotificationStatus(PyEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    type = Column(Enum(NotificationType))
    subject = Column(String(200))
    body = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    
    type = Column(Enum(NotificationType))
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Content
    subject = Column(String(200))
    body = Column(Text)
    data = Column(Text)  # JSON data for template variables
    
    # Delivery info
    recipient = Column(String(200))  # email, phone, etc.
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Metadata
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    retry_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    template = relationship("NotificationTemplate")

class UserNotificationSettings(Base):
    __tablename__ = "user_notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Email settings
    email_enabled = Column(Boolean, default=True)
    email_frequency = Column(String(20), default="immediate")  # immediate, daily, weekly
    
    # SMS settings
    sms_enabled = Column(Boolean, default=False)
    sms_phone = Column(String(20), nullable=True)
    
    # Push settings
    push_enabled = Column(Boolean, default=True)
    push_token = Column(String(500), nullable=True)
    
    # Notification preferences
    domain_notifications = Column(Boolean, default=True)
    ssl_notifications = Column(Boolean, default=True)
    billing_notifications = Column(Boolean, default=True)
    security_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="notification_settings")
```

### 2.2 Notification service
```python
# app/notifications/services.py
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.notifications.models import (
    Notification, NotificationTemplate, UserNotificationSettings,
    NotificationType, NotificationStatus
)
from app.models import User
from app.core.config import settings

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def send_notification(self, user_id: int, template_name: str, 
                         data: Dict[str, Any] = None, 
                         override_type: str = None) -> bool:
        """Send notification using template"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Get user settings
        settings = self.db.query(UserNotificationSettings).filter(
            UserNotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            settings = self.create_default_settings(user_id)
        
        # Get template
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.name == template_name,
            NotificationTemplate.is_active == True
        ).first()
        
        if not template:
            return False
        
        # Determine notification type
        notification_type = override_type or template.type.value
        
        # Check if user wants this type of notification
        if not self._should_send_notification(settings, notification_type, template_name):
            return False
        
        # Render template
        rendered_subject, rendered_body = self._render_template(template, data or {})
        
        # Create notification record
        notification = Notification(
            user_id=user_id,
            template_id=template.id,
            type=notification_type,
            subject=rendered_subject,
            body=rendered_body,
            data=str(data) if data else None,
            recipient=self._get_recipient(user, notification_type),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        self.db.add(notification)
        self.db.commit()
        
        # Send notification
        success = self._send_by_type(notification, user, settings)
        
        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
        else:
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
        
        self.db.commit()
        return success
    
    def send_domain_notification(self, user_id: int, domain_name: str, 
                               action: str, details: Dict = None):
        """Send domain-related notification"""
        template_map = {
            "created": "domain_created",
            "updated": "domain_updated", 
            "deleted": "domain_deleted",
            "expired": "domain_expired",
            "renewed": "domain_renewed"
        }
        
        template_name = template_map.get(action, "domain_notification")
        
        data = {
            "domain_name": domain_name,
            "action": action,
            "user_name": self.db.query(User).filter(User.id == user_id).first().name,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {})
        }
        
        return self.send_notification(user_id, template_name, data)
    
    def send_ssl_notification(self, user_id: int, domain_name: str,
                            action: str, details: Dict = None):
        """Send SSL-related notification"""
        template_map = {
            "generated": "ssl_generated",
            "renewed": "ssl_renewed",
            "expired": "ssl_expired",
            "revoked": "ssl_revoked"
        }
        
        template_name = template_map.get(action, "ssl_notification")
        
        data = {
            "domain_name": domain_name,
            "action": action,
            "user_name": self.db.query(User).filter(User.id == user_id).first().name,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {})
        }
        
        return self.send_notification(user_id, template_name, data)
    
    def send_billing_notification(self, user_id: int, invoice_id: int,
                                action: str, details: Dict = None):
        """Send billing-related notification"""
        template_map = {
            "invoice_created": "invoice_created",
            "payment_received": "payment_received",
            "payment_failed": "payment_failed",
            "subscription_expired": "subscription_expired",
            "subscription_renewed": "subscription_renewed"
        }
        
        template_name = template_map.get(action, "billing_notification")
        
        data = {
            "invoice_id": invoice_id,
            "action": action,
            "user_name": self.db.query(User).filter(User.id == user_id).first().name,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {})
        }
        
        return self.send_notification(user_id, template_name, data)
    
    def send_security_notification(self, user_id: int, event_type: str,
                                 details: Dict = None):
        """Send security-related notification"""
        template_map = {
            "login_failed": "security_login_failed",
            "password_changed": "security_password_changed",
            "two_factor_enabled": "security_2fa_enabled",
            "two_factor_disabled": "security_2fa_disabled",
            "suspicious_activity": "security_suspicious_activity"
        }
        
        template_name = template_map.get(event_type, "security_notification")
        
        data = {
            "event_type": event_type,
            "user_name": self.db.query(User).filter(User.id == user_id).first().name,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": details.get("ip_address", "unknown"),
            **(details or {})
        }
        
        return self.send_notification(user_id, template_name, data)
    
    def _should_send_notification(self, settings: UserNotificationSettings,
                                notification_type: str, template_name: str) -> bool:
        """Check if notification should be sent based on user settings"""
        if notification_type == "email" and not settings.email_enabled:
            return False
        
        if notification_type == "sms" and not settings.sms_enabled:
            return False
        
        if notification_type == "push" and not settings.push_enabled:
            return False
        
        # Check specific notification preferences
        if "domain" in template_name and not settings.domain_notifications:
            return False
        
        if "ssl" in template_name and not settings.ssl_notifications:
            return False
        
        if "billing" in template_name and not settings.billing_notifications:
            return False
        
        if "security" in template_name and not settings.security_notifications:
            return False
        
        return True
    
    def _render_template(self, template: NotificationTemplate, 
                        data: Dict[str, Any]) -> tuple:
        """Render template with data"""
        subject_template = Template(template.subject)
        body_template = Template(template.body)
        
        rendered_subject = subject_template.render(**data)
        rendered_body = body_template.render(**data)
        
        return rendered_subject, rendered_body
    
    def _get_recipient(self, user: User, notification_type: str) -> str:
        """Get recipient address based on notification type"""
        if notification_type == "email":
            return user.email
        
        if notification_type == "sms":
            settings = self.db.query(UserNotificationSettings).filter(
                UserNotificationSettings.user_id == user.id
            ).first()
            return settings.sms_phone if settings else None
        
        if notification_type == "push":
            settings = self.db.query(UserNotificationSettings).filter(
                UserNotificationSettings.user_id == user.id
            ).first()
            return settings.push_token if settings else None
        
        return None
    
    def _send_by_type(self, notification: Notification, user: User,
                     settings: UserNotificationSettings) -> bool:
        """Send notification based on type"""
        if notification.type == "email":
            return self._send_email(notification, user)
        
        elif notification.type == "sms":
            return self._send_sms(notification, settings)
        
        elif notification.type == "push":
            return self._send_push(notification, settings)
        
        return False
    
    def _send_email(self, notification: Notification, user: User) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_SENDER
            msg['To'] = user.email
            msg['Subject'] = notification.subject
            
            msg.attach(MIMEText(notification.body, 'html'))
            
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def _send_sms(self, notification: Notification, 
                 settings: UserNotificationSettings) -> bool:
        """Send SMS notification"""
        try:
            # Example using Twilio or similar service
            response = requests.post(
                settings.SMS_API_URL,
                auth=(settings.SMS_API_KEY, settings.SMS_API_SECRET),
                data={
                    'to': settings.sms_phone,
                    'from': settings.SMS_SENDER,
                    'body': notification.subject
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False
    
    def _send_push(self, notification: Notification,
                  settings: UserNotificationSettings) -> bool:
        """Send push notification"""
        try:
            # Example using Firebase Cloud Messaging
            payload = {
                'to': settings.push_token,
                'notification': {
                    'title': notification.subject,
                    'body': notification.body
                }
            }
            
            response = requests.post(
                settings.PUSH_API_URL,
                headers={'Authorization': f'key={settings.PUSH_API_KEY}'},
                json=payload
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Push notification failed: {e}")
            return False
    
    def create_default_settings(self, user_id: int) -> UserNotificationSettings:
        """Create default notification settings for user"""
        settings = UserNotificationSettings(
            user_id=user_id,
            email_enabled=True,
            email_frequency="immediate",
            sms_enabled=False,
            push_enabled=True
        )
        
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
    
    def get_user_notifications(self, user_id: int, limit: int = 50) -> List[Notification]:
        """Get user notifications"""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def cleanup_old_notifications(self, days: int = 30):
        """Clean up old notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_notifications = self.db.query(Notification).filter(
            Notification.created_at < cutoff_date
        ).all()
        
        for notification in old_notifications:
            self.db.delete(notification)
        
        self.db.commit()
```

## 3. Audit Logging

### 3.1 Audit models
```python
# app/audit/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), index=True)
    resource_type = Column(String(50), index=True)
    resource_id = Column(String(100), nullable=True)
    
    # Changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True)
    
    # Metadata
    severity = Column(String(20), default="info")  # info, warning, error, critical
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    event_type = Column(String(100), index=True)  # login_failed, password_changed, etc.
    severity = Column(String(20), default="info")
    
    # Event details
    details = Column(JSON)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Risk assessment
    risk_score = Column(Integer, default=0)  # 0-100
    is_suspicious = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="security_events")

class DataChangeLog(Base):
    __tablename__ = "data_change_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), index=True)
    record_id = Column(String(100), index=True)
    
    operation = Column(String(20))  # INSERT, UPDATE, DELETE
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
```

### 3.2 Audit service
```python
# app/audit/services.py
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.audit.models import AuditLog, SecurityEvent, DataChangeLog
from app.models import User

class AuditService:
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(self, user_id: Optional[int], action: str, 
                  resource_type: str, resource_id: Optional[str] = None,
                  old_values: Dict = None, new_values: Dict = None,
                  ip_address: str = None, user_agent: str = None,
                  severity: str = "info", description: str = None):
        """Log an audit action"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            description=description
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    def log_security_event(self, user_id: Optional[int], event_type: str,
                          details: Dict = None, ip_address: str = None,
                          user_agent: str = None, risk_score: int = 0):
        """Log a security event"""
        is_suspicious = risk_score > 50
        
        security_event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity="critical" if risk_score > 80 else "warning" if risk_score > 50 else "info",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            risk_score=risk_score,
            is_suspicious=is_suspicious
        )
        
        self.db.add(security_event)
        self.db.commit()
        
        # Log to audit trail
        self.log_action(
            user_id=user_id,
            action="security_event",
            resource_type="security",
            resource_id=str(security_event.id),
            new_values={"event_type": event_type, "risk_score": risk_score},
            ip_address=ip_address,
            severity="critical" if is_suspicious else "warning"
        )
    
    def log_data_change(self, table_name: str, record_id: str,
                       operation: str, old_data: Dict = None, 
                       new_data: Dict = None, changed_by: int = None):
        """Log data changes"""
        data_change = DataChangeLog(
            table_name=table_name,
            record_id=record_id,
            operation=operation,
            old_data=old_data,
            new_data=new_data,
            changed_by=changed_by
        )
        
        self.db.add(data_change)
        self.db.commit()
    
    def log_user_login(self, user: User, success: bool, 
                      ip_address: str = None, user_agent: str = None):
        """Log user login attempt"""
        if success:
            self.log_action(
                user_id=user.id,
                action="login_success",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                severity="info"
            )
        else:
            self.log_security_event(
                user_id=user.id if user else None,
                event_type="login_failed",
                details={"email": getattr(user, 'email', 'unknown')},
                ip_address=ip_address,
                user_agent=user_agent,
                risk_score=30
            )
    
    def log_domain_operation(self, user_id: int, action: str, domain_name: str,
                           old_data: Dict = None, new_data: Dict = None,
                           ip_address: str = None):
        """Log domain operation"""
        self.log_action(
            user_id=user_id,
            action=action,
            resource_type="domain",
            resource_id=domain_name,
            old_values=old_data,
            new_values=new_data,
            ip_address=ip_address,
            severity="info"
        )
    
    def log_ssl_operation(self, user_id: int, action: str, domain_name: str,
                         old_data: Dict = None, new_data: Dict = None,
                         ip_address: str = None):
        """Log SSL operation"""
        self.log_action(
            user_id=user_id,
            action=action,
            resource_type="ssl",
            resource_id=domain_name,
            old_values=old_data,
            new_values=new_data,
            ip_address=ip_address,
            severity="info"
        )
    
    def log_billing_operation(self, user_id: int, action: str, invoice_id: str,
                            details: Dict = None, ip_address: str = None):
        """Log billing operation"""
        self.log_action(
            user_id=user_id,
            action=action,
            resource_type="billing",
            resource_id=invoice_id,
            new_values=details,
            ip_address=ip_address,
            severity="warning" if "failed" in action else "info"
        )
    
    def get_audit_logs(self, user_id: Optional[int] = None, 
                      action: Optional[str] = None,
                      resource_type: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      limit: int = 100) -> list:
        """Get audit logs with filters"""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    def get_security_events(self, user_id: Optional[int] = None,
                           event_type: Optional[str] = None,
                           suspicious_only: bool = False,
                           limit: int = 100) -> list:
        """Get security events with filters"""
        query = self.db.query(SecurityEvent)
        
        if user_id:
            query = query.filter(SecurityEvent.user_id == user_id)
        
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        
        if suspicious_only:
            query = query.filter(SecurityEvent.is_suspicious == True)
        
        return query.order_by(SecurityEvent.created_at.desc()).limit(limit).all()
    
    def get_data_changes(self, table_name: Optional[str] = None,
                        record_id: Optional[str] = None,
                        operation: Optional[str] = None,
                        limit: int = 100) -> list:
        """Get data change logs with filters"""
        query = self.db.query(DataChangeLog)
        
        if table_name:
            query = query.filter(DataChangeLog.table_name == table_name)
        
        if record_id:
            query = query.filter(DataChangeLog.record_id == record_id)
        
        if operation:
            query = query.filter(DataChangeLog.operation == operation)
        
        return query.order_by(DataChangeLog.changed_at.desc()).limit(limit).all()
    
    def cleanup_audit_logs(self, days: int = 90):
        """Clean up old audit logs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old audit logs
        old_logs = self.db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).all()
        
        for log in old_logs:
            self.db.delete(log)
        
        # Delete old security events
        old_security_events = self.db.query(SecurityEvent).filter(
            SecurityEvent.created_at < cutoff_date
        ).all()
        
        for event in old_security_events:
            self.db.delete(event)
        
        # Delete old data change logs
        old_data_changes = self.db.query(DataChangeLog).filter(
            DataChangeLog.changed_at < cutoff_date
        ).all()
        
        for change in old_data_changes:
            self.db.delete(change)
        
        self.db.commit()
```

## 4. Business Rules & Validation

### 4.1 Business rules service
```python
# app/business_rules/services.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.models import User, Domain, SSLCertificate
from app.billing.services import BillingService
from app.notifications.services import NotificationService
from app.audit.services import AuditService
from sqlalchemy.orm import Session

class BusinessRulesService:
    def __init__(self, db: Session):
        self.db = db
        self.billing_service = BillingService(db)
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)
    
    def validate_domain_creation(self, user_id: int, domain_name: str) -> Dict[str, Any]:
        """Validate domain creation based on business rules"""
        result = {
            "allowed": False,
            "reasons": [],
            "warnings": []
        }
        
        # Check user subscription
        usage_check = self.billing_service.check_usage_limits(user_id)
        if not usage_check["allowed"]:
            result["reasons"].append("Subscription limit exceeded")
            return result
        
        # Check domain format
        if not self._is_valid_domain_format(domain_name):
            result["reasons"].append("Invalid domain format")
            return result
        
        # Check if domain already exists for user
        existing_domain = self.db.query(Domain).filter(
            Domain.name == domain_name,
            Domain.user_id == user_id
        ).first()
        
        if existing_domain:
            result["reasons"].append("Domain already exists")
            return result
        
        # Check domain availability (external API)
        try:
            # This would call the Websupport API or similar
            is_available = self._check_domain_availability(domain_name)
            if not is_available:
                result["warnings"].append("Domain may not be available")
        except Exception as e:
            result["warnings"].append(f"Could not verify domain availability: {str(e)}")
        
        result["allowed"] = len(result["reasons"]) == 0
        return result
    
    def validate_ssl_generation(self, user_id: int, domain_name: str) -> Dict[str, Any]:
        """Validate SSL certificate generation"""
        result = {
            "allowed": False,
            "reasons": [],
            "warnings": []
        }
        
        # Check if domain exists and belongs to user
        domain = self.db.query(Domain).filter(
            Domain.name == domain_name,
            Domain.user_id == user_id
        ).first()
        
        if not domain:
            result["reasons"].append("Domain not found or access denied")
            return result
        
        # Check if SSL already exists for domain
        existing_ssl = self.db.query(SSLCertificate).filter(
            SSLCertificate.domain_name == domain_name
        ).first()
        
        if existing_ssl:
            result["reasons"].append("SSL certificate already exists for this domain")
            return result
        
        # Check subscription limits
        usage_check = self.billing_service.check_usage_limits(user_id)
        if "ssl_certificates" in usage_check.get("limits_exceeded", []):
            result["reasons"].append("SSL certificate limit exceeded")
            return result
        
        result["allowed"] = len(result["reasons"]) == 0
        return result
    
    def validate_user_registration(self, email: str, password: str) -> Dict[str, Any]:
        """Validate user registration"""
        result = {
            "allowed": False,
            "reasons": [],
            "warnings": []
        }
        
        # Check email format
        if not self._is_valid_email(email):
            result["reasons"].append("Invalid email format")
            return result
        
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            result["reasons"].append("Email already registered")
            return result
        
        # Check password strength
        password_check = self._validate_password_strength(password)
        if not password_check["valid"]:
            result["reasons"].extend(password_check["reasons"])
            return result
        
        result["allowed"] = len(result["reasons"]) == 0
        return result
    
    def validate_subscription_upgrade(self, user_id: int, new_plan_type: str) -> Dict[str, Any]:
        """Validate subscription upgrade"""
        result = {
            "allowed": False,
            "reasons": [],
            "warnings": []
        }
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            result["reasons"].append("User not found")
            return result
        
        current_subscription = user.subscription
        if not current_subscription:
            result["reasons"].append("No active subscription")
            return result
        
        # Check if already on this plan
        if current_subscription.plan.plan_type == new_plan_type:
            result["reasons"].append("Already on this plan")
            return result
        
        # Check if plan exists
        new_plan = self.billing_service.get_plan_by_type(new_plan_type)
        if not new_plan:
            result["reasons"].append("Plan not found")
            return result
        
        # Check if downgrade is allowed (business rule)
        if self._is_downgrade(current_subscription.plan.plan_type, new_plan_type):
            # Add warning for downgrade
            result["warnings"].append("Downgrading may result in loss of features")
        
        result["allowed"] = len(result["reasons"]) == 0
        return result
    
    def apply_business_rules(self, action: str, user_id: int, 
                           data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules for specific actions"""
        if action == "create_domain":
            return self.validate_domain_creation(user_id, data.get("domain_name", ""))
        
        elif action == "generate_ssl":
            return self.validate_ssl_generation(user_id, data.get("domain_name", ""))
        
        elif action == "register_user":
            return self.validate_user_registration(
                data.get("email", ""), 
                data.get("password", "")
            )
        
        elif action == "upgrade_subscription":
            return self.validate_subscription_upgrade(
                user_id, 
                data.get("plan_type", "")
            )
        
        return {"allowed": True, "reasons": [], "warnings": []}
    
    def _is_valid_domain_format(self, domain_name: str) -> bool:
        """Validate domain format"""
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain_name)) and len(domain_name) <= 253
    
    def _check_domain_availability(self, domain_name: str) -> bool:
        """Check domain availability via external API"""
        # This would integrate with Websupport API or similar
        # For now, return True as placeholder
        return True
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {"valid": True, "reasons": []}
        
        if len(password) < 8:
            result["valid"] = False
            result["reasons"].append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            result["valid"] = False
            result["reasons"].append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            result["valid"] = False
            result["reasons"].append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            result["valid"] = False
            result["reasons"].append("Password must contain at least one number")
        
        return result
    
    def _is_downgrade(self, current_plan: str, new_plan: str) -> bool:
        """Check if this is a plan downgrade"""
        plan_order = ["free", "basic", "premium", "enterprise"]
        
        try:
            current_index = plan_order.index(current_plan)
            new_index = plan_order.index(new_plan)
            return new_index < current_index
        except ValueError:
            return False
    
    def enforce_rate_limits(self, user_id: int, action: str, 
                          window_minutes: int = 60, max_attempts: int = 10) -> bool:
        """Enforce rate limiting for actions"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        # Count recent actions by user
        recent_actions = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == action,
            AuditLog.created_at >= cutoff_time
        ).count()
        
        return recent_actions < max_attempts
    
    def check_suspicious_activity(self, user_id: int, ip_address: str) -> Dict[str, Any]:
        """Check for suspicious activity patterns"""
        result = {
            "is_suspicious": False,
            "risk_score": 0,
            "events": []
        }
        
        # Check for multiple failed login attempts
        recent_failures = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "login_failed",
            AuditLog.created_at >= datetime.utcnow() - timedelta(minutes=30)
        ).count()
        
        if recent_failures > 5:
            result["is_suspicious"] = True
            result["risk_score"] += 40
            result["events"].append("Multiple failed login attempts")
        
        # Check for unusual IP addresses
        # This would require storing and analyzing IP patterns
        
        # Check for rapid domain creation
        recent_domains = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "create_domain",
            AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        if recent_domains > 10:
            result["is_suspicious"] = True
            result["risk_score"] += 30
            result["events"].append("Rapid domain creation")
        
        return result
```

## 5. Implementation Steps

### 5.1 Week 1: Billing System
- [ ] Vytvoriť billing modely
- [ ] Implementovať billing service
- [ ] Vytvoriť API endpointy pre billing
- [ ] Pridať payment gateway integráciu

### 5.2 Week 2: Notification System
- [ ] Vytvoriť notification modely
- [ ] Implementovať notification service
- [ ] Nastaviť email, SMS a push notifikácie
- [ ] Vytvoriť notification templates

### 5.3 Week 3: Audit & Security
- [ ] Vytvoriť audit log modely
- [ ] Implementovať audit service
- [ ] Pridať automatické logovanie zmien
- [ ] Nastaviť security event monitoring

### 5.4 Week 4: Business Rules
- [ ] Vytvoriť business rules service
- [ ] Implementovať validation rules
- [ ] Pridať rate limiting
- [ ] Nastaviť suspicious activity detection

### 5.5 Week 5: Integration
- [ ] Integrovať billing s domain/SSL operáciami
- [ ] Pripojiť notifikácie k business events
- [ ] Pridať audit logging do všetkých operácií
- [ ] Testovať business rules

### 5.6 Week 6: Polish & Monitoring
- [ ] Vytvoriť billing reports
- [ ] Nastaviť notification analytics
- [ ] Pridať audit log reporting
- [ ] Optimalizovať performance

## 6. Best Practices

### 6.1 Billing best practices
- **Graceful degradation**: Poskytovať free tier aj pri problémoch s platbami
- **Clear communication**: Informovať užívateľov o zmene plánu, expiráciách
- **Flexible billing**: Podpora rôznych billing periodov a payment methodov
- **Data retention**: Uchovávať billing dáta podľa legislatívy
- **Security**: Šifrovať citlivé payment informácie

### 6.2 Notification best practices
- **User control**: Umožniť užívateľom nastavovať preferencie
- **Template system**: Používať flexibilný template systém
- **Delivery tracking**: Sledovať delivery rate a chyby
- **Rate limiting**: Ochrániť pred notification spamom
- **Multi-channel**: Podpora email, SMS, push notifikácií

### 6.3 Audit best practices
- **Complete logging**: Logovať všetky dôležité operácie
- **Immutable logs**: Zabezpečiť, že audit logy nie je možné modifikovať
- **Performance**: Minimalizovať dopad audit logovania na výkon
- **Retention policies**: Nastaviť vhodné politiky uchovávania logov
- **Access control**: Obmedziť prístup k audit logom

### 6.4 Business rules best practices
- **Centralized rules**: Uchovávať business rules na jednom mieste
- **Configurable**: Umožniť konfigurovať rules bez kódových zmien
- **Testing**: Dôkladne testovať všetky business rules
- **Documentation**: Dobre zdokumentovať všetky rules
- **Monitoring**: Sledovať vplyv rules na systém

Tento blueprint poskytuje komplexný návod na implementáciu business logic pre API Centrum Backend systém.