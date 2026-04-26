# Imagen de python que vamos a necesitar para el proyecto
FROM python:3.10 

#El directorio donde vamos a trabajar
WORKDIR /app

#se copian las dependencias al contenedor
COPY requirements.txt .

#instalar dependecias en el contenedor
RUN pip install -r requirements.txt

#pasamos todo el codigo que hemos hecho a sus carpetas correspondientes
COPY  backend/ .

#defino el puerto en el que va a trabajar nuestra aplicacion
EXPOSE 8000

# este comando inicia la app haciendo que se pueda ver desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]