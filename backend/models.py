from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os
import json

db = SQLAlchemy()

def get_current_user_id():
    """Helper function to get current user ID as integer from JWT"""
    from flask_jwt_extended import get_jwt_identity
    user_id_str = get_jwt_identity()
    return int(user_id_str) if user_id_str else None

def get_current_user():
    """Helper function to get current user object from JWT"""
    user_id = get_current_user_id()
    return User.query.get(user_id) if user_id else None

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='basic')  # basic, premium, admin
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    job_descriptions = db.relationship('JobDescription', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email.lower().strip()
        self.set_password(password)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def generate_tokens(self):
        """Generate JWT access and refresh tokens"""
        from datetime import timedelta

        access_token = create_access_token(
            identity=str(self.id),  # Convert to string for consistency
            additional_claims={
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'role': self.role
            },
            expires_delta=timedelta(hours=1)  # 1 hour expiry
        )
        refresh_token = create_refresh_token(
            identity=str(self.id),  # Convert to string for consistency
            expires_delta=timedelta(days=7)  # 7 days expiry
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour in seconds
        }
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        return True, "Password is valid"

    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role

    def generate_email_verification_token(self):
        """Generate email verification token"""
        import secrets
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = datetime.utcnow()
        return self.email_verification_token

    def verify_email(self, token):
        """Verify email with token"""
        if self.email_verification_token == token:
            self.is_email_verified = True
            self.email_verification_token = None
            self.email_verification_sent_at = None
            return True
        return False

    def is_verification_token_expired(self, hours=24):
        """Check if verification token is expired (default 24 hours)"""
        if not self.email_verification_sent_at:
            return True
        from datetime import timedelta
        expiry_time = self.email_verification_sent_at + timedelta(hours=hours)
        return datetime.utcnow() > expiry_time

    def is_premium(self):
        """Check if user has premium access"""
        return self.role in ['premium', 'admin']

    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

    def upgrade_to_premium(self):
        """Upgrade user to premium"""
        if self.role == 'basic':
            self.role = 'premium'
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def downgrade_to_basic(self):
        """Downgrade user to basic"""
        if self.role == 'premium':
            self.role = 'basic'
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        """Convert user object to dictionary (excluding password)"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role,
            'is_premium': self.is_premium(),
            'is_admin': self.is_admin(),
            'is_active': self.is_active,
            'is_email_verified': self.is_email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resume_count': len(self.resumes),
            'job_description_count': len(self.job_descriptions)
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File information
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    
    # Parsed content
    extracted_text = db.Column(db.Text)
    
    # NEW: Keyword analysis (US-05)
    keywords_extracted = db.Column(db.Boolean, default=False)
    technical_skills = db.Column(db.Text)  # JSON string of technical skills
    soft_skills = db.Column(db.Text)       # JSON string of soft skills
    other_keywords = db.Column(db.Text)    # JSON string of other keywords
    keyword_count = db.Column(db.Integer, default=0)
    
    # Metadata
    title = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    upload_status = db.Column(db.String(20), default='processing')
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, original_filename, file_path, file_size, file_type, title=None):
        self.user_id = user_id
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.file_type = file_type
        self.title = title or original_filename
    
    def get_file_size_formatted(self):
        """Return formatted file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def delete_file(self):
        """Delete the physical file from filesystem"""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                return True
        except Exception as e:
            print(f"Error deleting file {self.file_path}: {e}")
        return False
    
    def set_keywords(self, technical_skills=None, soft_skills=None, other_keywords=None):
        """Set extracted keywords"""
        if technical_skills:
            self.technical_skills = json.dumps(technical_skills)
        if soft_skills:
            self.soft_skills = json.dumps(soft_skills)
        if other_keywords:
            self.other_keywords = json.dumps(other_keywords)
        
        # Update keyword count
        total_keywords = 0
        if technical_skills:
            total_keywords += len(technical_skills)
        if soft_skills:
            total_keywords += len(soft_skills)
        if other_keywords:
            total_keywords += len(other_keywords)
        
        self.keyword_count = total_keywords
        self.keywords_extracted = True
    
    def get_keywords(self):
        """Get extracted keywords as Python objects"""
        return {
            'technical_skills': json.loads(self.technical_skills) if self.technical_skills else [],
            'soft_skills': json.loads(self.soft_skills) if self.soft_skills else [],
            'other_keywords': json.loads(self.other_keywords) if self.other_keywords else []
        }
    
    def to_dict(self, include_keywords=False):
        """Convert resume object to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_size_formatted': self.get_file_size_formatted(),
            'file_type': self.file_type,
            'title': self.title,
            'is_active': self.is_active,
            'upload_status': self.upload_status,
            'error_message': self.error_message,
            'has_extracted_text': bool(self.extracted_text),
            'text_length': len(self.extracted_text) if self.extracted_text else 0,
            'keywords_extracted': self.keywords_extracted,
            'keyword_count': self.keyword_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_keywords:
            data['keywords'] = self.get_keywords()
        
        return data
    
    def __repr__(self):
        return f'<Resume {self.original_filename} by User {self.user_id}>'

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Job Description Content
    title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    job_text = db.Column(db.Text, nullable=False)

    # NEW: Keyword analysis (US-05)
    keywords_extracted = db.Column(db.Boolean, default=False)
    technical_skills = db.Column(db.Text)  # JSON string of technical skills
    soft_skills = db.Column(db.Text)       # JSON string of soft skills
    other_keywords = db.Column(db.Text)    # JSON string of other keywords
    keyword_count = db.Column(db.Integer, default=0)

    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    word_count = db.Column(db.Integer, default=0)
    character_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, title, job_text, company_name=None):
        self.user_id = user_id
        self.title = title.strip()
        self.job_text = job_text.strip()
        self.company_name = company_name.strip() if company_name else None
        self.update_counts()

    def update_counts(self):
        """Update word and character counts"""
        if self.job_text:
            self.character_count = len(self.job_text)
            # Simple word count (split by whitespace)
            self.word_count = len(self.job_text.split())

    def set_keywords(self, technical_skills=None, soft_skills=None, other_keywords=None):
        """Set extracted keywords"""
        if technical_skills:
            self.technical_skills = json.dumps(technical_skills)
        if soft_skills:
            self.soft_skills = json.dumps(soft_skills)
        if other_keywords:
            self.other_keywords = json.dumps(other_keywords)

        # Update keyword count
        total_keywords = 0
        if technical_skills:
            total_keywords += len(technical_skills)
        if soft_skills:
            total_keywords += len(soft_skills)
        if other_keywords:
            total_keywords += len(other_keywords)

        self.keyword_count = total_keywords
        self.keywords_extracted = True

    def get_keywords(self):
        """Get extracted keywords as Python objects"""
        return {
            'technical_skills': json.loads(self.technical_skills) if self.technical_skills else [],
            'soft_skills': json.loads(self.soft_skills) if self.soft_skills else [],
            'other_keywords': json.loads(self.other_keywords) if self.other_keywords else []
        }

    @staticmethod
    def validate_job_description(title, job_text, company_name=None):
        """Validate job description data"""
        errors = []

        # Title validation
        if not title or not title.strip():
            errors.append('Job title is required')
        elif len(title.strip()) < 3:
            errors.append('Job title must be at least 3 characters long')
        elif len(title.strip()) > 255:
            errors.append('Job title must be less than 255 characters')

        # Job text validation
        if not job_text or not job_text.strip():
            errors.append('Job description text is required')
        elif len(job_text.strip()) < 50:
            errors.append('Job description must be at least 50 characters long')
        elif len(job_text.strip()) > 50000:
            errors.append('Job description must be less than 50,000 characters')

        # Company name validation (optional)
        if company_name and len(company_name.strip()) > 255:
            errors.append('Company name must be less than 255 characters')

        return errors

    def to_dict(self, include_text=False, include_keywords=False):
        """Convert job description object to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'company_name': self.company_name,
            'is_active': self.is_active,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'keywords_extracted': self.keywords_extracted,
            'keyword_count': self.keyword_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Include full text only if requested (for detailed view)
        if include_text:
            data['job_text'] = self.job_text

        # Include keywords if requested
        if include_keywords:
            data['keywords'] = self.get_keywords()

        return data

    def __repr__(self):
        return f'<JobDescription {self.title} by User {self.user_id}>'


class MatchScore(db.Model):
    """
    US-06: Model for storing resume-job description matching scores
    """
    __tablename__ = 'match_scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)

    # Matching scores (0-100%)
    overall_score = db.Column(db.Float, nullable=False)  # Overall matching percentage
    technical_score = db.Column(db.Float, default=0.0)   # Technical skills match
    soft_skills_score = db.Column(db.Float, default=0.0) # Soft skills match
    other_keywords_score = db.Column(db.Float, default=0.0) # Other keywords match

    # Detailed analysis
    total_resume_keywords = db.Column(db.Integer, default=0)
    total_jd_keywords = db.Column(db.Integer, default=0)
    matched_keywords = db.Column(db.Integer, default=0)

    # Algorithm details
    algorithm_used = db.Column(db.String(50), default='jaccard')  # jaccard, cosine, etc.

    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='match_scores')
    resume = db.relationship('Resume', backref='match_scores')
    job_description = db.relationship('JobDescription', backref='match_scores')

    def to_dict(self, include_details=False):
        """Convert match score object to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'job_description_id': self.job_description_id,
            'overall_score': round(self.overall_score, 2),
            'technical_score': round(self.technical_score, 2),
            'soft_skills_score': round(self.soft_skills_score, 2),
            'other_keywords_score': round(self.other_keywords_score, 2),
            'matched_keywords': self.matched_keywords,
            'algorithm_used': self.algorithm_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_details:
            data.update({
                'total_resume_keywords': self.total_resume_keywords,
                'total_jd_keywords': self.total_jd_keywords,
                'resume_title': self.resume.original_filename if self.resume else None,
                'job_title': self.job_description.title if self.job_description else None,
                'company_name': self.job_description.company_name if self.job_description else None
            })

        return data

    def get_score_category(self):
        """Get score category for color coding"""
        if self.overall_score >= 80:
            return 'excellent'
        elif self.overall_score >= 60:
            return 'good'
        elif self.overall_score >= 40:
            return 'fair'
        else:
            return 'poor'

    def __repr__(self):
        return f'<MatchScore {self.overall_score}% for Resume {self.resume_id} vs JD {self.job_description_id}>'


class Suggestion(db.Model):
    """
    Resume Suggestions Model - Stores individual suggestion recommendations
    Schema matches your exact specification
    """
    __tablename__ = 'resume_suggestions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    jd_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)

    # Suggestion Details (as per your schema)
    suggestion_type = db.Column(db.String(50), nullable=False)  # technical_skills, soft_skills, etc.
    priority = db.Column(db.String(20), nullable=False)  # high, medium, low, critical
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.JSON, nullable=True)  # JSON array of keywords
    action = db.Column(db.Text, nullable=True)

    # Additional fields for premium suggestions
    examples = db.Column(db.JSON, nullable=True)  # JSON array of examples
    tier = db.Column(db.String(20), default='basic')  # 'basic' or 'premium'

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('suggestions', lazy=True))
    resume = db.relationship('Resume', backref=db.backref('suggestions', lazy=True))
    job_description = db.relationship('JobDescription', foreign_keys=[jd_id], backref=db.backref('suggestions', lazy=True))

    def mark_as_implemented(self):
        """Mark suggestion as implemented by user"""
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'type': self.suggestion_type,
            'priority': self.priority,
            'title': self.title,
            'description': self.description,
            'keywords': self.keywords or [],
            'action': self.action,
            'examples': self.examples or [],
            'tier': self.tier,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Suggestion {self.suggestion_type} ({self.priority}) for Resume {self.resume_id}>'


