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
        
        onChange: function(selectedDates, dateStr) {
            // 1. Mostramos el div de horas
            document.getElementById('selector-horas').style.display = 'block';
            // 2. Escribimos la fecha seleccionada
            document.getElementById('fecha-elegida').innerText = dateStr;
            
            console.log("Buscando disponibilidad para " + dateStr);
        }

        
    });

});
