from pathlib import Path
import shutil,uuid,json,subprocess,re
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Response,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from .config import settings,STORAGE_ROOT
from .db import Base,engine,get_db
from .models import User,Project,MediaFile,SubtitleLine,Job
from .schemas import ProjectCreate,SubtitleBatch,TranscribeRequest
from .auth.routes import router as auth_router
from .auth.deps import get_current_user
from .services.transcribe import transcribe_file
from .services.exporters import export_srt,export_vtt,export_txt,export_ass
from .routes_styles import router as styles_router
Base.metadata.create_all(bind=engine)
app=FastAPI(title='LocalSubs API',version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(',') if x.strip()],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(auth_router); app.include_router(styles_router)
ALLOWED={'.mp4','.mov','.mkv','.webm','.mp3','.wav'}; MAX_BYTES=settings.max_upload_mb*1024*1024
@app.get('/health')
def health(): return {'ok':True,'ffmpeg':bool(shutil.which('ffmpeg')),'transcription':'local model loads on demand'}
def owned_project(pid,user,db):
 p=db.scalar(select(Project).where(Project.id==pid,Project.user_id==user.id))
 if not p: raise HTTPException(404,'Project not found')
 return p
def project_json(p): return {'id':p.id,'title':p.title,'language':p.language,'created_at':p.created_at.isoformat(),'media_count':len(p.media),'subtitle_count':len(p.subtitles)}
@app.get('/projects')
def list_projects(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 return [project_json(p) for p in db.scalars(select(Project).where(Project.user_id==user.id).order_by(Project.updated_at.desc())).all()]
@app.post('/projects')
def create_project(data:ProjectCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 p=Project(user_id=user.id,title=data.title.strip(),language=data.language); db.add(p); db.commit(); db.refresh(p); return project_json(p)
@app.get('/projects/{project_id}')
def get_project(project_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return project_json(owned_project(project_id,user,db))
@app.patch('/projects/{project_id}')
def update_project(project_id:int,data:ProjectCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 p=owned_project(project_id,user,db); p.title=data.title.strip(); p.language=data.language; db.commit(); db.refresh(p); return project_json(p)
@app.delete('/projects/{project_id}')
def delete_project(project_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 p=owned_project(project_id,user,db)
 for item in p.media:
  try: Path(item.path).unlink(missing_ok=True)
  except Exception: pass
 db.delete(p); db.commit(); return {'ok':True}
@app.post('/projects/{project_id}/media')
async def upload_media(project_id:int,file:UploadFile=File(...),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 p=owned_project(project_id,user,db); ext=Path(file.filename or '').suffix.lower()
 if ext not in ALLOWED: raise HTTPException(415,'Unsupported media type')
 folder=STORAGE_ROOT/str(user.id)/str(p.id); folder.mkdir(parents=True,exist_ok=True); target=folder/(uuid.uuid4().hex+ext); size=0
 try:
  with target.open('wb') as output:
   while True:
    chunk=await file.read(1024*1024)
    if not chunk: break
    size+=len(chunk)
    if size>MAX_BYTES: raise HTTPException(413,'File exceeds upload limit')
    output.write(chunk)
 except Exception: target.unlink(missing_ok=True); raise
 duration=None
 if shutil.which('ffprobe'):
  try:
   result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(target)],capture_output=True,text=True,timeout=15)
   if result.returncode==0: duration=float(result.stdout.strip())
  except Exception: pass
 media=MediaFile(project_id=p.id,path=str(target),original_name=Path(file.filename or 'media').name[:255],duration=duration); db.add(media); db.commit(); db.refresh(media)
 return {'id':media.id,'filename':media.original_name,'duration':duration,'stream_url':f'/projects/{p.id}/media/{media.id}/stream'}
@app.get('/projects/{project_id}/media/{media_id}/stream')
def stream_media(project_id:int,media_id:int,request:Request,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 owned_project(project_id,user,db); media=db.scalar(select(MediaFile).join(Project).where(MediaFile.id==media_id,MediaFile.project_id==project_id,Project.user_id==user.id))
 if not media or not Path(media.path).exists(): raise HTTPException(404,'Media not found')
 path=Path(media.path); size=path.stat().st_size; mime='video/mp4' if path.suffix.lower() in {'.mp4','.mov','.mkv','.webm'} else 'audio/mpeg'; rh=request.headers.get('range')
 if not rh: return FileResponse(path,media_type=mime,headers={'Accept-Ranges':'bytes'})
 match=re.match(r'bytes=(\d*)-(\d*)',rh)
 if not match: raise HTTPException(416,'Invalid range')
 start=int(match.group(1) or 0); end=int(match.group(2) or size-1)
 if start>=size or end<start: raise HTTPException(416,'Range not satisfiable')
 end=min(end,size-1)
 def chunks():
  with path.open('rb') as f:
   f.seek(start); remaining=end-start+1
   while remaining:
    data=f.read(min(1024*1024,remaining))
    if not data: break
    remaining-=len(data); yield data
 return StreamingResponse(chunks(),status_code=206,media_type=mime,headers={'Content-Range':f'bytes {start}-{end}/{size}','Accept-Ranges':'bytes','Content-Length':str(end-start+1)})
@app.get('/projects/{project_id}/subtitles')
def get_subtitles(project_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 owned_project(project_id,user,db); rows=db.scalars(select(SubtitleLine).where(SubtitleLine.project_id==project_id).order_by(SubtitleLine.line_index)).all()
 return [{'id':x.id,'start':x.start,'end':x.end,'text':x.text,'words':json.loads(x.words_json) if x.words_json else None} for x in rows]
@app.put('/projects/{project_id}/subtitles')
def put_subtitles(project_id:int,batch:SubtitleBatch,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 p=owned_project(project_id,user,db)
 for i,line in enumerate(batch.lines):
  if line.end<=line.start: raise HTTPException(422,f'Subtitle line {i+1} end must be after start')
 db.query(SubtitleLine).filter(SubtitleLine.project_id==p.id).delete()
 for i,line in enumerate(batch.lines): db.add(SubtitleLine(project_id=p.id,line_index=i,start=line.start,end=line.end,text=line.text,words_json=json.dumps(line.words,ensure_ascii=False) if line.words else None))
 db.commit(); return {'ok':True,'count':len(batch.lines)}
@app.post('/projects/{project_id}/transcribe')
def transcribe(project_id:int,data:TranscribeRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 p=owned_project(project_id,user,db); media=db.scalar(select(MediaFile).where(MediaFile.project_id==p.id).order_by(MediaFile.id.desc()))
 if not media: raise HTTPException(400,'Upload a media file first')
 job=Job(project_id=p.id,type='transcribe',status='running',progress=5); db.add(job); db.commit(); db.refresh(job)
 try:
  lines=transcribe_file(media.path,data.language or (None if p.language=='auto' else p.language),data.model_size or settings.whisper_model)
  db.query(SubtitleLine).filter(SubtitleLine.project_id==p.id).delete()
  for i,line in enumerate(lines): db.add(SubtitleLine(project_id=p.id,line_index=i,start=line['start'],end=line['end'],text=line['text'],words_json=json.dumps(line.get('words'),ensure_ascii=False)))
  job.status='done'; job.progress=100; db.commit(); return {'job_id':job.id,'status':job.status,'count':len(lines)}
 except Exception as exc:
  job.status='failed'; job.error=str(exc)[:1000]; db.commit(); raise HTTPException(500,f'Transcription failed: {str(exc)[:300]}')
@app.get('/jobs/{job_id}')
def get_job(job_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 job=db.scalar(select(Job).join(Project).where(Job.id==job_id,Project.user_id==user.id))
 if not job: raise HTTPException(404,'Job not found')
 return {'id':job.id,'type':job.type,'status':job.status,'progress':job.progress,'error':job.error}
@app.get('/projects/{project_id}/export/{fmt}')
def export_subtitles(project_id:int,fmt:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 owned_project(project_id,user,db); rows=db.scalars(select(SubtitleLine).where(SubtitleLine.project_id==project_id).order_by(SubtitleLine.line_index)).all(); lines=[{'start':x.start,'end':x.end,'text':x.text} for x in rows]
 formats={'srt':(export_srt,'application/x-subrip'),'vtt':(export_vtt,'text/vtt'),'txt':(export_txt,'text/plain'),'ass':(export_ass,'text/plain')}
 if fmt not in formats: raise HTTPException(400,'Supported formats: srt, vtt, txt, ass')
 fn,mime=formats[fmt]; return Response(content=fn(lines),media_type=mime,headers={'Content-Disposition':f'attachment; filename="localsubs-{project_id}.{fmt}"'})
