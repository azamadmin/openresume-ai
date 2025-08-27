"""
US-07: Basic & Premium Suggestions Routes
API endpoints for generating keyword suggestions and recommendations
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, Resume, JobDescription, MatchScore, Suggestion
from backend.middleware.auth_middleware import protected_route, premium_route, monitored_route
from backend.services.dynamic_suggestions_service import DynamicSuggestionsService
try:
    from backend.services.premium_suggestions_service import PremiumSuggestionsService
    premium_service = PremiumSuggestionsService()
except ImportError:
    premium_service = None
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for suggestions routes
suggestions_bp = Blueprint('suggestions', __name__, url_prefix='/api')

# Initialize services
dynamic_suggestions_service = DynamicSuggestionsService()


@suggestions_bp.route('/basic_suggestions', methods=['POST'])
@protected_route
def generate_basic_suggestions():
    """
    Generate basic suggestions by identifying missing keywords
    
    Expected JSON:
    {
        "resume_id": 1,
        "job_description_id": 2
    }
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        resume_id = data.get('resume_id')
        job_description_id = data.get('job_description_id')
        
        if not resume_id or not job_description_id:
            return jsonify({
                'success': False,
                'message': 'resume_id and job_description_id are required'
            }), 400
        
        # Validate that resume and job description belong to user
        resume = Resume.query.filter_by(
            id=resume_id,
            user_id=user.id,
            is_active=True
        ).first()
        
        job_description = JobDescription.query.filter_by(
            id=job_description_id,
            user_id=user.id,
            is_active=True
        ).first()
        
        if not resume:
            return jsonify({
                'success': False,
                'message': 'Resume not found or access denied'
            }), 404
        
        if not job_description:
            return jsonify({
                'success': False,
                'message': 'Job description not found or access denied'
            }), 404
        
        # Check if keywords are extracted
        if not resume.keywords_extracted:
            return jsonify({
                'success': False,
                'message': 'Resume keywords not extracted yet. Please extract keywords first.'
            }), 400
        
        if not job_description.keywords_extracted:
            return jsonify({
                'success': False,
                'message': 'Job description keywords not extracted yet. Please extract keywords first.'
            }), 400
        
        # Generate basic suggestions using the dynamic service
        suggestions_result = dynamic_suggestions_service.generate_basic_suggestions(
            resume_id=resume_id,
            job_description_id=job_description_id,
            user_id=user.id
        )

        if not suggestions_result['success']:
            return jsonify({
                'success': False,
                'message': suggestions_result.get('message', 'Failed to generate suggestions')
            }), 500

        logger.info(f"Generated basic suggestions for user {user.id}, resume {resume_id}, JD {job_description_id}")

        return jsonify({
            'success': True,
            'message': 'Basic suggestions generated successfully',
            'suggestions': suggestions_result['suggestions'],
            'total_suggestions': suggestions_result.get('total_suggestions', len(suggestions_result.get('suggestions', []))),
            'matching_score': suggestions_result.get('matching_score', {}),
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_basic_suggestions: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@suggestions_bp.route('/premium_suggestions', methods=['POST'])
@protected_route
@monitored_route
def generate_premium_suggestions():
    """
    Generate premium AI-powered suggestions using OpenAI API
    
    Expected JSON:
    {
        "resume_id": 1,
        "job_description_id": 2,
        "suggestion_type": "comprehensive" // optional: "comprehensive", "quick", "targeted"
    }
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check if user has premium access (you can implement premium user logic here)
        # For now, we'll allow all users to test
        # if not user.is_premium:
        #     return jsonify({
        #         'success': False,
        #         'message': 'Premium subscription required',
        #         'upgrade_required': True
        #     }), 403
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        resume_id = data.get('resume_id')
        job_description_id = data.get('job_description_id')
        
        if not resume_id or not job_description_id:
            return jsonify({
                'success': False,
                'message': 'resume_id and job_description_id are required'
            }), 400
        
        # Validate that resume and job description belong to user
        resume = Resume.query.filter_by(
            id=resume_id,
            user_id=user.id,
            is_active=True
        ).first()
        
        job_description = JobDescription.query.filter_by(
            id=job_description_id,
            user_id=user.id,
            is_active=True
        ).first()
        
        if not resume:
            return jsonify({
                'success': False,
                'message': 'Resume not found or access denied'
            }), 404
        
        if not job_description:
            return jsonify({
                'success': False,
                'message': 'Job description not found or access denied'
            }), 404
        
        # Check if keywords are extracted
        if not resume.keywords_extracted:
            return jsonify({
                'success': False,
                'message': 'Resume keywords not extracted yet. Please extract keywords first.'
            }), 400
        
        if not job_description.keywords_extracted:
            return jsonify({
                'success': False,
                'message': 'Job description keywords not extracted yet. Please extract keywords first.'
            }), 400
        
        # Generate premium suggestions using the dynamic service
        premium_result = dynamic_suggestions_service.generate_premium_suggestions(
            resume_id=resume_id,
            job_description_id=job_description_id,
            user_id=user.id
        )

        if not premium_result['success']:
            return jsonify({
                'success': False,
                'message': premium_result.get('message', 'Failed to generate premium suggestions')
            }), 500

        logger.info(f"Generated premium suggestions for user {user.id}, resume {resume_id}, JD {job_description_id}")

        return jsonify({
            'success': True,
            'message': 'Premium suggestions generated successfully',
            'suggestions': premium_result['suggestions'],
            'total_suggestions': premium_result.get('total_suggestions', len(premium_result.get('suggestions', []))),
            'matching_score': premium_result.get('matching_score', {}),
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_premium_suggestions: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@suggestions_bp.route('/suggestion_history', methods=['GET'])
@jwt_required()
def get_suggestion_history():
    """
    Get user's suggestion history
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50
        
        # Get suggestion history from database directly
        history = []
        try:
            suggestions = Suggestion.query.filter_by(user_id=user.id).order_by(
                Suggestion.created_at.desc()
            ).limit(limit).all()

            for suggestion in suggestions:
                history.append({
                    'id': suggestion.id,
                    'resume_id': suggestion.resume_id,
                    'job_description_id': suggestion.job_description_id,
                    'suggestion_type': suggestion.suggestion_type,
                    'created_at': suggestion.created_at.isoformat(),
                    'match_score': suggestion.match_score
                })
        except Exception as e:
            logger.error(f"Error getting suggestion history: {str(e)}")
        
        return jsonify({
            'success': True,
            'suggestion_history': history,
            'total_count': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_suggestion_history: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@suggestions_bp.route('/available_suggestions', methods=['GET'])
@jwt_required()
def get_available_suggestions():
    """
    Get available resume-JD combinations for generating suggestions
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get all active resumes (prioritize those with extracted keywords)
        resumes = Resume.query.filter_by(
            user_id=user.id,
            is_active=True
        ).all()

        # Get all active job descriptions (prioritize those with extracted keywords)
        job_descriptions = JobDescription.query.filter_by(
            user_id=user.id,
            is_active=True
        ).all()
        
        resume_list = []
        for resume in resumes:
            resume_list.append({
                'id': resume.id,
                'original_filename': resume.original_filename,
                'title': resume.title,
                'keyword_count': resume.keyword_count,
                'keywords_extracted': resume.keywords_extracted,
                'upload_date': resume.created_at.isoformat()
            })
        
        jd_list = []
        for jd in job_descriptions:
            jd_list.append({
                'id': jd.id,
                'title': jd.title,
                'company_name': jd.company_name,
                'keyword_count': jd.keyword_count,
                'keywords_extracted': jd.keywords_extracted,
                'created_date': jd.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'resumes': resume_list,
            'job_descriptions': jd_list,
            'total_combinations': len(resume_list) * len(jd_list)
        }), 200

    except Exception as e:
        logger.error(f"Error in get_available_suggestions: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@suggestions_bp.route('/latest_suggestions', methods=['GET'])
@protected_route
def get_latest_suggestions():
    """
    Get the latest suggestions for the user's most recent resume and job description
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        # Get most recent resume and job description with extracted keywords
        latest_resume = Resume.query.filter_by(
            user_id=user.id,
            is_active=True,
            keywords_extracted=True
        ).order_by(Resume.created_at.desc()).first()

        latest_jd = JobDescription.query.filter_by(
            user_id=user.id,
            is_active=True,
            keywords_extracted=True
        ).order_by(JobDescription.created_at.desc()).first()

        if not latest_resume:
            return jsonify({
                'success': False,
                'message': 'No processed resume found. Please upload a resume first.',
                'suggestions': [],
                'has_resume': False,
                'has_job_description': latest_jd is not None
            }), 200

        if not latest_jd:
            return jsonify({
                'success': False,
                'message': 'No job description found. Please upload a job description to get suggestions.',
                'suggestions': [],
                'has_resume': True,
                'has_job_description': False
            }), 200

        # Generate basic suggestions for the latest combination
        logger.info(f"Generating suggestions for resume {latest_resume.id} vs JD {latest_jd.id}")

        suggestions_result = dynamic_suggestions_service.generate_basic_suggestions(
            resume_id=latest_resume.id,
            job_description_id=latest_jd.id,
            user_id=user.id
        )

        logger.info(f"Suggestions result: success={suggestions_result.get('success')}, count={len(suggestions_result.get('suggestions', []))}")

        if not suggestions_result['success']:
            logger.error(f"Suggestions generation failed: {suggestions_result.get('message')}")
            return jsonify({
                'success': False,
                'message': f"Failed to generate suggestions: {suggestions_result.get('message', 'Unknown error')}",
                'suggestions': [],
                'has_resume': True,
                'has_job_description': True
            }), 500

        return jsonify({
            'success': True,
            'message': 'Latest suggestions retrieved successfully',
            'suggestions': suggestions_result['suggestions'],
            'total_suggestions': len(suggestions_result.get('suggestions', [])),
            'matching_score': suggestions_result.get('matching_score', {}),
            'resume': {
                'id': latest_resume.id,
                'title': latest_resume.title,
                'filename': latest_resume.original_filename
            },
            'job_description': {
                'id': latest_jd.id,
                'title': latest_jd.title,
                'company': latest_jd.company_name
            },
            'has_resume': True,
            'has_job_description': True,
            'generated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in get_latest_suggestions: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
