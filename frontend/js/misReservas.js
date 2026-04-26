document.addEventListener('DOMContentLoaded', async () => {
    let reservas = [];

    async function cargarReservas() {
        try {
            const usuario = JSON.parse(sessionStorage.getItem('usuario'));
            const idUsuario = usuario ? usuario.id : 1;
            const res = await fetch(`http://localhost:8000/reservas/${idUsuario}`);
            const data = await res.json();
            reservas = Array.isArray(data) ? data : [];
            renderSeccionCal();
            actualizarResumen();
        } catch (e) {
            console.error('Error:', e);
        }
    }

    const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
    const diasSemana = ['L','M','X','J','V','S','D'];
    let verMes = new Date();
    let diaSeleccionado = null;
    let selReserva = null;

    const parseFechaRepo = (str) => {
        if(!str) return new Date(0);
        const [d, m, y] = str.split('-');
        return new Date(y, m - 1, d);
    };

    function renderSeccionCal() {
        const seccion = document.getElementById('contenido-cal');
        seccion.innerHTML = `
            <div class="mes-nav">
                <button class="mes-btn" id="btn-prev">←</button>
                <span class="mes-titulo" id="mes-titulo"></span>
                <button class="mes-btn" id="btn-next">→</button>
            </div>
            <div class="cal" id="calendario"></div>
            <div class="leyenda">
                <div class="leyenda-item"><span class="punto gris"></span> Pasado</div>
                <div class="leyenda-item"><span class="punto verde"></span> Tu reserva</div>
                <div class="leyenda-item"><span class="punto seleccionado"></span> Seleccionado</div>
            </div>`;

        document.getElementById('btn-prev').onclick = () => { verMes.setMonth(verMes.getMonth() - 1); renderCal(); actualizarResumen(); };
        document.getElementById('btn-next').onclick = () => { verMes.setMonth(verMes.getMonth() + 1); renderCal(); actualizarResumen(); };
        renderCal();
    }

    function renderCal() {
        const año = verMes.getFullYear();
        const mes = verMes.getMonth();
        document.getElementById('mes-titulo').textContent = meses[mes] + ' ' + año;
        const cal = document.getElementById('calendario');
        cal.innerHTML = diasSemana.map(d => `<div class="cal-header">${d}</div>`).join('');

        let primerDia = new Date(año, mes, 1).getDay();
        primerDia = (primerDia === 0) ? 6 : primerDia - 1;

        for (let i = 0; i < primerDia; i++) cal.innerHTML += `<div class="cal-day vacio"></div>`;

        const totalDias = new Date(año, mes + 1, 0).getDate();
        const hoyReal = new Date();
        hoyReal.setHours(0, 0, 0, 0);

        const conReserva = reservas.map(r => r.fecha);

        for (let d = 1; d <= totalDias; d++) {
            const fechaObj = new Date(año, mes, d);
            const fechaStr = `${String(d).padStart(2,'0')}-${String(mes+1).padStart(2,'0')}-${año}`;
            
            const esHoy = hoyReal.getTime() === fechaObj.getTime();
            const esPasado = fechaObj < hoyReal;
            const tieneRes = conReserva.includes(fechaStr);
            const esSel = diaSeleccionado === fechaStr;

            let cls = 'cal-day';
            if (esPasado) cls += ' pasado'; // Bloqueo visual
            if (tieneRes) cls += ' tiene-reserva';
            if (esHoy) cls += ' hoy';
            if (esSel) cls += ' seleccionado';

            cal.innerHTML += `<div class="${cls}" data-fecha="${fechaStr}">${d}</div>`;
        }

        cal.querySelectorAll('.cal-day[data-fecha]').forEach(el => {
            el.onclick = () => {
                if (el.classList.contains('pasado')) return; // Bloqueo de clic
                diaSeleccionado = el.dataset.fecha;
                renderCal();
                mostrarDia(diaSeleccionado);
            };
        });
    }

    // Funciones mostrarDia, abrirModal, actualizarResumen... se mantienen igual
    function mostrarDia(fecha) {
        const [d, m, y] = fecha.split('-');
        document.getElementById('dia-sel').textContent = `${d}/${m}/${y}`;
        const delDia = reservas.filter(r => r.fecha === fecha);
        const lista = document.getElementById('lista-reservas');
        if (!delDia.length) { lista.innerHTML = '<p class="texto-vacio">Sin reservas este día.</p>'; return; }
        lista.innerHTML = delDia.map(r => `<div class="reserva-item" data-id="${r.id}" id="reserva-${r.id}"><div><div class="reserva-deporte">${r.deporte}</div><div class="reserva-horas">${r.hora}</div></div><span class="badge activa">activa</span></div>`).join('');
        lista.querySelectorAll('.reserva-item').forEach(el => { el.onclick = () => abrirModal(parseInt(el.dataset.id)); });
    }

    function abrirModal(id) {
        selReserva = reservas.find(r => r.id == id);
        if (!selReserva) return;
        const [d, m, y] = selReserva.fecha.split('-');
        const f = `${d}/${m}/${y}`;
        document.getElementById('m-deporte').textContent = selReserva.deporte;
        document.getElementById('m-fecha').textContent = f;
        document.getElementById('m-fecha2').textContent = f;
        document.getElementById('m-inicio').textContent = selReserva.hora;
        document.getElementById('m-fin').textContent = selReserva.hora;
        document.getElementById('m-dep').textContent = selReserva.deporte;
        document.getElementById('modal-detalle').style.display = 'flex';
    }

    function actualizarResumen() {
        document.getElementById('r-activas').textContent = reservas.length;
        const hoyReal = new Date(); hoyReal.setHours(0,0,0,0);
        const ordenadas = reservas.map(r => ({...r, fObj: parseFechaRepo(r.fecha)})).sort((a,b) => a.fObj - b.fObj);
        const prox = ordenadas.find(r => r.fObj >= hoyReal);
        document.getElementById('r-proxima').textContent = prox ? prox.fecha.split('-').slice(0,2).join('/') : '-';
        const mesVisible = verMes.getMonth();
        const añoVisible = verMes.getFullYear();
        const contadorMes = reservas.filter(r => {
            const date = parseFechaRepo(r.fecha);
            return date.getMonth() === mesVisible && date.getFullYear() === añoVisible;
        }).length;
        document.getElementById('r-mes').textContent = contadorMes;
    }

    document.getElementById('btn-cerrar').onclick = () => document.getElementById('modal-detalle').style.display = 'none';
    document.getElementById('btn-cancelar').onclick = () => { document.getElementById('modal-detalle').style.display = 'none'; document.getElementById('modal-confirmar').style.display = 'flex'; };
    document.getElementById('btn-no').onclick = () => { document.getElementById('modal-confirmar').style.display = 'none'; document.getElementById('modal-detalle').style.display = 'flex'; };
    document.getElementById('btn-modificar').onclick = () => { if (selReserva) window.location.href = `reservas.html?deporte=${selReserva.deporte.toLowerCase()}`; };

    document.getElementById('btn-si').onclick = async () => {
        if (!selReserva) return;
        const idABorrar = selReserva.id;
        const elementoReserva = document.getElementById(`reserva-${idABorrar}`);
        try {
            document.getElementById('modal-confirmar').style.display = 'none';
            if (elementoReserva) elementoReserva.classList.add('eliminando');
            const resPromise = fetch(`http://localhost:8000/reservas/${idABorrar}/cancelar`, { method: 'DELETE' });
            await Promise.all([resPromise, new Promise(r => setTimeout(r, 400))]);
            const res = await resPromise;
            if (res.ok) { reservas = reservas.filter(r => r.id !== idABorrar); renderCal(); actualizarResumen(); if (diaSeleccionado) mostrarDia(diaSeleccionado); }
        } catch (e) { console.error(e); }
    };

    cargarReservas();
});