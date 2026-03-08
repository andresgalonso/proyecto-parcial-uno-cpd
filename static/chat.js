
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

        socket.emit("conversaciones");

    }

});