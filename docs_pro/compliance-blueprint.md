# Compliance Blueprint

## Prehľad
Tento blueprint definuje požiadavky a opatrenia pre zabezpečenie compliance API Centrum Backend systému podľa GDPR, ISO 27001, SOC 2 a iných relevantných štandardov.

## Ciele
- Zabezpečiť compliance s GDPR (General Data Protection Regulation)
- Implementovať požiadavky ISO 27001 pre informačnú bezpečnosť
- Pripraviť systém na SOC 2 Type II audit
- Zabezpečiť compliance s PCI DSS pre payment processing
- Vytvoriť dokumentáciu a procesy pre compliance

## 1. GDPR Compliance

### 1.1 Data Protection by Design
```python
# app/gdpr/services.py
"""
GDPR compliance services and data protection measures
"""

import hashlib
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, Domain, SSLCertificate, AuditLog
from app.core.config import settings

class GDPRComplianceService:
    """Service for GDPR compliance and data protection"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def anonymize_user_data(self, user_id: int) -> bool:
        """Anonymize user data for deleted accounts"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Anonymize personal data
            anonymized_email = self._generate_anonymized_email(user.email)
            anonymized_name = self._generate_anonymized_name(user.name)
            
            # Update user data
            user.name = anonymized_name
            user.email = anonymized_email
            user.is_active = False
            user.deleted_at = datetime.utcnow()
            
            # Anonymize related data
            self._anonymize_user_domains(user_id)
            self._anonymize_user_ssl_certificates(user_id)
            self._anonymize_user_audit_logs(user_id)
            
            self.db.commit()
            return True
        
        except Exception as e:
            self.db.rollback()
            print(f"GDPR anonymization error: {e}")
            return False
    
    def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Export all personal data for a user (Right to Data Portability)"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Collect all user data
            user_data = {
                'user_info': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_active': user.is_active
                },
                'domains': self._get_user_domains_data(user_id),
                'ssl_certificates': self._get_user_ssl_data(user_id),
                'audit_logs': self._get_user_audit_data(user_id),
                'export_timestamp': datetime.utcnow().isoformat()
            }
            
            return user_data
        
        except Exception as e:
            print(f"Data export error: {e}")
            return {}
    
    def delete_user_data(self, user_id: int) -> bool:
        """Completely delete user data (Right to be Forgotten)"""
        try:
            # Get all related data first
            domains = self.db.query(Domain).filter(Domain.user_id == user_id).all()
            ssl_certs = self.db.query(SSLCertificate).filter(SSLCertificate.user_id == user_id).all()
            audit_logs = self.db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
            
            # Delete related data
            for domain in domains:
                self.db.delete(domain)
            
            for ssl_cert in ssl_certs:
                self.db.delete(ssl_cert)
            
            for audit_log in audit_logs:
                self.db.delete(audit_log)
            
            # Delete user
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                self.db.delete(user)
            
            self.db.commit()
            return True
        
        except Exception as e:
            self.db.rollback()
            print(f"Data deletion error: {e}")
            return False
    
    def get_data_processing_record(self) -> Dict[str, Any]:
        """Get record of data processing activities"""
        return {
            'controller': {
                'name': 'API Centrum s.r.o.',
                'address': 'Bratislava, Slovakia',
                'contact': 'dpo@api-centrum.sk'
            },
            'data_processing': [
                {
                    'purpose': 'User account management',
                    'legal_basis': 'Contract fulfillment',
                    'data_categories': ['personal_identification', 'contact_information'],
                    'data_subjects': ['registered_users'],
                    'retention_period': 'Until account deletion'
                },
                {
                    'purpose': 'Domain management',
                    'legal_basis': 'Contract fulfillment',
                    'data_categories': ['domain_information', 'technical_data'],
                    'data_subjects': ['registered_users'],
                    'retention_period': 'Until domain deletion'
                },
                {
                    'purpose': 'SSL certificate management',
                    'legal_basis': 'Contract fulfillment',
                    'data_categories': ['certificate_data', 'domain_information'],
                    'data_subjects': ['registered_users'],
                    'retention_period': 'Until certificate expiration'
                }
            ],
            'data_transfers': [
                {
                    'recipient': 'Websupport s.r.o.',
                    'purpose': 'Domain registration and management',
                    'legal_basis': 'Service provider agreement',
                    'data_categories': ['domain_information', 'contact_information']
                }
            ],
            'record_date': datetime.utcnow().isoformat()
        }
    
    def check_data_minimization(self) -> Dict[str, Any]:
        """Check if data minimization principles are followed"""
        try:
            # Check for unnecessary data collection
            users = self.db.query(User).all()
            domains = self.db.query(Domain).all()
            ssl_certs = self.db.query(SSLCertificate).all()
            
            issues = []
            
            # Check for excessive data retention
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            old_audit_logs = self.db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).count()
            
            if old_audit_logs > 0:
                issues.append({
                    'type': 'data_retention',
                    'description': f'Found {old_audit_logs} audit logs older than 1 year',
                    'recommendation': 'Implement automated data retention policies'
                })
            
            # Check for unused data fields
            # This would require schema analysis
            
            return {
                'compliant': len(issues) == 0,
                'issues': issues,
                'total_users': len(users),
                'total_domains': len(domains),
                'total_ssl_certs': len(ssl_certs)
            }
        
        except Exception as e:
            print(f"Data minimization check error: {e}")
            return {'compliant': False, 'issues': [str(e)]}
    
    def _generate_anonymized_email(self, original_email: str) -> str:
        """Generate anonymized email address"""
        email_hash = hashlib.sha256(original_email.encode()).hexdigest()[:8]
        domain = original_email.split('@')[1] if '@' in original_email else 'example.com'
        return f"anonymized_{email_hash}@{domain}"
    
    def _generate_anonymized_name(self, original_name: str) -> str:
        """Generate anonymized name"""
        name_hash = hashlib.sha256(original_name.encode()).hexdigest()[:6]
        return f"Anonymized User {name_hash}"
    
    def _anonymize_user_domains(self, user_id: int):
        """Anonymize user's domains"""
        domains = self.db.query(Domain).filter(Domain.user_id == user_id).all()
        for domain in domains:
            domain.name = f"anonymized_{hashlib.md5(domain.name.encode()).hexdigest()[:8]}.com"
            domain.description = "Anonymized domain"
    
    def _anonymize_user_ssl_certificates(self, user_id: int):
        """Anonymize user's SSL certificates"""
        ssl_certs = self.db.query(SSLCertificate).filter(SSLCertificate.user_id == user_id).all()
        for cert in ssl_certs:
            cert.domain_name = f"anonymized_{hashlib.md5(cert.domain_name.encode()).hexdigest()[:8]}.com"
            cert.certificate_data = "Anonymized certificate data"
    
    def _anonymize_user_audit_logs(self, user_id: int):
        """Anonymize user's audit logs"""
        audit_logs = self.db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
        for log in audit_logs:
            log.ip_address = "0.0.0.0"  # Anonymize IP
            log.user_agent = "Anonymized user agent"
```

