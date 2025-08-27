"""
US-06: Matching Score Service
Implements keyword matching algorithms to compare resumes with job descriptions
"""

import logging
from typing import Dict, List, Tuple, Set
from backend.models import db, Resume, JobDescription, MatchScore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingService:
    """
    Service for calculating matching scores between resumes and job descriptions
    """
    
    def __init__(self):
        self.logger = logger
    
    def calculate_match_score(self, resume_id: int, job_description_id: int, user_id: int) -> Dict:
        """
        Calculate comprehensive matching score between resume and job description
        
        Args:
            resume_id: ID of the resume
            job_description_id: ID of the job description
            user_id: ID of the user (for security)
            
        Returns:
            Dict containing matching results and score details
        """
        try:
            # Get resume and job description
            resume = Resume.query.filter_by(
                id=resume_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            job_description = JobDescription.query.filter_by(
                id=job_description_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not resume:
                raise ValueError(f"Resume {resume_id} not found")
            
            if not job_description:
                raise ValueError(f"Job description {job_description_id} not found")
            
            if not resume.keywords_extracted:
                raise ValueError(f"Resume {resume_id} keywords not extracted yet")
            
            if not job_description.keywords_extracted:
                raise ValueError(f"Job description {job_description_id} keywords not extracted yet")
            
            # Get keywords
            resume_keywords = resume.get_keywords()
            jd_keywords = job_description.get_keywords()
            
            # Calculate individual category scores
            technical_score = self._calculate_jaccard_similarity(
                resume_keywords['technical_skills'],
                jd_keywords['technical_skills']
            )
            
            soft_skills_score = self._calculate_jaccard_similarity(
                resume_keywords['soft_skills'],
                jd_keywords['soft_skills']
            )
            
            other_keywords_score = self._calculate_jaccard_similarity(
                resume_keywords['other_keywords'],
                jd_keywords['other_keywords']
            )
            
            # Calculate overall score (weighted average)
            overall_score = self._calculate_weighted_score(
                technical_score, soft_skills_score, other_keywords_score
            )
            
            # Count total keywords and matches
            total_resume_keywords = (
                len(resume_keywords['technical_skills']) +
                len(resume_keywords['soft_skills']) +
                len(resume_keywords['other_keywords'])
            )
            
            total_jd_keywords = (
                len(jd_keywords['technical_skills']) +
                len(jd_keywords['soft_skills']) +
                len(jd_keywords['other_keywords'])
            )
            
            # Count total matched keywords
            matched_keywords = self._count_total_matches(resume_keywords, jd_keywords)
            
            # Save or update match score in database
            match_score = self._save_match_score(
                user_id=user_id,
                resume_id=resume_id,
                job_description_id=job_description_id,
                overall_score=overall_score,
                technical_score=technical_score,
                soft_skills_score=soft_skills_score,
                other_keywords_score=other_keywords_score,
                total_resume_keywords=total_resume_keywords,
                total_jd_keywords=total_jd_keywords,
                matched_keywords=matched_keywords
            )
            
            self.logger.info(f"Match score calculated: {overall_score:.2f}% for resume {resume_id} vs JD {job_description_id}")
            
            return {
                'success': True,
                'match_score': match_score.to_dict(include_details=True),
                'detailed_scores': {
                    'technical_score': technical_score,
                    'soft_skills_score': soft_skills_score,
                    'other_keywords_score': other_keywords_score,
                    'overall_score': overall_score
                },
                'keyword_analysis': {
                    'total_resume_keywords': total_resume_keywords,
                    'total_jd_keywords': total_jd_keywords,
                    'matched_keywords': matched_keywords,
                    'match_percentage': (matched_keywords / max(total_jd_keywords, 1)) * 100
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating match score: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_jaccard_similarity(self, set1: List[str], set2: List[str]) -> float:
        """
        Calculate Jaccard similarity between two keyword sets
        
        Jaccard similarity = |A ∩ B| / |A ∪ B|
        
        Args:
            set1: First set of keywords
            set2: Second set of keywords
            
        Returns:
            Similarity score as percentage (0-100)
        """
        if not set1 and not set2:
            return 100.0  # Both empty = perfect match
        
        if not set1 or not set2:
            return 0.0  # One empty = no match
        
        # Convert to sets for intersection and union operations
        s1 = set(keyword.lower().strip() for keyword in set1)
        s2 = set(keyword.lower().strip() for keyword in set2)
        
        # Calculate Jaccard similarity
        intersection = len(s1.intersection(s2))
        union = len(s1.union(s2))
        
        if union == 0:
            return 0.0
        
        similarity = (intersection / union) * 100
        return round(similarity, 2)
    
    def _calculate_weighted_score(self, technical: float, soft_skills: float, other: float) -> float:
        """
        Calculate weighted overall score
        
        Weights:
        - Technical skills: 50%
        - Soft skills: 20%
        - Other keywords: 30%
        """
        weighted_score = (technical * 0.5) + (soft_skills * 0.2) + (other * 0.3)
        return round(weighted_score, 2)
    
    def _count_total_matches(self, resume_keywords: Dict, jd_keywords: Dict) -> int:
        """Count total number of matched keywords across all categories"""
        total_matches = 0
        
        for category in ['technical_skills', 'soft_skills', 'other_keywords']:
            resume_set = set(keyword.lower().strip() for keyword in resume_keywords[category])
            jd_set = set(keyword.lower().strip() for keyword in jd_keywords[category])
            total_matches += len(resume_set.intersection(jd_set))
        
        return total_matches
    
    def _save_match_score(self, **kwargs) -> MatchScore:
        """Save or update match score in database"""
        # Check if match score already exists
        existing_score = MatchScore.query.filter_by(
            user_id=kwargs['user_id'],
            resume_id=kwargs['resume_id'],
            job_description_id=kwargs['job_description_id'],
            is_active=True
        ).first()
        
        if existing_score:
            # Update existing score
            for key, value in kwargs.items():
                if hasattr(existing_score, key):
                    setattr(existing_score, key, value)
            existing_score.algorithm_used = 'jaccard'
            match_score = existing_score
        else:
            # Create new score
            match_score = MatchScore(
                algorithm_used='jaccard',
                **kwargs
            )
            db.session.add(match_score)
        
        db.session.commit()
        return match_score
    
    def get_match_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent match scores for a user"""
        try:
            match_scores = MatchScore.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(MatchScore.created_at.desc()).limit(limit).all()
            
            return [score.to_dict(include_details=True) for score in match_scores]
            
        except Exception as e:
            self.logger.error(f"Error fetching match history: {e}")
            return []
    
    def get_match_score(self, match_id: int, user_id: int) -> Dict:
        """Get specific match score details"""
        try:
            match_score = MatchScore.query.filter_by(
                id=match_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not match_score:
                return {'success': False, 'error': 'Match score not found'}
            
            return {
                'success': True,
                'match_score': match_score.to_dict(include_details=True)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching match score: {e}")
            return {'success': False, 'error': str(e)}
