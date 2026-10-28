from pathlib import Path
import subprocess
from faster_whisper import WhisperModel
from .ffmpeg import get_ffmpeg_path
_cache={}
def group_words(words):
 lines=[]; current=[]
 for w in words:
  if not current: current=[w]; continue
  joined=''.join(x['text'] for x in current)+w['text']; duration=w['end']-current[0]['start']
  if len(joined)>42 or duration>2.5 or joined.rstrip().endswith(('.', '?','!','।')):
   lines.append({'start':current[0]['start'],'end':current[-1]['end'],'text':''.join(x['text'] for x in current).strip(),'words':current}); current=[w]
  else: current.append(w)
 if current: lines.append({'start':current[0]['start'],'end':current[-1]['end'],'text':''.join(x['text'] for x in current).strip(),'words':current})
 return lines
def transcribe_file(path,language=None,model_size='small'):
 ffmpeg = get_ffmpeg_path()
 wav=str(Path(path).with_suffix('.localsubs.wav'))
 subprocess.run([ffmpeg,'-y','-i',path,'-vn','-ac','1','-ar','16000',wav],check=True,capture_output=True,text=True)
 try:
  model=_cache.get(model_size)
  if model is None:
   import ctranslate2
   device='cuda' if ctranslate2.get_cuda_device_count() else 'cpu'
   model=WhisperModel(model_size,device=device,compute_type='float16' if device=='cuda' else 'int8'); _cache[model_size]=model
  segments,_=model.transcribe(wav,language=language,word_timestamps=True,vad_filter=True)
  return group_words([{'start':float(w.start),'end':float(w.end),'text':w.word} for seg in segments for w in (seg.words or [])])
 finally: Path(wav).unlink(missing_ok=True)
