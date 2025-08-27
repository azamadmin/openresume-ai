#!/usr/bin/env python3
"""
Dr. Resume AI - Flask Application
AI-powered resume optimization and job matching platform
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env file (check multiple locations)
env_paths = [
    '.env',  # Current directory
    'backend/.env',  # Backend directory
    os.path.join(os.path.dirname(__file__), '.env')  # Same directory as this file
]

env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"🔧 Loaded .env file from: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print("🔧 No .env file found, using environment variables")

def create_app():

    # Create Flask app (only once!)
    app = Flask(__name__,
                template_folder='../frontend',
                static_folder='../frontend/static')

    # US-10: Add all main frontend HTML routes
    @app.route('/history')
    def serve_history():
        return render_template('us10_scan_history.html')

    @app.route('/us10_scan_history.html')
    def serve_scan_history_html():
        return render_template('us10_scan_history.html')

    @app.route('/login')
    def serve_login():
        return render_template('us10_login.html')

    @app.route('/register')
    def serve_register():
        return render_template('us10_register.html')

    @app.route('/dashboard')
    def serve_dashboard():
        return render_template('us10_dashboard.html')

    @app.route('/account')
    def serve_account():
        return render_template('us10_account.html')

    # Serve landing page
    @app.route('/')
    def serve_frontend():
        return render_template('index.html')

    # Add direct HTML file routes for compatibility
    @app.route('/us10_login.html')
    def serve_login_html():
        return render_template('us10_login.html')

    @app.route('/us10_register.html')
    def serve_register_html():
        return render_template('us10_register.html')

    @app.route('/us10_dashboard.html')
    def serve_dashboard_html():
        return render_template('us10_dashboard.html')

    @app.route('/us10_account.html')
    def serve_account_html():
        return render_template('us10_account.html')

    # Basic configuration
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, 'database', 'dr_resume_dev.db')
    upload_path = os.path.join(project_root, 'uploads')

    # Get environment variables with explicit debugging
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
    jwt_secret_key = os.getenv('JWT_SECRET_KEY', None)

    # CRITICAL: Ensure JWT_SECRET_KEY always matches SECRET_KEY
    if jwt_secret_key is None or jwt_secret_key != secret_key:
        print(f"🔧 FORCING JWT_SECRET_KEY to match SECRET_KEY for consistency")
        jwt_secret_key = secret_key

    # Ensure both secrets are the same for JWT to work properly
    app.config['SECRET_KEY'] = secret_key
    app.config['JWT_SECRET_KEY'] = jwt_secret_key

    # Debug: Log JWT secret key (first 10 chars only for security)
    print(f"🔑 SECRET_KEY (first 10 chars): {secret_key[:10]}...")
    print(f"🔑 JWT_SECRET_KEY (first 10 chars): {jwt_secret_key[:10]}...")
    print(f"🔑 Keys match: {secret_key == jwt_secret_key}")
    print(f"🔑 Environment JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY', 'NOT_SET')[:10]}...")
    print(f"🔑 Environment SECRET_KEY: {os.getenv('SECRET_KEY', 'NOT_SET')[:10]}...")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = upload_path
    app.config['RESUME_UPLOAD_FOLDER'] = upload_path
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # JWT Configuration
    from datetime import timedelta
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # 1 hour
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)  # 7 days

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(upload_path, exist_ok=True)

    # Initialize extensions
    CORS(app, origins=[
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'https://resume-doctor-ai-frontend.onrender.com',
        'https://resume-doctor-ai.onrender.com'
    ], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], supports_credentials=True, allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"])
    jwt = JWTManager(app)

    # JWT error handlers
    import logging
    logger = logging.getLogger("jwt_errors")
    logging.basicConfig(level=logging.INFO)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"JWT expired: header={jwt_header}, payload={jwt_payload}")
        return jsonify({'success': False, 'message': 'Token has expired', 'error': 'token_expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"JWT invalid: error={error}")
        logger.warning(f"JWT_SECRET_KEY being used: {app.config.get('JWT_SECRET_KEY', 'NOT_SET')[:10]}...")
        logger.warning(f"SECRET_KEY being used: {app.config.get('SECRET_KEY', 'NOT_SET')[:10]}...")
        return jsonify({'success': False, 'message': 'Invalid token', 'error': 'invalid_token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning(f"JWT missing: error={error}")
        return jsonify({'success': False, 'message': 'Authorization token required', 'error': 'missing_token'}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        logger.warning(f"JWT revoked: header={jwt_header}, payload={jwt_payload}")
        return jsonify({'success': False, 'message': 'Token has been revoked', 'error': 'token_revoked'}), 401

    # JWT refresh endpoint is now handled in auth_routes.py

    # Initialize database
    try:
        from backend import models
        db = models.db
        db.init_app(app)
        with app.app_context():
            db.create_all()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

    # Register Blueprints with better error handling
    print("🔧 Registering blueprints...")

    try:
        from backend.routes.us05_auth_routes import auth_bp
        app.register_blueprint(auth_bp)
        print("✅ auth_bp registered successfully")
    except Exception as e:
        print(f"❌ auth_bp failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        from backend.routes.us05_upload_routes import upload_bp
        app.register_blueprint(upload_bp)
        print("✅ upload_bp registered successfully")
    except Exception as e:
        print(f"❌ upload_bp failed: {e}")

    try:
        from backend.routes.us05_jd_routes import jd_bp
        app.register_blueprint(jd_bp)
        print("✅ jd_bp registered successfully")
    except Exception as e:
        print(f"❌ jd_bp failed: {e}")

    try:
        from backend.routes.us06_matching_routes import matching_bp
        app.register_blueprint(matching_bp)
        print("✅ matching_bp registered successfully")
    except Exception as e:
        print(f"❌ matching_bp failed: {e}")

    try:
        from backend.routes.us07_suggestions_routes import suggestions_bp
        app.register_blueprint(suggestions_bp)
        print("✅ suggestions_bp registered successfully")
    except Exception as e:
        print(f"❌ suggestions_bp failed: {e}")

    try:
        from backend.routes.us10_history_routes import history_bp
        app.register_blueprint(history_bp)
        print("✅ history_bp registered successfully")
    except Exception as e:
        print(f"❌ history_bp failed: {e}")

    try:
        from backend.routes.us10_account_routes import account_bp
        app.register_blueprint(account_bp)
        print("✅ account_bp registered successfully")
    except Exception as e:
        print(f"❌ account_bp failed: {e}")

    print("✅ Flask app created successfully")

    # Add security and cache-control headers to all responses
    @app.after_request
    def add_security_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Accept'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response

    return app

def main():
    """Main application entry point"""
    print("🚀 Starting Dr. Resume Application")
    print("=" * 52)

    project_root = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(project_root, 'database'), exist_ok=True)
    os.makedirs(os.path.join(project_root, 'uploads'), exist_ok=True)

    app = create_app()

    print("🌐 Starting Flask development server...")
    print("📍 Available at: http://localhost:5000")
    print("🔧 Debug mode: ON")
    print("=" * 52)

    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Dr. Resume...")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()

# Expose app for Gunicorn
app = create_app()
