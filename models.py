from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Brand(Base):
    __tablename__ = 'brands'
    idMarca = Column(Integer, primary_key=True, index=True)
    descMarca = Column(String(50), unique=True, index=True)
    models = relationship("Model", back_populates="brand")

class Model(Base):
    __tablename__ = 'models'
    idModelo = Column(Integer, primary_key=True, index=True)
    descModelo = Column(String(50), unique=True, index=True)
    idMarcaFk = Column(Integer, ForeignKey('brands.idMarca'))
    brand = relationship("Brand", back_populates="models")
    vehicles = relationship("Vehicle", back_populates="model")

class Activity(Base):
    __tablename__ = 'activitys'
    idIngreso = Column(Integer, primary_key=True, index=True)
    fecha = Column(String(21), unique=True, index=True)
    cantidad = Column(Integer, default=0)
    limite= Column(Integer, default=0)
    vehicles = relationship("Vehicle", back_populates="activity")
     
class Garaje(Base):
    __tablename__ = 'garajes'
    idGaraje = Column(Integer, primary_key=True, index=True)
    description = Column(String(21), unique=True, index=True)
    cantidad= Column(Integer, default=0)
    Cantidad_Examen = Column(Integer, default=0)
    limite= Column(Integer, default=0)
    Cerrado_examen= Column(Integer, default=0)
    vehicles = relationship("Vehicle", back_populates="garajes")
     

class Vehicle(Base):
    __tablename__ = 'vehicles'
    idVehiculo = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(50), unique=True, index=True)
    idMarcaFk = Column(Integer, ForeignKey('brands.idMarca'))
    idModeloFk = Column(Integer, ForeignKey('models.idModelo'))
    idIngresoFk = Column(Integer, ForeignKey('activitys.idIngreso'), nullable=True)
    Tipo_examen= Column(String(50), nullable=True)
    idGarajeFk = Column(Integer, ForeignKey('garajes.idGaraje'), nullable=True)
    activity = relationship("Activity", back_populates="vehicles", foreign_keys=[idIngresoFk])
    garajes = relationship("Garaje", back_populates="vehicles", foreign_keys=[idGarajeFk])
    brand = relationship("Brand")
    model = relationship("Model")

