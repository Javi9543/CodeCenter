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
 
    # Clave primaria, se autoincrementa (1, 2, 3...)
    id          = Column(Integer, primary_key=True, index=True)
 
    # Nombre completo visible en el área de clientes
    nombre      = Column(String, nullable=False)
 
    # El nombre con el que inicia sesión — debe ser único
    username    = Column(String, unique=True, index=True, nullable=False)
 
    # Email de contacto — también único
    email       = Column(String, unique=True, index=True, nullable=False)
 
    # Teléfono (opcional, se puede dejar en blanco)
    telefono    = Column(String, nullable=True)
 
    # Dirección (opcional)
    direccion   = Column(String, nullable=True)
 
    # Contraseña hasheada — NUNCA guardamos la contraseña en texto plano
    password    = Column(String, nullable=False)
 
    # True = administrador, False = cliente normal
    es_admin    = Column(Boolean, default=False)


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    deporte = Column(String, nullable=False)
    fecha = Column(String, nullable=False)
    hora = Column(String, nullable=False)
    usuario_id = Column(Integer, nullable=False, default=0)