const socket = io();

const toggle = document.getElementById('togglePass');
const pass = document.getElementById('passInput');
const loginBtn = document.querySelector('.btn-login');
const userInput = document.getElementById('userInput'); // Usamos el ID nuevo

toggle.addEventListener('click', () => {
    const isText = pass.type === 'text';
    pass.type = isText ? 'password' : 'text';
    toggle.textContent = isText ? 'visibility' : 'visibility_off';
});

loginBtn.addEventListener('click', () => {
    const username = userInput.value.trim();
    const password = pass.value;

    if (username === "") {
        alert("Por favor, ingresa un usuario");
        return;
    }

    console.log("Enviando login para:", username);
    socket.emit('login', { username: username, password: password });
});

socket.on('login_response', (data) => {
    if (data.success) {

        localStorage.setItem("usuario", data.user);

        window.location.href = "/chat-plantilla";

    } else {
        alert("Error: " + data.message);
    }
});
