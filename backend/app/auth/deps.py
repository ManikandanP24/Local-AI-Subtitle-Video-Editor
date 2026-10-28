from fastapi import Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from ..db import get_db
from ..models import User
from .security import decode_access_token
bearer=HTTPBearer(auto_error=False)
def get_current_user(creds:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
 if not creds: raise HTTPException(401,'Authentication required')
 try:
  p=decode_access_token(creds.credentials)
  if p.get('type')!='access': raise ValueError()
  uid=int(p['sub'])
 except (jwt.PyJWTError,ValueError,KeyError,TypeError): raise HTTPException(401,'Invalid or expired access token')
 user=db.get(User,uid)
 if not user or not user.is_active: raise HTTPException(401,'Invalid user')
 return user
