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
    """
    Tabla 'reservas' — guarda las reservas de cada usuario.
    """
    __tablename__ = "reservas"

    id          = Column(Integer, primary_key=True, index=True)
    id_usuario  = Column(Integer, nullable=False)
    deporte     = Column(String, nullable=False)
    fecha       = Column(String, nullable=False)
    hora_inicio = Column(String, nullable=False)
    hora_fin    = Column(String, nullable=False)
    estado      = Column(String, default="activa")