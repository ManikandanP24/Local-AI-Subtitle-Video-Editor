from pathlib import Path
import subprocess
from collections.abc import Callable

from faster_whisper import WhisperModel
from .ffmpeg import get_ffmpeg_path

_cache = {}


def group_words(words):
    lines = []
    current = []
    for word in words:
        if not current:
            current = [word]
            continue
        joined = ''.join(item['text'] for item in current) + word['text']
        duration = word['end'] - current[0]['start']
        if len(joined) > 42 or duration > 2.5 or joined.rstrip().endswith(('.', '?', '!', '।')):
            lines.append({
                'start': current[0]['start'],
                'end': current[-1]['end'],
                'text': ''.join(item['text'] for item in current).strip(),
                'words': current,
            })
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append({
            'start': current[0]['start'],
            'end': current[-1]['end'],
            'text': ''.join(item['text'] for item in current).strip(),
            'words': current,
        })
    return lines


def transcribe_file(path, language=None, model_size='small', progress_callback: Callable[[int], None] | None = None):
    ffmpeg = get_ffmpeg_path()
    wav = str(Path(path).with_suffix('.localsubs.wav'))
    if progress_callback:
        progress_callback(5)
    subprocess.run(
        [ffmpeg, '-y', '-i', path, '-vn', '-ac', '1', '-ar', '16000', wav],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        if progress_callback:
            progress_callback(15)

        model = _cache.get(model_size)
        if model is None:
            import ctranslate2
            device = 'cuda' if ctranslate2.get_cuda_device_count() else 'cpu'
            model = WhisperModel(
                model_size,
                device=device,
                compute_type='float16' if device == 'cuda' else 'int8',
            )
            _cache[model_size] = model
        if progress_callback:
            progress_callback(28)

        segments, info = model.transcribe(
            wav,
            language=language,
            word_timestamps=True,
            vad_filter=True,
        )
        duration = float(getattr(info, 'duration', 0) or 0)
        words = []
        last_progress = 28
        for segment in segments:
            words.extend(
                {'start': float(word.start), 'end': float(word.end), 'text': word.word}
                for word in (segment.words or [])
            )
            if progress_callback and duration > 0:
                current_progress = min(88, 28 + int(60 * min(float(segment.end) / duration, 1.0)))
                if current_progress > last_progress:
                    progress_callback(current_progress)
                    last_progress = current_progress

        if progress_callback:
            progress_callback(92)
        return group_words(words)
    finally:
        Path(wav).unlink(missing_ok=True)
