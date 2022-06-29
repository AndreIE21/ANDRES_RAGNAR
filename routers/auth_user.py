import sys
sys.path.append("..") #import everything in the parentdirectory of auth

from starlette.responses import RedirectResponse 

from lib2to3.pgen2 import token
from logging import raiseExceptions
from xml.dom import minicompat
from fastapi import Depends, HTTPException, status, APIRouter, Response, Form, Request
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
import models 
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta #so we can add expiration date to our tokens 
from jose import jwt, JWTError

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

models.Base.metadata.create_all(bind=engine) # cretee our database if auth is run befor main

ouauth2_bearer = OAuth2PasswordBearer(tokenUrl="token") # we are going to use a dependency that will extract data from authorizatino 


router = APIRouter(
    prefix="/auth_user",
    tags=["auth"],
    responses = {401: {"user": "Not authorized"}}
)

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None 

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password") 


def get_db():
    try:
        db = SessionLocal()
        yield db 
    finally:
        db.close ()


def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)    # verifies if the plained and hash passwords are the same 

def authenticate_user_tenant(username: str, password: str, db): 
    tenant = db.query(models.Tenants).filter(models.Tenants.username == username)\
        .first()

    if not tenant:
        return False

    if not verify_password(password, tenant.hashed_password):
        return False
    return tenant 





def create_access_token(username: str, user_id:int, expires_delta: Optional[timedelta]= None):
    encode= {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})  
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)      




async def get_current_tenant(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")




@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user_tenant(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True



@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("home.html", {"request":request})

@router.post("/", response_class=HTMLResponse)
async def login(request:Request, db:Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url = "/home", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("user_login.html", {"request": request, "msg":msg})
        return response 
    except HTTPException:
        msg = "Unknown Error" 
        return templates.TemplateResponse("user_login.html", {"request": request, "msg":msg})

@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("user_login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response

@router.get("/user_signup", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("user_signup.html", {"request": request})

@router.post("/user_signup", response_class=HTMLResponse)
async def register_user(request: Request, 
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: str = Form(...),
    phone_number: int = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)):

    user_model = models.Tenants()
    user_model.first_name = firstname
    user_model.last_name = lastname
    user_model.email = email
    user_model.phone_number = phone_number
    user_model.username = username

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password

    db.add(user_model)
    db.commit()

    msg = "User created with success"
    return templates.TemplateResponse("user_login.html", {"request": request, "msg": msg})





# EXCEPTIONS 


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, #FROM THE IMPORT WE DID 
        datail="could not validate credentials bro",
        headers={"WWW-Authenticate": "Bearer"},     
    )
    return credentials_exception

