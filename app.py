#from matplotlib.pyplot import get
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from pydoc import describe
from pyexpat import model
from typing import Optional, Generator, List
from fastapi import FastAPI, Depends, HTTPException, File, Form, UploadFile, Request
import models as models 
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routers.auth import get_current_user, get_user_exception
from routers.auth_user import get_current_tenant
from typing import List 
import shutil
import cloudinary
import cloudinary.uploader


from fastapi import FastAPI, Depends
import models
from database import engine
from routers import auth, main, auth_user
from starlette.staticfiles import StaticFiles

from pathlib import Path
import uuid


from typing import Optional
import aiofiles 

from starlette import status
from starlette.responses import RedirectResponse



app = FastAPI()

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


########## PAGINATION ###################

def pagination(response, page_num, page_size, start, end, listings_length):
    if end >= listings_length:
        response["pagination"]["next"] = "#"
        if page_num > 1:
            response["pagination"]["previous"] = f"/rentals?page_num={page_num-1}&page_size={page_size}"
        else:
            response["pagination"]["previous"] = "#"
    else:
        if page_num > 1:
            response["pagination"]["previous"] = f"/rentals?page_num={page_num-1}&page_size={page_size}"
        else:
            response["pagination"]["previous"] = "#"
            
        response["pagination"]["next"] = f"/rentals?page_num={page_num+1}&page_size={page_size}"

########### Pagination

@app.get("/", response_class=HTMLResponse)
async def start(request: Request):
    return templates.TemplateResponse("user_login.html", {"request": request})


#@app.get("/user_login", response_class=HTMLResponse)
#async def start(request: Request):
#    return templates.TemplateResponse("user_login.html", {"request": request})

@app.get("/landlord_signup", response_class=HTMLResponse)
async def start(request: Request):
    return templates.TemplateResponse("landlord_signup.html", {"request": request})

@app.get("/user_signup", response_class=HTMLResponse)
async def start(request: Request):
    return templates.TemplateResponse("user_signup.html", {"request": request})


@app.get("/analytics", response_class=HTMLResponse)
async def analytic(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})


@app.get("/listing", response_class=HTMLResponse)
async def list(request: Request):
    return templates.TemplateResponse("listing.html", {"request": request})


### Landlord 

@app.get("/landlord_login", response_class=HTMLResponse)
async def start(request: Request):
   return templates.TemplateResponse("landlord_login.html", {"request": request})

#for the user 
@app.get("/user_login", response_class=HTMLResponse)
async def start(request: Request):
   return templates.TemplateResponse("user_login.html", {"request": request})

