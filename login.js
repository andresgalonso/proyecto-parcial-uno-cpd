const toggle = document.getElementById('togglePass');
const pass = document.getElementById('passInput');

toggle.addEventListener('click', () => {
    const isText = pass.type === 'text';
    pass.type = isText ? 'password' : 'text';
    toggle.textContent = isText ? 'visibility' : 'visibility_off';
});