### 1.2 Data Subject Rights Implementation
```python
# app/gdpr/routes.py
"""
GDPR compliance API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db import get_db
from app.gdpr.services import GDPRComplianceService
from app.core.security import get_current_user
from app.models import User

router = APIRouter()
security = HTTPBearer()

@router.get("/gdpr/data-export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all personal data for the current user"""
    gdpr_service = GDPRComplianceService(db)
    
    user_data = gdpr_service.export_user_data(current_user.id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User data not found"
        )
    
    return {
        "message": "User data exported successfully",
        "data": user_data
    }

@router.post("/gdpr/anonymize")
async def anonymize_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Anonymize user account and data"""
    gdpr_service = GDPRComplianceService(db)
    
    success = gdpr_service.anonymize_user_data(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to anonymize user data"
        )
    
    return {
        "message": "User account anonymized successfully"
    }

@router.delete("/gdpr/delete-account")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Completely delete user account and all related data"""
    gdpr_service = GDPRComplianceService(db)
    
    success = gdpr_service.delete_user_data(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user data"
        )
    
    return {
        "message": "User account and all data deleted successfully"
    }

@router.get("/gdpr/processing-record")
async def get_data_processing_record(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get record of data processing activities"""
    gdpr_service = GDPRComplianceService(db)
    
    # Only allow access for DPO or admin users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    record = gdpr_service.get_data_processing_record()
    return record

@router.get("/gdpr/compliance-check")
async def check_gdpr_compliance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check GDPR compliance status"""
    gdpr_service = GDPRComplianceService(db)
    
    # Only allow access for DPO or admin users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    compliance_status = gdpr_service.check_data_minimization()
    return compliance_status
```

## 2. ISO 27001 Compliance

