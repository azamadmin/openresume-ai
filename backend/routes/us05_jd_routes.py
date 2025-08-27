from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, JobDescription
from backend.services.keyword_parser import KeywordParser
from datetime import datetime

# Create blueprint for job description routes
jd_bp = Blueprint('job_descriptions', __name__, url_prefix='/api')

# Initialize keyword parser
keyword_parser = KeywordParser()

@jd_bp.route('/upload_jd', methods=['POST'])
@jwt_required()
def upload_job_description():
    """
    Upload/create a new job description
    Supports both JSON payload and file upload (DOCX)

    For JSON:
    {
        "title": "Software Engineer",
        "company_name": "Tech Corp",
        "job_text": "We are looking for a skilled software engineer..."
    }

    For file upload:
    Content-Type: multipart/form-data
    Fields: title, company_name, job_file (DOCX)
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check if this is a file upload or JSON request
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle file upload
            title = request.form.get('title', '').strip()
            company_name = request.form.get('company_name', '').strip()

            # Check if file is present
            if 'job_file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No job description file provided'
                }), 400

            file = request.files['job_file']

            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No file selected'
                }), 400

            # Check file type
            if not file.filename.lower().endswith('.docx'):
                return jsonify({
                    'success': False,
                    'message': 'Only DOCX files are supported for file upload'
                }), 400

            # Extract text from DOCX file
            try:
                from backend.services.file_parser import FileParser
                success, job_text, error = FileParser.extract_text_from_docx(file)

                if not success:
                    return jsonify({
                        'success': False,
                        'message': f'Could not extract text from the uploaded file: {error}'
                    }), 400

            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Error processing file: {str(e)}'
                }), 400

        else:
            # Handle JSON request
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided'
                }), 400

            # Extract fields
            title = data.get('title', '').strip()
            company_name = data.get('company_name', '').strip()
            job_text = data.get('job_text', '').strip()
        
        # Validate job description
        validation_errors = JobDescription.validate_job_description(title, job_text, company_name)
        
        if validation_errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_errors
            }), 400
        
        # Create job description record
        job_description = JobDescription(
            user_id=current_user_id,
            title=title,
            job_text=job_text,
            company_name=company_name if company_name else None
        )
        
        db.session.add(job_description)
        db.session.commit()

        # US-05: Automatically extract keywords after successful job description creation
        try:
            keywords = keyword_parser.extract_keywords(job_text)
            job_description.set_keywords(
                technical_skills=keywords['technical_skills'],
                soft_skills=keywords['soft_skills'],
                other_keywords=keywords['other_keywords']
            )
            job_description.updated_at = datetime.utcnow()
            db.session.commit()
            current_app.logger.info(f"Keywords automatically extracted for job description {job_description.id}")
        except Exception as keyword_error:
            current_app.logger.error(f"Failed to extract keywords for job description {job_description.id}: {keyword_error}")
            # Don't fail the creation if keyword extraction fails

        # Note: Suggestions are now generated manually by clicking buttons, not automatically

        return jsonify({
            'success': True,
            'message': 'Job description saved successfully',
            'job_description': job_description.to_dict(include_text=True, include_keywords=True),
            'keywords_extracted': job_description.keywords_extracted
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to save job description. Please try again.',
            'error': str(e)
        }), 500

@jd_bp.route('/job_descriptions', methods=['GET'])
@jwt_required()
def get_user_job_descriptions():
    """Get all job descriptions for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        job_descriptions = JobDescription.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).order_by(JobDescription.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'job_descriptions': [jd.to_dict() for jd in job_descriptions],
            'count': len(job_descriptions)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching job descriptions',
            'error': str(e)
        }), 500

