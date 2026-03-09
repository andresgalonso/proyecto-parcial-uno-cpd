
const socket = io();

let usuarioActual = localStorage.getItem("usuario");
let conversacionActual = null;


/* ===========================
CONEXIÓN
=========================== */

socket.on("connect", () => {

    console.log("Conectado al servidor");

    socket.emit("conversaciones", {
    username: usuarioActual
});

});


/* ===========================
RECIBIR CONVERSACIONES
=========================== */

socket.on("lista_conversaciones", (data) => {

    const chatList = document.getElementById("chatList");

    chatList.innerHTML = "";

    data.conversaciones.forEach(chat => {

        const div = document.createElement("div");

        div.classList.add("friend-drawer");

        div.innerHTML = `
            <img src="/static/recursos/logo2-perfil.jpg" class="profile-image">
            <div class="text">
                <h6>${chat.nombre}</h6>
                <p></p>
            </div>
        `;

        div.onclick = () => abrirConversacion(chat.id, chat.nombre);

        chatList.appendChild(div);

        const hr = document.createElement("hr");
        hr.classList.add("m-0");

        chatList.appendChild(hr);

    });

});


/* ===========================
ABRIR CONVERSACIÓN
=========================== */

function abrirConversacion(id,nombre){

    conversacionActual = id;

    document.getElementById("chatNombre").textContent = nombre;

    socket.emit("obtener_mensajes", {
        conversacion_id:id
    });

}


/* ===========================
RECIBIR MENSAJES
=========================== */

socket.on("lista_mensajes", (data)=>{

    const chatBox = document.getElementById("chatBox");

    chatBox.innerHTML = "";

    data.mensajes.forEach(msg => {

        const div = document.createElement("div");

        if(msg.usuario === usuarioActual){

            div.classList.add("message","right");

        }else{

            div.classList.add("message","left");

        }

        div.textContent = msg.usuario + ": " + msg.mensaje;

        chatBox.appendChild(div);

    });

});


/* ===========================
LOGIN
=========================== */
socket.on("login_response",(data)=>{
    if(data.success){
        usuarioActual = data.user;
        socket.emit("conversaciones", { username: usuarioActual });
    }
});

/* ===========================
ENVIAR MENSAJES (NUEVO)
=========================== */
const mensajeInput = document.getElementById("mensajeInput");
const btnEnviar = document.getElementById("btnEnviar");
const searchInput = document.querySelector('.search-box input');

function enviarMensaje() {
    const texto = mensajeInput.value.trim();
    const destinatario = searchInput.value.trim();

    // 1. Validar que haya texto
    if (!texto) return;

    // 2. Validar que exista un destino (chat abierto o usuario en buscador)
    if (!conversacionActual && !destinatario) {
        alert("Selecciona un chat de la lista o busca un usuario para empezar.");
        return;
    }

    // 3. Emitir el evento
    socket.emit("send_message", {
        remitente: usuarioActual,
        destinatario: conversacionActual ? null : destinatario,
        conversacion_id: conversacionActual,
        mensaje: texto
    });

    mensajeInput.value = ""; // Limpiar input
}

btnEnviar.addEventListener("click", enviarMensaje);
mensajeInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") enviarMensaje();
});