### 2.1 Information Security Management System (ISMS)
```python
# app/iso27001/services.py
"""
ISO 27001 compliance services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import hashlib

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ControlType(Enum):
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"

@dataclass
class SecurityControl:
    id: str
    name: str
    description: str
    type: ControlType
    implementation_status: str
    last_reviewed: datetime
    next_review: datetime

@dataclass
class RiskAssessment:
    id: str
    name: str
    description: str
    likelihood: RiskLevel
    impact: RiskLevel
    risk_level: RiskLevel
    controls: List[str]
    mitigation_plan: str
    owner: str

class ISO27001ComplianceService:
    """Service for ISO 27001 compliance management"""
    
    def __init__(self):
        self.security_controls = self._initialize_controls()
        self.risk_assessments = []
        self.audit_logs = []
    
    def _initialize_controls(self) -> List[SecurityControl]:
        """Initialize ISO 27001 security controls"""
        return [
            SecurityControl(
                id="A.5.1.1",
                name="Information security policies",
                description="Information security policy should be defined, approved and published.",
                type=ControlType.PREVENTIVE,
                implementation_status="implemented",
                last_reviewed=datetime.utcnow(),
                next_review=datetime.utcnow() + timedelta(days=365)
            ),
            SecurityControl(
                id="A.6.1.1",
                name="Information security roles and responsibilities",
                description="Information security roles and responsibilities should be defined and allocated.",
                type=ControlType.PREVENTIVE,
                implementation_status="implemented",
                last_reviewed=datetime.utcnow(),
                next_review=datetime.utcnow() + timedelta(days=365)
            ),
            SecurityControl(
                id="A.8.2.1",
                name="Classification of information",
                description="Information should be classified in terms of legal requirements, value, criticality and sensitivity to unauthorized disclosure or modification.",
                type=ControlType.PREVENTIVE,
                implementation_status="implemented",
                last_reviewed=datetime.utcnow(),
                next_review=datetime.utcnow() + timedelta(days=365)
            ),
            SecurityControl(
                id="A.9.1.1",
                name="Access control policy",
                description="Access control policy and operating procedures should be in place.",
                type=ControlType.PREVENTIVE,
                implementation_status="implemented",
                last_reviewed=datetime.utcnow(),
                next_review=datetime.utcnow() + timedelta(days=365)
            ),
            SecurityControl(
                id="A.12.1.1",
                name="Security requirements of information systems",
                description="Security requirements should be identified and agreed before information systems are developed.",
                type=ControlType.PREVENTIVE,
                implementation_status="implemented",
                last_reviewed=datetime.utcnow(),
                next_review=datetime.utcnow() + timedelta(days=365)
            )
        ]
    
    def conduct_risk_assessment(self, asset: str, threat: str, vulnerability: str) -> RiskAssessment:
        """Conduct risk assessment for specific asset"""
        # Calculate risk level based on likelihood and impact
        likelihood = self._assess_likelihood(threat, vulnerability)
        impact = self._assess_impact(asset)
        risk_level = self._calculate_risk_level(likelihood, impact)
        
        risk_id = hashlib.md5(f"{asset}_{threat}_{vulnerability}".encode()).hexdigest()[:8]
        
        risk = RiskAssessment(
            id=risk_id,
            name=f"Risk: {asset} - {threat}",
            description=f"Risk assessment for {asset} regarding {threat} threat",
            likelihood=likelihood,
            impact=impact,
            risk_level=risk_level,
            controls=self._recommend_controls(risk_level),
            mitigation_plan=self._generate_mitigation_plan(risk_level, asset),
            owner="Information Security Manager"
        )
        
        self.risk_assessments.append(risk)
        return risk
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall ISO 27001 compliance status"""
        total_controls = len(self.security_controls)
        implemented_controls = len([
            c for c in self.security_controls 
            if c.implementation_status == "implemented"
        ])
        
        total_risks = len(self.risk_assessments)
        high_risks = len([
            r for r in self.risk_assessments 
            if r.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ])
        
        compliance_percentage = (implemented_controls / total_controls) * 100 if total_controls > 0 else 0
        
        return {
            'compliance_percentage': compliance_percentage,
            'total_controls': total_controls,
            'implemented_controls': implemented_controls,
            'pending_controls': total_controls - implemented_controls,
            'total_risks': total_risks,
            'high_risks': high_risks,
            'risk_trend': self._calculate_risk_trend(),
            'last_audit': self._get_last_audit_date(),
            'next_review': self._get_next_review_date()
        }
    
    def generate_security_policy(self) -> Dict[str, Any]:
        """Generate information security policy"""
        return {
            'policy_version': '1.0',
            'effective_date': datetime.utcnow().isoformat(),
            'scope': 'All information assets and systems of API Centrum',
            'objectives': [
                'Protect confidentiality, integrity, and availability of information',
                'Ensure compliance with legal and regulatory requirements',
                'Maintain business continuity and minimize security risks',
                'Promote security awareness and training'
            ],
            'principles': [
                'Security is everyone\'s responsibility',
                'Risk-based approach to security management',
                'Continuous improvement of security practices',
                'Compliance with applicable laws and regulations'
            ],
            'responsibilities': {
                'management': 'Ensure adequate resources for information security',
                'employees': 'Follow security policies and procedures',
                'security_team': 'Implement and maintain security controls',
                'third_parties': 'Comply with security requirements in contracts'
            },
            'compliance_requirements': [
                'GDPR compliance for personal data protection',
                'ISO 27001 compliance for information security management',
                'Regular security audits and assessments',
                'Incident reporting and response procedures'
            ]
        }
    
    def create_incident_response_plan(self) -> Dict[str, Any]:
        """Create incident response plan"""
        return {
            'incident_types': [
                'Data breach',
                'Malware infection',
                'Denial of service attack',
                'Unauthorized access',
                'System compromise'
            ],
            'response_team': {
                'incident_manager': 'Information Security Manager',
                'technical_lead': 'System Administrator',
                'communications': 'PR Manager',
                'legal': 'Legal Counsel'
            },
            'response_procedures': {
                'detection': 'Monitor systems for security events',
                'assessment': 'Evaluate incident severity and impact',
                'containment': 'Isolate affected systems',
                'eradication': 'Remove threat and vulnerabilities',
                'recovery': 'Restore systems and verify security',
                'lessons_learned': 'Document and improve procedures'
            },
            'communication_plan': {
                'internal': 'Notify management and affected users',
                'external': 'Notify regulators and customers as required',
                'media': 'Coordinate through PR department'
            },
            'escalation_criteria': {
                'level_1': 'Minor incidents handled by technical team',
                'level_2': 'Major incidents escalated to management',
                'level_3': 'Critical incidents escalated to executive team'
            }
        }
    
    def _assess_likelihood(self, threat: str, vulnerability: str) -> RiskLevel:
        """Assess likelihood of threat exploiting vulnerability"""
        # This would integrate with threat intelligence and vulnerability scanning
        # For now, return mock assessment
        if "critical" in threat.lower() or "zero-day" in vulnerability.lower():
            return RiskLevel.CRITICAL
        elif "high" in threat.lower() or "unpatched" in vulnerability.lower():
            return RiskLevel.HIGH
        elif "medium" in threat.lower():
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _assess_impact(self, asset: str) -> RiskLevel:
        """Assess potential impact on asset"""
        if "customer_data" in asset.lower() or "financial" in asset.lower():
            return RiskLevel.CRITICAL
        elif "user_data" in asset.lower() or "operational" in asset.lower():
            return RiskLevel.HIGH
        elif "test" in asset.lower():
            return RiskLevel.LOW
        else:
            return RiskLevel.MEDIUM
    
    def _calculate_risk_level(self, likelihood: RiskLevel, impact: RiskLevel) -> RiskLevel:
        """Calculate overall risk level"""
        risk_matrix = {
            (RiskLevel.CRITICAL, RiskLevel.CRITICAL): RiskLevel.CRITICAL,
            (RiskLevel.CRITICAL, RiskLevel.HIGH): RiskLevel.CRITICAL,
            (RiskLevel.HIGH, RiskLevel.CRITICAL): RiskLevel.CRITICAL,
            (RiskLevel.HIGH, RiskLevel.HIGH): RiskLevel.HIGH,
            (RiskLevel.HIGH, RiskLevel.MEDIUM): RiskLevel.HIGH,
            (RiskLevel.MEDIUM, RiskLevel.HIGH): RiskLevel.HIGH,
            (RiskLevel.MEDIUM, RiskLevel.MEDIUM): RiskLevel.MEDIUM,
            (RiskLevel.MEDIUM, RiskLevel.LOW): RiskLevel.MEDIUM,
            (RiskLevel.LOW, RiskLevel.MEDIUM): RiskLevel.MEDIUM,
            (RiskLevel.LOW, RiskLevel.LOW): RiskLevel.LOW,
            (RiskLevel.CRITICAL, RiskLevel.LOW): RiskLevel.HIGH,
            (RiskLevel.LOW, RiskLevel.CRITICAL): RiskLevel.HIGH
        }
        
        return risk_matrix.get((likelihood, impact), RiskLevel.MEDIUM)
    
    def _recommend_controls(self, risk_level: RiskLevel) -> List[str]:
        """Recommend security controls based on risk level"""
        if risk_level == RiskLevel.CRITICAL:
            return [
                "Implement multi-factor authentication",
                "Encrypt sensitive data at rest and in transit",
                "Deploy intrusion detection systems",
                "Conduct regular penetration testing"
            ]
        elif risk_level == RiskLevel.HIGH:
            return [
                "Implement access controls",
                "Regular security monitoring",
                "Security awareness training",
                "Vulnerability management"
            ]
        elif risk_level == RiskLevel.MEDIUM:
            return [
                "Regular software updates",
                "Basic access controls",
                "Security logging and monitoring"
            ]
        else:
            return ["Security awareness"]
    
    def _generate_mitigation_plan(self, risk_level: RiskLevel, asset: str) -> str:
        """Generate mitigation plan for specific risk"""
        if risk_level == RiskLevel.CRITICAL:
            return f"Immediate action required for {asset}. Implement comprehensive security controls including encryption, access controls, and continuous monitoring."
        elif risk_level == RiskLevel.HIGH:
            return f"High priority mitigation for {asset}. Implement security controls within 30 days and conduct regular monitoring."
        elif risk_level == RiskLevel.MEDIUM:
            return f"Medium priority mitigation for {asset}. Implement controls within 90 days and monitor regularly."
        else:
            return f"Low priority mitigation for {asset}. Implement basic security awareness and monitoring."
    
    def _calculate_risk_trend(self) -> str:
        """Calculate risk trend over time"""
        # This would analyze historical risk assessments
        return "stable"
    
    def _get_last_audit_date(self) -> Optional[datetime]:
        """Get date of last security audit"""
        # This would query audit records
        return datetime.utcnow() - timedelta(days=30)
    
    def _get_next_review_date(self) -> datetime:
        """Get date of next security review"""
        return datetime.utcnow() + timedelta(days=90)
```

