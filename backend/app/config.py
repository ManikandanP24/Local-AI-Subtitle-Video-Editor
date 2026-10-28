from pathlib import Path
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    jwt_secret: str = ""
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    whisper_model: str = "small"
    storage_dir: str = "../storage"
    max_upload_mb: int = 2048
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    admin_email: str = "admin@localsubs.app"
    admin_password: str = ""


settings = Settings()

# Generate and persist a secret for local development without overwriting
# the other values already present in backend/.env.
if not settings.jwt_secret:
    settings.jwt_secret = secrets.token_urlsafe(48)
    env_file = ROOT / ".env"
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines() if env_file.exists() else []
        for index, line in enumerate(lines):
            if line.strip().startswith("JWT_SECRET="):
                lines[index] = f"JWT_SECRET={settings.jwt_secret}"
                break
        else:
            lines.insert(0, f"JWT_SECRET={settings.jwt_secret}")
        env_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    except OSError:
        # The current process can still use its in-memory secret if the .env
        # file is read-only or the app is running in a restricted environment.
        pass

STORAGE_ROOT = Path(settings.storage_dir)
if not STORAGE_ROOT.is_absolute():
    STORAGE_ROOT = (ROOT / STORAGE_ROOT).resolve()
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
