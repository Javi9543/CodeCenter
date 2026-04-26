document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const deporteSeleccionado = urlParams.get('deporte');
    const cajaTitulo = document.getElementById('nombre-deporte');
    
    let verMes = new Date();
    let diaSeleccionado = null;
    let datosReserva = { deporte: '', fecha: '', hora: '', elemento: null };

    if (deporteSeleccionado && cajaTitulo) {
        cajaTitulo.innerText = deporteSeleccionado.toUpperCase();
    }

    function renderCal() {
        const contenedor = document.getElementById('contenido-cal');
        const año = verMes.getFullYear();
        const mes = verMes.getMonth();
        const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
        const diasSemana = ['L','M','X','J','V','S','D'];

        contenedor.innerHTML = `
            <div class="mes-nav">
                <button class="mes-btn" id="btn-prev">←</button>
                <span class="mes-titulo">${meses[mes]} ${año}</span>
                <button class="mes-btn" id="btn-next">→</button>
            </div>
            <div class="cal-grid" id="cal-grid"></div>
        `;

        const grid = document.getElementById('cal-grid');
        grid.innerHTML = diasSemana.map(d => `<div class="cal-header">${d}</div>`).join('');

        let primerDia = new Date(año, mes, 1).getDay();
        primerDia = (primerDia === 0) ? 6 : primerDia - 1;

        for (let i = 0; i < primerDia; i++) grid.innerHTML += `<div class="cal-day vacio"></div>`;

        const totalDias = new Date(año, mes + 1, 0).getDate();
        
        // Fecha de hoy a las 00:00 para comparar solo el día
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);

        for (let d = 1; d <= totalDias; d++) {
            const fechaObj = new Date(año, mes, d);
            const fechaStr = `${String(d).padStart(2,'0')}-${String(mes+1).padStart(2,'0')}-${año}`;
            
            const esHoy = hoy.getTime() === fechaObj.getTime();
            const esPasado = fechaObj < hoy;
            const esSel = diaSeleccionado === fechaStr;

            let cls = 'cal-day';
            if (esPasado) cls += ' pasado'; // Clase para días pasados
            if (esHoy) cls += ' hoy';
            if (esSel) cls += ' seleccionado';

            grid.innerHTML += `<div class="${cls}" data-fecha="${fechaStr}">${d}</div>`;
        }

        document.getElementById('btn-prev').onclick = () => { verMes.setMonth(verMes.getMonth() - 1); renderCal(); };
        document.getElementById('btn-next').onclick = () => { verMes.setMonth(verMes.getMonth() + 1); renderCal(); };

        grid.querySelectorAll('.cal-day[data-fecha]').forEach(el => {
            el.onclick = () => {
                // Si el día es pasado, no permitimos seleccionarlo
                if (el.classList.contains('pasado')) return;

                diaSeleccionado = el.dataset.fecha;
                renderCal(); 
                buscarHoras(diaSeleccionado);
            };
        });
    }

    function buscarHoras(fecha) {
        document.getElementById('selector-horas').style.display = 'block';
        document.getElementById('fecha-elegida').innerText = fecha;
        const grid = document.querySelector('.grid-horas');
        grid.innerHTML = "<p style='grid-column: 1/-1; text-align: center;'>Buscando disponibilidad...</p>";

        fetch(`http://localhost:8000/disponibilidad?deporte=${deporteSeleccionado}&fecha=${fecha}`)
            .then(res => res.json())
            .then(data => {
                grid.innerHTML = "";
                if (data.horas && data.horas.length > 0) {
                    data.horas.forEach(hora => {
                        const btn = document.createElement('button');
                        btn.className = "btn-reserva-hora";
                        btn.innerText = hora;
                        btn.onclick = () => {
                            datosReserva = { deporte: deporteSeleccionado, fecha: fecha, hora: hora, elemento: btn };
                            document.getElementById('texto-detalle-reserva').innerText = `Reserva de ${deporteSeleccionado} para el ${fecha} a las ${hora}.`;
                            document.getElementById('modal-confirmar').style.display = 'flex';
                        };
                        grid.appendChild(btn);
                    });
                } else {
                    grid.innerHTML = "<p style='grid-column: 1/-1; color: #999; text-align: center;'>No hay disponibilidad.</p>";
                }
            });
    }

    document.getElementById('btn-cancelar-reserva').onclick = () => document.getElementById('modal-confirmar').style.display = 'none';
    document.getElementById('btn-cerrar-exito').onclick = () => document.getElementById('modal-exito').style.display = 'none';

    document.getElementById('btn-aceptar-reserva').onclick = async () => {
        const user = JSON.parse(sessionStorage.getItem('usuario'));
        try {
            const res = await fetch('http://localhost:8000/reservar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...datosReserva, usuario_id: user.id })
            });
            if (res.ok) {
                document.getElementById('modal-confirmar').style.display = 'none';
                datosReserva.elemento.classList.add('reservado');
                setTimeout(() => {
                    datosReserva.elemento.remove();
                    if (document.querySelector('.grid-horas').children.length === 0) {
                        document.querySelector('.grid-horas').innerHTML = "<p>Horario completo.</p>";
                    }
                }, 300);
                document.getElementById('modal-exito').style.display = 'flex';
            }
        } catch (e) { console.error(e); }
    };

    renderCal();
});