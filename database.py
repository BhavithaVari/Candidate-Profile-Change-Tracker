"""
Database operations for resume tracking.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database operations for the application."""
    
    def __init__(self, db_path: str = "resume_tracker.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create candidates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create resumes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER,
                    version TEXT,
                    content TEXT,
                    profile TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id)
                )
            """)
            
            # Create comparisons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER,
                    prev_resume_id INTEGER,
                    updated_resume_id INTEGER,
                    result TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                    FOREIGN KEY (prev_resume_id) REFERENCES resumes (id),
                    FOREIGN KEY (updated_resume_id) REFERENCES resumes (id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def create_or_get_candidate(self, name: str, email: str = "") -> int:
        """Create a new candidate or get existing one."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if candidate exists
            cursor.execute(
                "SELECT id FROM candidates WHERE name = ? AND email = ?",
                (name, email)
            )
            result = cursor.fetchone()
            
            if result:
                candidate_id = result[0]
            else:
                cursor.execute(
                    "INSERT INTO candidates (name, email) VALUES (?, ?)",
                    (name, email)
                )
                candidate_id = cursor.lastrowid
                conn.commit()
            
            conn.close()
            return candidate_id
        except Exception as e:
            logger.error(f"Error creating/getting candidate: {e}")
            raise
    
    def save_resume(self, candidate_id: int, version: str, content: str, profile: Dict) -> int:
        """Save a resume to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            profile_json = json.dumps(profile, default=str)
            
            cursor.execute(
                """INSERT INTO resumes (candidate_id, version, content, profile)
                   VALUES (?, ?, ?, ?)""",
                (candidate_id, version, content, profile_json)
            )
            
            resume_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return resume_id
        except Exception as e:
            logger.error(f"Error saving resume: {e}")
            raise
    
    def save_comparison(self, candidate_id: int, prev_resume_id: int, 
                       updated_resume_id: int, result: Dict) -> int:
        """Save comparison result to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            result_json = json.dumps(result, default=str)
            
            cursor.execute(
                """INSERT INTO comparisons (candidate_id, prev_resume_id, updated_resume_id, result)
                   VALUES (?, ?, ?, ?)""",
                (candidate_id, prev_resume_id, updated_resume_id, result_json)
            )
            
            comparison_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return comparison_id
        except Exception as e:
            logger.error(f"Error saving comparison: {e}")
            raise
    
    def get_all_candidates(self) -> List[Dict]:
        """Get all candidates."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            return []
    
    def get_all_comparisons(self) -> List[Dict]:
        """Get all comparisons."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.*, cand.name as candidate_name
                FROM comparisons c
                LEFT JOIN candidates cand ON c.candidate_id = cand.id
                ORDER BY c.created_at DESC
            """)
            results = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON result
            for result in results:
                if result.get('result'):
                    try:
                        result['result'] = json.loads(result['result'])
                        result['overall_status'] = result['result'].get('overall_status', 'N/A')
                        result['total_changes'] = result['result'].get('statistics', {}).get('total', 0)
                        result['important_changes'] = result['result'].get('statistics', {}).get('important', 0)
                        result['minor_changes'] = result['result'].get('statistics', {}).get('minor', 0)
                        result['needs_review_changes'] = result['result'].get('statistics', {}).get('needs_review', 0)
                    except:
                        pass
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting comparisons: {e}")
            return []
    
    def get_comparison(self, comparison_id: int) -> Optional[Dict]:
        """Get a specific comparison."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM comparisons WHERE id = ?",
                (comparison_id,)
            )
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                data = dict(result)
                if data.get('result'):
                    data['result'] = json.loads(data['result'])
                return data
            
            return None
        except Exception as e:
            logger.error(f"Error getting comparison: {e}")
            return None
    
    def get_candidate_comparisons(self, candidate_id: int) -> List[Dict]:
        """Get all comparisons for a candidate."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM comparisons WHERE candidate_id = ? ORDER BY created_at DESC",
                (candidate_id,)
            )
            results = [dict(row) for row in cursor.fetchall()]
            
            for result in results:
                if result.get('result'):
                    try:
                        result['result'] = json.loads(result['result'])
                    except:
                        pass
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting candidate comparisons: {e}")
            return []