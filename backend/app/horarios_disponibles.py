from pyexpat import model
from sqlalchemy.orm import Session
from app import models

# Horarios Deportes
HorariosCentro = {
    "futbol" : ["17:00 - 18:00", "19:00 - 20:00", "20:00 - 21:00"],
    "padel" : ["8:00 -9:00", "10:00 - 11:00", "12:00 - 13:00"]
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
