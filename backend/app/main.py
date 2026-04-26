"""
main.py — Rutas de FastAPI
===========================
Aquí están todos los endpoints (URLs) de la API.
El frontend llama a estas rutas con fetch() para
iniciar sesión, obtener datos del usuario, etc.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib

from app.database import engine, get_db, Base
from app import models

# --- INICIALIZACIÓN ---
# Esto crea las tablas en la BD si no existen todavía
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeCenter API", version="1.0")

# --- CORS ---
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
    """Convierte la contraseña en un hash SHA-256. Nunca guardamos texto plano."""
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


# Ejecutamos la carga inicial al arrancar
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

class ReservaRequest(BaseModel):
    id_usuario:  int
    deporte:     str
    fecha:       str
    hora_inicio: str
    hora_fin:    str


# ============================================================
#   ENDPOINT: GET /
# ============================================================
@app.get("/")
def raiz():
    return {"mensaje": "API CodeCenter funcionando ✅"}


# ============================================================
#   ENDPOINT: POST /login
# ============================================================
@app.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.username == datos.username
    ).first()

    if not usuario or usuario.password != hashear_password(datos.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    return {
        "id":        usuario.id,
        "nombre":    usuario.nombre,
        "username":  usuario.username,
        "email":     usuario.email,
        "telefono":  usuario.telefono,
        "direccion": usuario.direccion,
        "es_admin":  usuario.es_admin
    }


# ============================================================
#   ENDPOINT: GET /usuarios/{id}
# ============================================================
@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id":        usuario.id,
        "nombre":    usuario.nombre,
        "username":  usuario.username,
        "email":     usuario.email,
        "telefono":  usuario.telefono,
        "direccion": usuario.direccion,
        "es_admin":  usuario.es_admin
    }


# ============================================================
#   ENDPOINT: PUT /usuarios/{id}
# ============================================================
@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    datos: ActualizarUsuarioRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id
    ).first()

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


# ============================================================
#   ENDPOINT: GET /admin/usuarios
# ============================================================
@app.get("/admin/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return [
        {
            "id":        u.id,
            "nombre":    u.nombre,
            "username":  u.username,
            "email":     u.email,
            "telefono":  u.telefono,
            "direccion": u.direccion,
            "es_admin":  u.es_admin
        }
        for u in usuarios
    ]


# ============================================================
#   ENDPOINTS RESERVAS
# ============================================================
@app.get("/reservas/{id_usuario}")
def get_reservas(id_usuario: int, db: Session = Depends(get_db)):
    reservas = db.query(models.Reserva).filter(
        models.Reserva.id_usuario == id_usuario
    ).order_by(models.Reserva.fecha).all()
    return [
        {
            "id": r.id,
            "id_usuario": r.id_usuario,
            "deporte": r.deporte,
            "fecha": r.fecha,
            "hora_inicio": r.hora_inicio,
            "hora_fin": r.hora_fin,
            "estado": r.estado
        }
        for r in reservas
    ]


@app.post("/reservas")
def crear_reserva(reserva: ReservaRequest, db: Session = Depends(get_db)):
    nueva = models.Reserva(
        id_usuario=reserva.id_usuario,
        deporte=reserva.deporte,
        fecha=reserva.fecha,
        hora_inicio=reserva.hora_inicio,
        hora_fin=reserva.hora_fin,
        estado="activa"
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"ok": True, "id": nueva.id}


@app.put("/reservas/{id}/cancelar")
def cancelar_reserva(id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva.estado = "cancelada"
    db.commit()
    return {"ok": True}


@app.put("/reservas/{id}")
def modificar_reserva(id: int, datos: ReservaRequest, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva.deporte     = datos.deporte
    reserva.fecha       = datos.fecha
    reserva.hora_inicio = datos.hora_inicio
    reserva.hora_fin    = datos.hora_fin
    db.commit()
    return {"ok": True}