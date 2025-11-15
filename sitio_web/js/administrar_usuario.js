//Obtener los datos actuales
document.addEventListener("DOMContentLoaded", async ()=>{
    try{
        const respuesta = await fetch("http://10.96.17.30:5000/api/perfil",{
            method: "GET",
            headers: {"Content-type": "application/json"},
            credentials: "include"
        });
        const data = await respuesta.json();

        if(data.exito){
            const {nombre, telefono, saldo} = data.datos_usuarios;
            document.getElementById("usuario").value=nombre;
            document.getElementById("telefono").value=telefono;

            document.getElementById("saldoUsuario").textContent= '$${saldo.toFixed(2)}';
        }else{
            alert("Error no has iniciado sesion");
            window.location.href ="login.html";
        }
    }catch(error){
        console.error("error al cargar el pefil: ", error);
        alert("Error en conexion al servidor, seras re dirigido.");
        window.location.href = "login.html";
    }
});
//Actualizar datos  
document.getElementById("fomActualizar").addEventListener("submit", async(e) =>{
    e.preventDefault();
    const usuario = document.getElementById("usuario").value.trim();
    const telefono = document.getElementById("telefono").value.trim();
    const mensaje = document.getElementById("mensaje");

    if(!usuario ||!telefono ){
        mensaje.textContent ="Completa los campos";
        mensaje.style.color="red";
        return
    }
    try{
        const respuesta = await fetch("http://10.96.17.30:5000/api/perfil",{
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify({usuario,telefono})
        });
        const data = await respuesta.json();

        if(data.exito){
            mensaje.textContent ="Datos actualizados con exito";
            mensaje.style.color = "green";
        }else{
            mensaje.textContent= data.mensaje;
            mensaje.textContent.color ="red";
        }
    }catch(error){
        console.error("Error al actualizar:", error);
        mensaje.textContent = "Error de conexión al actualizar.";
        mensaje.style.color = "orange";
    }
});

//cerrar sesion
document.getElementById("btnLogout").addEventListener("click", async () =>{
    const mensaje = document.getElementById("mensaje");
    try {
        const respuesta = await fetch("http://10.96.17.30:5000/logout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include"
        });

        const data = await respuesta.json();

        if (data.exito) {
            alert("Has cerrado sesión.");
            window.location.href = "login.html"; // Lo mandamos al login
        } else {
            mensaje.textContent = data.mensaje || "Error al cerrar sesión";
            mensaje.style.color = "red";
        }
    } catch (error) {
        console.error("Error al cerrar sesión:", error);
        mensaje.textContent = "Error de conexión al cerrar sesión.";
        mensaje.style.color = "orange";
    }
});

//eliminar cuenta
document.getElementById("btnDelete").addEventListener("click", async () => {
    const mensaje = document.getElementById("mensaje");

    // --- REQUERIMIENTO: La alerta de confirmación ---
    const confirmar = window.confirm(
        "¿ESTÁS SEGURO DE QUE QUIERES ELIMINAR TU CUENTA?\n\n" +
        "Esta acción es permanente y no se puede deshacer."
    );

    // Si el usuario presiona "Cancelar", la función se detiene aquí.
    if (!confirmar) {
        mensaje.textContent = "Acción cancelada.";
        mensaje.style.color = "gray";
        return; 
    }

    // Si el usuario presiona "Aceptar", continuamos:
    mensaje.textContent = "Eliminando cuenta...";
    mensaje.style.color = "orange";

    try {
        const respuesta = await fetch("http://10.96.17.30:5000/api/perfil", {
            method: "DELETE", // Usamos el método DELETE
            headers: { "Content-Type": "application/json" },
            credentials: "include" // ¡ESENCIAL para enviar la cookie de sesión!
        });

        const data = await respuesta.json();

        if (data.exito) {
            // Éxito. El backend ya borró la sesión.
            alert("Tu cuenta ha sido eliminada permanentemente.");
            // Redirigimos al registro, ya que la cuenta no existe
            window.location.href = "register.html"; 
        } else {
            // Si el backend da un error (ej. 500)
            mensaje.textContent = data.mensaje || "Error al eliminar la cuenta";
            mensaje.style.color = "red";
        }
    } catch (error) {
        console.error("Error al eliminar cuenta:", error);
        mensaje.textContent = "Error de conexión al eliminar.";
        mensaje.style.color = "orange";
    }
});