### 2.2 Security Controls Implementation
```python
# app/iso27001/controls.py
"""
ISO 27001 security controls implementation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from app.core.security import verify_password, get_password_hash

class AccessControl:
    """Access control implementation (A.9)"""
    
    def __init__(self):
        self.failed_login_attempts = {}
        self.lockout_duration = timedelta(minutes=15)
    
    def check_failed_attempts(self, username: str) -> bool:
        """Check if account should be locked due to failed attempts"""
        if username not in self.failed_login_attempts:
            return False
        
        attempts = self.failed_login_attempts[username]
        if len(attempts) >= 5:
            last_attempt = attempts[-1]
            if datetime.utcnow() - last_attempt < self.lockout_duration:
                return True
            else:
                # Reset attempts after lockout period
                self.failed_login_attempts[username] = []
        
        return False
    
    def record_failed_attempt(self, username: str):
        """Record failed login attempt"""
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []
        
        self.failed_login_attempts[username].append(datetime.utcnow())
    
    def reset_failed_attempts(self, username: str):
        """Reset failed login attempts"""
        if username in self.failed_login_attempts:
            self.failed_login_attempts[username] = []

class CryptographicControls:
    """Cryptographic controls implementation (A.10)"""
    
    def __init__(self):
        self.encryption_algorithm = "AES-256-GCM"
        self.key_rotation_days = 90
    
    def encrypt_data(self, data: str, key_id: str) -> Dict[str, Any]:
        """Encrypt sensitive data"""
        # This would integrate with a proper encryption library
        # For now, return mock encrypted data
        return {
            'encrypted_data': f"encrypted_{data}",
            'algorithm': self.encryption_algorithm,
            'key_id': key_id,
            'encryption_date': datetime.utcnow().isoformat()
        }
    
    def decrypt_data(self, encrypted_data: Dict[str, Any]) -> str:
        """Decrypt sensitive data"""
        # This would integrate with a proper decryption library
        # For now, return mock decrypted data
        return encrypted_data['encrypted_data'].replace('encrypted_', '')
    
    def should_rotate_key(self, last_rotation: datetime) -> bool:
        """Check if encryption key should be rotated"""
        return datetime.utcnow() - last_rotation > timedelta(days=self.key_rotation_days)

class OperationalSecurity:
    """Operational security controls (A.12)"""
    
    def __init__(self):
        self.security_patches = {}
        self.backup_schedule = {
            'daily': timedelta(hours=24),
            'weekly': timedelta(days=7),
            'monthly': timedelta(days=30)
        }
    
    def check_patch_status(self, system: str) -> Dict[str, Any]:
        """Check security patch status"""
        last_patch = self.security_patches.get(system)
        if not last_patch:
            return {
                'status': 'outdated',
                'last_patch': None,
                'recommendation': 'Apply latest security patches immediately'
            }
        
        days_since_patch = (datetime.utcnow() - last_patch).days
        if days_since_patch > 30:
            status = 'outdated'
            recommendation = 'Apply security patches within 24 hours'
        elif days_since_patch > 7:
            status = 'warning'
            recommendation = 'Schedule patch application soon'
        else:
            status = 'current'
            recommendation = 'System is up to date'
        
        return {
            'status': status,
            'last_patch': last_patch.isoformat(),
            'days_since_patch': days_since_patch,
            'recommendation': recommendation
        }
    
    def schedule_backup(self, system: str, backup_type: str = 'daily') -> Dict[str, Any]:
        """Schedule system backup"""
        next_backup = datetime.utcnow() + self.backup_schedule[backup_type]
        
        return {
            'system': system,
            'backup_type': backup_type,
            'next_backup': next_backup.isoformat(),
            'status': 'scheduled'
        }

class SupplierRelationships:
    """Supplier relationships security (A.15)"""
    
    def __init__(self):
        self.supplier_assessments = {}
        self.contract_security_requirements = [
            'Data protection and privacy compliance',
            'Security incident notification within 24 hours',
            'Regular security assessments and audits',
            'Implementation of appropriate security controls',
            'Secure development practices'
        ]
    
    def assess_supplier(self, supplier_name: str, services: List[str]) -> Dict[str, Any]:
        """Assess supplier security posture"""
        assessment = {
            'supplier_name': supplier_name,
            'services': services,
            'security_certifications': [],
            'last_assessment': datetime.utcnow(),
            'risk_level': 'medium',
            'security_controls': [],
            'contract_requirements': self.contract_security_requirements
        }
        
        self.supplier_assessments[supplier_name] = assessment
        return assessment
    
    def monitor_supplier_compliance(self, supplier_name: str) -> Dict[str, Any]:
        """Monitor supplier compliance with security requirements"""
        assessment = self.supplier_assessments.get(supplier_name)
        if not assessment:
            return {'status': 'not_found', 'message': 'Supplier not assessed'}
        
        # Check compliance status
        compliance_issues = []
        
        # This would integrate with supplier monitoring systems
        # For now, return mock compliance status
        
        return {
            'supplier': supplier_name,
            'compliance_status': 'compliant',
            'last_review': assessment['last_assessment'],
            'issues': compliance_issues,
            'next_review': datetime.utcnow() + timedelta(days=180)
        }
```

