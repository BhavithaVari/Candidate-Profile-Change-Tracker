"""
Profile extraction service with AI fallback support.
"""

from typing import Dict, Any, Tuple
from backend.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

class ProfileExtractor:
    """Extracts profile information with AI fallback."""
    
    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()
    
    def extract_profile(self, text: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract profile with automatic fallback.
        Returns: (profile_data, method_used)
        """
        if not text or len(text.strip()) < 10:
            logger.warning("Empty or very short text provided")
            return self._empty_profile(), "empty"
        
        # Use AI if available
        if self.ai_service.use_ai:
            try:
                profile, method = self.ai_service.extract_profile(text)
                if profile and method != "rule_based":
                    logger.info(f"Profile extracted using {method}")
                    return profile, method
            except Exception as e:
                logger.error(f"AI extraction failed: {e}")
        
        # Fallback to rule-based
        logger.info("Using rule-based extraction")
        return self._extract_rule_based(text), "rule_based"
    
    def _extract_rule_based(self, text: str) -> Dict[str, Any]:
        """Rule-based extraction with enhanced patterns."""
        import re
        
        profile = {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin_url": "",
            "skills": [],
            "job_titles": [],
            "employers": [],
            "education": [],
            "experience_years": 0.0,
            "employment_dates": [],
            "current_employer": "",
            "current_job_title": ""
        }
        
        # Try spaCy if available
        if hasattr(self.ai_service, 'spacy_nlp') and self.ai_service.spacy_nlp:
            doc = self.ai_service.spacy_nlp(text[:100000])
            
            # Extract entities
            for ent in doc.ents:
                if ent.label_ == "PERSON" and not profile["name"]:
                    profile["name"] = ent.text
                elif ent.label_ == "ORG":
                    profile["employers"].append(ent.text)
                elif ent.label_ == "GPE":
                    if not profile["location"]:
                        profile["location"] = ent.text
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            profile["email"] = emails[0]
        
        # Extract phone
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                profile["phone"] = phones[0]
                break
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedins = re.findall(linkedin_pattern, text)
        if linkedins:
            profile["linkedin_url"] = f"https://{linkedins[0]}"
        
        # Extract skills
        skill_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node", "django", "flask", "aws", "azure", "gcp", "docker", "kubernetes",
            "sql", "mongodb", "postgresql", "redis", "git", "jenkins", "ci/cd",
            "machine learning", "ai", "data science", "leadership", "management",
            "html", "css", "c++", "c#", "ruby", "php", "swift", "kotlin"
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                profile["skills"].append(skill)
        
        # Extract job titles
        title_patterns = [
            r'([A-Z][a-z]+)\s+(Engineer|Developer|Manager|Director|Analyst|Consultant|Architect|Lead)',
            r'(Senior|Lead|Principal|Chief|Head)\s+([A-Z][a-z]+)\s+(Engineer|Developer|Manager|Director)'
        ]
        for pattern in title_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    profile["job_titles"].append(' '.join(match))
                else:
                    profile["job_titles"].append(match)
        
        # Extract education
        edu_patterns = [
            r'(Bachelor|Master|PhD|BS|MS|BA|MA|MBA)\s+in\s+([A-Za-z\s]+)',
            r'(University|College|Institute)\s+of\s+([A-Za-z\s]+)'
        ]
        for pattern in edu_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    profile["education"].append({
                        "degree": match[0].capitalize(),
                        "field": match[1].strip() if len(match) > 1 else "",
                        "institution": "",
                        "year": ""
                    })
        
        # Extract experience years
        exp_patterns = [
            r'(\d+)\+?\s*(?:years|yrs?)\s*(?:of)?\s*experience',
            r'experience.*?(\d+)\+?\s*(?:years|yrs?)'
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    profile["experience_years"] = float(match.group(1))
                    break
                except:
                    pass
        
        # Clean up
        profile["employers"] = list(set(profile["employers"]))[:5]
        profile["skills"] = list(set(profile["skills"]))[:20]
        profile["job_titles"] = list(set(profile["job_titles"]))[:5]
        profile["education"] = profile["education"][:5]
        
        # Set current employer and title
        if profile["employers"]:
            profile["current_employer"] = profile["employers"][0]
        if profile["job_titles"]:
            profile["current_job_title"] = profile["job_titles"][0]
        
        return profile
    
    def _empty_profile(self) -> Dict[str, Any]:
        """Return empty profile."""
        return {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin_url": "",
            "skills": [],
            "job_titles": [],
            "employers": [],
            "education": [],
            "experience_years": 0.0,
            "employment_dates": [],
            "current_employer": "",
            "current_job_title": ""
        }