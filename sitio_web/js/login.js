// js/login.js (CORREGIDO)

document.getElementById("formLogin").addEventListener("submit", async (e) =>{
    e.preventDefault();
    
    // (Asegúrate de que la IP sea la correcta)
    const API_URL = "http://192.168.1.87:5000"; // (Usa la IP que tengas ahora)
    
    const usuario = document.getElementById("usuario").value.trim();
    const password = document.getElementById("password").value.trim();
    const menmsaje = document.getElementById("mensaje"); 

    if(!usuario || !password){
        menmsaje.textContent = "completa los campos";
        menmsaje.style.color ="red";
        return;
    }
    
    try{
        const respuesta = await fetch(`${API_URL}/login`,{
            method: "POST",
            headers: {"Content-Type": "application/json"}, 
            body : JSON.stringify({usuario, password}),
            credentials: "include" 
        });
        
        const data = await respuesta.json();

        if(data.exito){
            localStorage.setItem("usuarioActivo", data.usuario);
            menmsaje.textContent ="Inicio de sesión exitoso";
            menmsaje.style.color="green";

            setTimeout(()=>{
                window.location.href ="index.html"; 
            }, 1000);
        } else {
            menmsaje.textContent = data.mensaje || "Usuario o contraseña incorrectos";
            menmsaje.style.color = "red";
        }
    } catch(error){
        console.error("Error en fetch de login:", error);
        menmsaje.textContent="Error al conectar con el servidor";
        menmsaje.style.color ="orange";
    }
});