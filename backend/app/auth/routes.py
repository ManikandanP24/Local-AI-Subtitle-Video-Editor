from datetime import datetime,timedelta,timezone
import uuid
from fastapi import APIRouter,Depends,HTTPException,Response,Cookie
from sqlalchemy.orm import Session
from sqlalchemy import select,update
from ..config import settings
from ..db import get_db
from ..models import User,RefreshToken
from ..schemas import Credentials
from .security import hash_password,verify_password,new_refresh,hash_refresh,create_access_token
from .deps import get_current_user
router=APIRouter(prefix='/auth',tags=['auth'])
COOKIE='localsubs_refresh'
def issue(db,user_id,family):
 raw=new_refresh(); db.add(RefreshToken(user_id=user_id,family_id=family,token_hash=hash_refresh(raw),expires_at=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_days))); return raw
def payload(user): return {'access_token':create_access_token(user.id),'token_type':'bearer','user':{'id':user.id,'email':user.email,'is_admin':bool(user.is_admin)}}
def set_cookie(response,raw): response.set_cookie(COOKIE,raw,httponly=True,samesite='lax',secure=True,max_age=settings.refresh_token_days*86400,path='/auth')
@router.post('/register')
def register(data:Credentials,response:Response,db:Session=Depends(get_db)):
 email=data.email.lower().strip()
 if db.scalar(select(User).where(User.email==email)): raise HTTPException(400,'Unable to create account with these details')
 user=User(email=email,password_hash=hash_password(data.password)); db.add(user); db.flush(); raw=issue(db,user.id,uuid.uuid4().hex); db.commit(); set_cookie(response,raw); return payload(user)
@router.post('/login')
def login(data:Credentials,response:Response,db:Session=Depends(get_db)):
 user=db.scalar(select(User).where(User.email==data.email.lower().strip()))
 if not user or not verify_password(user.password_hash,data.password): raise HTTPException(401,'Invalid email or password')
 raw=issue(db,user.id,uuid.uuid4().hex); db.commit(); set_cookie(response,raw); return payload(user)
@router.post('/refresh')
def refresh(response:Response,raw:str|None=Cookie(default=None,alias=COOKIE),db:Session=Depends(get_db)):
 if not raw: raise HTTPException(401,'Refresh token missing')
 token=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==hash_refresh(raw)))
 if not token: raise HTTPException(401,'Invalid refresh token')
 now=datetime.now(timezone.utc); expiry=token.expires_at
 if expiry.tzinfo is None: expiry=expiry.replace(tzinfo=timezone.utc)
 if token.revoked_at:
  db.execute(update(RefreshToken).where(RefreshToken.family_id==token.family_id).values(revoked_at=now)); db.commit(); response.delete_cookie(COOKIE,path='/auth'); raise HTTPException(401,'Refresh token reuse detected; sign in again')
 if expiry<=now: token.revoked_at=now; db.commit(); raise HTTPException(401,'Refresh token expired')
 token.revoked_at=now; user=db.get(User,token.user_id)
 if not user or not user.is_active: db.commit(); raise HTTPException(401,'Invalid user')
 replacement=issue(db,user.id,token.family_id); db.commit(); set_cookie(response,replacement); return payload(user)
@router.post('/logout')
def logout(response:Response,raw:str|None=Cookie(default=None,alias=COOKIE),db:Session=Depends(get_db)):
 if raw:
  token=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==hash_refresh(raw)))
  if token and not token.revoked_at: token.revoked_at=datetime.now(timezone.utc); db.commit()
 response.delete_cookie(COOKIE,path='/auth'); return {'ok':True}
@router.get('/me')
def me(user:User=Depends(get_current_user)): return {'id':user.id,'email':user.email,'is_admin':bool(user.is_admin)}
