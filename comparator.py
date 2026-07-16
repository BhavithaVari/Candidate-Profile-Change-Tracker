"""
Comparison engine with AI fallback support.
"""

from typing import Dict, List, Any, Tuple
from backend.ai_service import AIService
from backend.classifier import ChangeClassifier
import logging

logger = logging.getLogger(__name__)

class Comparator:
    """Compares two profiles with AI enhancement and fallback."""
    
    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()
        self.classifier = ChangeClassifier(self.ai_service)
    
    def compare_profiles(self, prev_profile: Dict, updated_profile: Dict) -> Dict[str, Any]:
        """
        Compare two profiles with automatic AI fallback.
        """
        # Detect changes (rule-based)
        changes = self._detect_changes(prev_profile, updated_profile)
        
        # Classify changes (with AI fallback)
        classified_changes, method = self.classifier.classify_changes(changes)
        
        # Generate summary (with AI fallback)
        if self.ai_service.use_ai:
            summary, summary_method = self.ai_service.generate_summary(classified_changes, updated_profile)
        else:
            summary, summary_method = self._generate_summary(classified_changes), "rule_based"
        
        # Calculate statistics
        stats = self._calculate_statistics(classified_changes)
        
        return {
            "changes": classified_changes,
            "summary": summary,
            "statistics": stats,
            "overall_status": self._determine_overall_status(stats),
            "classification_method": method,
            "summary_method": summary_method,
            "ai_status": self.ai_service.get_status()
        }
    
    def _detect_changes(self, prev: Dict, updated: Dict) -> List[Dict]:
        """Detect changes using rule-based logic."""
        changes = []
        
        # Compare skills
        changes.extend(self._compare_skills(
            prev.get('skills', []),
            updated.get('skills', [])
        ))
        
        # Compare employers
        changes.extend(self._compare_employers(
            prev.get('employers', []),
            updated.get('employers', [])
        ))
        
        # Compare job titles
        changes.extend(self._compare_job_titles(
            prev.get('job_titles', []),
            updated.get('job_titles', [])
        ))
        
        # Compare experience
        changes.extend(self._compare_experience(
            prev.get('experience_years', 0),
            updated.get('experience_years', 0)
        ))
        
        # Compare location
        changes.extend(self._compare_location(
            prev.get('location', ''),
            updated.get('location', '')
        ))
        
        # Compare education
        changes.extend(self._compare_education(
            prev.get('education', []),
            updated.get('education', [])
        ))
        
        # Compare employment dates
        changes.extend(self._compare_employment_dates(
            prev.get('employment_dates', []),
            updated.get('employment_dates', [])
        ))
        
        return changes
    
    def _compare_skills(self, prev_skills: List[str], new_skills: List[str]) -> List[Dict]:
        """Compare skills."""
        changes = []
        prev_set = set(s.lower() for s in prev_skills)
        new_set = set(s.lower() for s in new_skills)
        
        # Added skills
        for skill in new_set - prev_set:
            changes.append({
                "type": "skill_added",
                "title": f"New skill: {skill}",
                "description": f"Added {skill} to skills",
                "previous_value": None,
                "new_value": skill,
                "context": {"skill": skill}
            })
        
        # Removed skills
        for skill in prev_set - new_set:
            changes.append({
                "type": "skill_removed",
                "title": f"Skill removed: {skill}",
                "description": f"Removed {skill} from skills",
                "previous_value": skill,
                "new_value": None,
                "context": {"skill": skill}
            })
        
        return changes
    
    def _compare_employers(self, prev_employers: List[str], new_employers: List[str]) -> List[Dict]:
        """Compare employers."""
        changes = []
        
        if prev_employers and new_employers:
            prev_set = set(e.lower() for e in prev_employers)
            new_set = set(e.lower() for e in new_employers)
            
            if prev_set != new_set:
                changes.append({
                    "type": "employer_changed",
                    "title": "Employer changed",
                    "description": f"Changed from {', '.join(prev_employers[:2])} to {', '.join(new_employers[:2])}",
                    "previous_value": ", ".join(prev_employers[:2]),
                    "new_value": ", ".join(new_employers[:2]),
                    "context": {"prev": prev_employers, "new": new_employers}
                })
        
        return changes
    
    def _compare_job_titles(self, prev_titles: List[str], new_titles: List[str]) -> List[Dict]:
        """Compare job titles."""
        changes = []
        
        if prev_titles and new_titles:
            if prev_titles[0] != new_titles[0]:
                changes.append({
                    "type": "job_title_changed",
                    "title": "Job title changed",
                    "description": f"Title changed from {prev_titles[0]} to {new_titles[0]}",
                    "previous_value": prev_titles[0],
                    "new_value": new_titles[0],
                    "context": {"prev": prev_titles, "new": new_titles}
                })
        
        return changes
    
    def _compare_experience(self, prev_years: float, new_years: float) -> List[Dict]:
        """Compare experience."""
        changes = []
        
        if new_years > prev_years:
            diff = new_years - prev_years
            changes.append({
                "type": "experience_increased",
                "title": f"Experience increased by {diff:.1f} years",
                "description": f"Total experience from {prev_years:.1f} to {new_years:.1f} years",
                "previous_value": str(prev_years),
                "new_value": str(new_years),
                "context": {"diff": diff}
            })
        elif prev_years > new_years:
            diff = prev_years - new_years
            changes.append({
                "type": "experience_decreased",
                "title": f"Experience decreased by {diff:.1f} years",
                "description": f"Total experience from {prev_years:.1f} to {new_years:.1f} years",
                "previous_value": str(prev_years),
                "new_value": str(new_years),
                "context": {"diff": diff}
            })
        
        return changes
    
    def _compare_location(self, prev_location: str, new_location: str) -> List[Dict]:
        """Compare location."""
        changes = []
        
        if prev_location and new_location and prev_location != new_location:
            changes.append({
                "type": "location_changed",
                "title": "Location changed",
                "description": f"Location changed from {prev_location} to {new_location}",
                "previous_value": prev_location,
                "new_value": new_location,
                "context": {"prev": prev_location, "new": new_location}
            })
        
        return changes
    
    def _compare_education(self, prev_education: List[Dict], new_education: List[Dict]) -> List[Dict]:
        """Compare education."""
        changes = []
        
        if len(new_education) > len(prev_education):
            for edu in new_education:
                if edu not in prev_education:
                    changes.append({
                        "type": "education_added",
                        "title": f"Education added: {edu.get('degree', '')}",
                        "description": f"Added {edu.get('degree', '')} from {edu.get('institution', '')}",
                        "previous_value": None,
                        "new_value": edu.get('degree', ''),
                        "context": {"education": edu}
                    })
        
        return changes
    
    def _compare_employment_dates(self, prev_dates: List[Dict], new_dates: List[Dict]) -> List[Dict]:
        """Compare employment dates."""
        changes = []
        
        # Check for gaps or overlaps (simplified)
        if len(new_dates) > 1:
            for i in range(1, len(new_dates)):
                # Simple check for overlap
                pass
        
        return changes
    
    def _generate_summary(self, changes: List[Dict]) -> str:
        """Generate rule-based summary."""
        if not changes:
            return "No changes detected."
        
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
        
        return f"Detected changes: {', '.join(summary_parts)}"
    
    def _calculate_statistics(self, changes: List[Dict]) -> Dict[str, int]:
        """Calculate statistics."""
        stats = {
            "total": len(changes),
            "important": 0,
            "minor": 0,
            "needs_review": 0
        }
        
        for change in changes:
            severity = change.get('severity', 'minor')
            if severity == 'important':
                stats['important'] += 1
            elif severity == 'needs_review':
                stats['needs_review'] += 1
            else:
                stats['minor'] += 1
        
        return stats
    
    def _determine_overall_status(self, stats: Dict[str, int]) -> str:
        """Determine overall status."""
        if stats['total'] == 0:
            return "No Significant Changes"
        
        important_ratio = stats['important'] / stats['total']
        
        if important_ratio > 0.5:
            return "Significant Profile Update"
        elif important_ratio > 0.25:
            return "Moderate Profile Update"
        else:
            return "Minor Profile Update"