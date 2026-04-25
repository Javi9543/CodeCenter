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
from app.horarios_disponibles import horasLibres
from app.horarios_disponibles import registraReserva
# --- INICIALIZACIÓN ---
# Esto crea las tablas en la BD si no existen todavía
Base.metadata.create_all(bind=engine)
 
app = FastAPI(title="CodeCenter API", version="1.0")
 
# --- CORS ---
# Necesario para que el frontend (Nginx en otro contenedor) pueda
# llamar al backend sin que el navegador lo bloquee.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción poner la URL real del frontend
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
                es_admin=False
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
        print("✅ 5 usuarios iniciales creados")
 
 
# Ejecutamos la carga inicial al arrancar
with engine.connect() as connection:
    from sqlalchemy.orm import Session as OrmSession
    with OrmSession(bind=connection) as db:
        crear_usuarios_iniciales(db)
 
 
# ============================================================
#   MODELOS DE ENTRADA (lo que el frontend envía en el body)
# ============================================================
class LoginRequest(BaseModel):
    username: str
    password: str
 
class ActualizarUsuarioRequest(BaseModel):
    nombre:    str | None = None
    email:     str | None = None
    telefono:  str | None = None
    direccion: str | None = None
    password:  str | None = None   # Solo si quiere cambiarla
 
 
# ============================================================
#   ENDPOINT: GET /
#   Comprueba que la API está viva
# ============================================================
@app.get("/")
def raiz():
    return {"mensaje": "API CodeCenter funcionando ✅"}
 
 
# ============================================================
#   ENDPOINT: POST /login
#   El frontend envía username + password y recibe los datos
#   del usuario si son correctos, o un error 401 si no.
# ============================================================
@app.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    # 1. Buscamos el usuario por username
    usuario = db.query(models.Usuario).filter(
        models.Usuario.username == datos.username
    ).first()
 
    # 2. Si no existe o la contraseña no coincide → error
    if not usuario or usuario.password != hashear_password(datos.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
 
    # 3. Si todo está bien → devolvemos los datos del usuario
    #    (sin la contraseña, nunca se envía al frontend)
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
#   Devuelve los datos de un usuario por su ID.
#   El área de clientes lo llama al cargar la página.
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
 
    # Solo actualizamos los campos que vengan rellenos
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

@app.get("/disponibilidad")
def obtener_disponibilidad(deporte: str, fecha: str, db: Session = Depends(get_db)):
    lista_horas = horasLibres(db, deporte, fecha)
    
    return {"horas": lista_horas}
 
class ReservaSchema(BaseModel):
    deporte: str
    fecha: str
    hora: str
    usuario_nombre: str

@app.post("/Reservar")
def enviar_reserva(reserva: ReservaSchema, db: Session = Depends(get_db)):
    exito = registraReserva(
        db=db, 
        deporte=reserva.deporte, 
        fecha=reserva.fecha, 
        hora=reserva.hora, 
        usuario=reserva.usuario_nombre
    )
    
    return {"status": "ok", "mensaje": "Reserva enviada a la lógica"}