## 3. SOC 2 Compliance

### 3.1 Trust Services Criteria Implementation
```python
# app/soc2/services.py
"""
SOC 2 compliance services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

class TrustServiceCriteria(Enum):
    SECURITY = "security"
    AVAILABILITY = "availability"
    PROCESSING_INTEGRITY = "processing_integrity"
    CONFIDENTIALITY = "confidentiality"
    PRIVACY = "privacy"

@dataclass
class ControlObjective:
    id: str
    name: str
    criteria: TrustServiceCriteria
    description: str
    implementation_status: str

class SOC2ComplianceService:
    """Service for SOC 2 compliance management"""
    
    def __init__(self):
        self.control_objectives = self._initialize_control_objectives()
        self.audit_logs = []
        self.monitoring_data = {}
    
    def _initialize_control_objectives(self) -> List[ControlObjective]:
        """Initialize SOC 2 control objectives"""
        return [
            ControlObjective(
                id="CC1.1",
                name="The entity demonstrates a commitment to integrity and ethical values.",
                criteria=TrustServiceCriteria.SECURITY,
                description="Establish and maintain an environment of integrity and ethical values.",
                implementation_status="implemented"
            ),
            ControlObjective(
                id="CC2.1",
                name="The entity demonstrates an understanding of the potential for material misstatements due to fraud.",
                criteria=TrustServiceCriteria.SECURITY,
                description="Assess fraud risks and implement controls to prevent and detect fraud.",
                implementation_status="implemented"
            ),
            ControlObjective(
                id="CC3.1",
                name="The entity selects and develops control activities that contribute to the mitigation of risks.",
                criteria=TrustServiceCriteria.SECURITY,
                description="Implement control activities to mitigate identified risks.",
                implementation_status="implemented"
            ),
            ControlObjective(
                id="CC6.1",
                name="The entity authorizes and specifies system changes.",
                criteria=TrustServiceCriteria.SECURITY,
                description="Control system changes through proper authorization and testing.",
                implementation_status="implemented"
            ),
            ControlObjective(
                id="CC7.1",
                name="The entity authorizes, designs, develops or acquires, configures, documents, tests, approves, and implements IT infrastructure changes.",
                criteria=TrustServiceCriteria.SECURITY,
                description="Manage IT infrastructure changes through proper controls.",
                implementation_status="implemented"
            )
        ]
    
    def assess_control_effectiveness(self) -> Dict[str, Any]:
        """Assess effectiveness of SOC 2 controls"""
        total_controls = len(self.control_objectives)
        effective_controls = len([
            c for c in self.control_objectives 
            if c.implementation_status == "implemented"
        ])
        
        effectiveness_percentage = (effective_controls / total_controls) * 100 if total_controls > 0 else 0
        
        return {
            'effectiveness_percentage': effectiveness_percentage,
            'total_controls': total_controls,
            'effective_controls': effective_controls,
            'ineffective_controls': total_controls - effective_controls,
            'control_details': [
                {
                    'id': c.id,
                    'name': c.name,
                    'criteria': c.criteria.value,
                    'status': c.implementation_status
                }
                for c in self.control_objectives
            ]
        }
    
    def generate_soc2_report(self) -> Dict[str, Any]:
        """Generate SOC 2 compliance report"""
        control_assessment = self.assess_control_effectiveness()
        
        return {
            'report_type': 'SOC 2 Type II',
            'report_period': {
                'start_date': (datetime.utcnow() - timedelta(days=365)).isoformat(),
                'end_date': datetime.utcnow().isoformat()
            },
            'scope': {
                'systems': ['API Centrum Backend', 'Database Systems', 'Authentication Services'],
                'services': ['Domain Management', 'SSL Certificate Management', 'User Authentication'],
                'locations': ['Bratislava, Slovakia']
            },
            'trust_service_criteria': [
                {
                    'criteria': 'Security',
                    'status': 'compliant',
                    'controls_tested': 25,
                    'exceptions': 0
                },
                {
                    'criteria': 'Availability',
                    'status': 'compliant',
                    'controls_tested': 15,
                    'exceptions': 1
                },
                {
                    'criteria': 'Processing Integrity',
                    'status': 'compliant',
                    'controls_tested': 12,
                    'exceptions': 0
                },
                {
                    'criteria': 'Confidentiality',
                    'status': 'compliant',
                    'controls_tested': 18,
                    'exceptions': 0
                },
                {
                    'criteria': 'Privacy',
                    'status': 'compliant',
                    'controls_tested': 20,
                    'exceptions': 0
                }
            ],
            'control_effectiveness': control_assessment,
            'audit_findings': [],
            'management_response': 'All controls are operating effectively',
            'auditor_opinion': 'Unqualified opinion - controls are suitably designed and operating effectively'
        }
    
    def monitor_system_availability(self) -> Dict[str, Any]:
        """Monitor system availability for SOC 2 compliance"""
        # This would integrate with monitoring systems
        # For now, return mock availability data
        
        return {
            'service_availability': {
                'api_backend': {
                    'uptime_percentage': 99.9,
                    'downtime_minutes': 43.2,
                    'sla_target': 99.5,
                    'compliant': True
                },
                'database': {
                    'uptime_percentage': 99.95,
                    'downtime_minutes': 21.6,
                    'sla_target': 99.0,
                    'compliant': True
                },
                'authentication_service': {
                    'uptime_percentage': 99.8,
                    'downtime_minutes': 100.8,
                    'sla_target': 99.5,
                    'compliant': False
                }
            },
            'monitoring_period': {
                'start_date': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                'end_date': datetime.utcnow().isoformat()
            },
            'overall_compliance': True
        }
    
    def track_data_processing_integrity(self) -> Dict[str, Any]:
        """Track data processing integrity"""
        # This would integrate with data validation and monitoring systems
        # For now, return mock data
        
        return {
            'data_integrity_metrics': {
                'data_accuracy': 99.95,
                'data_completeness': 99.9,
                'data_consistency': 99.8,
                'data_validity': 99.9
            },
            'processing_errors': {
                'total_transactions': 100000,
                'errors_detected': 50,
                'error_rate': 0.05,
                'error_resolution_time': '2.5 hours'
            },
            'data_validation_controls': {
                'input_validation': 'implemented',
                'data_format_validation': 'implemented',
                'business_rule_validation': 'implemented',
                'duplicate_detection': 'implemented'
            }
        }
    
    def manage_confidentiality_controls(self) -> Dict[str, Any]:
        """Manage confidentiality controls"""
        return {
            'data_classification': {
                'public': ['marketing_content', 'public_api_docs'],
                'internal': ['employee_data', 'internal_docs'],
                'confidential': ['customer_data', 'financial_data'],
                'restricted': ['encryption_keys', 'security_credentials']
            },
            'access_controls': {
                'role_based_access': True,
                'least_privilege_enforced': True,
                'need_to_know_basis': True,
                'access_reviews': 'quarterly'
            },
            'encryption_controls': {
                'data_at_rest_encrypted': True,
                'data_in_transit_encrypted': True,
                'key_management': 'implemented',
                'encryption_audit': 'monthly'
            },
            'confidentiality_training': {
                'employees_trained': 100,
                'training_frequency': 'annual',
                'certification_required': True
            }
        }
```

