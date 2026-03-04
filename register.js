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
