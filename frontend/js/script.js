console.log("Script iniciado...");

document.addEventListener('DOMContentLoaded', () => {
    const tarjetas = document.querySelectorAll('.tarjeta-clicable');
    
    console.log("Se han encontrado " + tarjetas.length + " tarjetas");

    tarjetas.forEach(tarjeta => {
        tarjeta.addEventListener('click', function(e) {
            // Evitamos cualquier comportamiento por defecto
            e.preventDefault(); 
            
            const deporte = this.getAttribute('data-deporte');
            console.log("Clic en: " + deporte);

            if (deporte) {
                // Forzamos la redirección
                const destino = "reservas.html?deporte=" + encodeURIComponent(deporte);
                console.log("Redirigiendo a: " + destino);
                window.location.assign(destino); 
            } else {
                alert("Error: Esta tarjeta no tiene data-deporte definido en el HTML");
            }
        });
    });
});