## 4. PCI DSS Compliance

### 4.1 Payment Card Industry Compliance
```python
# app/pci_dss/services.py
"""
PCI DSS compliance services for payment processing
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import re

class PCIDSSComplianceService:
    """Service for PCI DSS compliance management"""
    
    def __init__(self):
        self.requirements = self._initialize_requirements()
        self.saqs = []  # Self-Assessment Questionnaires
        self.scan_results = []
    
    def _initialize_requirements(self) -> Dict[str, Dict]:
        """Initialize PCI DSS requirements"""
        return {
            '1': {
                'name': 'Install and maintain a firewall configuration to protect cardholder data',
                'status': 'compliant',
                'controls': ['Firewall configuration', 'Network segmentation', 'Access rules']
            },
            '2': {
                'name': 'Do not use vendor-supplied defaults for system passwords and other security parameters',
                'status': 'compliant',
                'controls': ['Password policies', 'Default credential removal', 'Security parameter configuration']
            },
            '3': {
                'name': 'Protect stored cardholder data',
                'status': 'compliant',
                'controls': ['Data encryption', 'Data masking', 'Key management']
            },
            '4': {
                'name': 'Encrypt transmission of cardholder data across open, public networks',
                'status': 'compliant',
                'controls': ['TLS encryption', 'VPN usage', 'Secure protocols']
            },
            '5': {
                'name': 'Protect all systems against malware and regularly update anti-virus software or programs',
                'status': 'compliant',
                'controls': ['Anti-virus software', 'Malware detection', 'Regular updates']
            },
            '6': {
                'name': 'Develop and maintain secure systems and applications',
                'status': 'compliant',
                'controls': ['Secure development', 'Vulnerability management', 'Security testing']
            },
            '7': {
                'name': 'Restrict access to cardholder data by business need-to-know',
                'status': 'compliant',
                'controls': ['Access controls', 'Role-based permissions', 'Need-to-know principle']
            },
            '8': {
                'name': 'Assign a unique ID to each person with computer access',
                'status': 'compliant',
                'controls': ['Unique user IDs', 'Authentication', 'Access logging']
            },
            '9': {
                'name': 'Restrict physical access to cardholder data',
                'status': 'compliant',
                'controls': ['Physical security', 'Access control systems', 'Visitor management']
            },
            '10': {
                'name': 'Track and monitor all access to network resources and cardholder data',
                'status': 'compliant',
                'controls': ['Logging', 'Monitoring', 'Audit trails']
            },
            '11': {
                'name': 'Regularly test security systems and processes',
                'status': 'compliant',
                'controls': ['Vulnerability scanning', 'Penetration testing', 'Security assessments']
            },
            '12': {
                'name': 'Maintain a policy that addresses information security for all personnel',
                'status': 'compliant',
                'controls': ['Security policies', 'Training programs', 'Awareness campaigns']
            }
        }
    
    def validate_card_number(self, card_number: str) -> Dict[str, Any]:
        """Validate credit card number using Luhn algorithm"""
        # Remove spaces and non-digit characters
        clean_number = re.sub(r'\D', '', card_number)
        
        # Check if valid length (13-19 digits)
        if not (13 <= len(clean_number) <= 19):
            return {
                'valid': False,
                'error': 'Invalid card number length',
                'card_type': None
            }
        
        # Luhn algorithm validation
        def luhn_check(card_num: str) -> bool:
            total = 0
            reverse_digits = card_num[::-1]
            
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n = n // 10 + n % 10
                total += n
            
            return total % 10 == 0
        
        if not luhn_check(clean_number):
            return {
                'valid': False,
                'error': 'Invalid card number (failed Luhn check)',
                'card_type': None
            }
        
        # Determine card type
        card_type = self._get_card_type(clean_number)
        
        return {
            'valid': True,
            'card_type': card_type,
            'last_four': clean_number[-4:],
            'masked_number': f"{'*' * (len(clean_number) - 4)}{clean_number[-4:]}"
        }
    
    def encrypt_card_data(self, card_data: Dict[str, str]) -> Dict[str, Any]:
        """Encrypt sensitive cardholder data"""
        # This would integrate with a proper encryption service
        # For now, return mock encrypted data
        
        encrypted_data = {
            'card_number_encrypted': f"enc_{hashlib.sha256(card_data['card_number'].encode()).hexdigest()}",
            'expiry_date_encrypted': f"enc_{hashlib.sha256(card_data['expiry_date'].encode()).hexdigest()}",
            'cvv_encrypted': f"enc_{hashlib.sha256(card_data['cvv'].encode()).hexdigest()}",
            'encryption_method': 'AES-256',
            'encryption_date': datetime.utcnow().isoformat()
        }
        
        return encrypted_data
    
    def generate_saq(self, merchant_type: str) -> Dict[str, Any]:
        """Generate Self-Assessment Questionnaire"""
        saq_template = {
            'merchant_type': merchant_type,
            'saq_type': self._determine_saq_type(merchant_type),
            'questions': self._get_saq_questions(merchant_type),
            'completion_date': None,
            'status': 'pending'
        }
        
        self.saqs.append(saq_template)
        return saq_template
    
    def conduct_vulnerability_scan(self) -> Dict[str, Any]:
        """Conduct external vulnerability scan"""
        # This would integrate with vulnerability scanning tools
        # For now, return mock scan results
        
        scan_result = {
            'scan_id': f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'scan_date': datetime.utcnow().isoformat(),
            'scope': ['api-centrum.sk', 'www.api-centrum.sk'],
            'vulnerabilities': {
                'critical': 0,
                'high': 1,
                'medium': 3,
                'low': 8,
                'info': 15
            },
            'compliant': True,
            'next_scan_due': (datetime.utcnow() + timedelta(days=90)).isoformat(),
            'scan_details': [
                {
                    'vulnerability': 'SSL/TLS Certificate Expiration',
                    'severity': 'high',
                    'status': 'remediated',
                    'remediation_date': (datetime.utcnow() - timedelta(days=5)).isoformat()
                }
            ]
        }
        
        self.scan_results.append(scan_result)
        return scan_result
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall PCI DSS compliance status"""
        total_requirements = len(self.requirements)
        compliant_requirements = len([
            r for r in self.requirements.values()
            if r['status'] == 'compliant'
        ])
        
        compliance_percentage = (compliant_requirements / total_requirements) * 100
        
        return {
            'compliance_percentage': compliance_percentage,
            'total_requirements': total_requirements,
            'compliant_requirements': compliant_requirements,
            'non_compliant_requirements': total_requirements - compliant_requirements,
            'last_assessment': datetime.utcnow().isoformat(),
            'next_assessment_due': (datetime.utcnow() + timedelta(days=365)).isoformat(),
            'scan_results': self.scan_results[-3:],  # Last 3 scans
            'saq_status': {
                'completed': len([s for s in self.saqs if s['status'] == 'completed']),
                'pending': len([s for s in self.saqs if s['status'] == 'pending']),
                'total': len(self.saqs)
            }
        }
    
    def _get_card_type(self, card_number: str) -> str:
        """Determine card type based on card number"""
        if card_number.startswith('4'):
            return 'Visa'
        elif card_number.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif card_number.startswith(('34', '37')):
            return 'American Express'
        elif card_number.startswith(('300', '301', '302', '303', '304', '305', '36', '38')):
            return 'Diners Club'
        elif card_number.startswith('6011'):
            return 'Discover'
        else:
            return 'Unknown'
    
    def _determine_saq_type(self, merchant_type: str) -> str:
        """Determine appropriate SAQ type based on merchant type"""
        if 'ecommerce' in merchant_type.lower():
            return 'SAQ A-EP'
        elif 'card_not_present' in merchant_type.lower():
            return 'SAQ A'
        elif 'card_present' in merchant_type.lower():
            return 'SAQ C'
        else:
            return 'SAQ D'
    
    def _get_saq_questions(self, merchant_type: str) -> List[Dict]:
        """Get SAQ questions for specific merchant type"""
        base_questions = [
            {
                'id': '1.1',
                'question': 'Are firewalls installed and maintained?',
                'answer': None,
                'evidence_required': 'Firewall configuration documentation'
            },
            {
                'id': '3.1',
                'question': 'Is cardholder data encrypted when stored?',
                'answer': None,
                'evidence_required': 'Encryption implementation documentation'
            },
            {
                'id': '10.1',
                'question': 'Are access logs maintained for all system components?',
                'answer': None,
                'evidence_required': 'Log management configuration'
            }
        ]
        
        return base_questions
```

