/**
 * aClientes.js — Carga y actualiza los datos del usuario
 */
 
document.addEventListener('DOMContentLoaded', async () => {
 
    const usuarioGuardado = JSON.parse(sessionStorage.getItem('usuario') || 'null');
 
    if (!usuarioGuardado) {
        alert('Debes iniciar sesión primero.');
        window.location.href = 'login.html';
        return;
    }
 
    try {
        const respuesta = await fetch(`http://localhost:8000/usuarios/${usuarioGuardado.id}`);
        const usuario = await respuesta.json();
 
        document.getElementById('aside-nombre').textContent    = usuario.nombre    || '—';
        document.getElementById('aside-username').textContent  = '@' + (usuario.username || '');
        document.getElementById('aside-email').textContent     = usuario.email     || '—';
        document.getElementById('aside-telefono').textContent  = usuario.telefono  || '—';
        document.getElementById('aside-direccion').textContent = usuario.direccion || '—';
 
        document.getElementById('email').value     = usuario.email     || '';
        document.getElementById('telefono').value  = usuario.telefono  || '';
        document.getElementById('direccion').value = usuario.direccion || '';
 
    } catch (error) {
        console.error('Error al cargar los datos del usuario:', error);
    }
 
    const btnGuardar = document.getElementById('btn-guardar');
    const msgOk      = document.getElementById('msg-ok');
    const msgErr     = document.getElementById('msg-err');
 
    btnGuardar.addEventListener('click', async () => {
 
        msgOk.style.display  = 'none';
        msgErr.style.display = 'none';
 
        const datosActualizados = {
            email:     document.getElementById('email').value.trim()     || null,
            telefono:  document.getElementById('telefono').value.trim()  || null,
            direccion: document.getElementById('direccion').value.trim() || null,
        };
 
        const nuevaPassword = document.getElementById('password').value.trim();
        if (nuevaPassword) datosActualizados.password = nuevaPassword;
 
        try {
            const respuesta = await fetch(`http://localhost:8000/usuarios/${usuarioGuardado.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosActualizados)
            });
 
            if (respuesta.ok) {
                msgOk.style.display = 'block';
                document.getElementById('password').value = '';
 
                if (datosActualizados.email)     document.getElementById('aside-email').textContent     = datosActualizados.email;
                if (datosActualizados.telefono)  document.getElementById('aside-telefono').textContent  = datosActualizados.telefono;
                if (datosActualizados.direccion) document.getElementById('aside-direccion').textContent = datosActualizados.direccion;
 
            } else {
                msgErr.textContent   = 'Error al guardar. Inténtalo de nuevo.';
                msgErr.style.display = 'block';
            }
 
        } catch (error) {
            msgErr.textContent   = 'No se puede conectar con el servidor.';
            msgErr.style.display = 'block';
        }
    });
 
});