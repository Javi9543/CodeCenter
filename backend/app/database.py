"""
database.py — Conexión a la base de datos
==========================================
Aquí configuramos SQLAlchemy para conectarse a SQLite en local.
Cuando lo paséis a AWS, solo hay que cambiar la URL de conexión
por la de PostgreSQL en RDS (sin tocar nada más).
"""
 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
 
# --- URL DE CONEXIÓN ---
# ***************AWS**********************
# RDS_HOST     = "PEGAR-AQUI-EL-ENDPOINT-DE-RDS"   # Ej: codecenter.xxxx.eu-west-1.rds.amazonaws.com
# RDS_PORT     = "5432"
# RDS_USER     = "PEGAR-AQUI-EL-USUARIO"            # El que pusisteis al crear la RDS
# RDS_PASSWORD = "PEGAR-AQUI-LA-CONTRASEÑA"         # La que pusisteis al crear la RDS
# RDS_DB       = "PEGAR-AQUI-EL-NOMBRE-DE-LA-BD"    # Ej: codecenter
 
# DATABASE_URL = f"postgresql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
 
# engine = create_engine(DATABASE_URL)
# DATABASE_URL = "postgresql://usuario:contraseña@host-rds.amazonaws.com:5432/nombre_bd"

# **************LOCALHOST**********************
DATABASE_URL = "sqlite:///./codecenter.db"
 
# --- MOTOR ---
# El motor es el que abre la conexión real con la base de datos.
# check_same_thread=False es necesario solo para SQLite con FastAPI.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
 # ***********FIN****LOCALHOST******************
# --- SESIÓN ---
# Cada petición HTTP abre una sesión, hace su trabajo, y la cierra.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# --- BASE ---
# Todos los modelos (tablas) heredan de esta clase.
Base = declarative_base()
 
 
# --- DEPENDENCIA DE FASTAPI ---
# Esta función se inyecta en las rutas con Depends(get_db).
# Garantiza que la sesión siempre se cierre aunque haya un error.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 