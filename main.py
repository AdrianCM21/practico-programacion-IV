from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_302_FOUND
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import Brand,Model,Vehicle,Activity,Garaje, Base
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

@app.get("/getmodelformarcas/{id}")
def getmodelformarcas( id:str,db: Session = Depends(get_db) ):
    if(id!="0"):
        models=db.query(Model).filter_by(idMarcaFk=id).all()
    else:
        models=db.query(Model).all()
    
    return jsonable_encoder(models)

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
    modelos =db.query(Model).all()
    return templates.TemplateResponse("marca.html", {"request": request,"marcas":marcas,'modelos':modelos})


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
def Guardar_vehiculo(tipo_examen:str=Form(...),matricula: str = Form(...), idMarcaFk: str = Form(...),idModeloFk: str = Form(...),db: Session = Depends(get_db)):
    
    vehiculo = Vehicle(matricula=matricula,idMarcaFk=idMarcaFk,idModeloFk=idModeloFk,Tipo_examen=tipo_examen)
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    print(vehiculo.idVehiculo)
    return RedirectResponse(url='/vehiculo',status_code=HTTP_302_FOUND)


# Ejemplos del prof
@app.get("/get_models/{brand_id}")
async def get_models(brand_id: int, db: Session = Depends(get_db) ):
    
    models = db.query(Model).filter_by(idMarcaFk=brand_id).all()
    return JSONResponse(content=[{"idModelo": model.idModelo, "descModelo": model.descModelo} for model in models])

@app.get("/vehicles/")
async def read_vehicles(matricula: str = None, marca: str = None, modelo: str = None, garaje: str = None, db: Session = Depends(get_db)):
    query = db.query(Vehicle).options(joinedload(Vehicle.brand), joinedload(Vehicle.model), joinedload(Vehicle.garajes))
    if matricula:
        query = query.filter(Vehicle.matricula.ilike(f"%{matricula}%"))
    if marca:
        query = query.join(Brand).filter(Brand.descMarca.ilike(f"%{marca}%"))
    if modelo:
        query = query.join(Model).filter(Model.descModelo.ilike(f"%{modelo}%"))
    if garaje:
        query = query.join(Garaje).filter(Garaje.description.ilike(f"%{garaje}%"))
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
        activityDay.limite=activityDay.limite+1
        if (not (activityDay.limite<5)):
            print('limite 4 vehiculos alcansado')
            return JSONResponse(content={'msg':'No hay cupo','dia':activityDay.idIngreso})
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
    vehiculos = db.query(Vehicle).filter(Vehicle.idIngresoFk.is_(None)).all()
    return templates.TemplateResponse("registro.html", {"request": request,"vehiculos":vehiculos})

@app.get("/deleteregistro/{id}")
def delete_registro(id:int, db: Session = Depends(get_db)):
    vehiculos=db.query(Vehicle).filter_by(idVehiculo=id).first()
    auxidIngreso=vehiculos.idIngresoFk
    print(auxidIngreso)
    vehiculos.idIngresoFk=None
    db.commit()
    activityDay = db.query(Activity).filter_by(idIngreso=auxidIngreso).first()
    activityDay.cantidad = activityDay.cantidad - 1 
    db.commit()
    return JSONResponse(content={'msg':'Eliminado','dia':activityDay.idIngreso})
    
@app.get("/IngresosDia") 
def IngresosDia(request: Request, db: Session = Depends(get_db) ):
    ingresos =db.query(Activity).all()
    return templates.TemplateResponse("IngresosDia.html", {"request": request,"ingresos":ingresos})

@app.get("/garajes") 
def garajes(request: Request, db: Session = Depends(get_db) ):
    datos =db.query(Garaje).all()
    return templates.TemplateResponse("garaje.html", {"request": request,"datos":datos})

@app.get("/garajes_vehiculo/add")
def agregar_garaje_vehiculo(request: Request, db: Session = Depends(get_db)):
    garajes = db.query(Garaje).all()
    vehiculos = db.query(Vehicle).filter(Vehicle.Tipo_examen == "Normal", Vehicle.idGarajeFk.is_(None)).all()
    return templates.TemplateResponse("garaje_vehiculoForm.html", {"request": request, "garajes": garajes, "vehiculos": vehiculos})

