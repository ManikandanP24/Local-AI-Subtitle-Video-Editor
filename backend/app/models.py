from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
 __tablename__='users'
 id:Mapped[int]=mapped_column(Integer,primary_key=True)
 email:Mapped[str]=mapped_column(String(320),unique=True,index=True)
 password_hash:Mapped[str]=mapped_column(String(255))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
 is_active:Mapped[bool]=mapped_column(Boolean,default=True)
 projects:Mapped[list['Project']]=relationship(back_populates='user',cascade='all, delete-orphan')
class RefreshToken(Base):
 __tablename__='refresh_tokens'
 id:Mapped[int]=mapped_column(Integer,primary_key=True)
 user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True)
 family_id:Mapped[str]=mapped_column(String(64),index=True)
 token_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True)
 expires_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
 revoked_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Project(Base):
 __tablename__='projects'
 id:Mapped[int]=mapped_column(Integer,primary_key=True)
 user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True)
 title:Mapped[str]=mapped_column(String(200),default='Untitled project')
 language:Mapped[str]=mapped_column(String(30),default='auto')
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
 updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
 user:Mapped[User]=relationship(back_populates='projects')
 media:Mapped[list['MediaFile']]=relationship(back_populates='project',cascade='all, delete-orphan')
 subtitles:Mapped[list['SubtitleLine']]=relationship(back_populates='project',cascade='all, delete-orphan')
class MediaFile(Base):
 __tablename__='media_files'
 id:Mapped[int]=mapped_column(Integer,primary_key=True)
 project_id:Mapped[int]=mapped_column(ForeignKey('projects.id'),index=True)
 path:Mapped[str]=mapped_column(Text)
 original_name:Mapped[str]=mapped_column(String(255))
 kind:Mapped[str]=mapped_column(String(30),default='original')
 duration:Mapped[float|None]=mapped_column(Float,nullable=True)
 project:Mapped[Project]=relationship(back_populates='media')
class SubtitleLine(Base):
 __tablename__='subtitle_lines'
 id:Mapped[int]=mapped_column(Integer,primary_key=True)
 project_id:Mapped[int]=mapped_column(ForeignKey('projects.id'),index=True)
 line_index:Mapped[int]=mapped_column(Integer)
 start:Mapped[float]=mapped_column(Float)
 end:Mapped[float]=mapped_column(Float)
 text:Mapped[str]=mapped_column(Text)
 words_json:Mapped[str|None]=mapped_column(Text,nullable=True)
 project:Mapped[Project]=relationship(back_populates='subtitles')
class Job(Base):
 __tablename__='jobs'
 id:Mapped[int]=mapped_column(Integer,primary_key=True)
 project_id:Mapped[int]=mapped_column(ForeignKey('projects.id'),index=True)
 type:Mapped[str]=mapped_column(String(40))
 status:Mapped[str]=mapped_column(String(20),default='queued')
 progress:Mapped[int]=mapped_column(Integer,default=0)
 error:Mapped[str|None]=mapped_column(Text,nullable=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
