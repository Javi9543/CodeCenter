# Guia  


Este proycto consiste en el desarrollo y despliegue de una plataforma web para la gestión de un centro deportivo que hemos decidido llamarlo CodeCenter. el objetivo principal ha sido crear una interfaz intuitiva para los usuarios, donde puedan consultar cuotas, horarios, realizar reservas de las instalaciones de forma dinamica, etc.

El proyecto no solo se centra en el frontend, sino tambien en la infraestructura y el flujo de trabajo, empleando dockers, y simulando un entorno de trabajo real con Git. 


###  Preparacion del entorno


he creado los archivos base del Frontend configurados para poder trabajar en local. simulando el docker en la instancia, y he metido los siguientes archivos:

index.html: El contenido de la web simulando "pagina en obras", para comprobar que funciona.

![](./img/4.png)

default.conf: Las reglas del servidor.

¿que hace este directorio?
le dice a nginsx que hacer cuando alguien escribe localhost en el navegador.

Aqui es donde mas adelante se unira el frontend con el backend.

![](./img/2.png)

Dockerfile: Las instrucciones para montar la imagen del servidor.

![](./img/1.png)

docker-compose.yml: El mando a distancia para encenderlo todo. 

¿que contiene mi docker compose?
1. build: le digo que use el dockerfile que hay en el directorio frontend
2. el nombre del contenedor se va a llamar web_frontend
3. El puerto va a ser el 80
4. el volumen: es el tunel que hago desde la carpeta local y la carpeta del servidor de dentro del Docker.
5. la red app-network: es una red privada virtual.


![](./3.png)

he conectado la carpeta local con github

### Vamos a por ese frontend

yo me he encargado de la pagina de nuevas, reservas y la pagina de mis reservas. 

he hecho el html, el css y js, de mis paginas.

una vez que todos hemos conseguido hacer el git, hemos unificado, hemos normalizado los archivos. renombrando, limpiando el codigo, y por supuesto, aun falta trabajo...