#user
@app.get("/home", response_class=HTMLResponse)
async def list(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

#landlord
@app.get("/addlisting", response_class=HTMLResponse)
async def addlist(request: Request):
    return templates.TemplateResponse("addlisting_new.html", {"request": request})
   
cloudinary.config( 
  cloud_name = "farewell", 
  api_key = "356369275241493", 
  api_secret = "0R3T8SwazOOjEaLs7Izfa4gs4aQ" 
)

async def get_file(file_path: str) -> Generator:
    with open(file=file_path, mode="rb") as file_like:
        yield file_like.read()

#landlord
@app.post("/addlisting")
async def addlisting(
    request: Request,
    address: str = Form(...),
    city: str = Form(...),
    rent: int = Form(...),
    listing_info: str = Form(...),
    squaremetres: int = Form(...),
    rooms: int = Form(...),
    bedrooms: int = Form(...),
    bathrooms: int = Form(...),
    furnished: bool = Form(False),
    equipped: bool = Form(False),
    floor: int = Form(...),
    inside: str = Form(...),
    doorman: bool = Form(False),
    elevator: bool = Form(False),
    energy_label: str = Form(...),
    energy_consumption: int = Form(...),
    images: List[UploadFile] = File(...),
    video: UploadFile = File(...),
    highresimage: bool = Form(False),
    highresvideo: bool = Form(False),
    db: Session = Depends(get_db)):
    img_urls = ""
    for image in images:
        if highresimage == False:
            img_result = cloudinary.uploader.upload(image.file, quality=50, width = 350, folder = "listings/images/")
        else:
            img_result = cloudinary.uploader.upload(image.file, width = 350, folder = "listings/images/")
        img_url = img_result.get("url")
        img_urls = img_urls + ", " + img_url
    try:
        if highresvideo == False:
            vid_result = cloudinary.uploader.upload(video.file, quality = 50, width = 400, folder = "listings/videos/", resource_type = "video")
        else: 
            vid_result = cloudinary.uploader.upload(video.file, width = 400, folder = "listings/videos/", resource_type = "video")
        vid_url = vid_result.get("url")
    except:
        vid_url = "No video"

    user = await get_current_user(request)
    print(user)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_model = models.Listing()
    user_model.address = address
    user_model.city = city
    user_model.rent = rent
    user_model.listing_info = listing_info 
    user_model.squaremetres = squaremetres 
    user_model.rooms = rooms 
    user_model.bedrooms = bedrooms 
    user_model.bathrooms = bathrooms 
    user_model.furnished = furnished 
    user_model.equipped = equipped 
    user_model.floor = floor 
    user_model.inside = inside 
    user_model.doorman = doorman
    user_model.elevator = elevator 
    user_model.energy_label = energy_label 
    user_model.energy_consumption = energy_consumption
    user_model.img_urls = img_urls 
    user_model.vid_url = vid_url 

    user_model.landlord_id = user.get("id")

    db.add(user_model)
    db.commit()

    return templates.TemplateResponse("listing_landlord.html", {"request": request, 
        "address": address,
        "city": city,
        "rent": rent,
        "listing_info": listing_info,
        "squaremetres": squaremetres,
        "rooms": rooms,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "furnished": furnished,
        "equipped": equipped,
        "floor": floor,
        "inside": inside,
        "doorman": doorman,
        "elevator": elevator,
        "energy_label": energy_label,
        "energy_consumption": energy_consumption,
        "img_urls": img_urls,
        "vid_url": vid_url})


#landlord 
@app.get("/new_listings", response_class=HTMLResponse)
async def get_listings(request: Request, 
    page_num: int = 1, page_size: int = 4,
    db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    listings = db.query(models.Listing).filter(models.Listing.landlord_id == user.get("id")).all()
    listings.reverse()
    
    start = (page_num - 1) * page_size
    end = start + page_size
    ### DB CALL 
    ### DB CALL
    listings_length = len(listings)
    response = {
    "length": listings[start:end],
    "total": listings_length,
    "count": page_size,
    "pagination": {}
}
    pagination(response=response, page_num=page_num, page_size=page_size, start=start, end=end, listings_length=listings_length)
    return templates.TemplateResponse("rentals_landlord_template.html", {"request": request, "listings": listings[start:end],"response": response})

#user 

@app.get("/rentals", response_class=HTMLResponse)
async def get_listings(request: Request, 
    page_num: int = 1, page_size: int = 4,
    db: Session = Depends(get_db)):

    user = await get_current_tenant(request)
    if user is None:
        return RedirectResponse(url="/user_login", status_code=status.HTTP_302_FOUND)
    listings = db.query(models.Listing).all()
    listings.reverse()
    
    start = (page_num - 1) * page_size
    end = start + page_size
    ### DB CALL 
    ### DB CALL
    listings_length = len(listings)
    response = {
    "length": listings[start:end],
    "total": listings_length,
    "count": page_size,
    "pagination": {}
}
    pagination(response=response, page_num=page_num, page_size=page_size, start=start, end=end, listings_length=listings_length)
    return templates.TemplateResponse("rentals_user_template.html", {"request": request, "listings": listings[start:end],"response": response})



# click renting rendering 
#landlord
@app.get("/listings/{listing_id}", response_class = HTMLResponse)
async def read_listing(request: Request, listing_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None: 
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()   
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return templates.TemplateResponse("listing_landlord.html", {"request": request, 
        "address": listing.address,
        "city": listing.city,
        "rent": listing.rent,
        "listing_info": listing.listing_info,
        "squaremetres": listing.squaremetres,
        "rooms": listing.rooms,
        "bedrooms": listing.bedrooms,
        "bathrooms": listing.bathrooms,
        "furnished": listing.furnished,
        "equipped": listing.equipped,
        "floor": listing.floor,
        "inside": listing.inside,
        "doorman": listing.doorman,
        "elevator": listing.elevator,
        "energy_label": listing.energy_label,
        "energy_consumption": listing.energy_consumption,
        "img_urls": listing.img_urls,
        "vid_url": listing.vid_url})

#user
@app.get("/rentals/{listing_id}", response_class = HTMLResponse)
async def read_rentals(request: Request, listing_id: int, db: Session = Depends(get_db)):
    user = await get_current_tenant(request)
    if user is None: 
        return RedirectResponse(url="/auth_user", status_code=status.HTTP_302_FOUND)

    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()     
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")


    return templates.TemplateResponse("listing_user.html", 
        {"request": request, 
        "address": listing.address,
        "city": listing.city,
        "rent": listing.rent,
        "listing_info": listing.listing_info,
        "squaremetres": listing.squaremetres,
        "rooms": listing.rooms,
        "bedrooms": listing.bedrooms,
        "bathrooms": listing.bathrooms,
        "furnished": listing.furnished,
        "equipped": listing.equipped,
        "floor": listing.floor,
        "inside": listing.inside,
        "doorman": listing.doorman,
        "elevator": listing.elevator,
        "energy_label": listing.energy_label,
        "energy_consumption": listing.energy_consumption,
        "img_urls": listing.img_urls,
        "vid_url": listing.vid_url})


@app.get("/documents/", response_class=HTMLResponse)
async def get_docs(
    request: Request, db: Session = Depends(get_db)):
    user = await get_current_tenant(request)
    if user is None: 
        return RedirectResponse(url="/auth_user", status_code=status.HTTP_302_FOUND)

    documents = db.query(models.Document).filter(models.Document.tenant_id == user.get("id")).all()
    documents.reverse()
    
    return templates.TemplateResponse("documents_cloudinary.html", {"request": request, "documents": documents})


@app.post("/documents/", response_class=HTMLResponse)
async def upload_docs(
    request: Request,
    filetype: str = Form(...),
    filename: str = Form(...),
    pdfdocument: UploadFile = File(...),
    db: Session = Depends(get_db)):

    pdf_result = cloudinary.uploader.upload(pdfdocument.file, folder = "listings/documents/")
    pdf_url = pdf_result.get("url")

    user = await get_current_tenant(request)
    if user is None: 
        return RedirectResponse(url="/auth_user", status_code=status.HTTP_302_FOUND)

    document_model = models.Document()
    document_model.filetype = filetype
    document_model.filename = filename
    document_model.pdf_url = pdf_url

    document_model.tenant_id = user.get("id")

    db.add(document_model)
    db.commit()

  
    return templates.TemplateResponse("document_uploaded.html", {"request": request, 
                                                                    "filetype": filetype, 
                                                                    "filename": filename, "pdf_url": pdf_url})

app.include_router(auth.router)
app.include_router(auth_user.router)
