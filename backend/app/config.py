from pathlib import Path
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict
ROOT = Path(__file__).resolve().parents[1]
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    jwt_secret: str = ''
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    whisper_model: str = 'small'
    storage_dir: str = '../storage'
    max_upload_mb: int = 2048
    cors_origins: str = 'http://localhost:5173'
settings = Settings()
if not settings.jwt_secret:
    settings.jwt_secret = secrets.token_urlsafe(48)
    env = ROOT / '.env'
    env.write_text(f'JWT_SECRET={settings.jwt_secret}\n')
STORAGE_ROOT = Path(settings.storage_dir)
if not STORAGE_ROOT.is_absolute(): STORAGE_ROOT = (ROOT / STORAGE_ROOT).resolve()
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
