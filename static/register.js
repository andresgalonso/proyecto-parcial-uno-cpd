function bindToggle(toggleId, inputId) {
    const toggle = document.getElementById(toggleId);
    const input  = document.getElementById(inputId);
    toggle.addEventListener('click', () => {
        const isText = input.type === 'text';
        input.type          = isText ? 'password' : 'text';
        toggle.textContent  = isText ? 'visibility' : 'visibility_off';
    });
}

bindToggle('togglePass',    'passInput');
bindToggle('toggleConfirm', 'confirmInput');

const strengthColors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71'];

document.getElementById('passInput').addEventListener('input', function () {
    const val = this.value;
    let score = 0;
    if (val.length >= 8)            score++;
    if (/[A-Z]/.test(val))          score++;
    if (/[0-9]/.test(val))          score++;
    if (/[^A-Za-z0-9]/.test(val))   score++;

    document.querySelectorAll('#strengthBar span').forEach((bar, i) => {
        bar.style.background = i < score ? strengthColors[score - 1] : '#e0e0e0';
    });
});

const btnRegister = document.querySelector('.btn-register');
const inputs = document.querySelectorAll('.field input');

btnRegister.addEventListener('click', async () => {
    const datos = {
        nombre: inputs[0].value.trim(),
        apellido: inputs[1].value.trim(),
        correo: inputs[2].value.trim(),
        usuario: inputs[3].value.trim(),
        contrasena: document.getElementById('passInput').value
    };

    if (!datos.nombre || !datos.apellido || !datos.correo || !datos.usuario || !datos.contrasena){
        return alert("Por favor, llena todos los campos.");
    }
    try{
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify(datos)
        });

        const result = await response.json();

        if (result.success) {
            alert("Cuenta creada!!");
            window.location.href = "/login"
        } else{
            alert(result.message);
        }
    } catch (error){
        alert("Error de conexion con el servidor");
    }

});
