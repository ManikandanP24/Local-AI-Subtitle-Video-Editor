from pydantic import BaseModel, EmailStr, Field
class Credentials(BaseModel):
 email:EmailStr
 password:str=Field(min_length=8,max_length=128)
class ProjectCreate(BaseModel):
 title:str=Field(default='Untitled project',min_length=1,max_length=200)
 language:str='auto'
class SubtitleIn(BaseModel):
 start:float=Field(ge=0)
 end:float=Field(gt=0)
 text:str
 words:list[dict]|None=None
class SubtitleBatch(BaseModel):
 lines:list[SubtitleIn]
class TranscribeRequest(BaseModel):
 language:str|None=None
 model_size:str|None=None
