import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")
SESSION_SECRET = os.getenv("SESSION_SECRET")
