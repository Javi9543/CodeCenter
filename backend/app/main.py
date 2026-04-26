"""
main.py — Rutas de FastAPI
===========================
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from pydantic import BaseModel
import hashlib

from app.database import engine, get_db, Base
from app import models
from app.horarios_disponibles import horasLibres
from app.horarios_disponibles import registraReserva

# --- INICIALIZACIÓN ---
Base.metadata.create_all(bind=engine)

# Compatibilidad: asegurar columna usuario_id para reservas.
def asegurar_columna_usuario_id():
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    if "reservas" not in tablas:
        return
    columnas = {col["name"] for col in inspector.get_columns("reservas")}
    if "usuario_id" not in columnas:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE reservas ADD COLUMN usuario_id INTEGER NOT NULL DEFAULT 0"))

asegurar_columna_usuario_id()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeCenter API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#   FUNCIÓN AUXILIAR — Hash de contraseñas
# ============================================================
def hashear_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
#   CARGA INICIAL — 5 usuarios de ejemplo
# ============================================================
def crear_usuarios_iniciales(db: Session):
    if db.query(models.Usuario).count() == 0:
        usuarios = [
            models.Usuario(nombre="Ana Dieguez", username="ana", email="ana@gmail.com", telefono="600000001", direccion="Calle Deporte S/N, Atarfe", password=hashear_password("ana123"), es_admin=True),
            models.Usuario(nombre="Javier", username="javi", email="javi@email.com", telefono="600000002", direccion="Calle Mayor 1, Granada", password=hashear_password("javi123"), es_admin=False),
            models.Usuario(nombre="Gonzalo", username="gonzalo", email="gonzalo@email.com", telefono="600000003", direccion="Avenida Andalucía 5, Granada", password=hashear_password("gonzalo123"), es_admin=False),
            models.Usuario(nombre="Fernando", username="fernando", email="fernando@email.com", telefono="600000004", direccion="Plaza Nueva 3, Granada", password=hashear_password("fernando123"), es_admin=False),
            models.Usuario(nombre="Susana", username="susana", email="susana@email.com", telefono="600000004", direccion="Plaza Nueva 3, Granada", password=hashear_password("susana123"), es_admin=False),
        ]
        db.add_all(usuarios)
        db.commit()
        print("✅ 5 usuarios iniciales creados")


with engine.connect() as connection:
    from sqlalchemy.orm import Session as OrmSession
    with OrmSession(bind=connection) as db:
        crear_usuarios_iniciales(db)


# ============================================================
#   MODELOS DE ENTRADA
# ============================================================
class LoginRequest(BaseModel):
    username: str
    password: str

class ActualizarUsuarioRequest(BaseModel):
    nombre:    str | None = None
    email:     str | None = None
    telefono:  str | None = None
    direccion: str | None = None
    password:  str | None = None

class ReservaSchema(BaseModel):
    deporte: str
    fecha: str
    hora: str
    usuario_id: int


# ============================================================
#   ENDPOINTS GENERALES
# ============================================================
@app.get("/")
def raiz():
    return {"mensaje": "API CodeCenter funcionando ✅"}


@app.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.username == datos.username
    ).first()
    if not usuario or usuario.password != hashear_password(datos.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return {
        "id": usuario.id, "nombre": usuario.nombre, "username": usuario.username,
        "email": usuario.email, "telefono": usuario.telefono,
        "direccion": usuario.direccion, "es_admin": usuario.es_admin
    }


@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": usuario.id, "nombre": usuario.nombre, "username": usuario.username,
        "email": usuario.email, "telefono": usuario.telefono,
        "direccion": usuario.direccion, "es_admin": usuario.es_admin
    }


@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, datos: ActualizarUsuarioRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if datos.nombre:    usuario.nombre    = datos.nombre
    if datos.email:     usuario.email     = datos.email
    if datos.telefono:  usuario.telefono  = datos.telefono
    if datos.direccion: usuario.direccion = datos.direccion
    if datos.password:  usuario.password  = hashear_password(datos.password)
    db.commit()
    db.refresh(usuario)
    return {"mensaje": "Datos actualizados correctamente ✅"}


@app.get("/admin/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return [{"id": u.id, "nombre": u.nombre, "username": u.username, "email": u.email, "telefono": u.telefono, "direccion": u.direccion, "es_admin": u.es_admin} for u in usuarios]


# ============================================================
#   ENDPOINTS DISPONIBILIDAD Y RESERVAR (de Javi)
# ============================================================
@app.get("/disponibilidad")
def obtener_disponibilidad(deporte: str, fecha: str, db: Session = Depends(get_db)):
    lista_horas = horasLibres(db, deporte, fecha)
    return {"horas": lista_horas}


@app.post("/reservar")
def enviar_reserva(reserva: ReservaSchema, db: Session = Depends(get_db)):
    reserva_id = registraReserva(
        db=db,
        deporte=reserva.deporte,
        fecha=reserva.fecha,
        hora=reserva.hora,
        usuario_id=reserva.usuario_id
    )
    if reserva_id is None:
        raise HTTPException(status_code=500, detail="No se pudo guardar la reserva")
    return {"status": "ok", "reserva_id": reserva_id, "mensaje": "Reserva guardada"}


# ============================================================
#   ENDPOINTS MIS RESERVAS (de Gonzalo)
# ============================================================
@app.get("/reservas/{usuario_id}")
def get_reservas(usuario_id: int, db: Session = Depends(get_db)):
    reservas = db.query(models.Reserva).filter(
        models.Reserva.usuario_id == usuario_id
    ).order_by(models.Reserva.fecha).all()
    return [
        {
            "id": r.id,
            "usuario_id": r.usuario_id,
            "deporte": r.deporte,
            "fecha": r.fecha,
            "hora": r.hora
        }
        for r in reservas
    ]


@app.put("/reservas/{id}/cancelar")
def cancelar_reserva(id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(reserva)
    db.commit()
    return {"ok": True}