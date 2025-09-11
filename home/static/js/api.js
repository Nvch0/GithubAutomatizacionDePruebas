console.log('nasdbhjkas')
async function generateToken() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://localhost:8000/api/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById('accessToken').value = 'Bearer ' + data.access;  // Asegúrate de que 'access' sea el campo correcto en la respuesta JSON
    } else {
        Swal.fire({
            title: "Error",
            text: "Verifica tus credenciales",
            icon: "error"
          });
    }
}

function copyToken() {
    const tokenField = document.getElementById('accessToken');
    tokenField.select();
    document.execCommand('copy');
    Swal.fire({
        title: "Copiado",
        text: "Token copiado al portapapeles",
        icon: "success"
      });
}