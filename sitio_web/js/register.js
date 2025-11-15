document.getElementById("formRegister").addEventListener("submit", async(e) => {
    e.preventDefault();

    const usuario = document.getElementById("nombre").value.trim();
    const telefono = document.getElementById("telefono").value.trim();
    const password = document.getElementById("password").value.trim();
    const passwordConfirm = document.getElementById("passwordConfirm").value.trim();
    const mensaje = document.getElementById("mensaje");

    //validacion de campos vacios
    if(!usuario ||!telefono ||!password || !passwordConfirm){
        mensaje.textContent ="completa los campos";
        mensaje.style.color ="red";
        return;
    }

    //validacion de contraseña
    if(password !== passwordConfirm){
        mensaje.textContent ="la contraseña no coiciden";
        mensaje.style.color ="red";
        return
    }


    //enviamos al backend

    try{
        const respuesta = await fetch("http://10.96.17.30:5000/register",{
            method: "POST",
            headers: {"Content-type":"application/json"},
            body: JSON.stringify({usuario, password, telefono}),
            credentials: "include"
        });

        const data = await respuesta.json();

        if(data.exito){
            mensaje.textContent ="Usuario registrado con exito";
            mensaje.style.color="green";

            setTimeout(()=>{
                window.location.href ="login.html";
            },2000);
        }else{
            mensaje.textContent=data.mensaje;
            mensaje.style.color="red";
        }
    } catch(error){
        mensaje.textContent="Error al conectar con el servidor";
        mensaje.style.color="orange";
    }



});