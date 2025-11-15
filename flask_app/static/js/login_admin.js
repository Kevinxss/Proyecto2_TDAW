document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-login-admin");
    const mensaje = document.getElementById("mensaje");
    const API_URL = "http://127.0.0.1:5000";

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const datos = {
            usuario: document.getElementById("usuario").value,
            contrasena: document.getElementById("contrasena").value
        };

        mensaje.textContent = "Verificando...";
        mensaje.style.color = "gray";

        try {
            const respuesta = await fetch(`${API_URL}/login_admin`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(datos)
            });

            const resultado = await respuesta.json();

            if (respuesta.ok && resultado.exito) {
                if (resultado.es_admin) {
                    mensaje.textContent = "✅ ¡Bienvenido Administrador! Redirigiendo...";
                    mensaje.style.color = "green";

                    // Esperar un segundo antes de redirigir
                    setTimeout(() => {
                        window.location.href = "admin_dashboard"; // 👈 tu HTML correcto
                    }, 1000);
                } else {
                    mensaje.textContent = resultado.mensaje || "No tienes permisos de administrador.";
                    mensaje.style.color = "orange";
                }
            } else {
                mensaje.textContent = resultado.mensaje || "Credenciales incorrectas.";
                mensaje.style.color = "red";
            }
        } catch (error) {
            console.error("Error en login:", error);
            mensaje.textContent = "❌ Error al conectar con el servidor.";
            mensaje.style.color = "red";
        }
    });
});
