#!/usr/bin/env python3
"""
Fixed Flask Application for US-10
Complete integration with proper error handling and sequential US features
"""

from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from datetime import datetime
import os
import sys

def create_app():
    """Create and configure the Flask application"""
    print("🏗️ Creating Dr. Resume Flask App...")
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../frontend',
                static_folder='../frontend/static')
    
    # Basic configuration with absolute paths
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, 'database', 'dr_resume_dev.db')
    upload_path = os.path.join(project_root, 'uploads')

    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = upload_path
    app.config['RESUME_UPLOAD_FOLDER'] = upload_path  # Fix for upload routes
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Ensure directories exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(upload_path, exist_ok=True)
    
    # Initialize CORS
    CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired',
            'error': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Invalid token',
            'error': 'invalid_token'
        }), 401
    
    # Initialize database
    try:
        from models import db
        db.init_app(app)
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

    # Register routes with error handling
    try:
        from routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp)
        print("✅ Auth routes registered")
    except Exception as e:
        print(f"❌ Auth routes ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from routes.upload_routes import upload_bp
        app.register_blueprint(upload_bp)
        print("✅ Upload routes registered")
    except Exception as e:
        print(f"⚠️ Upload routes warning: {e}")
    
    try:
        from routes.jd_routes import jd_bp
        app.register_blueprint(jd_bp)
        print("✅ Job description routes registered")
    except Exception as e:
        print(f"⚠️ JD routes warning: {e}")
    
    # Keyword routes removed - keywords are now extracted automatically during upload
    
    try:
        from routes.matching_routes import matching_bp
        app.register_blueprint(matching_bp)
        print("✅ Matching routes registered")
    except Exception as e:
        print(f"⚠️ Matching routes warning: {e}")
    
    try:
        from routes.suggestions_routes import suggestions_bp
        app.register_blueprint(suggestions_bp)
        print("✅ Suggestions routes registered")
    except Exception as e:
        print(f"⚠️ Suggestions routes warning: {e}")

    try:
        from routes.history_routes import history_bp
        app.register_blueprint(history_bp)
        print("✅ History routes registered")
    except Exception as e:
        print(f"⚠️ History routes warning: {e}")

    try:
        from routes.account_route import account_bp
        app.register_blueprint(account_bp)
        print("✅ Account routes registered")
    except Exception as e:
        print(f"⚠️ Account routes warning: {e}")

    # Simple auth routes and test routes removed - using integrated routes only

    # Add missing API endpoints
    @app.route('/api/scan_history')
    @jwt_required()
    def scan_history():
        """Scan history endpoint (alias for history)"""
        try:
            from flask_jwt_extended import get_jwt_identity
            from models import MatchScore, Resume, JobDescription

            user_id = get_jwt_identity()

            # Get recent match scores
            matches = db.session.query(MatchScore, Resume, JobDescription)\
                .join(Resume, MatchScore.resume_id == Resume.id)\
                .join(JobDescription, MatchScore.job_description_id == JobDescription.id)\
                .filter(MatchScore.user_id == user_id)\
                .order_by(MatchScore.created_at.desc())\
                .limit(10)\
                .all()

            history = []
            for match, resume, jd in matches:
                history.append({
                    'id': match.id,
                    'resume_title': resume.title or resume.original_filename,
                    'job_title': jd.title,
                    'company': jd.company_name,
                    'overall_score': match.overall_score,
                    'created_at': match.created_at.isoformat()
                })

            return jsonify({
                'success': True,
                'history': history,
                'total': len(history)
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error loading history: {str(e)}'
            }), 500

    @app.route('/api/account')
    @jwt_required()
    def account_info():
        """Account information endpoint (alias for account_info)"""
        try:
            from flask_jwt_extended import get_jwt_identity
            from models import User

            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404

            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': getattr(user, 'role', 'user'),
                    'is_active': getattr(user, 'is_active', True),
                    'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error loading account: {str(e)}'
            }), 500

    @app.route('/api/change_password', methods=['PUT', 'POST'])
    @jwt_required()
    def change_password():
        """Change password endpoint"""
        try:
            from flask_jwt_extended import get_jwt_identity
            from models import User

            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404

            data = request.get_json()
            current_password = data.get('current_password')
            new_password = data.get('new_password')

            if not current_password or not new_password:
                return jsonify({
                    'success': False,
                    'message': 'Current password and new password are required'
                }), 400

            # Verify current password
            if not user.check_password(current_password):
                return jsonify({
                    'success': False,
                    'message': 'Current password is incorrect'
                }), 401

            # Update password
            user.set_password(new_password)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Password changed successfully'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error changing password: {str(e)}'
            }), 500

    @app.route('/api/test-full-suggestions', methods=['POST'])
    @jwt_required()
    def test_full_suggestions():
        """Test basic suggestions with proper data setup"""
        try:
            from flask_jwt_extended import get_jwt_identity
            from models import User, Resume, JobDescription
            from services.suggestions_service import SuggestionsService

            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404

            # Create or get test resume
            resume = Resume.query.filter_by(user_id=user_id).first()
            if not resume:
                resume = Resume(
                    user_id=user_id,
                    original_filename="test_resume.pdf",
                    file_path="/test/path/test_resume.pdf",
                    file_size=1000,
                    file_type="pdf",
                    title="Test Resume"
                )
                resume.extracted_text = "Python developer with JavaScript experience. Strong communication skills."
                resume.technical_skills = "python,javascript"
                resume.soft_skills = "communication"
                resume.other_keywords = "agile"
                resume.keywords_extracted = True

                db.session.add(resume)
                db.session.commit()

            # Create or get test job description
            jd = JobDescription.query.filter_by(user_id=user_id).first()
            if not jd:
                jd = JobDescription(
                    user_id=user_id,
                    title="Software Developer",
                    job_text="Looking for Python developer with React and SQL experience. Must have leadership and communication skills."
                )
                jd.technical_skills = "python,react,sql"
                jd.soft_skills = "communication,leadership"
                jd.other_keywords = "agile,scrum"
                jd.keywords_extracted = True

                db.session.add(jd)
                db.session.commit()

            # Generate suggestions
            suggestions_service = SuggestionsService()
            result = suggestions_service.generate_basic_suggestions(
                resume_id=resume.id,
                job_description_id=jd.id,
                user_id=user_id
            )

            return jsonify({
                'success': True,
                'message': 'Basic suggestions generated successfully',
                'suggestions': result,
                'resume_id': resume.id,
                'job_description_id': jd.id
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
    
    # Frontend routes
    @app.route('/')
    def landing():
        """Landing page"""
        return render_template('landing.html')
    
    @app.route('/register')
    def register_page():
        """Registration page"""
        return render_template('register.html')
    
    @app.route('/login')
    def login_page():
        """Login page"""
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/upload')
    def upload_page():
        """Upload page"""
        return render_template('upload.html')
    
    @app.route('/job-descriptions')
    def job_descriptions():
        """Job descriptions page"""
        return render_template('add_jd.html')

    @app.route('/add-job-description')
    def add_jd_page():
        """Add job description page (alternative route)"""
        return render_template('add_jd.html')
    
    @app.route('/keywords')
    def keywords():
        """Keywords page"""
        return render_template('keywords.html')
    
    @app.route('/matching')
    def matching():
        """Matching page"""
        return render_template('matching.html')
    
    @app.route('/suggestions')
    def suggestions():
        """Suggestions page"""
        return render_template('suggestions.html')
    
    @app.route('/account')
    def account():
        """Account page"""
        return render_template('account.html')
    
    # Health check endpoints
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Dr. Resume is running',
            'version': '1.0.0'
        })

    @app.route('/api/health')
    def api_health():
        """API health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Dr. Resume API is running',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        })

    # Test suggestions endpoint (no auth required)
    @app.route('/api/test-suggestions')
    def test_suggestions():
        """Test suggestions without authentication"""
        try:
            from services.dynamic_suggestions_service import DynamicSuggestionsService

            # Create test data in database first
            with app.app_context():
                from models import User, Resume, JobDescription

                # Get or create test user
                user = User.query.filter_by(email='test@drresume.com').first()
                if not user:
                    user = User(
                        first_name="Test",
                        last_name="User",
                        email="test@drresume.com",
                        password="password123"
                    )
                    db.session.add(user)
                    db.session.commit()

                # Create test resume if not exists
                resume = Resume.query.filter_by(user_id=user.id).first()
                if not resume:
                    resume = Resume(
                        user_id=user.id,
                        original_filename="test_resume.pdf",
                        file_path="/test/path",
                        file_size=1000,
                        file_type="pdf"
                    )
                    # Set additional fields after creation
                    resume.extracted_text = "Python developer with JavaScript experience"
                    resume.technical_skills = "python,javascript"
                    resume.soft_skills = "communication"
                    resume.other_keywords = "agile"
                    resume.keywords_extracted = True

                    db.session.add(resume)
                    db.session.commit()

                # Create test job description if not exists
                jd = JobDescription.query.filter_by(user_id=user.id).first()
                if not jd:
                    jd = JobDescription(
                        user_id=user.id,
                        title="Software Developer",
                        job_text="Looking for Python developer with React and SQL experience",
                        company_name="Test Company"
                    )
                    # Set additional fields after creation
                    jd.technical_skills = "python,react,sql"
                    jd.soft_skills = "communication,leadership"
                    jd.other_keywords = "agile,scrum"
                    jd.keywords_extracted = True

                    db.session.add(jd)
                    db.session.commit()

                # Test the suggestions service
                ai_service = DynamicSuggestionsService()
                result = ai_service.generate_basic_suggestions(
                    resume_id=resume.id,
                    job_description_id=jd.id,
                    user_id=user.id
                )

                return jsonify({
                    'success': True,
                    'message': 'Test suggestions generated successfully',
                    'suggestions': result
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500

    # Note: Resume upload endpoint is now handled by the upload_bp blueprint

    # Add job description endpoint
    @app.route('/api/add_job_description', methods=['POST'])
    @jwt_required()
    def add_job_description():
        """Add a new job description"""
        try:
            from models import db, JobDescription
            from services.keyword_parser import KeywordParser

            current_user_id = get_jwt_identity()
            data = request.get_json()

            title = data.get('title', '').strip()
            company_name = data.get('company_name', '').strip()
            job_text = data.get('job_text', '').strip()

            if not title:
                return jsonify({
                    'success': False,
                    'message': 'Job title is required'
                }), 400

            if not job_text:
                return jsonify({
                    'success': False,
                    'message': 'Job description text is required'
                }), 400

            # Create job description
            jd = JobDescription(
                user_id=current_user_id,
                title=title,
                company_name=company_name,
                job_text=job_text
            )

            # Extract keywords automatically
            try:
                keyword_parser = KeywordParser()
                keywords = keyword_parser.extract_keywords(job_text)
                jd.set_keywords(
                    technical_skills=keywords['technical_skills'],
                    soft_skills=keywords['soft_skills'],
                    other_keywords=keywords['other_keywords']
                )
                print(f"Keywords automatically extracted for job description {jd.id}")
            except Exception as keyword_error:
                print(f"Failed to extract keywords: {keyword_error}")

            db.session.add(jd)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Job description added successfully!',
                'job_description': {
                    'id': jd.id,
                    'title': jd.title,
                    'company_name': jd.company_name,
                    'keywords_extracted': jd.keywords_extracted
                }
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error adding job description: {str(e)}'
            }), 500

    # Available suggestions endpoint
    @app.route('/api/available_suggestions', methods=['GET'])
    @jwt_required()
    def available_suggestions():
        """Get available resumes and job descriptions for suggestions"""
        try:
            from models import db, Resume, JobDescription
            from flask_jwt_extended import get_jwt_identity

            current_user_id = get_jwt_identity()

            with app.app_context():
                # Get user's resumes
                resumes = Resume.query.filter_by(user_id=current_user_id).all()
                resume_list = []
                for resume in resumes:
                    # Count keywords for this resume (use the existing keyword_count field)
                    keyword_count = resume.keyword_count or 0
                    resume_list.append({
                        'id': resume.id,
                        'title': resume.title or resume.original_filename or f'Resume {resume.id}',
                        'filename': resume.original_filename,
                        'upload_date': resume.created_at.strftime('%Y-%m-%d') if resume.created_at else 'Unknown',
                        'keyword_count': keyword_count
                    })

                # Get user's job descriptions
                job_descriptions = JobDescription.query.filter_by(user_id=current_user_id).all()
                jd_list = []
                for jd in job_descriptions:
                    # Count keywords for this JD (use the existing keyword_count field)
                    keyword_count = jd.keyword_count or 0
                    jd_list.append({
                        'id': jd.id,
                        'title': jd.title or f'Job Description {jd.id}',
                        'company_name': jd.company_name or 'Unknown Company',
                        'created_date': jd.created_at.strftime('%Y-%m-%d') if jd.created_at else 'Unknown',
                        'keyword_count': keyword_count
                    })

                return jsonify({
                    'success': True,
                    'resumes': resume_list,
                    'job_descriptions': jd_list
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error loading data: {str(e)}'
            }), 500

    # Test endpoint to check available data (no auth required)
    @app.route('/api/test-available-data', methods=['GET'])
    def test_available_data():
        """Test endpoint to check available resumes and job descriptions"""
        try:
            from models import db, Resume, JobDescription

            with app.app_context():
                # Get all resumes
                resumes = Resume.query.all()
                resume_list = []
                for resume in resumes:
                    # Count keywords for this resume (use the existing keyword_count field)
                    keyword_count = resume.keyword_count or 0
                    resume_list.append({
                        'id': resume.id,
                        'title': resume.title or resume.original_filename or f'Resume {resume.id}',
                        'filename': resume.original_filename,
                        'user_id': resume.user_id,
                        'upload_date': resume.created_at.strftime('%Y-%m-%d') if resume.created_at else 'Unknown',
                        'keyword_count': keyword_count
                    })

                # Get all job descriptions
                job_descriptions = JobDescription.query.all()
                jd_list = []
                for jd in job_descriptions:
                    # Count keywords for this JD (use the existing keyword_count field)
                    keyword_count = jd.keyword_count or 0
                    jd_list.append({
                        'id': jd.id,
                        'title': jd.title or f'Job Description {jd.id}',
                        'company_name': jd.company_name or 'Unknown Company',
                        'user_id': jd.user_id,
                        'created_date': jd.created_at.strftime('%Y-%m-%d') if jd.created_at else 'Unknown',
                        'keyword_count': keyword_count
                    })

                return jsonify({
                    'success': True,
                    'total_resumes': len(resume_list),
                    'total_job_descriptions': len(jd_list),
                    'resumes': resume_list,
                    'job_descriptions': jd_list
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error loading data: {str(e)}'
            }), 500

    # Basic suggestions endpoint
    @app.route('/api/basic_suggestions', methods=['POST'])
    @jwt_required()
    def basic_suggestions():
        """Generate basic suggestions for resume improvement"""
        try:
            from services.suggestions_service import SuggestionsService

            current_user_id = get_jwt_identity()
            data = request.get_json()

            resume_id = data.get('resume_id')
            job_description_id = data.get('job_description_id')

            if not resume_id or not job_description_id:
                return jsonify({
                    'success': False,
                    'message': 'Resume ID and Job Description ID are required'
                }), 400

            with app.app_context():
                # Generate suggestions
                suggestions_service = SuggestionsService()
                result = suggestions_service.generate_basic_suggestions(
                    resume_id=resume_id,
                    job_description_id=job_description_id,
                    user_id=current_user_id
                )

                return jsonify(result)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error generating suggestions: {str(e)}'
            }), 500

    # Premium suggestions endpoint
    @app.route('/api/premium_suggestions', methods=['POST'])
    @jwt_required()
    def premium_suggestions():
        """Generate premium AI-powered suggestions"""
        try:
            from services.premium_suggestions_service import PremiumSuggestionsService

            current_user_id = get_jwt_identity()
            data = request.get_json()

            resume_id = data.get('resume_id')
            job_description_id = data.get('job_description_id')
            suggestion_type = data.get('suggestion_type', 'comprehensive')

            if not resume_id or not job_description_id:
                return jsonify({
                    'success': False,
                    'message': 'Resume ID and Job Description ID are required'
                }), 400

            with app.app_context():
                # Generate premium suggestions using advanced AI service
                premium_service = PremiumSuggestionsService()
                result = premium_service.generate_premium_suggestions(
                    resume_id=resume_id,
                    job_description_id=job_description_id,
                    user_id=current_user_id,
                    suggestion_type=suggestion_type
                )

                return jsonify({
                    'success': True,
                    'message': 'Premium suggestions generated successfully',
                    'suggestion_type': suggestion_type,
                    'suggestions': result,
                    'generated_at': datetime.now().isoformat()
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error generating premium suggestions: {str(e)}'
            }), 500

    # Suggestion history endpoint
    @app.route('/api/suggestion_history', methods=['GET'])
    @jwt_required()
    def suggestion_history():
        """Get suggestion history for the user"""
        try:
            from services.suggestions_service import SuggestionsService

            current_user_id = get_jwt_identity()
            limit = request.args.get('limit', 10, type=int)

            suggestions_service = SuggestionsService()
            history = suggestions_service.get_suggestion_history(current_user_id, limit)

            return jsonify({
                'success': True,
                'suggestion_history': history,
                'count': len(history)
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error loading suggestion history: {str(e)}'
            }), 500

    # Test upload endpoint (no auth required)
    @app.route('/api/test-upload', methods=['POST'])
    def test_upload():
        """Test upload functionality without file validation"""
        try:
            from models import db, User, Resume

            with app.app_context():
                # Get test user
                user = User.query.filter_by(email='testuser@example.com').first()
                if not user:
                    return jsonify({
                        'success': False,
                        'message': 'Test user not found. Please login first.'
                    }), 404

                # Create test resume
                resume = Resume(
                    user_id=user.id,
                    original_filename="test_resume.pdf",
                    file_path="/test/path/test_resume.pdf",
                    file_size=1000,
                    file_type="pdf",
                    title="Test Resume"
                )
                resume.extracted_text = "Python developer with JavaScript and React experience. Strong communication skills and agile methodology experience."
                resume.upload_status = 'completed'

                db.session.add(resume)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'Test resume uploaded successfully',
                    'resume': {
                        'id': resume.id,
                        'title': resume.title,
                        'filename': resume.original_filename
                    }
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500

    # Test basic suggestions endpoint (no auth required)
    @app.route('/api/test-basic-suggestions', methods=['POST', 'GET'])
    def test_basic_suggestions():
        """Test basic suggestions without authentication"""
        try:
            from services.suggestions_service import SuggestionsService

            # Create test data in database
            from models import db, User, Resume, JobDescription

            with app.app_context():
                # Get or create test user
                user = User.query.filter_by(email='test@drresume.com').first()
                if not user:
                    user = User(
                        first_name="Test",
                        last_name="User",
                        email="test@drresume.com"
                    )
                    user.set_password("password123")
                    db.session.add(user)
                    db.session.commit()

                # Create test resume
                resume = Resume(
                    user_id=user.id,
                    original_filename="test_resume.pdf",
                    file_path="/test/path",
                    file_size=1000,
                    file_type="pdf",
                    extracted_text="Python developer with JavaScript experience",
                    technical_skills="python,javascript",
                    soft_skills="communication",
                    other_keywords="agile"
                )
                db.session.add(resume)

                # Create test job description
                jd = JobDescription(
                    user_id=user.id,
                    title="Software Developer",
                    company_name="Test Company",
                    job_text="Looking for Python developer with React and SQL experience",
                    technical_skills="python,react,sql",
                    soft_skills="communication,leadership",
                    other_keywords="agile,scrum"
                )
                db.session.add(jd)
                db.session.commit()

                # Generate suggestions
                suggestions_service = SuggestionsService()
                result = suggestions_service.generate_basic_suggestions(
                    resume_id=resume.id,
                    job_description_id=jd.id,
                    user_id=user.id
                )

                return jsonify({
                    'success': True,
                    'message': 'Basic suggestions generated successfully',
                    'suggestions': result
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'error': 'not_found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'internal_error'
        }), 500
    
    print("✅ Flask app created successfully")
    return app

def main():
    """Main application entry point"""
    print("🩺" + "="*50 + "🩺")
    print("🚀 Starting Dr. Resume Application")
    print("="*52)
    
    # Create directories if they don't exist
    os.makedirs('../database', exist_ok=True)
    os.makedirs('../uploads', exist_ok=True)
    
    # Create and run app
    app = create_app()
    
    print("🌐 Starting Flask development server...")
    print("📍 Available at: http://localhost:5000")
    print("🔧 Debug mode: ON")
    print("="*52)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Dr. Resume...")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()