@jd_bp.route('/job_descriptions/<int:jd_id>', methods=['GET'])
@jwt_required()
def get_job_description_details(jd_id):
    """Get detailed information about a specific job description"""
    try:
        current_user_id = get_jwt_identity()
        
        job_description = JobDescription.query.filter_by(
            id=jd_id,
            user_id=current_user_id,
            is_active=True
        ).first()
        
        if not job_description:
            return jsonify({
                'success': False,
                'message': 'Job description not found'
            }), 404
        
        return jsonify({
            'success': True,
            'job_description': job_description.to_dict(include_text=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching job description details',
            'error': str(e)
        }), 500

@jd_bp.route('/job_descriptions/<int:jd_id>', methods=['PUT'])
@jwt_required()
def update_job_description(jd_id):
    """Update a job description"""
    try:
        current_user_id = get_jwt_identity()
        
        job_description = JobDescription.query.filter_by(
            id=jd_id,
            user_id=current_user_id,
            is_active=True
        ).first()
        
        if not job_description:
            return jsonify({
                'success': False,
                'message': 'Job description not found'
            }), 404
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Extract fields
        title = data.get('title', job_description.title).strip()
        company_name = data.get('company_name', job_description.company_name or '').strip()
        job_text = data.get('job_text', job_description.job_text).strip()
        
        # Validate job description
        validation_errors = JobDescription.validate_job_description(title, job_text, company_name)
        
        if validation_errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_errors
            }), 400
        
        # Update job description
        job_description.title = title
        job_description.company_name = company_name if company_name else None
        job_description.job_text = job_text
        job_description.update_counts()
        job_description.updated_at = datetime.utcnow()

        # US-05: Re-extract keywords if job text changed
        try:
            keywords = keyword_parser.extract_keywords(job_text)
            job_description.set_keywords(
                technical_skills=keywords['technical_skills'],
                soft_skills=keywords['soft_skills'],
                other_keywords=keywords['other_keywords']
            )
            current_app.logger.info(f"Keywords re-extracted for updated job description {job_description.id}")
        except Exception as keyword_error:
            current_app.logger.error(f"Failed to re-extract keywords for job description {job_description.id}: {keyword_error}")
            # Don't fail the update if keyword extraction fails

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Job description updated successfully',
            'job_description': job_description.to_dict(include_text=True, include_keywords=True),
            'keywords_extracted': job_description.keywords_extracted
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error updating job description',
            'error': str(e)
        }), 500

@jd_bp.route('/job_descriptions/<int:jd_id>', methods=['DELETE'])
@jwt_required()
def delete_job_description(jd_id):
    """Delete a job description"""
    try:
        current_user_id = get_jwt_identity()
        
        job_description = JobDescription.query.filter_by(
            id=jd_id,
            user_id=current_user_id
        ).first()
        
        if not job_description:
            return jsonify({
                'success': False,
                'message': 'Job description not found'
            }), 404
        
        # Delete database record
        db.session.delete(job_description)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job description deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting job description',
            'error': str(e)
        }), 500

@jd_bp.route('/job_descriptions/<int:jd_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_job_description(jd_id):
    """Create a copy of an existing job description"""
    try:
        current_user_id = get_jwt_identity()
        
        original_jd = JobDescription.query.filter_by(
            id=jd_id,
            user_id=current_user_id,
            is_active=True
        ).first()
        
        if not original_jd:
            return jsonify({
                'success': False,
                'message': 'Job description not found'
            }), 404
        
        # Create duplicate with modified title
        duplicate_jd = JobDescription(
            user_id=current_user_id,
            title=f"{original_jd.title} (Copy)",
            job_text=original_jd.job_text,
            company_name=original_jd.company_name
        )
        
        db.session.add(duplicate_jd)
        db.session.commit()

        # US-05: Automatically extract keywords for duplicated job description
        try:
            keywords = keyword_parser.extract_keywords(duplicate_jd.job_text)
            duplicate_jd.set_keywords(
                technical_skills=keywords['technical_skills'],
                soft_skills=keywords['soft_skills'],
                other_keywords=keywords['other_keywords']
            )
            duplicate_jd.updated_at = datetime.utcnow()
            db.session.commit()
            current_app.logger.info(f"Keywords automatically extracted for duplicated job description {duplicate_jd.id}")
        except Exception as keyword_error:
            current_app.logger.error(f"Failed to extract keywords for duplicated job description {duplicate_jd.id}: {keyword_error}")
            # Don't fail the duplication if keyword extraction fails

        return jsonify({
            'success': True,
            'message': 'Job description duplicated successfully',
            'job_description': duplicate_jd.to_dict(include_text=True, include_keywords=True),
            'keywords_extracted': duplicate_jd.keywords_extracted
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error duplicating job description',
            'error': str(e)
        }), 500
