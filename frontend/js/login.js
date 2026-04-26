/**
 * login.js — Conecta el formulario de login con la API
 * ======================================================
 * Cuando el usuario pulsa "Entrar":
 *   1. Recoge username y password del formulario
 *   2. Llama a POST /login en el backend
 *   3. Si es correcto → guarda los datos en sessionStorage y redirige
 *   4. Si falla → muestra un mensaje de error
 */
 
document.addEventListener('DOMContentLoaded', () => {
 
    const boton = document.querySelector('button');
    const inputUser = document.getElementById('user');
    const inputPass = document.getElementById('password');
 
    // Eliminamos el <a> dentro del botón, la redirección la hacemos por JS
    boton.innerHTML = 'Entrar';
 
    // Creamos el mensaje de error (oculto por defecto)
    const mensajeError = document.createElement('p');
    mensajeError.style.cssText = 'color:#e84c2b; text-align:center; margin-top:10px;';
    mensajeError.style.display = 'none';
    boton.insertAdjacentElement('afterend', mensajeError);
 
    boton.addEventListener('click', async () => {
        const username = inputUser.value.trim();
        const password = inputPass.value.trim();
 
        // Validación básica
        if (!username || !password) {
            mensajeError.textContent = 'Por favor, rellena todos los campos.';
            mensajeError.style.display = 'block';
            return;
        }
 
        boton.textContent = 'Comprobando...';
        boton.disabled = true;
 
        try {
            const respuesta = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
 
            if (respuesta.ok) {
                // ✅ Login correcto
                const usuario = await respuesta.json();
 
                // Guardamos los datos del usuario para usarlos en otras páginas
                sessionStorage.setItem('usuario', JSON.stringify(usuario));
 
                // Redirigimos según si es admin o cliente normal
                if (usuario.es_admin) {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'nuevaReserva.html';
                }
 
            } else {
                // ❌ Usuario o contraseña incorrectos
                mensajeError.textContent = 'Usuario o contraseña incorrectos. Inténtalo de nuevo.';
                mensajeError.style.display = 'block';
                boton.textContent = 'Entrar';
                boton.disabled = false;
            }
 
        } catch (error) {
            // Error de red (backend no arrancado, etc.)
            mensajeError.textContent = 'No se puede conectar con el servidor. ¿Está el backend arrancado?';
            mensajeError.style.display = 'block';
            boton.textContent = 'Entrar';
            boton.disabled = false;
        }
    });
 
});
 