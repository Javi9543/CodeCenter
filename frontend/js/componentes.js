document.addEventListener('DOMContentLoaded', () => {
    const headerElement = document.querySelector('header');
    const footerElement = document.querySelector('footer');

    // --- NAV GENERAL ---
    const navGeneral = `
    <nav class="navbar">
        <div class="logo"><img src="img/logo.png"></div>
        <ul class="nav-menu">
            <li><a href="index.html">Inicio</a></li>
            <li><a href="instalaciones.html">Instalaciones</a></li>
            <li><a href="horario.html">Horario</a></li>
            <li><a href="cuotas.html">Cuotas</a></li>
            <li><a href="contacto.html">Contacto</a></li>
            <li><a href="login.html">Area clientes</a></li>
        </ul>
        <div class="menu-toggle" id="mobile-menu">
            <span></span><span></span><span></span>
        </div>
    </nav>`;

    // --- NAV CLIENTES ---
    const navClientes = `
    <nav class="navbar">
        <div class="logo"><img src="img/logo.png"></div>
        <ul class="nav-menu">
            <li><a href="index.html">Inicio</a></li>
            <li><a href="instalaciones.html">Instalaciones</a></li>
            <li><a href="horario.html">Horario</a></li>
            <li><a href="contacto.html">Contacto</a></li>
            <li><a href="reservas.html">Mis Reservas</a></li>
            <li><a href="nuevaReserva.html">Nueva Reserva</a></li>
            <li class="usuario-logeado">
                <a href="perfil.html">
                    <span class="icono-user">👤</span> Hola, Juan Pérez
                </a>
            </li>
        </ul>          
        <div class="menu-toggle" id="mobile-menu">
            <span></span><span></span><span></span>
        </div>
    </nav>`;

    // --- FOOTER  ---
    const footerHTML = `
        <address>
            <p>VISITANOS EN:</p>
            <p>Calle Deporte S/N</p>
            <p>Atarfe, Granada</p>
            <p><a href="https://maps.app.goo.gl/YENijyQXo9Ayx89B7" target="_blank" style="color: #5D9CEC; text-decoration: none;">📍 Ver en Google Maps</a></p>
        </address>
        <div class="footer-centro">
            <p>© 2026 CodeCenter. Todos los derechos reservados.</p>
        </div>
        <div class="footer-redes">
            <img src="img/facebook.png" alt="FB">
            <img src="img/instagram.png" alt="IG">
            <img src="img/twiter.png" alt="TW">
            <img src="img/telegram.png" alt="TG">
            <img src="img/whatsapp.png" alt="WA">
        </div>`;

    // Inyectar header segun nav
    if (headerElement) {
        const tipo = headerElement.getAttribute('data-nav');
        headerElement.innerHTML = (tipo === 'clientes') ? navClientes : navGeneral;

         // --- LÓGICA DEL MENÚ MÓVIL ---
        const mobileMenu = document.getElementById('mobile-menu');
        const navMenu = document.querySelector('.nav-menu');

        if (mobileMenu) {
            mobileMenu.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                mobileMenu.classList.toggle('is-active');
            });
        }
    }
    
    // Inyectar footer
    if (footerElement) {
        footerElement.innerHTML = footerHTML;
    }
});