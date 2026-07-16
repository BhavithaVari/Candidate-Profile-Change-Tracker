"""
Data models for the application.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Candidate:
    """Candidate model representing a person whose resume is being tracked."""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Candidate':
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            email=data.get('email', ''),
            created_at=data.get('created_at')
        )

@dataclass
class Resume:
    """Resume model representing a candidate's resume version."""
    id: Optional[int] = None
    candidate_id: int = 0
    version: str = ""
    content: str = ""
    profile: Dict[str, Any] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.profile is None:
            self.profile = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "version": self.version,
            "content": self.content,
            "profile": self.profile,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resume':
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            candidate_id=data.get('candidate_id', 0),
            version=data.get('version', ''),
            content=data.get('content', ''),
            profile=data.get('profile', {}),
            created_at=data.get('created_at')
        )

@dataclass
class Comparison:
    """Comparison model representing a comparison between two resume versions."""
    id: Optional[int] = None
    candidate_id: int = 0
    prev_resume_id: int = 0
    updated_resume_id: int = 0
    result: Dict[str, Any] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.result is None:
            self.result = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "prev_resume_id": self.prev_resume_id,
            "updated_resume_id": self.updated_resume_id,
            "result": self.result,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comparison':
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            candidate_id=data.get('candidate_id', 0),
            prev_resume_id=data.get('prev_resume_id', 0),
            updated_resume_id=data.get('updated_resume_id', 0),
            result=data.get('result', {}),
            created_at=data.get('created_at')
        )