from venv import create
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os 
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
  cloud_name = "dxhdxbedp", 
  api_key = "552497812426217", 
  api_secret = "HTsyA53RosfW3btxsZF_qKS1hQU",
)



#SQLALCHEMY_DABASE_URL = "sqlite:///./solomon.db"


SQLALCHEMY_DABASE_URL = os.environ.get("DATABASE_URL")
if SQLALCHEMY_DABASE_URL.startswith("postgres://"):
  SQLALCHEMY_DABASE_URL = SQLALCHEMY_DABASE_URL.replace("postgres://", "postgresql://", 1)


engine  = create_engine(
    SQLALCHEMY_DABASE_URL)

#engine = create_engine(SQLALCHEMY_DABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


