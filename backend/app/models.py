"""
models.py — Definición de las tablas
======================================
Cada clase aquí es una tabla en la base de datos.
SQLAlchemy se encarga de crearla automáticamente.
"""

from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Usuario(Base):
    """
    Tabla 'usuarios' — guarda los datos de cada cliente registrado.
    """
    __tablename__ = "usuarios"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, nullable=False)
    username    = Column(String, unique=True, index=True, nullable=False)
    email       = Column(String, unique=True, index=True, nullable=False)
    telefono    = Column(String, nullable=True)
    direccion   = Column(String, nullable=True)
    password    = Column(String, nullable=False)
    es_admin    = Column(Boolean, default=False)


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    deporte = Column(String, nullable=False)
    fecha = Column(String, nullable=False)
    hora = Column(String, nullable=False)
    usuario_id = Column(Integer, nullable=False, default=0)
 
