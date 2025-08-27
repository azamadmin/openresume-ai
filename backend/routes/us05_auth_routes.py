from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from backend.models import db, User
import re

# Create blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Test route to verify blueprint is working
@auth_bp.route('/auth-test', methods=['GET'])
def auth_test():
    """Test route to verify auth blueprint is registered"""
    return jsonify({'success': True, 'message': 'Auth blueprint is working!'}), 200

# Refresh access token endpoint
@auth_bp.route('/refresh', methods=['POST', 'OPTIONS'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))  # Convert string back to int
        if not user or not user.is_active:
            return jsonify({'success': False, 'message': 'User not found or inactive'}), 404
        # Create a new access token
        access_token = create_access_token(
            identity=str(user.id),  # Convert to string for consistency
            additional_claims={
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        )
        return jsonify({'success': True, 'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Token refresh failed', 'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (same as US-03)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        errors = []
        
        if not first_name: errors.append('First name is required')
        if not last_name: errors.append('Last name is required')
        if not email: errors.append('Email is required')
        if not password: errors.append('Password is required')
        if not confirm_password: errors.append('Password confirmation is required')
        
        if email and not User.validate_email(email):
            errors.append('Invalid email format')
        
        if password:
            is_valid, message = User.validate_password(password)
            if not is_valid: errors.append(message)
        
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match')
        
        if email and User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if errors:
            return jsonify({'success': False, 'message': 'Validation failed', 'errors': errors}), 400
        
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)

        # Generate email verification token
        verification_token = new_user.generate_email_verification_token()

        db.session.add(new_user)
        db.session.commit()

        # Send verification email (for now, just return the token in response)
        # In production, you would send this via email service

        return jsonify({
            'success': True,
            'message': 'Account created successfully! Please check your email for verification link.',
            'user': new_user.to_dict(),
            'verification_token': verification_token  # Remove this in production
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Registration failed. Please try again.', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens (same as US-03)"""
    try:
        print("🔐 Login attempt received")
        data = request.get_json()
        print(f"📝 Request data: {data}")

        if not data:
            print("❌ No data provided")
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        print(f"📧 Email: {email}, Password length: {len(password) if password else 0}")

        errors = []
        if not email: errors.append('Email is required')
        if not password: errors.append('Password is required')

        if errors:
            print(f"❌ Validation errors: {errors}")
            return jsonify({'success': False, 'message': 'Validation failed', 'errors': errors}), 400

        user = User.query.filter_by(email=email).first()
        print(f"👤 User found: {user is not None}")

        if not user:
            print("❌ User not found")
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        if not user.is_active:
            print("❌ User not active")
            return jsonify({'success': False, 'message': 'Account is deactivated. Please contact support.'}), 401

        password_check = user.check_password(password)
        print(f"🔑 Password check result: {password_check}")

        if not password_check:
            print("❌ Password check failed")
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        print("✅ Login successful, generating tokens...")
        user.update_last_login()
        tokens = user.generate_tokens()
        print(f"🎫 Tokens generated: {tokens is not None}")

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'tokens': tokens
        }), 200

    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Login failed. Please try again.', 'error': str(e)}), 500

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """Check if email is already registered"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        user_exists = User.query.filter_by(email=email).first() is not None
        
        return jsonify({'success': True, 'exists': user_exists}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error checking email', 'error': str(e)}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        token = data.get('token', '').strip()

        if not email or not token:
            return jsonify({'success': False, 'message': 'Email and token are required'}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if user.is_email_verified:
            return jsonify({'success': True, 'message': 'Email already verified'}), 200

        if user.is_verification_token_expired():
            return jsonify({'success': False, 'message': 'Verification token has expired'}), 400

        if user.verify_email(token):
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Email verified successfully! You can now log in.',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid verification token'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Email verification failed', 'error': str(e)}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification token"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if user.is_email_verified:
            return jsonify({'success': True, 'message': 'Email already verified'}), 200

        # Generate new verification token
        verification_token = user.generate_email_verification_token()
        db.session.commit()

        # Send verification email (for now, just return the token in response)
        # In production, you would send this via email service

        return jsonify({
            'success': True,
            'message': 'Verification email sent! Please check your email.',
            'verification_token': verification_token  # Remove this in production
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to resend verification email', 'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile (protected route)"""
    try:
        # Get current user from JWT
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))  # Convert string back to int
        if not user or not user.is_active:
            return jsonify({'success': False, 'message': 'User not found or inactive'}), 401
        return jsonify({'success': True, 'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error fetching profile', 'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    try:
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Logout failed', 'error': str(e)}), 500
