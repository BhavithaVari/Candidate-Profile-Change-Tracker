# test_imports.py
print("Testing imports...")

try:
    from backend.database import Database
    print("✓ Database imported successfully")
except Exception as e:
    print(f"✗ Database import failed: {e}")

try:
    from backend.models import Candidate, Resume, Comparison
    print("✓ Models imported successfully")
except Exception as e:
    print(f"✗ Models import failed: {e}")

try:
    from backend.ai_service import AIService
    print("✓ AI Service imported successfully")
except Exception as e:
    print(f"✗ AI Service import failed: {e}")

try:
    from backend.classifier import ChangeClassifier
    print("✓ Classifier imported successfully")
except Exception as e:
    print(f"✗ Classifier import failed: {e}")

try:
    from backend.comparator import Comparator
    print("✓ Comparator imported successfully")
except Exception as e:
    print(f"✗ Comparator import failed: {e}")

try:
    from backend.profile_extractor import ProfileExtractor
    print("✓ Profile Extractor imported successfully")
except Exception as e:
    print(f"✗ Profile Extractor import failed: {e}")

print("\nAll imports tested!")