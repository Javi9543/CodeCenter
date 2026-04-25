from sqlalchemy.orm import Session
from app import models

# Horarios Deportes
HorariosCentro = {
    "padel" : ["08:00 - 09:00", "10:00 - 11:00", "12:00 - 13:00"],
    "tenis" : ["9:10 - 14:10", "14:20 - 18:40", "19:40 - 20:00"],
    "correr" : ["08: 15 - 14:15",  "16:25 - 20:45"],
    "spinning" : ["08:15 - 09:15", "10:15 - 11:15", "16:15 - 17:15"],
    "boxeo" : ["9:15 - 11:15" , "16:15 - 18:20", "20:15 - 22:15"],
    "funcional" : ["08:15 - 15:15", "16:15 - 22:15"],
    "crostra" : ["10:15 - 11:15" , "12:15 - 13:15", "16:15 - 18:15"],
    "pesas" : ["09:15 - 11:15", "12:30 - 13:30", "16:30 - 17:30"],
    "nadar" : ["10:15 - 12:15", "13-45, 14:00", "18:30 - 20:00"],
    "futbol" : ["08:00 - 10:00", "11:00 - 13:00", "16:00 - 18:00"],
    "basket" : ["09:00 - 11:00", "12:00 - 14:00", "17:00 - 19:00"],
    "voley" : ["10:00 - 12:00", "16:00 - 18:00", "19:00 - 22:00"]
}

# Con esto se mostrarán las horas libres y ocultará las horas que no estan disponibles
def horasLibres(db, deporte: str, fecha:str):
    deporte_nomb = deporte.lower()
    
    #Comprobar que el deporte seleccionado existe, si no muestra una lista vacia
    horario_aux = HorariosCentro.get(deporte_nomb, [])

    if not horario_aux:
        return []

    # Buscar reservas que ya HAY en la bd para luego mostrar las horas disponibles
    reservado = db.query(models.Reserva).filter(
        models.Reserva.deporte == deporte_nomb, 
        models.Reserva.fecha == fecha
        ).all()

    horas_reserv = {reserv.hora for reserv in reservado}

    # Esto muestra las horas disponibles SIN las horas ya reservadas
    horasDisp = [hora for hora in horario_aux if hora not in horas_reserv]
    return horasDisp

def registraReserva(db: Session, deporte: str, fecha: str, hora: str, usuario_id: int):
    try:
        nuevaReserva = models.Reserva(
            deporte = deporte,
            fecha = fecha,
            hora = hora,
            usuario_id = usuario_id
        ) 
        db.add(nuevaReserva)
        db.commit()
        db.refresh(nuevaReserva)
        print("Reserva Guardada")
        return True

    except Exception as e: 
        db.rollback()
        print("Error al insertar la reserva")
        return False