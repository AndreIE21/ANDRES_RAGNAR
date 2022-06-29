from operator import index
from pickle import TRUE
from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey
ForeignKey
from sqlalchemy.orm import relationship
from database import Base 


class Landlords(Base):

    __tablename__ = "landlords"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, index=True)
    username = Column(String, index=True)
    phone_number = Column(Integer, index=True)
    hashed_password = Column(String)

    listing = relationship("Listing", back_populates="owner")


class Tenants(Base):

    __tablename__ = "tenant"

    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, index=True)
    username = Column(String, index=True)
    phone_number = Column(Integer, index=True)
    hashed_password = Column(String)

    document = relationship("Document", back_populates="owner")

    

class Listing(Base):

    __tablename__ = "listing"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    city = Column(String)
    rent = Column(Integer)
    listing_info = Column(String)
    squaremetres = Column(Integer)
    rooms = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    furnished = Column(Boolean)
    equipped = Column(Boolean)
    floor = Column(Integer)
    inside = Column(String)
    doorman = Column(Boolean)
    elevator = Column(Boolean)
    energy_label = Column(String)
    energy_consumption = Column(Integer)
    img_urls = Column(String)
    vid_url = Column(String)
    landlord_id = Column(Integer, ForeignKey("landlords.id"))

    owner = relationship("Landlords", back_populates = "listing")
   

class Document(Base):

    __tablename__  = "document"

    id = Column(Integer, primary_key=True, index=True)
    filetype = Column(String)
    filename = Column(String)
    pdf_url = Column(String)
    tenant_id = Column(Integer, ForeignKey("tenant.id"))


    owner = relationship("Tenants", back_populates = "document")




