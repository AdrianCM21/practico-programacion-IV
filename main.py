from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import DatosParcial, Base
from listar import listar as listarRuter
from cargar import cargar as cargarRuter
from config import DATABASE_URL


app = FastAPI()

# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Configuración de las plantillas de Jinja2
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(listarRuter)
app.include_router(cargarRuter)
# app.include_router(listarRuter, prefix="/")
# Función para obtener la sesión de la base de datos
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

# Ruta para la página de inicio
@app.get("/")
def cargar_raiz(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,'auto':'/static/image/Rayo_McQueen.png'})