/* ===========================
RECIBIR MENSAJES EN TIEMPO REAL (NUEVO)
=========================== */
socket.on("nuevo_mensaje", (msg) => {
    // Si era un chat nuevo mediante buscador y nosotros mandamos el mensaje
    if (!conversacionActual && searchInput.value.trim() && msg.usuario === usuarioActual) {
        conversacionActual = msg.conversacion_id;
        document.getElementById("chatNombre").textContent = "Chat con " + searchInput.value.trim();
        searchInput.value = "";
    }

    // Dibujar el mensaje si pertenece al chat abierto
    if (msg.conversacion_id === conversacionActual) {
        const chatBox = document.getElementById("chatBox");
        const div = document.createElement("div");

        div.classList.add("message", msg.usuario === usuarioActual ? "right" : "left");
        div.textContent = msg.usuario + ": " + msg.mensaje;

        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Refrescar lista lateral para actualizar el menú de chats
    socket.emit("conversaciones", { username: usuarioActual });
});

/* ===========================
CONTACTOS Y MENÚ
=========================== */

// 1. Mostrar la lista de contactos cuando pulsamos el globo de texto
document.getElementById("btnVerContactos").addEventListener("click", () => {
    socket.emit("obtener_contactos", { username: usuarioActual });
});

socket.on("lista_contactos", (data) => {
    const chatList = document.getElementById("chatList");
    // Cambiamos el título visualmente para saber que estamos en Contactos
    chatList.innerHTML = `<h6 class="p-3 mb-0 text-muted" style="background: #f8f9fa;">Tus Contactos</h6><hr class="m-0">`;

    if (!data.contactos || data.contactos.length === 0) {
        chatList.innerHTML += `<p class="p-3 text-muted text-center">No tienes contactos aún.</p>`;
        return;
    }

    data.contactos.forEach(contacto => {
        const div = document.createElement("div");
        div.classList.add("friend-drawer");
        div.innerHTML = `
            <img src="/static/recursos/logo2-perfil.jpg" class="profile-image">
            <div class="text">
                <h6>${contacto.nombre}</h6>
            </div>
        `;

        // Al hacer clic en el contacto, lo preparamos para un chat nuevo o existente
        div.onclick = () => {
            document.querySelector('.search-box input').value = contacto.nombre;
            conversacionActual = null;
            document.getElementById("chatNombre").textContent = "Chat con " + contacto.nombre;
            document.getElementById("chatBox").innerHTML = "";
        };

        chatList.appendChild(div);
        chatList.appendChild(document.createElement("hr")).classList.add("m-0");
    });
});

// 2. Lógica para el botón "Agregar" dentro del Modal
document.getElementById("btnGuardarContacto").addEventListener("click", () => {
    const nuevoContacto = document.getElementById("inputNuevoContacto").value.trim();
    if (!nuevoContacto) return;

    socket.emit("agregar_contacto", {
        mi_usuario: usuarioActual,
        nuevo_contacto: nuevoContacto
    });
});

// 3. Respuesta al intentar agregar un contacto
socket.on("respuesta_contacto", (data) => {
    alert(data.message);

    if (data.success) {
        // Ocultar el modal de Bootstrap
        const modalEl = document.getElementById('modalAgregarContacto');
        const modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        modalInstance.hide();

        // Limpiar el campo de texto
        document.getElementById("inputNuevoContacto").value = "";

        // Recargar la lista de contactos para que aparezca el nuevo
        socket.emit("obtener_contactos", { username: usuarioActual });
    }
});

/* ===========================
CREAR GRUPO
=========================== */
document.getElementById("btnGuardarGrupo").addEventListener("click", () => {
    const nombreGrupo = document.getElementById("inputNombreGrupo").value.trim();
    const miembrosStr = document.getElementById("inputMiembrosGrupo").value.trim();

    if (!nombreGrupo) {
        alert("El grupo debe tener un nombre.");
        return;
    }

    // Emitimos los datos al servidor
    socket.emit("crear_grupo", {
        creador: usuarioActual,
        nombre_grupo: nombreGrupo,
        miembros: miembrosStr
    });
});

socket.on("respuesta_grupo", (data) => {
    alert(data.message);

    if (data.success) {
        // Ocultar el modal
        const modalEl = document.getElementById('modalCrearGrupo');
        const modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        modalInstance.hide();

        // Limpiar inputs
        document.getElementById("inputNombreGrupo").value = "";
        document.getElementById("inputMiembrosGrupo").value = "";

        // Recargar la lista de conversaciones para ver el grupo nuevo
        socket.emit("conversaciones", { username: usuarioActual });
    }
});