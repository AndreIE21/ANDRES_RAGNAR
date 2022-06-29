from pydoc import describe
from pyexpat import model
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, File, Form, UploadFile
import models as models 
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List 
import shutil



from typing import Optional
import aiofiles 

app = FastAPI()

models.Base.metadata.create_all(bind = engine)

#rather or not we get a db session we allways clos de db 
def get_db():
    try:
        db = SessionLocal()
        yield db 
    finally:
        db.close()

class Todo(BaseModel):#all the variables from todo that i want to recieve as a post request
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be btw 1-5") #greater than0 and less than 6 so 5
    complete: bool 

@app.get("/")
async def read_all(db : Session = Depends(get_db)): #agarrando la sesion de la funcion de arriba get_db 
    return db.query(models.Todos).all()

@app.get("/todos/user")
async def read_all_by_user(user: dict = Depends(get_current_user),
        db:Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()


@app.get("/todo/{todo_id}") #filtrando por el id == primary key 
async def read_todo(todo_id: int, 
                    user:dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first() #after it finds that element it will return that element, we don't have to navigate the entire databse
    if todo_model is not None:
        return todo_model 
    raise http_exception() #if not it will raise an exeption our inport library

@app.post("/")
async def create_todo(todo: Todo, 
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = models.Todos()
    todo_model.title = todo.title 
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")

    db.add(todo_model) #places an object on this session 
    db.commit() # this will commit the previus add model 

    return succesfull_response(201)



@app.put("/{todo_id}")
async def update_todo(todo_id: int, 
                    todo: Todo, 
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()

    if todo_model is None:
        raise http_exception()
    
    todo_model.title = todo.title 
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete 

    db.add(todo_model)
    db.commit()

    return succesfull_response(200)



@app.delete("/{todo_id}")
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()

    if todo_model is None:
        raise http_exception()

    db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .delete()

    db.commit()

    return succesfull_response(200)



@app.post("/upload")
async def root(file: UploadFile = File(...)):
    with open(f'{file.filename}', "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)

    return {"file_name": file.filename}



@app.post("/image")
async def upload_images(files: List[UploadFile] = File(...)):
    for andres in files:
        with open(f'{andres.filename}', "wb") as buffer: 
            shutil.copyfileobj(andres.file, buffer)

    return {"file_name": "Nice Bro"}


def succesfull_response(status_code: int):
     return {
        'status':status_code,
        'transaction': 'Successful'
    }

def http_exception():
    return HTTPException(status_code = 404, detail= "Todo not found")

#https://stackoverflow.com/questions/63580229/how-to-save-uploadfile-in-fastapi
#this one is to save the file 

