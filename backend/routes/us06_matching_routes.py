"""
US-06: Matching Score Routes
API endpoints for calculating and retrieving resume-job description matching scores
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Resume, JobDescription, MatchScore
from backend.services.matching_service import MatchingService
from datetime import datetime

# Create blueprint for matching routes
matching_bp = Blueprint('matching', __name__, url_prefix='/api')

# Initialize matching service
matching_service = MatchingService()


@matching_bp.route('/calculate_match', methods=['POST'])
@jwt_required()
def calculate_match_score():
    """
    Calculate matching score between resume and job description
    Expected JSON payload:
    {
        "resume_id": 1,
        "job_description_id": 2
    }
    """
    try:
        current_user_id = get_jwt_identity()
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
                'message': 'Both resume_id and job_description_id are required'
            }), 400
        
        # Calculate match score
        result = matching_service.calculate_match_score(
            resume_id=resume_id,
            job_description_id=job_description_id,
            user_id=current_user_id
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': 'Failed to calculate match score',
                'error': result.get('error')
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Match score calculated successfully',
            'match_score': result['match_score'],
            'detailed_scores': result['detailed_scores'],
            'keyword_analysis': result['keyword_analysis']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in calculate_match_score: {e}")
        return jsonify({
            'success': False,
            'message': 'Error calculating match score',
            'error': str(e)
        }), 500






