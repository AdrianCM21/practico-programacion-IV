from fastapi import APIRouter,Request,Form
from fastapi.templating import Jinja2Templates
from models import DatosParcial, Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import DATABASE_URL
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

listar = APIRouter()
templates = Jinja2Templates(directory="templates")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
listar.mount("/static", StaticFiles(directory="static"), name="static")

# Función para obtener la sesión de la base de datos
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

@listar.get("/listar")
def crear_vehiculo(request: Request, db: Session = Depends(get_db) ):
    datos = db.query(DatosParcial).all()
    return templates.TemplateResponse("listar.html", {"request": request,"datos":datos,"foto":"/static/image/scooby.jpg"})

@listar.get("/obtener/{id}")
def obtener(request: Request,id:int, db: Session = Depends(get_db) ):
    datos = db.query(DatosParcial).filter(DatosParcial.Id == id).first()
    if datos:
        return JSONResponse(content={"Detalles": datos.Detalle})
    return JSONResponse(content={"Detalles": "No se encontraron Detalles"})


@listar.get("/borrar/{id}")
def borrar(id: int, db: Session = Depends(get_db)):
    dato = db.query(DatosParcial).filter(DatosParcial.Id == id).first()
    if dato:
        db.delete(dato)
        db.commit()
        return RedirectResponse(url='/listar',status_code=HTTP_302_FOUND)
    return HTTPException(status_code=404, detail="Ciudad no encontrado")