@app.get("/garajes/add")
def agregar_garaje(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("garajeForm.html", {"request": request})

@app.post("/garajes/add")
def agregar_garajepost( garaje_modelo: str = Form(...),garaje_cantidad:str=Form(...),db: Session = Depends(get_db)):
    garaje_cantidad = int(garaje_cantidad) 
    garaje = Garaje(description=garaje_modelo,cantidad=0,Cantidad_Examen=garaje_cantidad)
    db.add(garaje)
    db.commit()
    return RedirectResponse(url='/garajes',status_code=HTTP_302_FOUND)


@app.post("/garajes/edit")
def edit_garajepost( cerrado:str=Form(...),garaje_id:str=Form(...),garaje_modelo: str = Form(...),garaje_cantidad:str=Form(...),db: Session = Depends(get_db)):
    garaje = db.query(Garaje).filter(Garaje.idGaraje == garaje_id).first()

    if garaje is None:
        return {"error": "Garaje not found"}
    garaje.description = garaje_modelo
    garaje.Cantidad_Examen = int(garaje_cantidad)
    garaje.Cerrado_examen= int(cerrado)

    db.commit()

    return RedirectResponse(url='/garajes', status_code=HTTP_302_FOUND)

@app.post("/garajes_vehiculo/add")
def agregar_garaje_vehiculopost( idGarajeFk: str = Form(...),idVehiculoFk: str = Form(...),db: Session = Depends(get_db)):
    garaje = db.query(Garaje).filter_by(idGaraje=idGarajeFk).first()
    if garaje.limite>=garaje.Cantidad_Examen:
        return RedirectResponse(url='/garajes',status_code=HTTP_302_FOUND)
    if garaje.Cerrado_examen==1:
        return RedirectResponse(url='/garajes',status_code=HTTP_302_FOUND)
    garaje.limite = garaje.limite + 1
    garaje.cantidad = garaje.cantidad + 1
    vehiculo = db.query(Vehicle).filter_by(idVehiculo=idVehiculoFk).first()
    vehiculo.idGarajeFk = garaje.idGaraje
    db.commit()
    return RedirectResponse(url='/garajes',status_code=HTTP_302_FOUND)
@app.get("/deletegarajes/{id}")
def borrar(id: int, db: Session = Depends(get_db)):
    garaje = db.query(Garaje).filter_by(idGaraje=id).first()
    if garaje:
        db.query(Vehicle).filter_by(idGarajeFk=garaje.idGaraje).update({"idGarajeFk": None})
        db.delete(garaje)
        db.commit()
        return RedirectResponse(url='/garajes',status_code=HTTP_302_FOUND)
    raise HTTPException(status_code=404, detail="Garaje no encontrado")

@app.get("/editgarajes/{id}")
def editgarajes(id: int, request: Request, db: Session = Depends(get_db)):
    garaje = db.query(Garaje).filter_by(idGaraje=id).first()
    if garaje:
        return templates.TemplateResponse("garaje_edit.html", {"request": request, "garaje": garaje})
    raise HTTPException(status_code=404, detail="Garaje no encontrado")

@app.get("/datos_activity/{fecha1}")
def getActivity(fecha1:str, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter_by(fecha=fecha1).first()
    return jsonable_encoder(activity)


@app.get("/datos_activityforid/{fecha1}")
def getActivityforid(fecha1:str, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter_by(idIngreso=fecha1).first()
    return jsonable_encoder(activity)

@app.get("/getselect")
def getselect(db: Session = Depends(get_db)):
    vehiculos = db.query(Vehicle).filter(Vehicle.idIngresoFk.is_(None)).all()
    return jsonable_encoder(vehiculos)



@app.get("/editvehiculo/{id}")
def editvehiculo(id: int, request: Request, db: Session = Depends(get_db)):
    print('dfakjshd')
    vehicle = db.query(Vehicle).filter_by(idVehiculo=id).first()
    if vehicle:
        return templates.TemplateResponse("vehiculo_edit.html", {"request": request, "vehiculo": vehicle})
    raise HTTPException(status_code=404, detail="Garaje no encontrado")



@app.post("/vehiculo/edit")
def edit_vehicle( tipo_examen:str=Form(...),idv: str = Form(...),db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.idVehiculo == idv).first()

    if vehicle is None:
        return {"error": "Garaje not found"}
    vehicle.Tipo_examen = tipo_examen

    db.commit()

    return RedirectResponse(url='/vehiculos', status_code=HTTP_302_FOUND)