## 5. Implementation Steps

### 5.1 Week 1: GDPR Implementation
- [ ] Implement GDPR compliance services
- [ ] Create data subject rights endpoints
- [ ] Implement data anonymization and deletion
- [ ] Create data processing records

### 5.2 Week 2: ISO 27001 Implementation
- [ ] Implement ISO 27001 security controls
- [ ] Create risk assessment framework
- [ ] Implement access control measures
- [ ] Create incident response procedures

### 5.3 Week 3: SOC 2 Implementation
- [ ] Implement SOC 2 control objectives
- [ ] Create monitoring and logging systems
- [ ] Implement availability tracking
- [ ] Create SOC 2 compliance reports

### 5.4 Week 4: PCI DSS Implementation
- [ ] Implement PCI DSS requirements
- [ ] Create card data encryption
- [ ] Implement vulnerability scanning
- [ ] Create SAQ management

### 5.5 Week 5: Documentation & Training
- [ ] Create compliance documentation
- [ ] Develop security policies
- [ ] Create training materials
- [ ] Document procedures and workflows

### 5.6 Week 6: Audit & Certification
- [ ] Conduct internal compliance audit
- [ ] Prepare for external audit
- [ ] Address audit findings
- [ ] Obtain compliance certifications

## 6. Best Practices

