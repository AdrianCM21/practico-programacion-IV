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
    __tablename__ = 'activity'
    idIngreso = Column(Integer, primary_key=True, index=True)
    fecha = Column(String(21), unique=True, index=True)
    cantidad = Column(Integer, default=1)
    vehicles = relationship("Vehicle", back_populates="activity")
     


class Vehicle(Base):
    __tablename__ = 'vehicles'
    idVehiculo = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(50), unique=True, index=True)
    idMarcaFk = Column(Integer, ForeignKey('brands.idMarca'))
    idModeloFk = Column(Integer, ForeignKey('models.idModelo'))
    idIngresoFk = Column(Integer, ForeignKey('activity.idIngreso'), nullable=True)
    activity = relationship("Activity", back_populates="vehicles", foreign_keys=[idIngresoFk])
    brand = relationship("Brand")
    model = relationship("Model")

