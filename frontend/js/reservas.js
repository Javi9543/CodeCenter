document.addEventListener('DOMContentLoaded', () => {
    // 1. Capturamos la URL actual
    const urlParams = new URLSearchParams(window.location.search);

    // 2. Sacamos el valor de "deporte"
    const deporteSeleccionado = urlParams.get('deporte');

    // 3. Lo pintamos en el HTML (asegúrate de tener un id="nombre-deporte")
    const cajaTitulo = document.getElementById('nombre-deporte');

    if (deporteSeleccionado && cajaTitulo) {
        // Ponemos la primera letra en mayúscula para que quede bonito
        const textoFinal = deporteSeleccionado.charAt(0).toUpperCase() + deporteSeleccionado.slice(1);
        cajaTitulo.innerText = textoFinal;

        console.log("Calendario cargado para: " + textoFinal);
    }

    // --- 2. LÓGICA DEL CALENDARIO (Flatpickr) ---
    flatpickr("#calendario-inline", {
        inline: true,            // Siempre visible
        locale: "es",            // En español
        minDate: "today",        // No permite el pasado
        dateFormat: "d-m-Y",     // Formato día-mes-año

        onChange: function (selectedDates, dateStr) {
            // 1. Mostramos el div de horas
            document.getElementById('selector-horas').style.display = 'block';
            // 2. Escribimos la fecha seleccionada
            document.getElementById('fecha-elegida').innerText = dateStr;

            const contendorLista = document.querySelector('.grid-horas');
            contendorLista.innerHTML = "Buscando horarios...";

            console.log("Buscando disponibilidad para " + dateStr);

            fetch(`http://localhost:8000/disponibilidad?deporte=${deporteSeleccionado}&fecha=${dateStr}`)
                .then(response => response.json())
                .then(data => {
                    contendorLista.innerHTML = "";

                    if (data.horas && data.horas.length > 0) {
                        data.horas.forEach(hora => {

                            // elementos, de texto 
                            const fila = document.createElement('div');
                            fila.style.display = "flex";
                            fila.style.justifyContent = "center";
                            fila.style.alignItems = "center";
                            fila.style.gap = "15px";
                            fila.style.marginBottom = "8px";

                            const infoHora = document.createElement('p');
                            infoHora.innerText = "· " + hora;
                            infoHora.style.margin = "0";
                            infoHora.style.fontWeight = "500";

                            // boton de reserva para las horas disponibles
                            const botonReservar = document.createElement('button');
                            botonReservar.innerText = "Reservar";
                            botonReservar.className = "btn-azul";
                            botonReservar.style.backgroundColor = "#5D9CEC";
                            botonReservar.style.color = "white";
                            botonReservar.style.border = "none";
                            botonReservar.style.padding = "5px";
                            botonReservar.style.borderRadius = "8px";
                            botonReservar.style.cursor = "pointer";

                            botonReservar.onclick = () => { realizarReserva(deporteSeleccionado, dateStr, hora) };
                            fila.appendChild(infoHora);
                            fila.appendChild(botonReservar);
                            contendorLista.appendChild(fila);

                        });
                    } else {
                        contendorLista.innerHTML = "<p>No hay horarios disponibles</p>";
                    }

                    // funcion para enviar reservas
                    function realizarReserva(deporte, fecha, hora) {
                        const usuario = JSON.parse(sessionStorage.getItem('usuario'));
                        if (confirm(`¿Quiere reservar ${deporte} para la fecha ${fecha} en el rango de: ${hora}?`)) {
                            fetch('http://localhost:8000/reservar', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    deporte: deporte,
                                    fecha: fecha,
                                    hora: hora,
                                    usuario_id: usuario.id
                                })
                            })
                            .then(res => res.json())
                            .then(data => {alert("Reserva Confirmada, gracias por reservar")})
                            .catch(err => alert("Error al conectar con el servidor"));
                        }
                    }
            }   );
        }


    });

});
