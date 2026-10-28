import shutil
from functools import lru_cache

@lru_cache(maxsize=1)
def get_ffmpeg_path() -> str:
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path:
            return path
    except Exception:
        pass
    raise RuntimeError('FFmpeg is required. Install it on the host or include imageio-ffmpeg.')

def ffmpeg_available() -> bool:
    try:
        get_ffmpeg_path()
        return True
    except RuntimeError:
        return False
