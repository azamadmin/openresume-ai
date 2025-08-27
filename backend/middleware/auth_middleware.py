"""
US-10: Authentication and Authorization Middleware
Enhanced JWT protection with role-based access control
"""

from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from backend.models import User, db
import logging

# Set up logging
logger = logging.getLogger(__name__)

def enhanced_jwt_required(optional=False, premium_required=False):
    """
    Enhanced JWT decorator with role-based access control
    
    Args:
        optional: If True, allows access without token but populates user info if available
        premium_required: If True, requires user to have premium role
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verify JWT token
                if optional:
                    # For optional routes, try to verify but don't fail if no token
                    try:
                        verify_jwt_in_request(optional=True)
                        current_user_id = get_jwt_identity()
                        current_user = None
                        
                        if current_user_id:
                            current_user = User.query.get(current_user_id)
                            if not current_user or not current_user.is_active:
                                current_user = None
                                current_user_id = None
                        
                        # Add user info to request context
                        request.current_user_id = current_user_id
                        request.current_user = current_user
                        
                    except Exception as e:
                        logger.warning(f"Optional JWT verification failed: {e}")
                        request.current_user_id = None
                        request.current_user = None
                else:
                    # For required routes, strict verification
                    verify_jwt_in_request()
                    current_user_id = get_jwt_identity()
                    
                    if not current_user_id:
                        return jsonify({
                            'success': False,
                            'message': 'Authentication required',
                            'error': 'missing_token'
                        }), 401
                    
                    # Get user from database
                    current_user = User.query.get(current_user_id)
                    
                    if not current_user:
                        return jsonify({
                            'success': False,
                            'message': 'User not found',
                            'error': 'invalid_user'
                        }), 401
                    
                    if not current_user.is_active:
                        return jsonify({
                            'success': False,
                            'message': 'Account is deactivated',
                            'error': 'account_deactivated'
                        }), 401
                    
                    # Add user info to request context
                    request.current_user_id = current_user_id
                    request.current_user = current_user
                    
                    # Check premium access if required
                    if premium_required:
                        if not hasattr(current_user, 'role') or current_user.role != 'premium':
                            return jsonify({
                                'success': False,
                                'message': 'Premium subscription required',
                                'error': 'premium_required',
                                'upgrade_url': '/upgrade'
                            }), 403
                
                # Call the original function
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Authentication error in {f.__name__}: {e}")
                
                # Handle different JWT errors
                error_message = str(e).lower()
                
                if 'expired' in error_message:
                    return jsonify({
                        'success': False,
                        'message': 'Token has expired',
                        'error': 'token_expired'
                    }), 401
                elif 'invalid' in error_message or 'decode' in error_message:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid token',
                        'error': 'invalid_token'
                    }), 401
                elif 'missing' in error_message:
                    return jsonify({
                        'success': False,
                        'message': 'Authentication token required',
                        'error': 'missing_token'
                    }), 401
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Authentication failed',
                        'error': 'auth_failed'
                    }), 401
        
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator for admin-only routes
    """
    @wraps(f)
    @enhanced_jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = request.current_user
        
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Administrator access required',
                'error': 'admin_required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit_check(max_requests=100, window_minutes=60):
    """
    Simple rate limiting decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For now, just log the request
            # In production, implement proper rate limiting with Redis
            logger.info(f"API call to {f.__name__} from user {getattr(request, 'current_user_id', 'anonymous')}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_api_access(f):
    """
    Decorator to log API access for security monitoring
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(request, 'current_user_id', 'anonymous')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        logger.info(f"API Access: {f.__name__} | User: {user_id} | IP: {ip_address} | UA: {user_agent}")
        
        try:
            result = f(*args, **kwargs)
            logger.info(f"API Success: {f.__name__} | User: {user_id}")
            return result
        except Exception as e:
            logger.error(f"API Error: {f.__name__} | User: {user_id} | Error: {e}")
            raise
    
    return decorated_function

# Convenience decorators for common use cases
def public_route(f):
    """Public route - no authentication required"""
    return enhanced_jwt_required(optional=True)(f)

def protected_route(f):
    """Protected route - authentication required"""
    return enhanced_jwt_required()(f)

def premium_route(f):
    """Premium route - authentication + premium role required"""
    return enhanced_jwt_required(premium_required=True)(f)

def monitored_route(f):
    """Route with access logging"""
    return log_api_access(f)

def rate_limited_route(max_requests=100, window_minutes=60):
    """Route with rate limiting"""
    def decorator(f):
        return rate_limit_check(max_requests, window_minutes)(f)
    return decorator
