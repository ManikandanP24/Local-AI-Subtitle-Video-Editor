import hashlib, secrets
from datetime import datetime,timedelta,timezone
import jwt
from argon2 import PasswordHasher
from ..config import settings
_hasher=PasswordHasher()
def hash_password(password:str)->str: return _hasher.hash(password)
def verify_password(encoded:str,password:str)->bool:
 try: return _hasher.verify(encoded,password)
 except Exception: return False
def hash_refresh(raw:str)->str: return hashlib.sha256(raw.encode()).hexdigest()
def new_refresh()->str: return secrets.token_urlsafe(48)
def create_access_token(user_id:int)->str:
 now=datetime.now(timezone.utc)
 return jwt.encode({'sub':str(user_id),'iat':now,'exp':now+timedelta(minutes=settings.access_token_minutes),'type':'access'},settings.jwt_secret,algorithm='HS256')
def decode_access_token(token:str)->dict: return jwt.decode(token,settings.jwt_secret,algorithms=['HS256'],options={'require':['exp','sub']})
