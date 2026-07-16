"""
AI Service with intelligent fallback mechanisms.
Supports Gemini AI with automatic fallback to rule-based logic.
"""

import os
import json
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Try to import AI libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIService:
    """AI Service with automatic fallback to rule-based logic."""
    
    def __init__(self, use_ai: bool = False, gemini_api_key: str = None):
        self.use_ai = use_ai
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.gemini_model = None
        self.spacy_nlp = None
        self.sentence_transformer = None
        
        # Statistics
        self.ai_success_count = 0
        self.ai_failure_count = 0
        self.fallback_count = 0
        self.token_usage = 0
        self.token_limit = 1000000  # Monthly limit
        
        # Load models if AI is enabled
        if self.use_ai:
            self._load_models()
    
    def _load_models(self):
        """Load AI models with graceful failure."""
        # Load Gemini
        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                logger.info("Gemini AI model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Gemini: {e}")
                self.use_ai = False
        
        # Load spaCy for NLP tasks
        if SPACY_AVAILABLE:
            try:
                # Try to load model, download if not available
                try:
                    self.spacy_nlp = spacy.load('en_core_web_sm')
                except:
                    spacy.cli.download('en_core_web_sm')
                    self.spacy_nlp = spacy.load('en_core_web_sm')
                logger.info("spaCy model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load spaCy: {e}")
        
        # Load sentence transformer for semantic similarity
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Sentence Transformer loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
    
    def extract_profile(self, text: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract profile using AI with fallback to rule-based.
        Returns: (profile_data, method_used)
        """
        if self._should_use_ai():
            try:
                result = self._extract_with_gemini(text)
                if result:
                    self.ai_success_count += 1
                    self._track_tokens(text)
                    return result, "ai"
            except Exception as e:
                logger.error(f"Gemini extraction failed: {e}")
                self.ai_failure_count += 1
        
        # Fallback to rule-based
        self.fallback_count += 1
        return self._extract_rule_based(text), "rule_based"
    
    def _extract_with_gemini(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract using Gemini AI."""
        if not self.gemini_model:
            return None
        
        try:
            # Truncate text if too long
            if len(text) > 10000:
                text = text[:10000]
            
            prompt = f"""
            Extract structured information from this resume text.
            Return ONLY valid JSON with these fields:
            {{
                "name": "Full name",
                "email": "Email address",
                "phone": "Phone number",
                "location": "City, State",
                "linkedin_url": "LinkedIn URL",
                "skills": ["skill1", "skill2"],
                "job_titles": ["title1", "title2"],
                "employers": ["employer1", "employer2"],
                "education": [{{"institution": "", "degree": "", "year": "", "field": ""}}],
                "experience_years": 0.0,
                "employment_dates": [{{"employer": "", "title": "", "start": "", "end": "", "isCurrent": false}}],
                "current_employer": "",
                "current_job_title": ""
            }}
            
            Resume Text:
            {text}
            """
            
            response = self.gemini_model.generate_content(prompt, timeout=30)
            
            # Extract JSON from response
            response_text = response.text
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(response_text.strip())
            
        except Exception as e:
            logger.error(f"Gemini extraction error: {e}")
            return None
    
    def _extract_rule_based(self, text: str) -> Dict[str, Any]:
        """Enhanced rule-based extraction with NLP."""
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
        
        # Use spaCy if available
        if self.spacy_nlp:
            doc = self.spacy_nlp(text[:100000])
            
            # Extract entities
            for ent in doc.ents:
                if ent.label_ == "PERSON" and not profile["name"]:
                    profile["name"] = ent.text
                elif ent.label_ == "ORG":
                    profile["employers"].append(ent.text)
                elif ent.label_ == "GPE":
                    if not profile["location"]:
                        profile["location"] = ent.text
            
            # Extract skills
            profile["skills"] = self._extract_skills_with_spacy(doc)
            
            # Extract dates
            profile["employment_dates"] = self._extract_dates_with_spacy(doc)
        
        # Extract email (regex)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            profile["email"] = emails[0]
        
        # Extract phone (regex)
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                profile["phone"] = phones[0]
                break
        
        # Extract LinkedIn (regex)
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedins = re.findall(linkedin_pattern, text)
        if linkedins:
            profile["linkedin_url"] = f"https://{linkedins[0]}"
        
        # Extract job titles
        profile["job_titles"] = self._extract_job_titles(text)
        
        # Extract education
        profile["education"] = self._extract_education(text)
        
        # Extract experience years
        profile["experience_years"] = self._extract_experience_years(text)
        
        # Clean up - remove duplicates
        profile["employers"] = list(set(profile["employers"]))[:5]
        profile["skills"] = list(set(profile["skills"]))[:20]
        profile["job_titles"] = list(set(profile["job_titles"]))[:5]
        
        # Set current employer and title (first in list if available)
        if profile["employers"]:
            profile["current_employer"] = profile["employers"][0]
        if profile["job_titles"]:
            profile["current_job_title"] = profile["job_titles"][0]
        
        return profile
    
    def _extract_skills_with_spacy(self, doc) -> List[str]:
        """Extract skills using spaCy patterns."""
        skill_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node", "django", "flask", "aws", "azure", "gcp", "docker", "kubernetes",
            "sql", "mongodb", "postgresql", "redis", "git", "jenkins", "ci/cd",
            "machine learning", "ai", "data science", "leadership", "management",
            "html", "css", "c++", "c#", "ruby", "php", "swift", "kotlin", "rust",
            "spring", "hibernate", "jpa", "rest api", "graphql", "microservices"
        ]
        
        skills = []
        text_lower = doc.text.lower()
        
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill)
        
        return skills
    
    def _extract_dates_with_spacy(self, doc) -> List[Dict[str, str]]:
        """Extract employment dates using spaCy."""
        dates = []
        text = doc.text
        
        # Look for date patterns
        date_pattern = r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|present)'
        matches = re.findall(date_pattern, text, re.IGNORECASE)
        
        for match in matches:
            dates.append({
                "start": match[0],
                "end": match[1],
                "isCurrent": "present" in match[1].lower()
            })
        
        return dates
    
    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles using regex patterns."""
        title_patterns = [
            r'([A-Z][a-z]+)\s+(Engineer|Developer|Manager|Director|Analyst|Consultant|Architect|Lead|Specialist)',
            r'(Senior|Lead|Principal|Chief|Head)\s+([A-Z][a-z]+)\s+(Engineer|Developer|Manager|Director)',
            r'([A-Z][a-z]+)\s+[A-Z][a-z]+\s+(Engineer|Developer|Manager|Director)'
        ]
        
        titles = []
        for pattern in title_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    titles.append(' '.join(match))
                else:
                    titles.append(match)
        
        return titles
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information."""
        education = []
        
        edu_patterns = [
            r'(Bachelor|Master|PhD|BS|MS|BA|MA|MBA)\s+in\s+([A-Za-z\s]+)',
            r'(Bachelor|Master|PhD|BS|MS|BA|MA|MBA)\s+of\s+([A-Za-z\s]+)',
            r'(University|College|Institute)\s+of\s+([A-Za-z\s]+)'
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    education.append({
                        "degree": match[0].capitalize(),
                        "field": match[1].strip() if len(match) > 1 else "",
                        "institution": "",
                        "year": ""
                    })
        
        return education[:5]  # Limit to 5
    
    def _extract_experience_years(self, text: str) -> float:
        """Extract years of experience."""
        patterns = [
            r'(\d+)\+?\s*(?:years|yrs?)\s*(?:of)?\s*experience',
            r'experience.*?(\d+)\+?\s*(?:years|yrs?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        return 0.0
    
    def classify_changes(self, changes: List[Dict]) -> Tuple[List[Dict], str]:
        """Classify changes with AI fallback."""
        if self._should_use_ai() and changes:
            try:
                result = self._classify_with_gemini(changes)
                if result:
                    self.ai_success_count += 1
                    return result, "ai"
            except Exception as e:
                logger.error(f"Gemini classification failed: {e}")
                self.ai_failure_count += 1
        
        # Fallback to rule-based
        self.fallback_count += 1
        return self._classify_rule_based(changes), "rule_based"
    
    def _classify_with_gemini(self, changes: List[Dict]) -> Optional[List[Dict]]:
        """Classify using Gemini AI."""
        if not self.gemini_model:
            return None
        
        try:
            changes_json = json.dumps(changes, default=str)
            prompt = f"""
            Classify each change as "important", "minor", or "needs_review".
            Consider career impact, skill relevance, and industry standards.
            
            Changes:
            {changes_json}
            
            Return ONLY valid JSON array:
            [{{"index": 0, "severity": "important", "reason": "reason"}}]
            """
            
            response = self.gemini_model.generate_content(prompt, timeout=30)
            
            response_text = response.text
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            classifications = json.loads(response_text.strip())
            
            # Merge with changes
            for classification in classifications:
                idx = classification.get('index')
                if idx is not None and idx < len(changes):
                    changes[idx]['severity'] = classification.get('severity', 'needs_review')
                    changes[idx]['classification_reason'] = classification.get('reason', '')
                    changes[idx]['confidence'] = 0.85
            
            return changes
            
        except Exception as e:
            logger.error(f"Gemini classification error: {e}")
            return None
    
    def _classify_rule_based(self, changes: List[Dict]) -> List[Dict]:
        """Rule-based classification."""
        for i, change in enumerate(changes):
            change_type = change.get('type', '')
            
            if change_type in ['employer_changed', 'job_title_changed', 'education_added']:
                change['severity'] = 'important'
                change['classification_reason'] = f'Significant career change: {change_type}'
            
            elif change_type == 'skill_added':
                skill = change.get('new_value', '').lower()
                important_skills = ['python', 'java', 'aws', 'docker', 'kubernetes', 
                                  'react', 'typescript', 'machine learning', 'ai']
                if any(s in skill for s in important_skills):
                    change['severity'] = 'important'
                    change['classification_reason'] = f'Important skill added: {skill}'
                else:
                    change['severity'] = 'minor'
                    change['classification_reason'] = f'Skill added: {skill}'
            
            elif change_type in ['experience_increased']:
                diff = change.get('context', {}).get('diff', 0)
                if diff >= 2:
                    change['severity'] = 'important'
                    change['classification_reason'] = f'Significant experience increase: {diff} years'
                else:
                    change['severity'] = 'minor'
                    change['classification_reason'] = f'Minor experience increase: {diff} years'
            
            elif change_type in ['location_changed', 'employment_date_overlap']:
                change['severity'] = 'needs_review'
                change['classification_reason'] = f'Change needs verification: {change_type}'
            
            else:
                change['severity'] = 'minor'
                change['classification_reason'] = 'Minor change detected'
            
            change['confidence'] = 0.8
        
        return changes
    
    def generate_summary(self, changes: List[Dict], profile: Dict) -> Tuple[str, str]:
        """Generate summary with AI fallback."""
        if self._should_use_ai():
            try:
                result = self._summary_with_gemini(changes, profile)
                if result:
                    self.ai_success_count += 1
                    return result, "ai"
            except Exception as e:
                logger.error(f"Gemini summary failed: {e}")
                self.ai_failure_count += 1
        
        # Fallback to rule-based
        self.fallback_count += 1
        return self._summary_rule_based(changes), "rule_based"
    
    def _summary_with_gemini(self, changes: List[Dict], profile: Dict) -> Optional[str]:
        """Generate summary using Gemini."""
        if not self.gemini_model:
            return None
        
        try:
            changes_summary = [{
                "type": c.get('type', ''),
                "description": c.get('description', ''),
                "severity": c.get('severity', '')
            } for c in changes[:20]]
            
            changes_json = json.dumps(changes_summary, default=str)
            profile_json = json.dumps(profile, default=str)
            
            prompt = f"""
            Generate a professional summary of profile changes.
            Format: 2-3 paragraphs, recruiter-friendly tone.
            
            Profile: {profile_json[:2000]}
            Changes: {changes_json}
            
            Summary:
            """
            
            response = self.gemini_model.generate_content(prompt, timeout=30)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini summary error: {e}")
            return None
    
    def _summary_rule_based(self, changes: List[Dict]) -> str:
        """Rule-based summary generation."""
        if not changes:
            return "No changes detected in the candidate's profile."
        
        # Group changes by type
        changes_by_type = {}
        for change in changes:
            change_type = change.get('type', 'unknown')
            if change_type not in changes_by_type:
                changes_by_type[change_type] = []
            changes_by_type[change_type].append(change)
        
        summary_parts = []
        for change_type, type_changes in changes_by_type.items():
            count = len(type_changes)
            label = change_type.replace('_', ' ').title()
            summary_parts.append(f"{count} {label}")
        
        summary = f"Detected changes: {', '.join(summary_parts)}"
        
        if changes_by_type.get('employer_changed'):
            summary += " Company change detected."
        if changes_by_type.get('skill_added'):
            top_skills = [c.get('new_value', '') for c in changes_by_type['skill_added'][:3]]
            summary += f" New skills: {', '.join(top_skills)}"
        
        return summary
    
    def _should_use_ai(self) -> bool:
        """Check if AI should be used."""
        if not self.use_ai or not self.gemini_model:
            return False
        
        # Check token limits
        if self.token_usage >= self.token_limit:
            logger.warning("AI token limit reached")
            return False
        
        return True
    
    def _track_tokens(self, text: str):
        """Track token usage."""
        self.token_usage += len(text.split())
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI service status."""
        total = self.ai_success_count + self.ai_failure_count + self.fallback_count
        return {
            "enabled": self.use_ai,
            "ai_enabled": bool(self.gemini_model),
            "ai_success_count": self.ai_success_count,
            "ai_failure_count": self.ai_failure_count,
            "fallback_count": self.fallback_count,
            "token_used": self.token_usage,
            "token_limit": self.token_limit,
            "token_remaining": max(0, self.token_limit - self.token_usage),
            "success_rate": (self.ai_success_count / (total + 1)) * 100,
            "fallback_rate": (self.fallback_count / (total + 1)) * 100,
            "spacy_available": SPACY_AVAILABLE,
            "sentence_transformer_available": SENTENCE_TRANSFORMER_AVAILABLE
        }