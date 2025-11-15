// js/carrito.js

const API_URL = "http://10.96.17.30:5000"; // (Usa la IP que corresponda)
const POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon";
const PRECIO_POKEMON = 500; // El precio que definimos

// 1. Verificar sesión
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch(`${API_URL}/api/perfil`, {
            method: "GET",
            credentials: "include"
        });
        if (!res.ok) throw new Error("Sesión no válida");
        
        cargarCarrito(); // Cargar carrito si la sesión es válida
    } catch (error) {
        alert("Debes iniciar sesión primero.");
        window.location.href = "login.html";
    }
});

// 2. Cargar el carrito
async function cargarCarrito() {
    const contenedor = document.getElementById("carrito-container");
    const spanTotal = document.getElementById("total-precio");
    contenedor.innerHTML = ""; // Limpiar "Cargando..."
    let precioTotalCalculado = 0;
    
    try {
        const res = await fetch(`${API_URL}/api/carrito`, {
            method: "GET",
            credentials: "include"  
        });
        const data = await res.json();

        if (!data.exito || data.items.length === 0) {
            contenedor.innerHTML = "<p>Tu carrito está vacío.</p>";
            spanTotal.textContent = "$0.00";
            return;
        }

        // data.items es: [{'id_pokemon': 25, 'cantidad': 2}, ...]
        for (let item of data.items) {
            const pokeRes = await fetch(`${POKEAPI_URL}/${item.id_pokemon}`);
            if (pokeRes.ok) {
                const pokeData = await pokeRes.json();
                const subtotal = item.cantidad * PRECIO_POKEMON;
                precioTotalCalculado += subtotal; // Sumar al total
                
                const card = document.createElement("div");
                card.className = "card";
                card.innerHTML = `
                    <h3>${pokeData.name}</h3>
                    <img src="${pokeData.sprites.front_default}" alt="${pokeData.name}">
                    <p>Cantidad: ${item.cantidad}</p>
                    <p>Precio Unit.: $${PRECIO_POKEMON.toFixed(2)}</p>
                    <p><strong>Subtotal: $${subtotal.toFixed(2)}</strong></p>
                    <button class="btn-remove-cart" data-id="${pokeData.id}">❌ Quitar</button>
                    `;
                contenedor.appendChild(card);
            }
        }
        // Actualizar el total en el HTML
        spanTotal.textContent = `$${precioTotalCalculado.toFixed(2)}`;
        
    } catch (error) {
        contenedor.innerHTML = "<p>Error al cargar el carrito.</p>";
    }
}

// 3. Delegación de eventos para "Quitar" y "Comprar Todo"
document.addEventListener("click", async (e) => {
    
    // -- Botón Quitar --
    if (e.target.classList.contains("btn-remove-cart")) {
        const pokemonId = e.target.dataset.id;
        if (!confirm(`¿Seguro que quieres quitar este Pokémon del carrito?`)) {
            return;
        }
        try {
            const res = await fetch(`${API_URL}/api/carrito/${pokemonId}`, {
                method: "DELETE",
                credentials: "include"
            });
            const data = await res.json();
            alert(data.mensaje);
            if (data.exito) {
                cargarCarrito(); // Recargar el carrito
            }
        } catch (error) {
            alert("Error de conexión al eliminar.");
        }
    }
    
    // -- Botón Comprar Todo (Checkout) --
    if (e.target.id === "btn-checkout") {
        const mensajeEl = document.getElementById("mensaje-checkout");
        if (!confirm(`¿Estás seguro de que quieres comprar todo el carrito?`)) {
            return;
        }
        
        mensajeEl.textContent = "Procesando compra...";
        mensajeEl.style.color = "orange";
        
        try {
            const res = await fetch(`${API_URL}/checkout`, {
                method: "POST",
                credentials: "include"
            });
            const data = await res.json();

            if (data.exito) {
                mensajeEl.textContent = `${data.mensaje} Tu nuevo saldo es $${data.nuevo_saldo.toFixed(2)}`;
                mensajeEl.style.color = "green";
                alert("¡Compra exitosa!");
                cargarCarrito(); // El carrito ahora estará vacío
            } else {
                mensajeEl.textContent = data.mensaje; // Ej. "Saldo insuficiente"
                mensajeEl.style.color = "red";
                alert(`Error: ${data.mensaje}`);
            }
        } catch (error) {
            mensajeEl.textContent = "Error de conexión al procesar la compra.";
            mensajeEl.style.color = "red";
        }
    }
});