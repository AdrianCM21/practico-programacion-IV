from fastapi import APIRouter,Request,Form
from fastapi.templating import Jinja2Templates
from models import DatosParcial, Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import DATABASE_URL
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from fastapi import  Depends,  Request, Form

listar = APIRouter()
templates = Jinja2Templates(directory="templates")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Función para obtener la sesión de la base de datos
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

cargar = APIRouter()
templates = Jinja2Templates(directory="templates")

@cargar.get("/cargar")
def agregar(request: Request  ):

    return templates.TemplateResponse("cargar.html", {"request": request})
@cargar.post("/cargar")
async def respuesta(detalle: str = Form(...),dato_combo: str = Form(...),dato: str = Form(...), db: Session = Depends(get_db)):
    datos = DatosParcial(Dato=dato,Detalle=detalle,ValordelCombo=dato_combo)
    db.add(datos)
    db.commit()
    return RedirectResponse(url='/',status_code=HTTP_302_FOUND)