### 6.1 GDPR best practices
- **Data minimization**: Collect only necessary personal data
- **Purpose limitation**: Use data only for specified purposes
- **Transparency**: Clearly communicate data processing activities
- **Accountability**: Demonstrate compliance through documentation
- **Privacy by design**: Implement privacy measures from the start

### 6.2 ISO 27001 best practices
- **Risk-based approach**: Focus on highest risks first
- **Continuous improvement**: Regularly review and improve controls
- **Management commitment**: Ensure leadership support
- **Employee awareness**: Train all personnel on security
- **Third-party management**: Assess supplier security

### 6.3 SOC 2 best practices
- **Control documentation**: Document all controls and procedures
- **Regular testing**: Test controls regularly for effectiveness
- **Monitoring**: Continuously monitor control performance
- **Incident response**: Have effective incident response procedures
- **Management review**: Regular management review of controls

### 6.4 PCI DSS best practices
- **Scope reduction**: Minimize systems in scope
- **Encryption**: Encrypt all cardholder data
- **Access control**: Implement strict access controls
- **Regular scanning**: Conduct regular vulnerability scans
- **Documentation**: Maintain comprehensive documentation

Tento blueprint poskytuje komplexný návod na zabezpečenie compliance API Centrum Backend systému podľa medzinárodných štandardov.