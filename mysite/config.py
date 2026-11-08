from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'coursera_secret_key_fastapi_backend_2026_motionweb')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_LIFETIME_DAYS = int(os.getenv('ACCESS_TOKEN_LIFETIME_DAYS', '7'))
REFRESH_TOKEN_LIFETIME_DAYS = int(os.getenv('REFRESH_TOKEN_LIFETIME_DAYS', '60'))
