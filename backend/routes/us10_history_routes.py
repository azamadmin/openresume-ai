"""
US-10: Dashboard & Scan History Routes
API endpoints for retrieving user's scan history, statistics, and dashboard data
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Resume, JobDescription, MatchScore
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import json

# Create blueprint for history routes
history_bp = Blueprint('history', __name__, url_prefix='/api')


@history_bp.route('/history', methods=['GET'])
@jwt_required()
def get_scan_history():
    """
    Get user's complete scan history with pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 50)
    - sort_by: Sort field (default: 'created_at')
    - sort_order: Sort order 'asc' or 'desc' (default: 'desc')
    - filter_score: Filter by score range 'excellent', 'good', 'fair', 'poor'
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
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        filter_score = request.args.get('filter_score', None)
        
        # Build query
        query = db.session.query(MatchScore).filter_by(user_id=current_user_id)
        
        # Apply score filter
        if filter_score:
            if filter_score == 'excellent':
                query = query.filter(MatchScore.overall_score >= 80)
            elif filter_score == 'good':
                query = query.filter(MatchScore.overall_score >= 60, MatchScore.overall_score < 80)
            elif filter_score == 'fair':
                query = query.filter(MatchScore.overall_score >= 40, MatchScore.overall_score < 60)
            elif filter_score == 'poor':
                query = query.filter(MatchScore.overall_score < 40)
        
        # Apply sorting
        if hasattr(MatchScore, sort_by):
            sort_column = getattr(MatchScore, sort_by)
            if sort_order == 'asc':
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(MatchScore.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format scan history
        scan_history = []
        for match in pagination.items:
            # Get resume and job description details
            resume = Resume.query.get(match.resume_id)
            job_description = JobDescription.query.get(match.job_description_id)
            
            scan_data = {
                'id': match.id,
                'match_score': round(match.overall_score, 2),
                'score_category': match.get_score_category(),
                'technical_score': round(match.technical_score, 2),
                'soft_skills_score': round(match.soft_skills_score, 2),
                'other_keywords_score': round(match.other_keywords_score, 2),
                'matched_keywords': match.matched_keywords,
                'total_resume_keywords': match.total_resume_keywords,
                'total_jd_keywords': match.total_jd_keywords,
                'algorithm_used': match.algorithm_used,
                'created_at': match.created_at.isoformat() if match.created_at else None,
                'resume': {
                    'id': resume.id if resume else None,
                    'title': resume.title if resume else 'Untitled Resume',
                    'filename': resume.original_filename if resume else 'Unknown',
                    'upload_date': resume.created_at.isoformat() if resume and resume.created_at else None
                },
                'job_description': {
                    'id': job_description.id if job_description else None,
                    'title': job_description.title if job_description else 'Untitled Job',
                    'company_name': job_description.company_name if job_description else 'Unknown Company',
                    'created_date': job_description.created_at.isoformat() if job_description and job_description.created_at else None
                },
                'suggestions_available': True,  # All scans can generate suggestions
                'premium_suggestions_available': True  # Premium available for all users
            }
            scan_history.append(scan_data)
        
        return jsonify({
            'success': True,
            'scan_history': scan_history,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'sort_by': sort_by,
                'sort_order': sort_order,
                'filter_score': filter_score
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting scan history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve scan history',
            'error': str(e)
        }), 500


@history_bp.route('/dashboard_stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """
    Get dashboard statistics for the user
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
        
        # Get basic counts
        total_resumes = Resume.query.filter_by(user_id=current_user_id, is_active=True).count()
        total_job_descriptions = JobDescription.query.filter_by(user_id=current_user_id, is_active=True).count()
        total_scans = MatchScore.query.filter_by(user_id=current_user_id).count()
        
        # Get score statistics
        score_stats = db.session.query(
            func.avg(MatchScore.overall_score).label('avg_score'),
            func.max(MatchScore.overall_score).label('max_score'),
            func.min(MatchScore.overall_score).label('min_score')
        ).filter_by(user_id=current_user_id).first()
        
        # Get score distribution
        excellent_count = MatchScore.query.filter_by(user_id=current_user_id).filter(MatchScore.overall_score >= 80).count()
        good_count = MatchScore.query.filter_by(user_id=current_user_id).filter(MatchScore.overall_score >= 60, MatchScore.overall_score < 80).count()
        fair_count = MatchScore.query.filter_by(user_id=current_user_id).filter(MatchScore.overall_score >= 40, MatchScore.overall_score < 60).count()
        poor_count = MatchScore.query.filter_by(user_id=current_user_id).filter(MatchScore.overall_score < 40).count()
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_scans = MatchScore.query.filter_by(user_id=current_user_id).filter(MatchScore.created_at >= seven_days_ago).count()
        
        # Get top performing resume
        top_resume_query = db.session.query(
            Resume.id,
            Resume.title,
            Resume.original_filename,
            func.avg(MatchScore.overall_score).label('avg_score'),
            func.count(MatchScore.id).label('scan_count')
        ).join(MatchScore).filter(
            Resume.user_id == current_user_id,
            Resume.is_active == True
        ).group_by(Resume.id).order_by(func.avg(MatchScore.overall_score).desc()).first()
        
        top_resume = None
        if top_resume_query:
            top_resume = {
                'id': top_resume_query.id,
                'title': top_resume_query.title or 'Untitled Resume',
                'filename': top_resume_query.original_filename,
                'average_score': round(top_resume_query.avg_score, 2),
                'scan_count': top_resume_query.scan_count
            }
        
        return jsonify({
            'success': True,
            'stats': {
                'total_resumes': total_resumes,
                'total_job_descriptions': total_job_descriptions,
                'total_scans': total_scans,
                'recent_scans_7_days': recent_scans,
                'score_statistics': {
                    'average_score': round(score_stats.avg_score, 2) if score_stats.avg_score else 0,
                    'highest_score': round(score_stats.max_score, 2) if score_stats.max_score else 0,
                    'lowest_score': round(score_stats.min_score, 2) if score_stats.min_score else 0
                },
                'score_distribution': {
                    'excellent': excellent_count,  # 80-100%
                    'good': good_count,           # 60-79%
                    'fair': fair_count,           # 40-59%
                    'poor': poor_count            # 0-39%
                },
                'top_performing_resume': top_resume
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve dashboard statistics',
            'error': str(e)
        }), 500


@history_bp.route('/recent_activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """
    Get recent activity for dashboard
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
        
        # Get recent scans (last 5)
        recent_scans = db.session.query(MatchScore).filter_by(
            user_id=current_user_id
        ).order_by(MatchScore.created_at.desc()).limit(5).all()
        
        # Get recent resumes (last 3)
        recent_resumes = Resume.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).order_by(Resume.created_at.desc()).limit(3).all()
        
        # Get recent job descriptions (last 3)
        recent_jds = JobDescription.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).order_by(JobDescription.created_at.desc()).limit(3).all()
        
        # Format recent scans
        formatted_scans = []
        for scan in recent_scans:
            resume = Resume.query.get(scan.resume_id)
            job_description = JobDescription.query.get(scan.job_description_id)
            
            formatted_scans.append({
                'id': scan.id,
                'match_score': round(scan.overall_score, 2),
                'score_category': scan.get_score_category(),
                'resume_title': resume.title if resume else 'Untitled Resume',
                'job_title': job_description.title if job_description else 'Untitled Job',
                'company_name': job_description.company_name if job_description else 'Unknown Company',
                'created_at': scan.created_at.isoformat() if scan.created_at else None
            })
        
        # Format recent resumes
        formatted_resumes = []
        for resume in recent_resumes:
            formatted_resumes.append({
                'id': resume.id,
                'title': resume.title or 'Untitled Resume',
                'filename': resume.original_filename,
                'keywords_extracted': resume.keywords_extracted,
                'keyword_count': resume.keyword_count,
                'created_at': resume.created_at.isoformat() if resume.created_at else None
            })
        
        # Format recent job descriptions
        formatted_jds = []
        for jd in recent_jds:
            formatted_jds.append({
                'id': jd.id,
                'title': jd.title,
                'company_name': jd.company_name,
                'keywords_extracted': jd.keywords_extracted,
                'keyword_count': jd.keyword_count,
                'created_at': jd.created_at.isoformat() if jd.created_at else None
            })
        
        return jsonify({
            'success': True,
            'recent_activity': {
                'recent_scans': formatted_scans,
                'recent_resumes': formatted_resumes,
                'recent_job_descriptions': formatted_jds
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting recent activity: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve recent activity',
            'error': str(e)
        }), 500
