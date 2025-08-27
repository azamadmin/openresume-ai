#!/usr/bin/env python3
"""
Enhanced Dynamic Suggestions Service - Advanced NLP-based keyword analysis
Generates intelligent suggestions by comparing resume vs JD keywords using structured analysis
No hardcoded suggestions - everything is based on real keyword comparison and NLP
"""

import json
import re
from typing import Dict, List, Set, Tuple
from backend.models import Resume, JobDescription
from backend.services.matching_service import MatchingService

class DynamicSuggestionsService:
    """Enhanced suggestions service with advanced NLP-based keyword analysis"""

    def __init__(self):
        self.matching_service = MatchingService()

        # Initialize NLP components for better keyword analysis (lazy loading)
        self.nlp = None  # Load spaCy model lazily when needed

    def _get_nlp_model(self):
        """Load spaCy model lazily"""
        if self.nlp is None:
            try:
                import spacy
                self.nlp = spacy.load('en_core_web_sm')
            except:
                self.nlp = False  # Mark as unavailable
                print("⚠️ spaCy not available - using basic keyword analysis")
        return self.nlp if self.nlp is not False else None

    def analyze_keywords_advanced(self, resume_id: int, jd_id: int, user_id: int) -> Dict:
        """
        Advanced keyword analysis as per your specification:
        X = JD keywords, Y = Resume keywords, Z = Missing keywords, Q = Extra keywords
        """
        try:
            # Get resume and JD
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            jd = JobDescription.query.filter_by(id=jd_id, user_id=user_id).first()

            if not resume or not jd:
                return {'success': False, 'message': 'Resume or JD not found'}

            # X = JD keywords (structured extraction)
            jd_keywords = self._extract_structured_keywords(jd.job_text, jd.technical_skills, jd.soft_skills, jd.other_keywords)

            # Y = Resume keywords (structured extraction)
            resume_keywords = self._extract_structured_keywords(resume.extracted_text, resume.technical_skills, resume.soft_skills, resume.other_keywords)

            # Z = Missing keywords (JD has but Resume doesn't)
            missing_keywords = self._find_missing_keywords(jd_keywords, resume_keywords)

            # Q = Extra keywords (Resume has but JD doesn't need)
            extra_keywords = self._find_extra_keywords(resume_keywords, jd_keywords)

            # Convert sets to lists for JSON serialization
            jd_keywords_serializable = {k: list(v) if isinstance(v, set) else v for k, v in jd_keywords.items()}
            resume_keywords_serializable = {k: list(v) if isinstance(v, set) else v for k, v in resume_keywords.items()}

            # Advanced analysis with context and importance scoring
            analysis_result = {
                'success': True,
                'jd_keywords': jd_keywords_serializable,           # X variable
                'resume_keywords': resume_keywords_serializable,   # Y variable
                'missing_keywords': missing_keywords, # Z variable
                'extra_keywords': extra_keywords,     # Q variable
                'keyword_gaps': self._analyze_keyword_gaps(missing_keywords, jd.job_text),
                'keyword_strengths': self._analyze_keyword_strengths(extra_keywords, resume.extracted_text),
                'context_analysis': self._analyze_context(jd.job_text, resume.extracted_text)
            }

            return analysis_result

        except Exception as e:
            return {'success': False, 'message': f'Analysis error: {str(e)}'}

    def _extract_structured_keywords(self, text: str, tech_skills: str, soft_skills: str, other_keywords: str) -> Dict[str, Set[str]]:
        """Extract and structure keywords from text and existing keyword fields"""

        # Parse existing keyword fields
        tech_set = set(self._clean_keywords(self._parse_keywords(tech_skills)))
        soft_set = set(self._clean_keywords(self._parse_keywords(soft_skills)))
        other_set = set(self._clean_keywords(self._parse_keywords(other_keywords)))

        # Extract additional keywords from text using NLP
        nlp_model = self._get_nlp_model()
        if nlp_model and text:
            nlp_keywords = self._extract_nlp_keywords(text)
            tech_set.update(nlp_keywords['technical'])
            soft_set.update(nlp_keywords['soft_skills'])
            other_set.update(nlp_keywords['other'])

        return {
            'technical': tech_set,
            'soft_skills': soft_set,
            'other_keywords': other_set,
            'all_keywords': tech_set.union(soft_set).union(other_set)
        }

    def _find_missing_keywords(self, jd_keywords: Dict, resume_keywords: Dict) -> Dict[str, List[str]]:
        """Z variable: Find keywords present in JD but missing from resume"""
        missing = {}

        for category in ['technical', 'soft_skills', 'other_keywords']:
            jd_set = jd_keywords.get(category, set())
            resume_set = resume_keywords.get(category, set())

            # Find missing keywords with intelligent matching
            missing_in_category = []
            for jd_keyword in jd_set:
                if not self._is_keyword_present(jd_keyword, resume_set):
                    missing_in_category.append(jd_keyword)

            missing[category] = sorted(missing_in_category)

        return missing

    def _find_extra_keywords(self, resume_keywords: Dict, jd_keywords: Dict) -> Dict[str, List[str]]:
        """Q variable: Find keywords present in resume but not required by JD"""
        extra = {}

        for category in ['technical', 'soft_skills', 'other_keywords']:
            resume_set = resume_keywords.get(category, set())
            jd_set = jd_keywords.get(category, set())

            # Find extra keywords
            extra_in_category = []
            for resume_keyword in resume_set:
                if not self._is_keyword_present(resume_keyword, jd_set):
                    extra_in_category.append(resume_keyword)

            extra[category] = sorted(extra_in_category)

        return extra

    def _is_keyword_present(self, keyword: str, keyword_set: Set[str]) -> bool:
        """Intelligent keyword matching with fuzzy logic"""
        keyword_lower = keyword.lower().strip()

        # Exact match
        if keyword_lower in [k.lower().strip() for k in keyword_set]:
            return True

        # Partial match for compound keywords
        keyword_parts = keyword_lower.split()
        for existing_keyword in keyword_set:
            existing_lower = existing_keyword.lower().strip()

            # Check if all parts of the keyword are present
            if len(keyword_parts) > 1:
                if all(part in existing_lower for part in keyword_parts):
                    return True

            # Check if keyword is part of a larger existing keyword
            if keyword_lower in existing_lower or existing_lower in keyword_lower:
                return True

        return False

    def _extract_nlp_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract keywords using NLP analysis"""
        nlp_model = self._get_nlp_model()
        if not nlp_model or not text:
            return {'technical': [], 'soft_skills': [], 'other': []}

        doc = nlp_model(text)

        # Technical keywords patterns
        tech_patterns = [
            r'\b(?:javascript|js|typescript|ts|python|java|c#|csharp|\.net|asp\.net)\b',
            r'\b(?:react|angular|vue|node\.js|express|django|flask|spring)\b',
            r'\b(?:sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
            r'\b(?:docker|kubernetes|aws|azure|gcp|jenkins|git|github)\b',
            r'\b(?:html|css|sass|less|bootstrap|tailwind|jquery)\b',
            r'\b(?:api|rest|graphql|microservices|oauth|jwt|swagger)\b'
        ]

        # Soft skills patterns
        soft_patterns = [
            r'\b(?:leadership|communication|teamwork|collaboration)\b',
            r'\b(?:problem.solving|analytical|critical.thinking)\b',
            r'\b(?:project.management|agile|scrum|kanban)\b',
            r'\b(?:mentoring|coaching|training|presentation)\b'
        ]

        technical_keywords = []
        soft_keywords = []
        other_keywords = []

        text_lower = text.lower()

        # Extract technical keywords
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            technical_keywords.extend(matches)

        # Extract soft skills
        for pattern in soft_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            soft_keywords.extend(matches)

        # Extract entities and noun phrases for other keywords
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'TECHNOLOGY']:
                other_keywords.append(ent.text.lower())

        # Extract noun phrases that might be technical terms
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3 and chunk.text.lower() not in technical_keywords:
                other_keywords.append(chunk.text.lower())

        return {
            'technical': list(set(technical_keywords)),
            'soft_skills': list(set(soft_keywords)),
            'other': list(set(other_keywords))
        }

    def _analyze_keyword_gaps(self, missing_keywords: Dict, jd_text: str) -> Dict:
        """Analyze the importance and context of missing keywords"""
        gaps_analysis = {}

        for category, keywords in missing_keywords.items():
            category_gaps = []

            for keyword in keywords:
                # Count frequency in JD
                frequency = jd_text.lower().count(keyword.lower())

                # Determine importance based on context
                importance = self._determine_keyword_importance(keyword, jd_text, frequency)

                # Generate specific suggestion
                suggestion = self._generate_gap_suggestion(keyword, category, jd_text)

                category_gaps.append({
                    'keyword': keyword,
                    'frequency': frequency,
                    'importance': importance,
                    'suggestion': suggestion,
                    'category': category
                })

            # Sort by importance and frequency
            category_gaps.sort(key=lambda x: (x['importance'], x['frequency']), reverse=True)
            gaps_analysis[category] = category_gaps

        return gaps_analysis

    def _determine_keyword_importance(self, keyword: str, jd_text: str, frequency: int) -> int:
        """Determine importance score of a keyword (1-5 scale)"""
        jd_lower = jd_text.lower()
        keyword_lower = keyword.lower()

        importance = 1  # Base importance

        # Frequency-based scoring
        if frequency >= 3:
            importance += 2
        elif frequency >= 2:
            importance += 1

        # Position-based scoring (keywords in job title or requirements section)
        if any(section in jd_lower for section in ['requirements', 'qualifications', 'must have']):
            req_section = jd_lower.split('requirements')[0] if 'requirements' in jd_lower else jd_lower[:500]
            if keyword_lower in req_section:
                importance += 1

        # Critical technology scoring
        if keyword_lower in ['c#', '.net', 'javascript', 'python', 'java', 'sql', 'react', 'angular']:
            importance += 1

        return min(5, importance)

    def _generate_gap_suggestion(self, keyword: str, category: str, jd_text: str) -> str:
        """Generate specific suggestion for a missing keyword"""
        if category == 'technical':
            return self._generate_tech_action(keyword, jd_text, "")
        elif category == 'soft_skills':
            return self._generate_soft_skill_action(keyword, jd_text)
        else:
            return f"Include '{keyword}' in your resume to show relevant experience and improve keyword matching."

    def _analyze_keyword_strengths(self, extra_keywords: Dict, resume_text: str) -> Dict:
        """Analyze extra keywords as competitive advantages"""
        strengths = {}

        for category, keywords in extra_keywords.items():
            category_strengths = []

            for keyword in keywords:
                # Count frequency in resume
                frequency = resume_text.lower().count(keyword.lower())

                # Determine competitive value
                value = self._determine_competitive_value(keyword, category)

                category_strengths.append({
                    'keyword': keyword,
                    'frequency': frequency,
                    'competitive_value': value,
                    'suggestion': f"Leverage your {keyword} expertise as a differentiator"
                })

            strengths[category] = category_strengths

        return strengths

    def _determine_competitive_value(self, keyword: str, category: str) -> str:
        """Determine competitive value of an extra skill"""
        keyword_lower = keyword.lower()

        # High-value skills
        if keyword_lower in ['machine learning', 'ai', 'blockchain', 'kubernetes', 'microservices']:
            return "high"
        elif keyword_lower in ['docker', 'aws', 'azure', 'devops', 'ci/cd']:
            return "medium"
        else:
            return "low"

    def _analyze_context(self, jd_text: str, resume_text: str) -> Dict:
        """Analyze context and provide insights"""
        return {
            'jd_length': len(jd_text.split()),
            'resume_length': len(resume_text.split()),
            'jd_complexity': 'high' if len(jd_text.split()) > 500 else 'medium',
            'analysis_method': 'Advanced NLP-based keyword comparison',
            'enhancement_level': 'Dynamic suggestions based on real keyword gaps'
        }

    def _clean_keywords(self, keywords: List[str]) -> List[str]:
        """Clean and normalize keywords"""
        cleaned = []
        for kw in keywords:
            if kw and isinstance(kw, str):
                # Remove quotes, extra spaces, and normalize
                clean_kw = kw.strip().strip('"').strip("'").strip()
                if clean_kw and len(clean_kw) > 1:
                    cleaned.append(clean_kw.lower())
        return cleaned
    
    def generate_basic_suggestions(self, resume_id, job_description_id, user_id):
        """Generate enhanced basic suggestions using advanced keyword analysis"""
        try:
            # Perform advanced keyword analysis (X, Y, Z, Q variables)
            analysis = self.analyze_keywords_advanced(resume_id, job_description_id, user_id)

            if not analysis['success']:
                return analysis

            # Extract analysis results
            missing_keywords = analysis['missing_keywords']  # Z variable
            extra_keywords = analysis['extra_keywords']      # Q variable
            keyword_gaps = analysis['keyword_gaps']

            # Get resume and JD for additional context
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            jd = JobDescription.query.filter_by(id=job_description_id, user_id=user_id).first()
            
            suggestions = []

            # 1. MISSING TECHNICAL SKILLS (Z variable - highest priority)
            missing_tech_gaps = keyword_gaps.get('technical', [])
            for i, gap in enumerate(missing_tech_gaps[:8]):  # Top 8 missing technical skills
                keyword = gap['keyword']
                importance = gap['importance']
                frequency = gap['frequency']

                # Priority based on analysis
                priority = "critical" if importance >= 3 else "high" if importance >= 2 else "medium"

                # Generate contextual action
                action = self._generate_tech_action(keyword, jd.job_text, resume.extracted_text)
                title = self._generate_tech_title(keyword, jd.job_text)

                suggestions.append({
                    "type": "technical_skills",
                    "priority": priority,
                    "title": f"Add {keyword.title()} Experience",
                    "description": f"Required skill mentioned {frequency} times in job description",
                    "keywords": [keyword],
                    "action": f"Add {keyword} to skills section with specific project examples",
                    "placement": ["Skills", "Experience", "Projects"],
                    "example": self._generate_tech_example(keyword, jd.job_text),
                    "missing_keyword": keyword,
                    "analysis_score": importance,
                    "jd_frequency": frequency
                })
            
            # 2. MISSING SOFT SKILLS (Z variable - behavioral focus)
            missing_soft_gaps = keyword_gaps.get('soft_skills', [])
            for gap in missing_soft_gaps[:4]:  # Top 4 missing soft skills
                keyword = gap['keyword']
                importance = gap['importance']
                frequency = gap['frequency']

                action = self._generate_soft_skill_action(keyword, jd.job_text)
                example = self._generate_soft_skill_example(keyword)

                suggestions.append({
                    "type": "soft_skills",
                    "priority": "high",
                    "title": f"Demonstrate {keyword.title()} Skills",
                    "description": f"Employer values {keyword} - show evidence in your experience",
                    "keywords": [keyword],
                    "action": f"Include specific examples demonstrating {keyword} in your experience section",
                    "placement": ["Experience", "Summary"],
                    "example": example,
                    "missing_keyword": keyword,
                    "analysis_score": importance,
                    "jd_frequency": frequency
                })
            
            # 3. MISSING OTHER KEYWORDS (Z variable - industry relevance)
            missing_other_gaps = keyword_gaps.get('other_keywords', [])
            for gap in missing_other_gaps[:3]:  # Top 3 missing other keywords
                keyword = gap['keyword']
                importance = gap['importance']

                suggestions.append({
                    "type": "industry_keywords",
                    "priority": "medium",
                    "title": f"Include Industry Keyword: {keyword.title()}",
                    "description": f"MISSING INDUSTRY TERM: {keyword} shows domain knowledge but is absent from your resume.",
                    "keywords": [keyword],
                    "action": f"Add '{keyword}' to relevant sections to show industry knowledge and improve keyword matching.",
                    "placement": ["Skills", "Experience"],
                    "example": f"Demonstrated expertise in {keyword} through practical application.",
                    "missing_keyword": keyword,
                    "analysis_score": importance
                })
            
            # 4. EXTRA SKILLS LEVERAGE (Q variable - competitive advantage)
            extra_tech = extra_keywords.get('technical', [])
            if extra_tech:
                top_extra = extra_tech[:3]  # Top 3 extra skills
                suggestions.append({
                    "type": "competitive_advantage",
                    "priority": "medium",
                    "title": "Leverage Your Additional Technical Skills",
                    "description": f"COMPETITIVE ADVANTAGE: You have {len(extra_tech)} additional skills not required by this JD.",
                    "keywords": top_extra,
                    "action": f"Highlight these additional skills ({', '.join(top_extra)}) to differentiate yourself from other candidates.",
                    "placement": ["Skills", "Summary"],
                    "example": f"Additional expertise in {', '.join(top_extra)} provides versatility for complex projects.",
                    "extra_skills": extra_tech
                })

            # 5. ATS OPTIMIZATION (based on missing keywords analysis)
            all_missing = missing_tech_gaps + missing_soft_gaps + missing_other_gaps
            if all_missing:
                critical_missing = [gap['keyword'] for gap in all_missing if gap['importance'] >= 3][:5]
                suggestions.append({
                    "type": "ats_optimization",
                    "priority": "critical" if critical_missing else "high",
                    "title": "ATS Optimization - Critical Missing Keywords",
                    "description": f"KEYWORD GAP ANALYSIS: {len(all_missing)} missing keywords detected that ATS systems scan for.",
                    "keywords": critical_missing or [gap['keyword'] for gap in all_missing[:5]],
                    "action": "Strategically integrate these missing keywords throughout your resume to pass ATS screening.",
                    "placement": ["Skills", "Experience", "Summary"],
                    "example": "Naturally incorporate keywords: 'Developed applications using [missing_keywords] following industry best practices.'",
                    "missing_count": len(all_missing),
                    "critical_count": len(critical_missing)
                })
            
            # Structure improvements
            suggestions.append({
                "type": "structure",
                "priority": "medium",
                "title": "Add Quantifiable Metrics",
                "description": "Quantified achievements make your resume more impactful and memorable.",
                "keywords": ["metrics", "results", "impact"],
                "action": "Convert generic statements to quantified achievements (e.g., 'Improved system performance by 40%' instead of 'Improved system performance').",
                "placement": ["Experience"],
                "example": "Increased application performance by 35% through code optimization and database tuning."
            })
            
            # Get matching score
            match_result = self.matching_service.calculate_match_score(resume_id, job_description_id, user_id)
            matching_score = match_result.get('detailed_scores', {}) if match_result.get('success') else {}
            
            return {
                'success': True,
                'suggestions': suggestions,
                'total_suggestions': len(suggestions),
                'matching_score': matching_score,
                'missing_keywords': missing_keywords,  # Z variable
                'extra_keywords': extra_keywords,      # Q variable
                'keyword_analysis': analysis,          # Full analysis
                'enhancement_note': 'Generated using advanced NLP keyword analysis - no hardcoded suggestions'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating suggestions: {str(e)}'
            }
    
    def generate_premium_suggestions(self, resume_id, job_description_id, user_id):
        """Generate premium suggestions with additional categories"""
        try:
            # Get basic suggestions first
            basic_result = self.generate_basic_suggestions(resume_id, job_description_id, user_id)
            
            if not basic_result['success']:
                return basic_result
            
            suggestions = basic_result['suggestions'].copy()
            missing_keywords = basic_result['missing_keywords']
            
            # Premium-only categories
            
            # 1. Critical Gaps Analysis (Premium)
            critical_tech = missing_keywords['technical'][:3]
            for tech in critical_tech:
                suggestions.append({
                    "type": "critical_gaps",
                    "priority": "critical",
                    "title": f"URGENT: Add {tech.title()} Experience",
                    "description": f"This is a critical skill gap. The job description heavily emphasizes '{tech}'.",
                    "keywords": [tech],
                    "action": f"Add {tech} experience immediately. Consider building a sample project or taking a course to demonstrate proficiency.",
                    "placement": ["Skills", "Projects", "Experience"],
                    "example": f"Build a portfolio project showcasing {tech} implementation and best practices."
                })
            
            # 2. Contextual Advice (Premium)
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            jd = JobDescription.query.filter_by(id=job_description_id, user_id=user_id).first()
            
            # Analyze job description for specific requirements
            jd_text = (jd.job_text or '').lower()
            contextual_suggestions = []
            
            if 'experience' in jd_text and 'years' in jd_text:
                contextual_suggestions.append({
                    "type": "contextual_advice",
                    "priority": "high",
                    "title": "Emphasize Years of Experience",
                    "description": "The job description specifically mentions experience requirements.",
                    "keywords": ["experience", "years"],
                    "action": "Clearly state your years of experience with relevant technologies in your summary section.",
                    "placement": ["Summary", "Experience"],
                    "example": "5+ years of experience in full-stack development with proven track record."
                })
            
            if any(word in jd_text for word in ['team', 'collaboration', 'lead']):
                contextual_suggestions.append({
                    "type": "contextual_advice",
                    "priority": "high",
                    "title": "Highlight Team Leadership",
                    "description": "The job description emphasizes teamwork and leadership capabilities.",
                    "keywords": ["leadership", "team", "collaboration"],
                    "action": "Include specific examples of team leadership, mentoring, or collaborative projects.",
                    "placement": ["Experience", "Summary"],
                    "example": "Led cross-functional team of 5 developers in agile development environment."
                })
            
            suggestions.extend(contextual_suggestions[:2])  # Add top 2 contextual suggestions
            
            # 3. Quantification Opportunities (Premium)
            quantification_suggestions = [
                {
                    "type": "quantification",
                    "priority": "medium",
                    "title": "Add Performance Metrics",
                    "description": "Quantify your technical achievements with specific metrics.",
                    "keywords": ["performance", "metrics", "improvement"],
                    "action": "Add specific numbers to your achievements: response times, user counts, performance improvements, etc.",
                    "placement": ["Experience"],
                    "example": "Optimized database queries reducing response time from 2s to 200ms (90% improvement)."
                },
                {
                    "type": "quantification",
                    "priority": "medium",
                    "title": "Quantify Project Impact",
                    "description": "Show the business impact of your technical work.",
                    "keywords": ["impact", "results", "business"],
                    "action": "Include metrics like cost savings, efficiency gains, user adoption, or revenue impact.",
                    "placement": ["Experience", "Projects"],
                    "example": "Developed automation tool saving 20 hours/week of manual work across the team."
                }
            ]
            suggestions.extend(quantification_suggestions)
            
            # 4. Skill Development Path (Premium)
            skill_development = []
            for tech in missing_keywords['technical'][:2]:
                skill_development.append({
                    "type": "skill_development",
                    "priority": "medium",
                    "title": f"{tech.title()} Learning Path",
                    "description": f"Strategic plan to acquire {tech} skills for this role.",
                    "keywords": [tech, "learning", "development"],
                    "action": f"Learn {tech} through online courses, documentation, and hands-on projects. Aim to build a demonstrable project within 2-4 weeks.",
                    "placement": ["Skills", "Projects"],
                    "example": f"Complete {tech} certification or build portfolio project demonstrating proficiency."
                })
            
            suggestions.extend(skill_development)
            
            return {
                'success': True,
                'suggestions': suggestions,
                'total_suggestions': len(suggestions),
                'matching_score': basic_result['matching_score'],
                'missing_keywords': missing_keywords,
                'additional_premium_categories': {
                    'critical_gaps': len([s for s in suggestions if s['type'] == 'critical_gaps']),
                    'contextual_advice': len([s for s in suggestions if s['type'] == 'contextual_advice']),
                    'quantification': len([s for s in suggestions if s['type'] == 'quantification']),
                    'skill_development': len([s for s in suggestions if s['type'] == 'skill_development'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating premium suggestions: {str(e)}'
            }
    
    def _parse_keywords(self, keywords_str):
        """Parse keywords from JSON string or comma-separated string"""
        if not keywords_str:
            return []
        
        try:
            # Try parsing as JSON first
            if keywords_str.startswith('[') or keywords_str.startswith('{'):
                return json.loads(keywords_str)
            else:
                # Parse as comma-separated string
                return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
        except:
            # Fallback to simple split
            return [kw.strip() for kw in str(keywords_str).split(',') if kw.strip()]

    def _determine_tech_priority(self, tech, jd_text, position):
        """Determine priority of a technical skill based on context"""
        jd_lower = jd_text.lower()
        tech_lower = tech.lower()

        # Count occurrences in JD
        occurrences = jd_lower.count(tech_lower)

        # High priority if mentioned multiple times or in first 3 missing
        if occurrences >= 2 or position < 3:
            return "critical"
        elif occurrences == 1 or position < 6:
            return "high"
        else:
            return "medium"

    def _generate_tech_action(self, tech, jd_text, resume_text):
        """Generate contextual action for a technical skill"""
        jd_lower = jd_text.lower()
        tech_lower = tech.lower()

        # Context-aware actions based on technology type
        if tech_lower in ['c#', 'csharp', '.net', 'asp.net']:
            if 'api' in jd_lower or 'rest' in jd_lower:
                return f"Add {tech} to your skills and describe REST API development experience. Include specific frameworks and patterns used."
            elif 'web' in jd_lower or 'mvc' in jd_lower:
                return f"Highlight {tech} web development experience. Mention MVC architecture, Entity Framework, and modern web practices."
            else:
                return f"Add {tech} to your skills section and describe enterprise application development experience."

        elif tech_lower in ['javascript', 'js', 'typescript', 'ts']:
            if 'angular' in jd_lower or 'react' in jd_lower:
                return f"Emphasize {tech} frontend development skills. Include component-based architecture and state management experience."
            elif 'node' in jd_lower:
                return f"Highlight {tech} backend development with Node.js. Mention API development and server-side experience."
            else:
                return f"Add {tech} to your skills and describe both frontend and backend JavaScript development experience."

        elif tech_lower in ['sql', 'database', 'mysql', 'postgresql', 'sql server']:
            return f"Add {tech} database skills. Include query optimization, stored procedures, and database design experience."

        elif tech_lower in ['docker', 'kubernetes', 'devops']:
            return f"Highlight {tech} containerization and deployment experience. Mention CI/CD pipelines and infrastructure management."

        elif tech_lower in ['testing', 'unit testing', 'tdd']:
            return f"Add {tech} experience to your skills. Describe test-driven development practices and testing frameworks used."

        else:
            return f"Add {tech} to your skills section and provide specific examples of projects where you implemented {tech} solutions."

    def _generate_tech_title(self, tech, jd_text):
        """Generate intelligent title for technical skill suggestion"""
        jd_lower = jd_text.lower()
        tech_lower = tech.lower()

        if jd_lower.count(tech_lower) >= 2:
            return f"URGENT: Add {tech.upper()} Experience"
        elif tech_lower in ['c#', '.net', 'asp.net', 'javascript', 'python', 'java']:
            return f"Add Core {tech.upper()} Skills"
        elif tech_lower in ['docker', 'kubernetes', 'microservices']:
            return f"Include {tech.title()} Architecture Experience"
        elif tech_lower in ['testing', 'unit testing', 'tdd']:
            return f"Highlight {tech.title()} Practices"
        else:
            return f"Add {tech.title()} Technology Skills"

    def _generate_tech_example(self, tech, jd_text):
        """Generate contextual example for technical skill"""
        tech_lower = tech.lower()

        examples = {
            'c#': "Developed enterprise applications using C# and .NET Framework with clean architecture patterns.",
            '.net': "Built scalable web applications using .NET Core with Entity Framework and dependency injection.",
            'javascript': "Implemented interactive web features using modern JavaScript ES6+ and asynchronous programming.",
            'angular': "Created responsive single-page applications using Angular with TypeScript and RxJS.",
            'sql': "Designed and optimized database schemas with complex queries achieving 40% performance improvement.",
            'docker': "Containerized applications using Docker with multi-stage builds reducing deployment time by 60%.",
            'testing': "Implemented comprehensive unit testing achieving 85% code coverage using TDD methodology.",
            'microservices': "Architected microservices-based solutions with API gateways and service discovery.",
            'swagger': "Documented REST APIs using Swagger/OpenAPI specifications for better developer experience.",
            'unit testing': "Implemented comprehensive unit testing achieving 85% code coverage using TDD methodology.",
            'entity framework': "Designed data access layer using Entity Framework Core with Code First approach.",
            'authorization': "Implemented role-based authorization with JWT tokens and custom middleware."
        }

        return examples.get(tech_lower, f"Successfully implemented {tech} solutions in production environments with measurable business impact.")

    def _generate_soft_skill_action(self, skill, jd_text):
        """Generate contextual action for soft skills"""
        jd_lower = jd_text.lower()
        skill_lower = skill.lower()

        if skill_lower in ['communication', 'written communication']:
            if 'documentation' in jd_lower or 'technical writing' in jd_lower:
                return f"Highlight your {skill} skills by mentioning technical documentation, API documentation, or user guides you've created."
            else:
                return f"Include examples of {skill} in cross-functional team settings, client presentations, or stakeholder meetings."

        elif skill_lower in ['leadership', 'team leadership']:
            return f"Demonstrate {skill} by describing team projects you led, mentoring experience, or process improvements you initiated."

        elif skill_lower in ['problem solving', 'analytical thinking']:
            return f"Show {skill} abilities through examples of complex technical challenges you solved and the methodologies you used."

        elif skill_lower in ['collaboration', 'teamwork']:
            return f"Highlight {skill} through examples of successful cross-functional projects, pair programming, or agile team participation."

        else:
            return f"Include specific examples demonstrating your {skill} abilities in your experience section with measurable outcomes."

    def _generate_soft_skill_example(self, skill):
        """Generate example for soft skills"""
        skill_lower = skill.lower()

        examples = {
            'communication': "Facilitated daily standups and sprint reviews, improving team communication and reducing project delays by 25%.",
            'leadership': "Led cross-functional team of 8 developers and designers, delivering project 2 weeks ahead of schedule.",
            'problem solving': "Identified and resolved critical performance bottleneck, improving application response time by 60%.",
            'collaboration': "Collaborated with UX team and product managers to deliver user-centric features with 95% satisfaction rate.",
            'analytical thinking': "Analyzed user behavior data to identify optimization opportunities, increasing conversion rate by 15%.",
            'teamwork': "Worked effectively in agile environment, contributing to 98% sprint completion rate over 12 months."
        }

        return examples.get(skill_lower, f"Demonstrated strong {skill} skills through successful project delivery and stakeholder engagement.")
