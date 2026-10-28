from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..config import STORAGE_ROOT, settings
from ..db import get_db
from ..models import User, Project
from ..auth.deps import get_current_user

router = APIRouter(tags=["styles"])
MAX_MOGRT_BYTES = min(settings.max_upload_mb, 500) * 1024 * 1024

@router.post("/projects/{project_id}/styles/mogrt")
async def upload_mogrt(project_id: int, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.scalar(select(Project).where(Project.id == project_id, Project.user_id == user.id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if Path(file.filename or "").suffix.lower() != ".mogrt":
        raise HTTPException(status_code=415, detail="Please upload a .mogrt file")
    folder = STORAGE_ROOT / str(user.id) / str(project_id) / "styles"
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"{uuid.uuid4().hex}.mogrt"
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_MOGRT_BYTES:
                    raise HTTPException(status_code=413, detail="MOGRT file exceeds upload limit")
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return {"filename": Path(file.filename or "style.mogrt").name[:255], "size_bytes": size,
            "status": "uploaded", "render_note": "MOGRT stored as a style asset. Premiere Pro/After Effects is required to render the template; FFmpeg does not execute MOGRT files."}
