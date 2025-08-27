"""
US-10: Account Settings Routes
API endpoints for updating user account information
"""

from flask import Blueprint, request, jsonify, current_app
from backend.models import db, User
from backend.middleware.auth_middleware import protected_route, monitored_route
from werkzeug.security import check_password_hash
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint for account routes
account_bp = Blueprint('account', __name__, url_prefix='/api')


@account_bp.route('/update_account', methods=['PUT'])
@protected_route
@monitored_route
def update_account():
    """
    Update user account information
    
    Expected JSON:
    {
        "email": "new@example.com",  // optional
        "password": "newpassword",   // optional
        "current_password": "currentpassword",  // required for critical changes
        "first_name": "New Name",    // optional
        "last_name": "New Last"      // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Get current user from middleware
        user = request.current_user
        
        # Track what's being updated
        updates = {}
        requires_password_verification = False
        
        # Check if critical changes are being made
        if 'email' in data or 'password' in data:
            requires_password_verification = True
        
        # Verify current password for critical changes
        if requires_password_verification:
            current_password = data.get('current_password')
            
            if not current_password:
                return jsonify({
                    'success': False,
                    'message': 'Current password required for email or password changes'
                }), 400
            
            if not user.check_password(current_password):
                return jsonify({
                    'success': False,
                    'message': 'Current password is incorrect'
                }), 401
        
        # Update email
        if 'email' in data:
            new_email = data['email'].strip().lower()
            
            # Validate email format
            if not User.validate_email(new_email):
                return jsonify({
                    'success': False,
                    'message': 'Invalid email format'
                }), 400
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({
                    'success': False,
                    'message': 'Email already in use'
                }), 409
            
            updates['email'] = new_email
            user.email = new_email
        
        # Update password
        if 'password' in data:
            new_password = data['password']
            
            # Validate password
            is_valid, message = User.validate_password(new_password)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
            # Check if new password is different from current
            if user.check_password(new_password):
                return jsonify({
                    'success': False,
                    'message': 'New password must be different from current password'
                }), 400
            
            updates['password'] = 'Updated'
            user.set_password(new_password)
        
        # Update first name
        if 'first_name' in data:
            first_name = data['first_name'].strip()
            
            if not first_name:
                return jsonify({
                    'success': False,
                    'message': 'First name cannot be empty'
                }), 400
            
            updates['first_name'] = first_name
            user.first_name = first_name
        
        # Update last name
        if 'last_name' in data:
            last_name = data['last_name'].strip()
            
            if not last_name:
                return jsonify({
                    'success': False,
                    'message': 'Last name cannot be empty'
                }), 400
            
            updates['last_name'] = last_name
            user.last_name = last_name
        
        # Check if any updates were made
        if not updates:
            return jsonify({
                'success': False,
                'message': 'No valid updates provided'
            }), 400
        
        # Save changes
        user.updated_at = db.func.now()
        db.session.commit()
        
        logger.info(f"Account updated for user {user.id}: {list(updates.keys())}")
        
        return jsonify({
            'success': True,
            'message': 'Account updated successfully',
            'updated_fields': list(updates.keys()),
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating account: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to update account',
            'error': str(e)
        }), 500


@account_bp.route('/change_password', methods=['PUT'])
@protected_route
@monitored_route
def change_password():
    """
    Dedicated endpoint for password changes with enhanced security
    
    Expected JSON:
    {
        "current_password": "currentpassword",
        "new_password": "newpassword",
        "confirm_password": "newpassword"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Get current user from middleware
        user = request.current_user
        
        # Validate required fields
        required_fields = ['current_password', 'new_password', 'confirm_password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 401
        
        # Check if new password matches confirmation
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'New password and confirmation do not match'
            }), 400
        
        # Validate new password
        is_valid, message = User.validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Check if new password is different from current
        if user.check_password(new_password):
            return jsonify({
                'success': False,
                'message': 'New password must be different from current password'
            }), 400
        
        # Update password
        user.set_password(new_password)
        user.updated_at = db.func.now()
        db.session.commit()
        
        logger.info(f"Password changed for user {user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing password: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to change password',
            'error': str(e)
        }), 500


@account_bp.route('/account_info', methods=['GET'])
@protected_route
def get_account_info():
    """
    Get current user account information
    """
    try:
        user = request.current_user
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get account information',
            'error': str(e)
        }), 500


@account_bp.route('/delete_account', methods=['DELETE'])
@protected_route
@monitored_route
def delete_account():
    """
    Delete user account (soft delete - deactivate)
    
    Expected JSON:
    {
        "password": "currentpassword",
        "confirm_deletion": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        user = request.current_user
        
        # Verify password
        password = data.get('password')
        if not password:
            return jsonify({
                'success': False,
                'message': 'Password required for account deletion'
            }), 400
        
        if not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Password is incorrect'
            }), 401
        
        # Confirm deletion intent
        if not data.get('confirm_deletion'):
            return jsonify({
                'success': False,
                'message': 'Account deletion must be confirmed'
            }), 400
        
        # Soft delete - deactivate account
        user.is_active = False
        user.updated_at = db.func.now()
        db.session.commit()
        
        logger.warning(f"Account deactivated for user {user.id} ({user.email})")
        
        return jsonify({
            'success': True,
            'message': 'Account has been deactivated'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting account: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to delete account',
            'error': str(e)
        }), 500
