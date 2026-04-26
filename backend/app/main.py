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
from sqlalchemy import inspect, text
from pydantic import BaseModel
import hashlib

from app.database import engine, get_db, Base
from app import models
from app.horarios_disponibles import horasLibres
from app.horarios_disponibles import registraReserva

# ============================================================
#   INICIALIZACIÓN Y CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================================

# Esto crea las tablas en la BD si no existen todavía
Base.metadata.create_all(bind=engine)

def asegurar_columna_usuario_id():
    """
    Compatibilidad: asegura que la columna usuario_id exista en la tabla reservas.
    """
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    if "reservas" not in tablas:
        return
    columnas = {col["name"] for col in inspector.get_columns("reservas")}
    if "usuario_id" not in columnas:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE reservas ADD COLUMN usuario_id INTEGER NOT NULL DEFAULT 0"))

asegurar_columna_usuario_id()

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
#   CARGA INICIAL — 4 usuarios de ejemplo
# ============================================================
def crear_usuarios_iniciales(db: Session):
    """
    Si la tabla está vacía, inserta 4 usuarios de prueba.
    Se llama automáticamente al arrancar la app.
    """
    if db.query(models.Usuario).count() == 0:
        usuarios = [
            models.Usuario(
                nombre="Ana Dieguez",
                username="ana",
                email="ana@gmail.com",
                telefono="600000001",
                direccion="Calle Deporte S/N, Atarfe",
                password=hashear_password("ana123"),
                es_admin=True
            ),
            models.Usuario(
                nombre="Javier",
                username="javi",
                email="javi@email.com",
                telefono="600000002",
                direccion="Calle Mayor 1, Granada",
                password=hashear_password("javi123"),
                es_admin=False
            ),
            models.Usuario(
                nombre="Gonzalo",
                username="gonzalo",
                email="gonzalo@email.com",
                telefono="600000003",
                direccion="Avenida Andalucía 5, Granada",
                password=hashear_password("gonzalo123"),
                es_admin=False
            ),
            models.Usuario(
                nombre="Fernando",
                username="fernando",
                email="fernando@email.com",
                telefono="600000004",
                direccion="Plaza Nueva 3, Granada",
                password=hashear_password("fernando123"),
                es_admin=False
            ),
            models.Usuario(
                nombre="Susana",
                username="susana",
                email="susana@email.com",
                telefono="600000004",
                direccion="Plaza Nueva 3, Granada",
                password=hashear_password("susana123"),
                es_admin=False
            ),
        ]
        db.add_all(usuarios)
        db.commit()
        print("✅ Usuarios iniciales creados")

# Ejecutamos la carga inicial al arrancar
with engine.connect() as connection:
    from sqlalchemy.orm import Session as OrmSession
    with OrmSession(bind=connection) as db:
        crear_usuarios_iniciales(db)

# ============================================================
#   MODELOS DE ENTRADA (Esquemas Pydantic)
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
#   ENDPOINTS: GESTIÓN DE USUARIOS
# ============================================================

@app.get("/")
def raiz():
    return {"mensaje": "API CodeCenter funcionando ✅"}

@app.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.username == datos.username).first()
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
    if not usuario: raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": usuario.id, "nombre": usuario.nombre, "username": usuario.username, 
        "email": usuario.email, "telefono": usuario.telefono, 
        "direccion": usuario.direccion, "es_admin": usuario.es_admin
    }

# ============================================================
#   ENDPOINT: PUT /usuarios/{id}
#   Actualiza los datos del usuario (área de clientes).
#   Solo se actualizan los campos que el usuario haya rellenado.
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
#   Solo para el administrador: lista todos los usuarios.
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
#   ENDPOINTS: DISPONIBILIDAD Y RESERVAS
# ============================================================

@app.get("/disponibilidad")
def obtener_disponibilidad(deporte: str, fecha: str, db: Session = Depends(get_db)):
    return {"horas": horasLibres(db, deporte, fecha)}

@app.post("/reservar")
def enviar_reserva(reserva: ReservaSchema, db: Session = Depends(get_db)):
    reserva_id = registraReserva(
        db=db, deporte=reserva.deporte, fecha=reserva.fecha, 
        hora=reserva.hora, usuario_id=reserva.usuario_id
    )
    if reserva_id is None: raise HTTPException(status_code=500, detail="No se pudo guardar")
    return {"status": "ok", "reserva_id": reserva_id}

@app.get("/reservas/{usuario_id}")
def obtener_reservas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(models.Reserva).filter(models.Reserva.usuario_id == usuario_id).all()

@app.delete("/reservas/{reserva_id}/cancelar")
@app.put("/reservas/{reserva_id}/cancelar")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(reserva)
    db.commit()
    return {"status": "ok", "mensaje": "Reserva eliminada"}