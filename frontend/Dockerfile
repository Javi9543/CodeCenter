# Usamos la imagen oficial de Nginx
FROM nginx:alpine

# Copiamos nuestra configuración personalizada de Nginx
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copiamos el código de nuestra web a la carpeta que Nginx usa para servir archivos
COPY . /usr/share/nginx/html

# Exponemos el puerto 80
EXPOSE 80
