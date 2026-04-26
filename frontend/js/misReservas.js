document.addEventListener('DOMContentLoaded', async () => {

    let reservas = [];

    try {
        const res = await fetch('http://localhost:8000/reservas/1');
        reservas = await res.json();
    } catch (e) {
        console.error('Error cargando reservas:', e);
    }

    const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
    const diasSemana = ['L','M','X','J','V','S','D'];

    let verMes = new Date();
    let diaSeleccionado = null;
    let selReserva = null;

    function diasConReserva() {
        return reservas.filter(r => r.estado === 'activa').map(r => r.fecha);
    }

    function renderSeccionCal() {
        const seccion = document.getElementById('contenido-cal');
        const activas = reservas.filter(r => r.estado === 'activa');

        let aviso = activas.length === 0 ? `
            <div class="sin-reservas">
                <p class="sin-reservas-texto">No tienes ninguna reserva activa.</p>
                <a href="nuevaReserva.html" class="btn-ir-reservar">Hacer una reserva</a>
            </div>` : '';

        seccion.innerHTML = `
            <div class="mes-nav">
                <button class="mes-btn" id="btn-prev">&#8592;</button>
                <span class="mes-titulo" id="mes-titulo"></span>
                <button class="mes-btn" id="btn-next">&#8594;</button>
            </div>
            <div class="cal" id="calendario"></div>
            ${aviso}
            <div class="leyenda">
                <div class="leyenda-item"><span class="punto gris"></span> Día normal</div>
                <div class="leyenda-item"><span class="punto verde"></span> Tu reserva</div>
                <div class="leyenda-item"><span class="punto oscuro"></span> Seleccionado</div>
            </div>
        `;

        document.getElementById('btn-prev').addEventListener('click', () => {
            verMes.setMonth(verMes.getMonth() - 1);
            renderCal();
        });
        document.getElementById('btn-next').addEventListener('click', () => {
            verMes.setMonth(verMes.getMonth() + 1);
            renderCal();
        });

        renderCal();
    }

    function renderCal() {
        const año = verMes.getFullYear();
        const mes = verMes.getMonth();
        document.getElementById('mes-titulo').textContent = meses[mes] + ' ' + año;

        const cal = document.getElementById('calendario');
        cal.innerHTML = diasSemana.map(d => `<div class="cal-header">${d}</div>`).join('');

        let primerDia = new Date(año, mes, 1).getDay();
        primerDia = primerDia === 0 ? 6 : primerDia - 1;

        for (let i = 0; i < primerDia; i++) {
            cal.innerHTML += `<div class="cal-day vacio"></div>`;
        }

        const totalDias = new Date(año, mes + 1, 0).getDate();
        const hoy = new Date();
        const conReserva = diasConReserva();

        for (let d = 1; d <= totalDias; d++) {
            const fechaStr = `${año}-${String(mes+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
            const esHoy = hoy.getFullYear()===año && hoy.getMonth()===mes && hoy.getDate()===d;
            const tieneRes = conReserva.includes(fechaStr);
            const esSel = diaSeleccionado === fechaStr;

            let cls = 'cal-day';
            if (tieneRes) cls += ' tiene-reserva';
            if (esHoy) cls += ' hoy';
            if (esSel) cls += ' seleccionado';

            cal.innerHTML += `<div class="${cls}" data-fecha="${fechaStr}">${d}</div>`;
        }

        cal.querySelectorAll('.cal-day[data-fecha]').forEach(el => {
            el.addEventListener('click', () => {
                diaSeleccionado = el.dataset.fecha;
                renderCal();
                mostrarDia(diaSeleccionado);
            });
        });
    }

    function mostrarDia(fecha) {
        const [y, m, d] = fecha.split('-');
        document.getElementById('dia-sel').textContent = `${d}/${m}/${y}`;

        const delDia = reservas.filter(r => r.fecha === fecha);
        const lista = document.getElementById('lista-reservas');

        if (!delDia.length) {
            lista.innerHTML = '<p class="texto-vacio">No tienes reservas este día.</p>';
            return;
        }

        lista.innerHTML = delDia.map(r => `
            <div class="reserva-item ${r.estado}" data-id="${r.id}">
                <div>
                    <div class="reserva-deporte">${r.deporte}</div>
                    <div class="reserva-horas">${r.hora_inicio} – ${r.hora_fin}</div>
                </div>
                <span class="badge ${r.estado}">${r.estado}</span>
            </div>
        `).join('');

        lista.querySelectorAll('.reserva-item').forEach(el => {
            el.addEventListener('click', () => abrirModal(parseInt(el.dataset.id)));
        });
    }

    function abrirModal(id) {
        selReserva = reservas.find(r => r.id == id);
        if (!selReserva) return;

        const [y, m, d] = selReserva.fecha.split('-');
        const fechaFormateada = `${d}/${m}/${y}`;

        document.getElementById('m-deporte').textContent = selReserva.deporte;
        document.getElementById('m-fecha').textContent = fechaFormateada;
        document.getElementById('m-fecha2').textContent = fechaFormateada;
        document.getElementById('m-inicio').textContent = selReserva.hora_inicio;
        document.getElementById('m-fin').textContent = selReserva.hora_fin;
        document.getElementById('m-dep').textContent = selReserva.deporte;
        document.getElementById('m-estado').textContent = selReserva.estado.charAt(0).toUpperCase() + selReserva.estado.slice(1);

        const estadoBar = document.getElementById('modal-estado-bar');
        if (selReserva.estado === 'cancelada') {
            estadoBar.style.background = '#fee';
            estadoBar.style.color = '#e74c3c';
        } else {
            estadoBar.style.background = '#d4f5e9';
            estadoBar.style.color = '#01c38d';
        }

        document.getElementById('btn-cancelar').disabled = selReserva.estado === 'cancelada';
        document.getElementById('btn-modificar').disabled = selReserva.estado === 'cancelada';

        document.getElementById('modal-detalle').style.display = 'flex';
    }

    function actualizarResumen() {
        const activas = reservas.filter(r => r.estado === 'activa');
        document.getElementById('r-activas').textContent = activas.length;

        const hoy = new Date();
        const prox = activas
            .filter(r => new Date(r.fecha) >= hoy)
            .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))[0];

        if (prox) {
            const [y, m, d] = prox.fecha.split('-');
            document.getElementById('r-proxima').textContent = `${d}/${m}`;
        } else {
            document.getElementById('r-proxima').textContent = '-';
        }

        document.getElementById('r-mes').textContent = activas
            .filter(r => new Date(r.fecha).getMonth() === hoy.getMonth()).length;
    }

    document.getElementById('btn-cerrar').addEventListener('click', () => {
        document.getElementById('modal-detalle').style.display = 'none';
    });

    document.getElementById('btn-cancelar').addEventListener('click', () => {
        document.getElementById('modal-detalle').style.display = 'none';
        document.getElementById('modal-confirmar').style.display = 'flex';
    });

    document.getElementById('btn-no').addEventListener('click', () => {
        document.getElementById('modal-confirmar').style.display = 'none';
        document.getElementById('modal-detalle').style.display = 'flex';
    });

    document.getElementById('btn-si').addEventListener('click', async () => {
        if (selReserva) {
            await fetch(`http://localhost:8000/reservas/${selReserva.id}/cancelar`, {
                method: 'PUT'
            });
            selReserva.estado = 'cancelada';
            document.getElementById('modal-confirmar').style.display = 'none';
            if (diaSeleccionado) mostrarDia(diaSeleccionado);
            renderSeccionCal();
            actualizarResumen();
        }
    });

    document.getElementById('btn-modificar').addEventListener('click', () => {
        if (selReserva) {
            document.getElementById('modal-detalle').style.display = 'none';
            window.location.href = `nuevaReserva.html?modificar=${selReserva.id}&deporte=${selReserva.deporte}&fecha=${selReserva.fecha}&hora_inicio=${selReserva.hora_inicio}&hora_fin=${selReserva.hora_fin}`;
        }
    });

    renderSeccionCal();
    actualizarResumen();
});
