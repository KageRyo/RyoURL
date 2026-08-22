import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "tests" / ".env")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8003/api/')

from anonymous_user import AnonymousUser
from authenticated_user import AuthenticatedUser
from admin_user import AdminUser
