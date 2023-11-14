from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_302_FOUND
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import Brand,Model,Vehicle,Activity, Base
from pydantic import BaseModel
from config import DATABASE_URL
from starlette.responses import JSONResponse
from sqlalchemy.orm import sessionmaker, joinedload


app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Configuración de las plantillas de Jinja2
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.get("/modelo")
def crear_modelo(request: Request, db: Session = Depends(get_db) ):
    modelos =db.query(Model).all()

    return templates.TemplateResponse("model.html", {"request": request,"modelos":modelos})

@app.get("/modelo/add")
def agregar_modelo(request: Request , db: Session = Depends(get_db) ):
    marcas = db.query(Brand).all()
    return templates.TemplateResponse("modelForm.html", {"request": request,"marcas":marcas})
@app.post("/modelo")
def guardar_modelo(nombre_modelo: str = Form(...), marca: int = Form(...), db: Session = Depends(get_db)):
    modelo = Model(descModelo=nombre_modelo, idMarcaFk=marca)
    db.add(modelo)
    db.commit()
    return RedirectResponse(url='/modelo', status_code=HTTP_302_FOUND)

@app.get("/marca")
def crear_marca(request: Request, db: Session = Depends(get_db) ):
    marcas = db.query(Brand).all()
    return templates.TemplateResponse("marca.html", {"request": request,"marcas":marcas})

@app.get("/marca/add")
def agregar_marca(request: Request ):
    return templates.TemplateResponse("marcaForm.html", {"request": request})

@app.post("/marca")
def Guardar_marca(nombre_marca: str = Form(...), db: Session = Depends(get_db)):
    marca = Brand(descMarca=nombre_marca)
    db.add(marca)
    db.commit()
    return RedirectResponse(url='/marca',status_code=HTTP_302_FOUND)




@app.get("/vehiculo")
def crear_vehiculo(request: Request, db: Session = Depends(get_db) ):
    vehiculos = db.query(Vehicle).all()
    return templates.TemplateResponse("vehiculo.html", {"request": request,"vehiculos":vehiculos})

@app.get("/vehiculo/add")
def agregar_vehiculo(request: Request, db: Session = Depends(get_db)  ):
    marcas = db.query(Brand).all()
    modelos =db.query(Model).all()
    return templates.TemplateResponse("vehiculoForm.html", {"request": request,"marcas":marcas,"modelos":modelos})

@app.post("/vehiculo")
def Guardar_vehiculo(matricula: str = Form(...), idMarcaFk: str = Form(...),idModeloFk: str = Form(...),db: Session = Depends(get_db)):
    
    vehiculo = Vehicle(matricula=matricula,idMarcaFk=idMarcaFk,idModeloFk=idModeloFk)
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    print(vehiculo.idVehiculo)
    return RedirectResponse(url='/vehiculo',status_code=HTTP_302_FOUND)

# Ejemplos del prof
@app.get("/get_models/{brand_id}")
async def get_models(brand_id: int, db: Session = Depends(get_db) ):
    
    models = db.query(Model).filter_by(idMarcaFk=brand_id).all()
    print('asdjfñalsdkjfñlsdkj')
    return JSONResponse(content=[{"idModelo": model.idModelo, "descModelo": model.descModelo} for model in models])

@app.get("/vehicles/")
async def read_vehicles(matricula: str = None, marca: str = None, modelo: str = None,db: Session = Depends(get_db)):
    query = db.query(Vehicle).options(joinedload(Vehicle.brand), joinedload(Vehicle.model))
    if matricula:
        query = query.filter(Vehicle.matricula.ilike(f"%{matricula}%"))
    if marca:
        query = query.join(Brand).filter(Brand.descMarca.ilike(f"%{marca}%"))
    if modelo:
        query = query.join(Model).filter(Model.descModelo.ilike(f"%{modelo}%"))
    vehicles = query.all()
    return vehicles

# Enpoint para registro de actividad 1
@app.post("/activity")
async def guardar_activity(request: Request, db: Session = Depends(get_db)):
    dia=0
    cant=0
    form_data = await request.form()
    fechaEnviada = form_data['fecha']
    idVehiculoEnviado  = form_data['matricula']
    
    activityDay = db.query(Activity).filter_by(fecha=fechaEnviada).first()
    if activityDay:
        cant=activityDay.cantidad + 1
        dia=activityDay.idIngreso
        Vehiculo = db.query(Vehicle).filter_by(idVehiculo=idVehiculoEnviado).first()
        if Vehiculo.idIngresoFk==activityDay.idIngreso:
            return JSONResponse(content={'msg':'Ya esta registrado','dia':activityDay.idIngreso})
        activityDay.cantidad = cant
        Vehiculo.idIngresoFk = activityDay.idIngreso
        db.commit()  
    
    else:
        activityAdd = Activity(fecha=fechaEnviada,cantidad=1)
        db.add(activityAdd)
        db.commit()
        db.refresh(activityAdd)
        Vehiculo = db.query(Vehicle).filter_by(idVehiculo=idVehiculoEnviado).first()
        Vehiculo.idIngresoFk = activityAdd.idIngreso
        db.commit()
        cant=activityAdd.cantidad
        dia=activityAdd.idIngreso
    
    
    return JSONResponse(content={'msg':'Registrado','dia':dia,'cantidad':cant})
    


@app.get("/registroget/{id}")
def resgistro(id:int, db: Session = Depends(get_db) ):
    vehiculos=db.query(Vehicle).filter_by(idIngresoFk=id).all()
    return jsonable_encoder(vehiculos)

@app.get("/registro")
def resgistro(request: Request, db: Session = Depends(get_db) ):
    vehiculos = db.query(Vehicle).all()
    return templates.TemplateResponse("registro.html", {"request": request,"vehiculos":vehiculos})

@app.get("/deleteregistro/{id}")
def delete_registro(id:int, db: Session = Depends(get_db)):
   
    vehiculos=db.query(Vehicle).filter_by(idVehiculo=id).first()
    auxidIngreso=vehiculos.idIngresoFk
    vehiculos.idIngresoFk=None
    db.commit()
    activityDay = db.query(Activity).filter_by(idIngreso=auxidIngreso).first()
    activityDay.cantidad = activityDay.cantidad - 1 
    db.commit()
    return JSONResponse(content={'msg':'Eliminado','dia':activityDay.idIngreso})
    

